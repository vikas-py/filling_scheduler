"""
Progress Tracker.

Tracks progress of schedules and comparisons, broadcasts updates via WebSocket.
"""

import logging
import time

from fillscheduler.api.websocket.manager import connection_manager
from fillscheduler.api.websocket.protocol import (
    create_comparison_progress_message,
    create_schedule_completed_message,
    create_schedule_failed_message,
    create_schedule_progress_message,
)

logger = logging.getLogger(__name__)


class ScheduleProgress:
    """
    Track progress of a schedule execution.

    Provides methods to update progress and broadcast to WebSocket subscribers.
    """

    def __init__(self, schedule_id: int, total_lots: int):
        """
        Initialize schedule progress tracker.

        Args:
            schedule_id: Schedule ID
            total_lots: Total number of lots to schedule
        """
        self.schedule_id = schedule_id
        self.total_lots = total_lots
        self.lots_completed = 0
        self.current_lot: str | None = None
        self.start_time = time.time()
        self.status = "running"

    @property
    def channel(self) -> str:
        """Get WebSocket channel name for this schedule."""
        return f"schedule:{self.schedule_id}"

    @property
    def progress(self) -> float:
        """Calculate progress percentage (0-100)."""
        if self.total_lots == 0:
            return 0.0
        return min(100.0, (self.lots_completed / self.total_lots) * 100.0)

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time

    @property
    def estimated_remaining(self) -> float | None:
        """Estimate remaining time in seconds."""
        if self.lots_completed == 0 or self.total_lots == 0:
            return None

        avg_time_per_lot = self.elapsed_time / self.lots_completed
        remaining_lots = self.total_lots - self.lots_completed
        return avg_time_per_lot * remaining_lots

    async def update(
        self,
        lots_completed: int | None = None,
        current_lot: str | None = None,
        message: str | None = None,
    ) -> None:
        """
        Update progress and broadcast to subscribers.

        Args:
            lots_completed: Number of lots completed
            current_lot: Current lot being processed
            message: Progress message
        """
        if lots_completed is not None:
            self.lots_completed = lots_completed
        if current_lot is not None:
            self.current_lot = current_lot

        # Create progress message
        progress_msg = create_schedule_progress_message(
            schedule_id=self.schedule_id,
            progress=self.progress,
            status=self.status,
            message=message,
            current_lot=self.current_lot,
            lots_completed=self.lots_completed,
            lots_total=self.total_lots,
            elapsed_time=self.elapsed_time,
            estimated_remaining=self.estimated_remaining,
        )

        # Broadcast to channel subscribers
        await connection_manager.broadcast_to_channel(self.channel, progress_msg)

        logger.debug(
            f"Schedule {self.schedule_id} progress: {self.progress:.1f}% "
            f"({self.lots_completed}/{self.total_lots})"
        )

    async def complete(
        self,
        makespan: float,
        utilization: float,
        changeovers: int,
        lots_scheduled: int,
    ) -> None:
        """
        Mark schedule as completed and broadcast final status.

        Args:
            makespan: Schedule makespan
            utilization: Resource utilization
            changeovers: Number of changeovers
            lots_scheduled: Number of lots scheduled
        """
        self.status = "completed"

        completion_msg = create_schedule_completed_message(
            schedule_id=self.schedule_id,
            makespan=makespan,
            utilization=utilization,
            changeovers=changeovers,
            lots_scheduled=lots_scheduled,
            execution_time=self.elapsed_time,
        )

        await connection_manager.broadcast_to_channel(self.channel, completion_msg)

        logger.info(
            f"Schedule {self.schedule_id} completed: "
            f"makespan={makespan:.2f}h, utilization={utilization:.1f}%, "
            f"time={self.elapsed_time:.2f}s"
        )

    async def fail(self, error: str, error_type: str | None = None) -> None:
        """
        Mark schedule as failed and broadcast error.

        Args:
            error: Error message
            error_type: Error type
        """
        self.status = "failed"

        failure_msg = create_schedule_failed_message(
            schedule_id=self.schedule_id, error=error, error_type=error_type
        )

        await connection_manager.broadcast_to_channel(self.channel, failure_msg)

        logger.error(f"Schedule {self.schedule_id} failed: {error}")


class ComparisonProgress:
    """
    Track progress of a comparison run.

    Provides methods to update progress and broadcast to WebSocket subscribers.
    """

    def __init__(self, comparison_id: int, total_strategies: int):
        """
        Initialize comparison progress tracker.

        Args:
            comparison_id: Comparison ID
            total_strategies: Total number of strategies to compare
        """
        self.comparison_id = comparison_id
        self.total_strategies = total_strategies
        self.strategies_completed = 0
        self.current_strategy: str | None = None
        self.start_time = time.time()
        self.status = "running"

    @property
    def channel(self) -> str:
        """Get WebSocket channel name for this comparison."""
        return f"comparison:{self.comparison_id}"

    @property
    def progress(self) -> float:
        """Calculate progress percentage (0-100)."""
        if self.total_strategies == 0:
            return 0.0
        return min(100.0, (self.strategies_completed / self.total_strategies) * 100.0)

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time

    async def update(
        self,
        strategies_completed: int | None = None,
        current_strategy: str | None = None,
        message: str | None = None,
    ) -> None:
        """
        Update progress and broadcast to subscribers.

        Args:
            strategies_completed: Number of strategies completed
            current_strategy: Current strategy being run
            message: Progress message
        """
        if strategies_completed is not None:
            self.strategies_completed = strategies_completed
        if current_strategy is not None:
            self.current_strategy = current_strategy

        # Create progress message
        progress_msg = create_comparison_progress_message(
            comparison_id=self.comparison_id,
            progress=self.progress,
            status=self.status,
            message=message,
            strategies_completed=self.strategies_completed,
            strategies_total=self.total_strategies,
            current_strategy=self.current_strategy,
            elapsed_time=self.elapsed_time,
        )

        # Broadcast to channel subscribers
        await connection_manager.broadcast_to_channel(self.channel, progress_msg)

        logger.debug(
            f"Comparison {self.comparison_id} progress: {self.progress:.1f}% "
            f"({self.strategies_completed}/{self.total_strategies})"
        )


class ProgressTracker:
    """
    Global progress tracker for schedules and comparisons.

    Manages active progress trackers and provides factory methods.
    """

    def __init__(self):
        """Initialize progress tracker."""
        self.schedule_trackers: dict[int, ScheduleProgress] = {}
        self.comparison_trackers: dict[int, ComparisonProgress] = {}

    def create_schedule_tracker(self, schedule_id: int, total_lots: int) -> ScheduleProgress:
        """
        Create a schedule progress tracker.

        Args:
            schedule_id: Schedule ID
            total_lots: Total number of lots

        Returns:
            ScheduleProgress instance
        """
        tracker = ScheduleProgress(schedule_id, total_lots)
        self.schedule_trackers[schedule_id] = tracker
        return tracker

    def get_schedule_tracker(self, schedule_id: int) -> ScheduleProgress | None:
        """
        Get schedule progress tracker.

        Args:
            schedule_id: Schedule ID

        Returns:
            ScheduleProgress instance or None
        """
        return self.schedule_trackers.get(schedule_id)

    def remove_schedule_tracker(self, schedule_id: int) -> None:
        """
        Remove schedule progress tracker.

        Args:
            schedule_id: Schedule ID
        """
        self.schedule_trackers.pop(schedule_id, None)

    def create_comparison_tracker(
        self, comparison_id: int, total_strategies: int
    ) -> ComparisonProgress:
        """
        Create a comparison progress tracker.

        Args:
            comparison_id: Comparison ID
            total_strategies: Total number of strategies

        Returns:
            ComparisonProgress instance
        """
        tracker = ComparisonProgress(comparison_id, total_strategies)
        self.comparison_trackers[comparison_id] = tracker
        return tracker

    def get_comparison_tracker(self, comparison_id: int) -> ComparisonProgress | None:
        """
        Get comparison progress tracker.

        Args:
            comparison_id: Comparison ID

        Returns:
            ComparisonProgress instance or None
        """
        return self.comparison_trackers.get(comparison_id)

    def remove_comparison_tracker(self, comparison_id: int) -> None:
        """
        Remove comparison progress tracker.

        Args:
            comparison_id: Comparison ID
        """
        self.comparison_trackers.pop(comparison_id, None)


# Global progress tracker instance
progress_tracker = ProgressTracker()
