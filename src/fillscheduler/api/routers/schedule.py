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

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
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
    from fillscheduler.api.database.session import SessionLocal

    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return

        try:
            # Update status to running
            schedule.status = "running"
            schedule.started_at = datetime.utcnow()
            db.commit()

            # Run scheduler
            result = await run_schedule(lots_data, start_time, strategy, config_data)

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

        except Exception as e:
            # Update schedule with error
            schedule.status = "failed"
            schedule.error_message = str(e)
            schedule.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/schedule", response_model=ScheduleResponse, status_code=202)
async def create_schedule(
    request: ScheduleRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new schedule.

    Accepts lots data and configuration, starts scheduling in background.
    Returns immediately with schedule ID and status.

    - **name**: Optional schedule name
    - **lots_data**: List of lot dictionaries (lot_id, lot_type, vials, fill_hours)
    - **strategy**: Strategy name (default: smart-pack)
    - **config**: Optional configuration parameters
    - **start_time**: Schedule start time (default: now)

    Returns 202 Accepted with schedule ID. Check status with GET /schedule/{id}.
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

    # Parse start_time if provided
    if request.start_time:
        try:
            start_dt = datetime.fromisoformat(request.start_time)
        except (ValueError, AttributeError):
            start_dt = datetime.utcnow()
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

    # Delete associated result first
    db.query(ScheduleResult).filter(ScheduleResult.schedule_id == schedule_id).delete()

    # Delete schedule
    db.delete(schedule)
    db.commit()

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
async def list_strategies():
    """
    Get list of available scheduling strategies.

    Returns information about each strategy:
    - Name
    - Aliases
    - Description
    """
    strategies = get_available_strategies()
    return strategies
