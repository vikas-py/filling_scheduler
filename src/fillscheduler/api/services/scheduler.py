"""
Scheduler service for API.

Wraps the core scheduling logic and provides async interface for API endpoints.
Handles conversion between API schemas and core models.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from fillscheduler.config import AppConfig
from fillscheduler.models import Activity, Lot
from fillscheduler.scheduler import plan_schedule

# Thread pool for running CPU-bound scheduling tasks
_executor = ThreadPoolExecutor(max_workers=4)


def _convert_lot_dict_to_lot(lot_data: dict[str, Any]) -> Lot:
    """
    Convert API lot dictionary to core Lot model.

    Args:
        lot_data: Dictionary with keys: lot_id, lot_type, vials, fill_hours

    Returns:
        Lot object
    """
    return Lot(
        lot_id=str(lot_data.get("lot_id", "")),
        lot_type=str(lot_data.get("lot_type", "")),
        vials=int(lot_data.get("vials", 0)),
        fill_hours=float(lot_data.get("fill_hours", 0.0)),
    )


def _convert_activity_to_dict(activity: Activity) -> dict[str, Any]:
    """
    Convert core Activity model to API dictionary.

    Args:
        activity: Activity object

    Returns:
        Dictionary with activity data
    """
    return {
        "start": activity.start.isoformat(),
        "end": activity.end.isoformat(),
        "kind": activity.kind,
        "lot_id": activity.lot_id,
        "lot_type": activity.lot_type,
        "note": activity.note,
        "duration_hours": (activity.end - activity.start).total_seconds() / 3600.0,
    }


def _create_config_from_dict(config_data: dict[str, Any] | None = None) -> AppConfig:
    """
    Create AppConfig from API configuration dictionary.

    Args:
        config_data: Optional dictionary with config parameters

    Returns:
        AppConfig object
    """
    if config_data is None:
        return AppConfig()

    cfg = AppConfig()

    # Update config with provided values
    if "WINDOW_HOURS" in config_data:
        cfg.WINDOW_HOURS = float(config_data["WINDOW_HOURS"])
    if "CLEAN_HOURS" in config_data:
        cfg.CLEAN_HOURS = float(config_data["CLEAN_HOURS"])
    if "CHANGEOVER_MATRIX" in config_data:
        cfg.CHANGEOVER_MATRIX = config_data["CHANGEOVER_MATRIX"]  # type: ignore[attr-defined]
    if "CHANGEOVER_DEFAULT" in config_data:
        cfg.CHANGEOVER_DEFAULT = float(config_data["CHANGEOVER_DEFAULT"])  # type: ignore[attr-defined]

    return cfg


def _run_scheduler_sync(
    lots: list[Lot], start_time: datetime, strategy: str, config: AppConfig
) -> tuple[list[Activity], float, dict[str, Any]]:
    """
    Run the scheduler synchronously (CPU-bound operation).

    Args:
        lots: List of Lot objects
        start_time: Schedule start time
        strategy: Strategy name
        config: AppConfig object

    Returns:
        Tuple of (activities, makespan, kpis)
    """
    return plan_schedule(lots, start_time, config, strategy)


async def run_schedule(
    lots_data: list[dict[str, Any]],
    start_time: datetime,
    strategy: str = "smart-pack",
    config_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run scheduling algorithm asynchronously.

    Args:
        lots_data: List of lot dictionaries
        start_time: Schedule start time
        strategy: Strategy name (default: "smart-pack")
        config_data: Optional configuration dictionary

    Returns:
        Dictionary with:
        - activities: List of activity dictionaries
        - makespan: Makespan in hours
        - kpis: Dictionary of KPI values
        - strategy: Strategy used
        - lots_count: Number of lots scheduled
    """
    # Convert API data to core models
    lots = [_convert_lot_dict_to_lot(lot) for lot in lots_data]
    config = _create_config_from_dict(config_data)

    # Run scheduling in thread pool (CPU-bound)
    loop = asyncio.get_event_loop()
    activities, makespan, kpis = await loop.run_in_executor(
        _executor, _run_scheduler_sync, lots, start_time, strategy, config
    )

    # Convert results to API format
    activities_data = [_convert_activity_to_dict(a) for a in activities]

    return {
        "activities": activities_data,
        "makespan": makespan,
        "kpis": kpis,
        "strategy": strategy,
        "lots_count": len(lots),
        "activities_count": len(activities),
        "fill_count": sum(1 for a in activities if a.kind == "FILL"),
        "changeover_count": sum(1 for a in activities if a.kind == "CHANGEOVER"),
        "clean_count": sum(1 for a in activities if a.kind == "CLEAN"),
    }


async def validate_lots_data(lots_data: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Validate lots data without running the scheduler.

    Args:
        lots_data: List of lot dictionaries

    Returns:
        Dictionary with validation results:
        - valid: True if all lots are valid
        - errors: List of error messages
        - warnings: List of warning messages
        - lots_count: Number of lots
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not lots_data:
        errors.append("No lots provided")
        return {"valid": False, "errors": errors, "warnings": warnings, "lots_count": 0}

    # Validate each lot
    for i, lot in enumerate(lots_data):
        # Check required fields
        required_fields = ["lot_id", "lot_type", "vials", "fill_hours"]
        for field in required_fields:
            if field not in lot:
                errors.append(f"Lot {i}: Missing required field '{field}'")

        # Validate data types and values
        if "vials" in lot:
            try:
                vials = int(lot["vials"])
                if vials <= 0:
                    errors.append(f"Lot {i}: vials must be positive (got {vials})")
            except (ValueError, TypeError):
                errors.append(f"Lot {i}: vials must be a number (got {lot['vials']})")

        if "fill_hours" in lot:
            try:
                fill_hours = float(lot["fill_hours"])
                if fill_hours <= 0:
                    errors.append(f"Lot {i}: fill_hours must be positive (got {fill_hours})")
                elif fill_hours > 100:
                    warnings.append(f"Lot {i}: fill_hours is very large ({fill_hours}h)")
            except (ValueError, TypeError):
                errors.append(f"Lot {i}: fill_hours must be a number (got {lot['fill_hours']})")

        # Check lot_id uniqueness
        lot_ids = [lot.get("lot_id") for lot in lots_data]
        duplicates = [lid for lid in set(lot_ids) if lot_ids.count(lid) > 1]
        if duplicates:
            warnings.append(f"Duplicate lot_ids found: {duplicates}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "lots_count": len(lots_data),
    }


def get_available_strategies() -> list[dict[str, str]]:
    """
    Get list of available scheduling strategies.

    Returns:
        List of dictionaries with strategy information:
        - name: Strategy name
        - aliases: List of alternative names
        - description: Strategy description
    """
    strategies = [
        {
            "name": "smart-pack",
            "aliases": ["smart_pack", "smartpack", "smart"],
            "description": "Intelligent packing with type-aware bin packing (default)",
        },
        {
            "name": "spt-pack",
            "aliases": ["spt_pack", "sptpack", "spt"],
            "description": "Shortest Processing Time first",
        },
        {
            "name": "lpt-pack",
            "aliases": ["lpt_pack", "lptpack", "lpt"],
            "description": "Longest Processing Time first",
        },
        {
            "name": "cfs-pack",
            "aliases": ["cfs_pack", "cfspack", "cfs"],
            "description": "Customer First Scheduling",
        },
        {
            "name": "hybrid-pack",
            "aliases": ["hybrid_pack", "hybrid"],
            "description": "Hybrid strategy combining multiple approaches",
        },
        {
            "name": "milp-opt",
            "aliases": ["milp_opt", "milpopt", "milp"],
            "description": "MILP optimization (requires PuLP)",
        },
    ]
    return strategies


def calculate_schedule_stats(activities: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calculate additional statistics for a schedule.

    Args:
        activities: List of activity dictionaries

    Returns:
        Dictionary with statistics:
        - utilization: Fill time / total time
        - avg_changeover: Average changeover time
        - max_changeover: Maximum changeover time
        - clean_percentage: Clean time / total time
    """
    if not activities:
        return {}

    fill_activities = [a for a in activities if a["kind"] == "FILL"]
    changeover_activities = [a for a in activities if a["kind"] == "CHANGEOVER"]
    clean_activities = [a for a in activities if a["kind"] == "CLEAN"]

    total_fill = sum(a["duration_hours"] for a in fill_activities)
    total_changeover = sum(a["duration_hours"] for a in changeover_activities)
    total_clean = sum(a["duration_hours"] for a in clean_activities)

    # Calculate total time from first start to last end
    start_time = datetime.fromisoformat(activities[0]["start"])
    end_time = datetime.fromisoformat(activities[-1]["end"])
    total_time = (end_time - start_time).total_seconds() / 3600.0

    stats = {
        "utilization": (total_fill / total_time * 100) if total_time > 0 else 0,
        "fill_hours": total_fill,
        "changeover_hours": total_changeover,
        "clean_hours": total_clean,
        "total_hours": total_time,
        "clean_percentage": (total_clean / total_time * 100) if total_time > 0 else 0,
    }

    if changeover_activities:
        changeover_durations = [a["duration_hours"] for a in changeover_activities]
        stats["avg_changeover"] = sum(changeover_durations) / len(changeover_durations)
        stats["max_changeover"] = max(changeover_durations)
        stats["min_changeover"] = min(changeover_durations)

    return stats
