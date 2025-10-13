"""
Tests for WebSocket Protocol.

Tests message schemas, validation, and message factory functions.
"""

import pytest
from pydantic import ValidationError

from fillscheduler.api.websocket.protocol import (
    ComparisonProgressData,
    MessageType,
    ScheduleCompletedData,
    ScheduleFailedData,
    ScheduleProgressData,
    SubscribeMessage,
    UnsubscribeMessage,
    WebSocketMessage,
    create_connected_message,
    create_error_message,
    create_message,
    create_schedule_completed_message,
    create_schedule_failed_message,
    create_schedule_progress_message,
    parse_message,
)


def test_message_type_enum():
    """Test MessageType enum values."""
    assert MessageType.SUBSCRIBE == "subscribe"
    assert MessageType.UNSUBSCRIBE == "unsubscribe"
    assert MessageType.PING == "ping"
    assert MessageType.PONG == "pong"
    assert MessageType.SCHEDULE_STARTED == "schedule.started"
    assert MessageType.SCHEDULE_PROGRESS == "schedule.progress"
    assert MessageType.SCHEDULE_COMPLETED == "schedule.completed"
    assert MessageType.SCHEDULE_FAILED == "schedule.failed"


def test_websocket_message_creation():
    """Test creating a basic WebSocket message."""
    msg = WebSocketMessage(type=MessageType.PING, data={"test": "data"})

    assert msg.type == MessageType.PING
    assert msg.data == {"test": "data"}
    assert msg.timestamp is not None


def test_websocket_message_to_dict():
    """Test converting WebSocket message to dictionary."""
    msg = WebSocketMessage(
        type=MessageType.PONG, timestamp="2025-10-13T10:00:00", data={"key": "value"}
    )

    result = msg.to_dict()
    assert result["type"] == "pong"
    assert result["timestamp"] == "2025-10-13T10:00:00"
    assert result["data"] == {"key": "value"}


def test_subscribe_message_validation():
    """Test SubscribeMessage validation."""
    # Valid message
    msg = SubscribeMessage(channel="schedule:123")
    assert msg.channel == "schedule:123"
    assert msg.type == MessageType.SUBSCRIBE

    # Invalid message (missing colon)
    with pytest.raises(ValidationError):
        SubscribeMessage(channel="invalid")

    # Invalid message (empty)
    with pytest.raises(ValidationError):
        SubscribeMessage(channel="")


def test_unsubscribe_message():
    """Test UnsubscribeMessage."""
    msg = UnsubscribeMessage(channel="comparison:456")
    assert msg.channel == "comparison:456"
    assert msg.type == MessageType.UNSUBSCRIBE


def test_schedule_progress_data_validation():
    """Test ScheduleProgressData validation."""
    # Valid data
    data = ScheduleProgressData(
        schedule_id=1,
        status="running",
        progress=50.5,
        message="Processing lot 5 of 10",
        current_lot="LOT005",
        lots_completed=5,
        lots_total=10,
        elapsed_time=120.5,
        estimated_remaining=115.0,
    )

    assert data.schedule_id == 1
    assert data.progress == 50.5
    assert data.current_lot == "LOT005"

    # Invalid progress (> 100)
    with pytest.raises(ValidationError):
        ScheduleProgressData(schedule_id=1, status="running", progress=150.0)

    # Invalid progress (< 0)
    with pytest.raises(ValidationError):
        ScheduleProgressData(schedule_id=1, status="running", progress=-10.0)


def test_schedule_completed_data():
    """Test ScheduleCompletedData."""
    data = ScheduleCompletedData(
        schedule_id=1,
        makespan=24.5,
        utilization=85.5,
        changeovers=3,
        lots_scheduled=10,
        execution_time=125.0,
    )

    assert data.schedule_id == 1
    assert data.status == "completed"
    assert data.makespan == 24.5
    assert data.utilization == 85.5


def test_schedule_failed_data():
    """Test ScheduleFailedData."""
    data = ScheduleFailedData(
        schedule_id=1, error="Validation failed", error_type="VALIDATION_ERROR"
    )

    assert data.schedule_id == 1
    assert data.status == "failed"
    assert data.error == "Validation failed"
    assert data.error_type == "VALIDATION_ERROR"


def test_comparison_progress_data():
    """Test ComparisonProgressData validation."""
    data = ComparisonProgressData(
        comparison_id=1,
        status="running",
        progress=60.0,
        message="Running strategy 3 of 5",
        strategies_completed=3,
        strategies_total=5,
        current_strategy="smart-pack",
        elapsed_time=300.0,
    )

    assert data.comparison_id == 1
    assert data.progress == 60.0
    assert data.current_strategy == "smart-pack"


def test_create_message():
    """Test create_message factory function."""
    result = create_message(MessageType.PING, {"test": "data"})

    assert result["type"] == "ping"
    assert result["data"] == {"test": "data"}
    assert "timestamp" in result


def test_parse_message_valid():
    """Test parsing a valid JSON message."""
    json_str = '{"type": "ping", "data": {}, "timestamp": "2025-10-13T10:00:00"}'
    msg = parse_message(json_str)

    assert msg is not None
    assert msg.type == MessageType.PING


def test_parse_message_invalid_json():
    """Test parsing invalid JSON."""
    msg = parse_message("not valid json")
    assert msg is None


def test_parse_message_missing_type():
    """Test parsing message with missing type."""
    json_str = '{"data": {}, "timestamp": "2025-10-13T10:00:00"}'
    msg = parse_message(json_str)
    assert msg is None


def test_create_error_message():
    """Test creating an error message."""
    result = create_error_message("Something went wrong", "ERROR_CODE")

    assert result["type"] == "error"
    assert result["data"]["error"] == "Something went wrong"
    assert result["data"]["code"] == "ERROR_CODE"


def test_create_error_message_without_code():
    """Test creating error message without error code."""
    result = create_error_message("Error occurred")

    assert result["type"] == "error"
    assert result["data"]["error"] == "Error occurred"
    assert "code" not in result["data"]


def test_create_connected_message():
    """Test creating a connection confirmation message."""
    result = create_connected_message("conn123", 42)

    assert result["type"] == "connected"
    assert result["data"]["connection_id"] == "conn123"
    assert result["data"]["user_id"] == 42
    assert "message" in result["data"]


def test_create_schedule_progress_message():
    """Test creating a schedule progress message."""
    result = create_schedule_progress_message(
        schedule_id=1,
        progress=75.0,
        status="running",
        message="Almost done",
        current_lot="LOT008",
        lots_completed=8,
        lots_total=10,
    )

    assert result["type"] == "schedule.progress"
    assert result["data"]["schedule_id"] == 1
    assert result["data"]["progress"] == 75.0
    assert result["data"]["current_lot"] == "LOT008"


def test_create_schedule_completed_message():
    """Test creating a schedule completion message."""
    result = create_schedule_completed_message(
        schedule_id=1,
        makespan=24.5,
        utilization=85.0,
        changeovers=3,
        lots_scheduled=10,
        execution_time=120.5,
    )

    assert result["type"] == "schedule.completed"
    assert result["data"]["schedule_id"] == 1
    assert result["data"]["makespan"] == 24.5
    assert result["data"]["utilization"] == 85.0
    assert result["data"]["status"] == "completed"


def test_create_schedule_failed_message():
    """Test creating a schedule failure message."""
    result = create_schedule_failed_message(
        schedule_id=1, error="Validation error", error_type="VALIDATION"
    )

    assert result["type"] == "schedule.failed"
    assert result["data"]["schedule_id"] == 1
    assert result["data"]["error"] == "Validation error"
    assert result["data"]["error_type"] == "VALIDATION"
    assert result["data"]["status"] == "failed"


def test_message_timestamp_auto_generation():
    """Test that messages auto-generate timestamps."""
    result = create_message(MessageType.PING)

    assert "timestamp" in result
    # Verify it's a valid ISO format timestamp
    timestamp = result["timestamp"]
    assert "T" in timestamp  # ISO format includes T separator
