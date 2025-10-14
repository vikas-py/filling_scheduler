"""
Schedule API endpoints.

Provides REST API for:
- Creating schedules
- Retrieving schedule details
- Listing user schedules
- Deleting schedules
- Exporting schedules
- Validating lots data
- Getting available strategies
"""

import csv
import io
import json as json_module
from datetime import datetime

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from fillscheduler.api.database.session import get_db
from fillscheduler.api.dependencies import get_current_active_user
from fillscheduler.api.models.database import Schedule, ScheduleResult, User
from fillscheduler.api.models.schemas import (
    MessageResponse,
    ScheduleDetailResponse,
    ScheduleListResponse,
    ScheduleRequest,
    ScheduleResponse,
)
from fillscheduler.api.services.scheduler import (
    calculate_schedule_stats,
    get_available_strategies,
    run_schedule,
    validate_lots_data,
)

router = APIRouter()


async def _run_schedule_background(
    schedule_id: int,
    lots_data: list[dict],
    start_time: datetime,
    strategy: str,
    config_data: dict | None,
):
    """
    Background task to run scheduling algorithm.

    Updates schedule status and creates result in database.
    Creates its own database session to avoid session issues.
    """
    import logging
    import time
    import traceback

    from fillscheduler.api.database.session import SessionLocal
    from fillscheduler.api.websocket.tracker import progress_tracker

    logger = logging.getLogger(__name__)
    db = SessionLocal()

    # Create progress tracker for WebSocket updates
    tracker = progress_tracker.create_schedule_tracker(schedule_id, len(lots_data))

    try:
        # FIX Bug #1: Retry logic for race condition with commit
        max_retries = 3
        schedule = None
        for attempt in range(max_retries):
            schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
            if schedule:
                break
            logger.warning(f"Schedule {schedule_id} not found, attempt {attempt + 1}/{max_retries}")
            time.sleep(0.1 * (attempt + 1))  # Exponential backoff

        if not schedule:
            logger.error(f"Schedule {schedule_id} not found after {max_retries} retries")
            await tracker.fail("Schedule not found in database", "NOT_FOUND")
            return

        try:
            # Update status to running
            schedule.status = "running"
            schedule.started_at = datetime.utcnow()
            db.commit()

            # Send initial progress update (0%)
            await tracker.update(lots_completed=0, message="Starting schedule execution...")

            # Run scheduler
            result = await run_schedule(lots_data, start_time, strategy, config_data)

            # Send progress update after scheduling (80%)
            await tracker.update(
                lots_completed=int(len(lots_data) * 0.8),
                message="Schedule complete, saving results...",
            )

            # Calculate additional stats
            stats = calculate_schedule_stats(result["activities"])

            # Create schedule result (serialize JSON fields)
            import json as json_module

            schedule_result = ScheduleResult(
                schedule_id=schedule_id,
                makespan=result["makespan"],
                utilization=stats.get("utilization", 0.0),
                changeovers=result["changeover_count"],
                lots_scheduled=result["lots_count"],
                window_violations=0,  # TODO: Calculate window violations
                kpis_json=json_module.dumps(result["kpis"]),
                activities_json=json_module.dumps(result["activities"]),
            )
            db.add(schedule_result)

            # Update schedule status
            schedule.status = "completed"
            schedule.completed_at = datetime.utcnow()
            db.commit()

            # Send completion update via WebSocket
            await tracker.complete(
                makespan=result["makespan"],
                utilization=stats.get("utilization", 0.0),
                changeovers=result["changeover_count"],
                lots_scheduled=result["lots_count"],
            )

        except ValueError as e:
            # FIX Bug #6: Distinguish validation errors from bugs
            logger.warning(f"Schedule {schedule_id} validation error: {e}")
            schedule.status = "failed"
            schedule.error_message = f"Validation Error: {str(e)}"
            schedule.completed_at = datetime.utcnow()
            db.commit()

            # Send failure update via WebSocket
            await tracker.fail(str(e), "VALIDATION_ERROR")

        except FileNotFoundError as e:
            # Missing resources (expected)
            logger.error(f"Schedule {schedule_id} resource not found: {e}")
            schedule.status = "failed"
            schedule.error_message = f"Resource Not Found: {str(e)}"
            schedule.completed_at = datetime.utcnow()
            db.commit()

            # Send failure update via WebSocket
            await tracker.fail(str(e), "FILE_NOT_FOUND")

        except Exception as e:
            # FIX Bug #6: Log full traceback for unexpected errors
            logger.exception(f"Schedule {schedule_id} unexpected error: {e}")
            full_traceback = traceback.format_exc()
            schedule.status = "failed"
            schedule.error_message = f"{type(e).__name__}: {str(e)[:500]}"
            # Store traceback in error_message if short enough, otherwise truncate
            if len(full_traceback) < 1000:
                schedule.error_message += f"\n\nTraceback:\n{full_traceback}"
            schedule.completed_at = datetime.utcnow()
            db.commit()

            # Send failure update via WebSocket
            await tracker.fail(schedule.error_message, type(e).__name__)

    finally:
        db.close()
        # Remove tracker after completion
        progress_tracker.remove_schedule_tracker(schedule_id)


@router.post("/schedule", response_model=ScheduleResponse, status_code=202)
async def create_schedule_from_file(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    strategy: str = Form(...),
    config: str = Form(...),
    csv_file: UploadFile = File(...),
    description: str | None = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ScheduleResponse:
    """
    Create a new schedule from CSV file upload.

    Accepts a CSV file with lots data and configuration.
    Returns immediately with schedule ID and status.

    - **name**: Schedule name
    - **strategy**: Strategy name (LPT, SPT, CFS, SMART, HYBRID, MILP)
    - **config**: JSON string with configuration parameters
    - **csv_file**: CSV file with columns: Lot ID, Type, Vials
    - **description**: Optional description

    Returns 202 Accepted with schedule ID. Check status with GET /schedule/{id}.
    """
    # Validate file type
    if not csv_file.filename or not csv_file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only CSV files are allowed."
        )

    # Read and parse CSV file
    try:
        content = await csv_file.read()
        csv_text = content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_text))

        # Convert CSV rows to lots_data format
        # Default fill rate: 19,920 vials/hour (332 vials/min * 60 min/h)
        FILL_RATE_VPH = 19920.0
        
        lots_data = []
        for row in csv_reader:
            # Map CSV columns to expected format
            # CSV has: "Lot ID", "Type", "Vials"
            vials = int(row.get("Vials", 0))
            lot = {
                "lot_id": row.get("Lot ID", "").strip(),
                "lot_type": row.get("Type", "").strip(),
                "vials": vials,
                "fill_hours": vials / FILL_RATE_VPH,  # Calculate fill hours from vials
            }
            lots_data.append(lot)

        if not lots_data:
            raise HTTPException(status_code=400, detail="CSV file is empty or has no valid data")

    except UnicodeDecodeError as e:
        raise HTTPException(
            status_code=400, detail="Unable to decode CSV file. Please ensure it's UTF-8 encoded."
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data in CSV file: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV file: {str(e)}") from e

    # Parse config JSON
    try:
        config_dict = json_module.loads(config) if config else {}
    except json_module.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid config JSON: {str(e)}") from e

    # Validate lots data
    validation = await validate_lots_data(lots_data)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid lots data",
                "errors": validation["errors"],
                "warnings": validation["warnings"],
            },
        )

    # Create schedule record
    schedule = Schedule(
        user_id=current_user.id,
        name=name,
        description=description,
        strategy=strategy,
        status="pending",
        config_json=json_module.dumps(config_dict),
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    # Start background task with proper arguments
    background_tasks.add_task(
        _run_schedule_background,
        schedule.id,
        lots_data,
        datetime.utcnow(),  # start_time
        strategy,
        config_dict,  # config_data
    )

    return schedule


@router.post("/schedule/json", response_model=ScheduleResponse, status_code=202)
async def create_schedule(
    request: ScheduleRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new schedule with JSON lots data.

    Alternative endpoint that accepts lots data as JSON instead of CSV file.
    Useful for programmatic access or when lots data is already structured.

    - **name**: Optional schedule name
    - **lots_data**: List of lot dictionaries (lot_id, lot_type, vials, fill_hours)
    - **strategy**: Strategy name (default: smart-pack)
    - **config**: Optional configuration parameters
    - **start_time**: Schedule start time (default: now)

    Returns 202 Accepted with schedule ID. Check status with GET /schedule/{id}.

    NOTE: For CSV file uploads, use POST /schedule instead.
    """
    # Validate lots data
    validation = await validate_lots_data(request.lots_data)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid lots data",
                "errors": validation["errors"],
                "warnings": validation["warnings"],
            },
        )

    # Create schedule record
    import json as json_module

    schedule = Schedule(
        user_id=current_user.id,
        name=request.name or f"Schedule {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        strategy=request.strategy,
        status="pending",
        config_json=json_module.dumps(request.config or {}),
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    # FIX Bug #4: Parse start_time with proper timezone handling
    if request.start_time:
        try:
            from datetime import timezone

            # Parse with timezone awareness
            start_dt = datetime.fromisoformat(request.start_time)

            # Ensure timezone-aware
            if start_dt.tzinfo is None:
                import logging

                logging.getLogger(__name__).warning(
                    f"start_time has no timezone, assuming UTC: {request.start_time}"
                )
                start_dt = start_dt.replace(tzinfo=timezone.utc)

            # Convert to UTC for consistency (remove tzinfo for naive datetime)
            start_dt = start_dt.astimezone(timezone.utc).replace(tzinfo=None)

        except (ValueError, AttributeError) as e:
            import logging

            logging.getLogger(__name__).error(
                f"Invalid start_time format: {request.start_time}, error: {e}"
            )
            raise HTTPException(
                status_code=400,
                detail="Invalid start_time format. Use ISO 8601 format with timezone "
                "(e.g., '2025-10-13T10:00:00+00:00' or '2025-10-13T10:00:00Z')",
            ) from e
    else:
        start_dt = datetime.utcnow()

    # Start background task
    background_tasks.add_task(
        _run_schedule_background,
        schedule.id,
        request.lots_data,
        start_dt,
        request.strategy,
        request.config,
    )

    return ScheduleResponse(
        id=schedule.id,
        name=schedule.name,
        strategy=schedule.strategy,
        status=schedule.status,
        created_at=schedule.created_at,
        started_at=schedule.started_at,
        completed_at=schedule.completed_at,
        error_message=schedule.error_message,
    )


@router.get("/schedule/{schedule_id}", response_model=ScheduleDetailResponse)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get schedule details including results.

    Returns schedule information, status, and results (if completed).
    """
    schedule = (
        db.query(Schedule)
        .filter(Schedule.id == schedule_id, Schedule.user_id == current_user.id)
        .first()
    )

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Get result if available
    result = db.query(ScheduleResult).filter(ScheduleResult.schedule_id == schedule_id).first()

    response = ScheduleDetailResponse(
        id=schedule.id,
        name=schedule.name,
        strategy=schedule.strategy,
        status=schedule.status,
        created_at=schedule.created_at,
        started_at=schedule.started_at,
        completed_at=schedule.completed_at,
        error_message=schedule.error_message,
        result=None,
    )

    if result:
        import json as json_module

        from fillscheduler.api.models.schemas import ScheduleResultResponse

        response.result = ScheduleResultResponse(
            makespan=result.makespan,
            utilization=result.utilization,
            changeovers=result.changeovers,
            lots_scheduled=result.lots_scheduled,
            window_violations=result.window_violations,
            kpis_json=json_module.loads(result.kpis_json) if result.kpis_json else {},
            activities_json=(
                json_module.loads(result.activities_json) if result.activities_json else []
            ),
        )

    return response


@router.get("/schedules", response_model=ScheduleListResponse)
async def list_schedules(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    strategy: str | None = Query(None, description="Filter by strategy"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List user's schedules with pagination and filters.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status**: Filter by status (pending, running, completed, failed)
    - **strategy**: Filter by strategy name
    """
    # Build query
    query = db.query(Schedule).filter(Schedule.user_id == current_user.id)

    if status:
        query = query.filter(Schedule.status == status)
    if strategy:
        query = query.filter(Schedule.strategy == strategy)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    schedules = query.order_by(Schedule.created_at.desc()).offset(offset).limit(page_size).all()

    # Convert to response
    schedule_responses = [
        ScheduleResponse(
            id=s.id,
            name=s.name,
            strategy=s.strategy,
            status=s.status,
            created_at=s.created_at,
            started_at=s.started_at,
            completed_at=s.completed_at,
            error_message=s.error_message,
        )
        for s in schedules
    ]

    return ScheduleListResponse(
        schedules=schedule_responses, total=total, page=page, page_size=page_size
    )


@router.delete("/schedule/{schedule_id}", response_model=MessageResponse)
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a schedule.

    Deletes the schedule and its results from the database.
    Only the owner can delete their schedules.
    """
    schedule = (
        db.query(Schedule)
        .filter(Schedule.id == schedule_id, Schedule.user_id == current_user.id)
        .first()
    )

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # FIX Bug #2: Use CASCADE delete (defined in model relationship)
    # No need to manually delete ScheduleResult - SQLAlchemy handles it
    # The model has: cascade="all, delete-orphan"
    try:
        db.delete(schedule)
        db.commit()
    except Exception as e:
        # Rollback on error to maintain consistency
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete schedule: {str(e)}") from e

    return MessageResponse(message=f"Schedule {schedule_id} deleted successfully")


@router.get("/schedule/{schedule_id}/export")
async def export_schedule(
    schedule_id: int,
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Export schedule to JSON or CSV format.

    - **format**: Export format (json or csv)
    """
    schedule = (
        db.query(Schedule)
        .filter(Schedule.id == schedule_id, Schedule.user_id == current_user.id)
        .first()
    )

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if schedule.status != "completed":
        raise HTTPException(status_code=400, detail="Schedule not completed yet")

    result = db.query(ScheduleResult).filter(ScheduleResult.schedule_id == schedule_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Schedule result not found")

    import json as json_module

    if format == "json":
        return JSONResponse(
            content={
                "schedule": {
                    "id": schedule.id,
                    "name": schedule.name,
                    "strategy": schedule.strategy,
                    "status": schedule.status,
                    "created_at": schedule.created_at.isoformat(),
                    "completed_at": (
                        schedule.completed_at.isoformat() if schedule.completed_at else None
                    ),
                },
                "results": {
                    "makespan": result.makespan,
                    "utilization": result.utilization,
                    "changeovers": result.changeovers,
                    "lots_scheduled": result.lots_scheduled,
                    "kpis": json_module.loads(result.kpis_json) if result.kpis_json else {},
                    "activities": (
                        json_module.loads(result.activities_json) if result.activities_json else []
                    ),
                },
            }
        )

    elif format == "csv":
        # Convert activities to CSV format
        import csv
        import io

        activities_data = (
            json_module.loads(result.activities_json) if result.activities_json else []
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Start", "End", "Kind", "Lot ID", "Lot Type", "Note", "Duration (h)"])

        # Write activities
        for activity in activities_data:
            writer.writerow(
                [
                    activity["start"],
                    activity["end"],
                    activity["kind"],
                    activity.get("lot_id", ""),
                    activity.get("lot_type", ""),
                    activity.get("note", ""),
                    activity.get("duration_hours", 0.0),
                ]
            )

        # Return CSV response
        from fastapi.responses import Response

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=schedule_{schedule_id}.csv"},
        )


@router.post("/schedule/validate", response_model=dict)
async def validate_schedule_data(
    lots_data: list[dict], current_user: User = Depends(get_current_active_user)
):
    """
    Validate lots data without creating a schedule.

    Checks lots data for:
    - Required fields
    - Valid data types
    - Positive values
    - Duplicate lot IDs (warning)

    Returns validation results with errors and warnings.
    """
    validation = await validate_lots_data(lots_data)
    return validation


@router.get("/strategies", response_model=list[dict])
async def list_strategies(current_user: User = Depends(get_current_active_user)):
    """
    Get list of available scheduling strategies.

    FIX Bug #3: Added authentication requirement.

    Returns information about each strategy:
    - Name
    - Aliases
    - Description

    Requires authentication.
    """
    strategies = get_available_strategies()
    return strategies
