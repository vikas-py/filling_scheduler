"""
Tests for WebSocket Progress Tracker.

Tests schedule and comparison progress tracking with broadcasting.
"""

from unittest.mock import AsyncMock, patch

import pytest

from fillscheduler.api.websocket.tracker import (
    ComparisonProgress,
    ProgressTracker,
    ScheduleProgress,
)


@pytest.mark.asyncio
async def test_schedule_progress_initialization():
    """Test ScheduleProgress initialization."""
    tracker = ScheduleProgress(schedule_id=1, total_lots=10)

    assert tracker.schedule_id == 1
    assert tracker.total_lots == 10
    assert tracker.lots_completed == 0
    assert tracker.current_lot is None
    assert tracker.status == "running"
    assert tracker.progress == 0.0


@pytest.mark.asyncio
async def test_schedule_progress_channel_name():
    """Test schedule progress channel naming."""
    tracker = ScheduleProgress(schedule_id=123, total_lots=5)
    assert tracker.channel == "schedule:123"


@pytest.mark.asyncio
async def test_schedule_progress_calculation():
    """Test progress percentage calculation."""
    tracker = ScheduleProgress(schedule_id=1, total_lots=10)

    # 0% complete
    assert tracker.progress == 0.0

    # 50% complete
    tracker.lots_completed = 5
    assert tracker.progress == 50.0

    # 100% complete
    tracker.lots_completed = 10
    assert tracker.progress == 100.0

    # Over 100% (capped)
    tracker.lots_completed = 15
    assert tracker.progress == 100.0


@pytest.mark.asyncio
async def test_schedule_progress_elapsed_time():
    """Test elapsed time tracking."""
    tracker = ScheduleProgress(schedule_id=1, total_lots=10)

    # Should have some elapsed time
    assert tracker.elapsed_time >= 0.0


@pytest.mark.asyncio
async def test_schedule_progress_estimated_remaining():
    """Test estimated remaining time calculation."""
    tracker = ScheduleProgress(schedule_id=1, total_lots=10)

    # No estimate when no lots completed
    tracker.lots_completed = 0
    assert tracker.estimated_remaining is None

    # Estimate when some lots completed
    tracker.lots_completed = 5
    import time

    time.sleep(0.1)  # Some time passes
    estimate = tracker.estimated_remaining
    assert estimate is not None
    assert estimate > 0


@pytest.mark.asyncio
@patch("fillscheduler.api.websocket.tracker.connection_manager")
async def test_schedule_progress_update_broadcasts(mock_manager):
    """Test that progress updates broadcast to WebSocket."""
    mock_manager.broadcast_to_channel = AsyncMock(return_value=1)

    tracker = ScheduleProgress(schedule_id=1, total_lots=10)
    await tracker.update(lots_completed=5, current_lot="LOT005", message="Half done")

    # Verify broadcast was called
    mock_manager.broadcast_to_channel.assert_called_once()
    args = mock_manager.broadcast_to_channel.call_args

    # Check channel
    assert args[0][0] == "schedule:1"

    # Check message structure
    message = args[0][1]
    assert message["type"] == "schedule.progress"
    assert message["data"]["schedule_id"] == 1
    assert message["data"]["progress"] == 50.0
    assert message["data"]["current_lot"] == "LOT005"
    assert message["data"]["message"] == "Half done"


@pytest.mark.asyncio
@patch("fillscheduler.api.websocket.tracker.connection_manager")
async def test_schedule_complete_broadcasts(mock_manager):
    """Test that completion broadcasts to WebSocket."""
    mock_manager.broadcast_to_channel = AsyncMock(return_value=1)

    tracker = ScheduleProgress(schedule_id=1, total_lots=10)
    await tracker.complete(makespan=24.5, utilization=85.0, changeovers=3, lots_scheduled=10)

    # Verify broadcast was called
    mock_manager.broadcast_to_channel.assert_called_once()
    args = mock_manager.broadcast_to_channel.call_args

    # Check message
    message = args[0][1]
    assert message["type"] == "schedule.completed"
    assert message["data"]["schedule_id"] == 1
    assert message["data"]["makespan"] == 24.5
    assert message["data"]["status"] == "completed"


@pytest.mark.asyncio
@patch("fillscheduler.api.websocket.tracker.connection_manager")
async def test_schedule_fail_broadcasts(mock_manager):
    """Test that failure broadcasts to WebSocket."""
    mock_manager.broadcast_to_channel = AsyncMock(return_value=1)

    tracker = ScheduleProgress(schedule_id=1, total_lots=10)
    await tracker.fail("Validation failed", error_type="VALIDATION_ERROR")

    # Verify broadcast was called
    mock_manager.broadcast_to_channel.assert_called_once()
    args = mock_manager.broadcast_to_channel.call_args

    # Check message
    message = args[0][1]
    assert message["type"] == "schedule.failed"
    assert message["data"]["schedule_id"] == 1
    assert message["data"]["error"] == "Validation failed"
    assert message["data"]["error_type"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_comparison_progress_initialization():
    """Test ComparisonProgress initialization."""
    tracker = ComparisonProgress(comparison_id=1, total_strategies=5)

    assert tracker.comparison_id == 1
    assert tracker.total_strategies == 5
    assert tracker.strategies_completed == 0
    assert tracker.current_strategy is None
    assert tracker.status == "running"
    assert tracker.progress == 0.0


@pytest.mark.asyncio
async def test_comparison_progress_channel_name():
    """Test comparison progress channel naming."""
    tracker = ComparisonProgress(comparison_id=456, total_strategies=3)
    assert tracker.channel == "comparison:456"


@pytest.mark.asyncio
async def test_comparison_progress_calculation():
    """Test comparison progress percentage calculation."""
    tracker = ComparisonProgress(comparison_id=1, total_strategies=5)

    # 0% complete
    assert tracker.progress == 0.0

    # 40% complete
    tracker.strategies_completed = 2
    assert tracker.progress == 40.0

    # 100% complete
    tracker.strategies_completed = 5
    assert tracker.progress == 100.0


@pytest.mark.asyncio
@patch("fillscheduler.api.websocket.tracker.connection_manager")
async def test_comparison_progress_update_broadcasts(mock_manager):
    """Test that comparison updates broadcast to WebSocket."""
    mock_manager.broadcast_to_channel = AsyncMock(return_value=1)

    tracker = ComparisonProgress(comparison_id=1, total_strategies=5)
    await tracker.update(
        strategies_completed=2, current_strategy="smart-pack", message="Running strategy 2"
    )

    # Verify broadcast
    mock_manager.broadcast_to_channel.assert_called_once()
    args = mock_manager.broadcast_to_channel.call_args

    message = args[0][1]
    assert message["type"] == "comparison.progress"
    assert message["data"]["comparison_id"] == 1
    assert message["data"]["progress"] == 40.0
    assert message["data"]["current_strategy"] == "smart-pack"


def test_progress_tracker_create_schedule_tracker():
    """Test creating a schedule progress tracker."""
    tracker = ProgressTracker()
    schedule_tracker = tracker.create_schedule_tracker(schedule_id=1, total_lots=10)

    assert schedule_tracker.schedule_id == 1
    assert schedule_tracker.total_lots == 10
    assert 1 in tracker.schedule_trackers


def test_progress_tracker_get_schedule_tracker():
    """Test retrieving a schedule progress tracker."""
    tracker = ProgressTracker()
    tracker.create_schedule_tracker(schedule_id=1, total_lots=10)

    retrieved = tracker.get_schedule_tracker(1)
    assert retrieved is not None
    assert retrieved.schedule_id == 1

    # Non-existent tracker
    assert tracker.get_schedule_tracker(999) is None


def test_progress_tracker_remove_schedule_tracker():
    """Test removing a schedule progress tracker."""
    tracker = ProgressTracker()
    tracker.create_schedule_tracker(schedule_id=1, total_lots=10)

    assert 1 in tracker.schedule_trackers

    tracker.remove_schedule_tracker(1)
    assert 1 not in tracker.schedule_trackers


def test_progress_tracker_create_comparison_tracker():
    """Test creating a comparison progress tracker."""
    tracker = ProgressTracker()
    comparison_tracker = tracker.create_comparison_tracker(comparison_id=1, total_strategies=5)

    assert comparison_tracker.comparison_id == 1
    assert comparison_tracker.total_strategies == 5
    assert 1 in tracker.comparison_trackers


def test_progress_tracker_get_comparison_tracker():
    """Test retrieving a comparison progress tracker."""
    tracker = ProgressTracker()
    tracker.create_comparison_tracker(comparison_id=1, total_strategies=5)

    retrieved = tracker.get_comparison_tracker(1)
    assert retrieved is not None
    assert retrieved.comparison_id == 1

    # Non-existent tracker
    assert tracker.get_comparison_tracker(999) is None


def test_progress_tracker_remove_comparison_tracker():
    """Test removing a comparison progress tracker."""
    tracker = ProgressTracker()
    tracker.create_comparison_tracker(comparison_id=1, total_strategies=5)

    assert 1 in tracker.comparison_trackers

    tracker.remove_comparison_tracker(1)
    assert 1 not in tracker.comparison_trackers
