"""
Comparison router for comparing multiple scheduling strategies.

Provides endpoints to:
- Create comparisons (run multiple strategies in parallel)
- Get comparison results
- List comparisons
- Delete comparisons
"""

import json as json_module
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from fillscheduler.api.dependencies import get_current_active_user, get_db
from fillscheduler.api.models.database import Comparison, ComparisonResult, User
from fillscheduler.api.models.schemas import (
    ComparisonDetailResponse,
    ComparisonListResponse,
    ComparisonRequest,
    ComparisonResponse,
    ComparisonStrategyResult,
    MessageResponse,
)
from fillscheduler.api.services.comparison import (
    calculate_best_strategy,
    compute_lots_hash,
    run_comparison,
)
from fillscheduler.api.services.scheduler import get_available_strategies, validate_lots_data

router = APIRouter()


async def _run_comparison_background(
    comparison_id: int,
    lots_data: list[dict],
    strategies: list[str],
    start_time: datetime,
    config_data: dict | None = None,
):
    """
    Background task to run comparison across multiple strategies.

    Args:
        comparison_id: ID of the comparison
        lots_data: List of lot dictionaries
        strategies: List of strategy names
        start_time: Schedule start datetime
        config_data: Optional configuration
    """
    from fillscheduler.api.database.session import SessionLocal

    db = SessionLocal()
    try:
        # Get comparison
        comparison = db.query(Comparison).filter(Comparison.id == comparison_id).first()
        if not comparison:
            return

        # Update status to running
        comparison.status = "running"
        comparison.started_at = datetime.utcnow()
        db.commit()

        # Run comparison
        result = await run_comparison(lots_data, strategies, start_time, config_data)

        # Save results for each strategy
        for strategy_result in result["results"]:
            comparison_result = ComparisonResult(
                comparison_id=comparison_id,
                strategy=strategy_result["strategy"],
                status=strategy_result["status"],
                error_message=strategy_result.get("error_message"),
                makespan=strategy_result.get("makespan"),
                utilization=strategy_result.get("utilization"),
                changeovers=strategy_result.get("changeovers"),
                lots_scheduled=strategy_result.get("lots_scheduled"),
                window_violations=strategy_result.get("window_violations"),
                kpis_json=(
                    json_module.dumps(strategy_result["kpis"])
                    if strategy_result.get("kpis")
                    else None
                ),
                activities_json=(
                    json_module.dumps(strategy_result["activities"])
                    if strategy_result.get("activities")
                    else None
                ),
                execution_time=strategy_result.get("execution_time"),
            )
            db.add(comparison_result)

        # Calculate best strategy
        best_strategy = calculate_best_strategy(result["results"])

        # Update comparison status
        comparison.status = "completed"
        comparison.best_strategy = best_strategy
        comparison.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        # Update comparison with error
        comparison.status = "failed"
        comparison.error_message = str(e)
        comparison.completed_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


@router.post("/compare", response_model=ComparisonResponse, status_code=202)
async def create_comparison(
    request: ComparisonRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a comparison to run multiple strategies in parallel.

    This endpoint:
    1. Validates the lots data
    2. Validates all strategy names
    3. Creates a comparison record
    4. Starts background task to run all strategies
    5. Returns immediately with 202 Accepted

    The comparison runs asynchronously. Use GET /compare/{id} to check status.
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

    # Validate all strategies
    available_strategies = get_available_strategies()
    available_names = [s["name"] for s in available_strategies]
    for strategy in request.strategies:
        if strategy not in available_names:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy '{strategy}'. Available strategies: {', '.join(available_names)}",
            )

    # Check for duplicate strategies
    if len(request.strategies) != len(set(request.strategies)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate strategies in request. Each strategy should appear only once.",
        )

    # Parse start_time if provided
    if request.start_time:
        try:
            start_dt = datetime.fromisoformat(request.start_time)
        except (ValueError, AttributeError):
            start_dt = datetime.utcnow()
    else:
        start_dt = datetime.utcnow()

    # Compute lots hash for caching/deduplication
    lots_hash = compute_lots_hash(request.lots_data)

    # Create comparison record
    comparison = Comparison(
        user_id=current_user.id,
        name=request.name or f"Comparison {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        lots_data_hash=lots_hash,
        lots_data_json=json_module.dumps(request.lots_data),
        strategies=json_module.dumps(request.strategies),
        status="pending",
        config_json=json_module.dumps(request.config or {}),
    )
    db.add(comparison)
    db.commit()
    db.refresh(comparison)

    # Start background task
    background_tasks.add_task(
        _run_comparison_background,
        comparison.id,
        request.lots_data,
        request.strategies,
        start_dt,
        request.config,
    )

    return ComparisonResponse(
        id=comparison.id,
        name=comparison.name,
        strategies=json_module.loads(comparison.strategies),
        status=comparison.status,
        created_at=comparison.created_at,
        started_at=comparison.started_at,
        completed_at=comparison.completed_at,
    )


@router.get("/compare/{comparison_id}", response_model=ComparisonDetailResponse)
async def get_comparison(
    comparison_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get comparison details and results.

    Returns comparison metadata and results for all strategies.
    If comparison is still running, results will be partial or empty.
    """
    # Get comparison (verify ownership)
    comparison = (
        db.query(Comparison)
        .filter(Comparison.id == comparison_id, Comparison.user_id == current_user.id)
        .first()
    )

    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")

    # Get results
    results = (
        db.query(ComparisonResult).filter(ComparisonResult.comparison_id == comparison_id).all()
    )

    # Convert results to response format
    strategy_results = []
    for result in results:
        strategy_results.append(
            ComparisonStrategyResult(
                strategy=result.strategy,
                status=result.status,
                error_message=result.error_message,
                makespan=result.makespan,
                utilization=result.utilization,
                changeovers=result.changeovers,
                lots_scheduled=result.lots_scheduled,
                window_violations=result.window_violations,
                execution_time=result.execution_time,
                kpis_json=json_module.loads(result.kpis_json) if result.kpis_json else None,
                activities_json=(
                    json_module.loads(result.activities_json) if result.activities_json else None
                ),
            )
        )

    return ComparisonDetailResponse(
        id=comparison.id,
        name=comparison.name,
        strategies=json_module.loads(comparison.strategies),
        status=comparison.status,
        created_at=comparison.created_at,
        started_at=comparison.started_at,
        completed_at=comparison.completed_at,
        best_strategy=comparison.best_strategy,
        error_message=comparison.error_message,
        results=strategy_results if strategy_results else None,
    )


@router.get("/comparisons", response_model=ComparisonListResponse)
async def list_comparisons(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List user's comparisons with pagination and filtering.

    Query Parameters:
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)
    - status: Filter by status (pending, running, completed, failed)
    """
    # Build query
    query = db.query(Comparison).filter(Comparison.user_id == current_user.id)

    # Apply status filter
    if status:
        query = query.filter(Comparison.status == status)

    # Get total count
    total = query.count()

    # Apply pagination
    comparisons = (
        query.order_by(Comparison.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Calculate pages
    pages = (total + page_size - 1) // page_size

    # Convert to response format
    comparison_responses = []
    for comp in comparisons:
        comparison_responses.append(
            ComparisonResponse(
                id=comp.id,
                name=comp.name,
                strategies=json_module.loads(comp.strategies),
                status=comp.status,
                created_at=comp.created_at,
                started_at=comp.started_at,
                completed_at=comp.completed_at,
            )
        )

    return ComparisonListResponse(
        comparisons=comparison_responses, total=total, page=page, page_size=page_size, pages=pages
    )


@router.delete("/compare/{comparison_id}", response_model=MessageResponse)
async def delete_comparison(
    comparison_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a comparison and all its results.

    This operation is permanent and cannot be undone.
    Only the owner can delete a comparison.
    """
    # Get comparison (verify ownership)
    comparison = (
        db.query(Comparison)
        .filter(Comparison.id == comparison_id, Comparison.user_id == current_user.id)
        .first()
    )

    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")

    # Delete comparison (cascade will delete results)
    db.delete(comparison)
    db.commit()

    return MessageResponse(message=f"Comparison {comparison_id} deleted successfully")
