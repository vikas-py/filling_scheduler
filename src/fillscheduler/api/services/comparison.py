"""
Comparison service for running and comparing multiple scheduling strategies.

This service allows users to run multiple strategies in parallel on the same
lots data and compare the results to find the best strategy for their use case.
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime
from typing import Any, cast

from fillscheduler.api.services.scheduler import (
    _convert_lot_dict_to_lot,
    _create_config_from_dict,
    _run_scheduler_sync,
)


def compute_lots_hash(lots_data: list[dict[str, Any]]) -> str:
    """
    Compute SHA256 hash of lots data for caching.

    Args:
        lots_data: List of lot dictionaries

    Returns:
        Hex string of SHA256 hash
    """
    # Sort and normalize data for consistent hashing
    normalized = json.dumps(lots_data, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()


async def run_single_strategy(
    lots_data: list[dict[str, Any]],
    start_time: datetime,
    strategy: str,
    config_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run a single strategy and return results.

    Args:
        lots_data: List of lot dictionaries
        start_time: Schedule start datetime
        strategy: Strategy name
        config_data: Optional configuration dictionary

    Returns:
        Dictionary with results or error information
    """
    start_exec = time.time()

    try:
        # Convert lots data to Lot objects
        lots = [_convert_lot_dict_to_lot(lot) for lot in lots_data]

        # Create config
        config = _create_config_from_dict(config_data)

        # Run scheduler in thread pool
        loop = asyncio.get_event_loop()
        from concurrent.futures import ThreadPoolExecutor

        # Use a separate executor for each strategy to avoid blocking
        with ThreadPoolExecutor(max_workers=1) as executor:
            activities, makespan, kpis = await loop.run_in_executor(
                executor, _run_scheduler_sync, lots, start_time, strategy, config
            )

        execution_time = time.time() - start_exec

        # Convert activities to dictionaries
        from fillscheduler.api.services.scheduler import _convert_activity_to_dict

        activities_dicts = [_convert_activity_to_dict(act) for act in activities]

        # Calculate additional stats
        from fillscheduler.api.services.scheduler import calculate_schedule_stats

        stats = calculate_schedule_stats(activities_dicts)

        return {
            "status": "completed",
            "makespan": makespan,
            "utilization": stats.get("utilization", 0.0),
            "changeovers": len([a for a in activities if a.kind == "changeover"]),
            "lots_scheduled": len([a for a in activities if a.kind == "fill"]),
            "window_violations": 0,  # TODO: Calculate from activities
            "kpis": kpis,
            "activities": activities_dicts,
            "execution_time": execution_time,
            "error_message": None,
        }

    except Exception as e:
        execution_time = time.time() - start_exec
        return {
            "status": "failed",
            "makespan": None,
            "utilization": None,
            "changeovers": None,
            "lots_scheduled": None,
            "window_violations": None,
            "kpis": None,
            "activities": None,
            "execution_time": execution_time,
            "error_message": str(e),
        }


async def run_comparison(
    lots_data: list[dict[str, Any]],
    strategies: list[str],
    start_time: datetime,
    config_data: dict[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Run multiple strategies in parallel and return all results.

    Args:
        lots_data: List of lot dictionaries
        strategies: List of strategy names to compare
        start_time: Schedule start datetime
        config_data: Optional configuration dictionary

    Returns:
        Dictionary with strategy results
    """
    # Run all strategies in parallel
    tasks = [
        run_single_strategy(lots_data, start_time, strategy, config_data) for strategy in strategies
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Convert exceptions to error results
    strategy_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            strategy_results.append(
                {
                    "strategy": strategies[i],
                    "status": "failed",
                    "error_message": str(result),
                    "makespan": None,
                    "utilization": None,
                    "changeovers": None,
                    "lots_scheduled": None,
                    "window_violations": None,
                    "kpis": None,
                    "activities": None,
                    "execution_time": None,
                }
            )
        else:
            # Type narrowing: result is dict[str, Any] here (not an Exception)
            result_dict = cast(dict[str, Any], result)
            strategy_results.append({"strategy": strategies[i], **result_dict})

    return {"results": strategy_results}


def calculate_best_strategy(results: list[dict[str, Any]]) -> str | None:
    """
    Calculate the best strategy based on results.

    Priority:
    1. Minimize makespan (primary objective)
    2. Maximize utilization (secondary)
    3. Minimize changeovers (tertiary)

    Args:
        results: List of strategy result dictionaries

    Returns:
        Name of best strategy or None if no valid results
    """
    # Filter to completed results only
    completed = [
        r for r in results if r.get("status") == "completed" and r.get("makespan") is not None
    ]

    if not completed:
        return None

    # Sort by: makespan (asc), utilization (desc), changeovers (asc)
    # Normalize to handle different scales
    def score(result):
        makespan = result.get("makespan", float("inf"))
        utilization = result.get("utilization", 0.0)
        changeovers = result.get("changeovers", float("inf"))

        # Lower score is better
        # Makespan weight: 10x (most important)
        # Utilization weight: -5x (higher is better, so negative)
        # Changeover weight: 1x
        return (makespan * 10) - (utilization * 5) + changeovers

    best = min(completed, key=score)
    return best.get("strategy")


def get_comparison_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Get summary statistics for a comparison.

    Args:
        results: List of strategy result dictionaries

    Returns:
        Dictionary with summary statistics
    """
    completed = [
        r for r in results if r.get("status") == "completed" and r.get("makespan") is not None
    ]
    failed = [r for r in results if r.get("status") == "failed"]

    if not completed:
        return {
            "total_strategies": len(results),
            "completed": 0,
            "failed": len(failed),
            "best_strategy": None,
            "best_makespan": None,
            "worst_makespan": None,
            "avg_makespan": None,
            "makespan_range": None,
        }

    makespans = [r["makespan"] for r in completed]
    best_makespan = min(makespans)
    worst_makespan = max(makespans)
    avg_makespan = sum(makespans) / len(makespans)

    return {
        "total_strategies": len(results),
        "completed": len(completed),
        "failed": len(failed),
        "best_strategy": calculate_best_strategy(results),
        "best_makespan": best_makespan,
        "worst_makespan": worst_makespan,
        "avg_makespan": avg_makespan,
        "makespan_range": worst_makespan - best_makespan,
        "makespan_improvement": (
            ((worst_makespan - best_makespan) / worst_makespan * 100) if worst_makespan > 0 else 0
        ),
    }
