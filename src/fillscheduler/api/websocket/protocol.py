"""
WebSocket Protocol.

Defines message schemas, types, and protocol handlers for WebSocket communication.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types."""

    # Client -> Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"

    # Server -> Client
    PONG = "pong"
    ERROR = "error"
    CONNECTED = "connected"

    # Schedule updates
    SCHEDULE_STARTED = "schedule.started"
    SCHEDULE_PROGRESS = "schedule.progress"
    SCHEDULE_COMPLETED = "schedule.completed"
    SCHEDULE_FAILED = "schedule.failed"

    # Comparison updates
    COMPARISON_STARTED = "comparison.started"
    COMPARISON_PROGRESS = "comparison.progress"
    COMPARISON_COMPLETED = "comparison.completed"
    COMPARISON_FAILED = "comparison.failed"


class WebSocketMessage(BaseModel):
    """Base WebSocket message schema."""

    type: MessageType = Field(..., description="Message type")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Message timestamp (ISO 8601)",
    )
    data: dict[str, Any] = Field(default_factory=dict, description="Message payload")

    @field_validator("timestamp", mode="before")
    @classmethod
    def ensure_iso_format(cls, v):
        """Ensure timestamp is in ISO format."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "timestamp": self.timestamp,
            "data": self.data,
        }


class SubscribeMessage(BaseModel):
    """Subscribe to a channel."""

    type: MessageType = Field(default=MessageType.SUBSCRIBE)
    channel: str = Field(..., description="Channel to subscribe (e.g., 'schedule:123')")

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v):
        """Validate channel format."""
        if not v or ":" not in v:
            raise ValueError("Invalid channel format. Use 'type:id' (e.g., 'schedule:123')")
        return v


class UnsubscribeMessage(BaseModel):
    """Unsubscribe from a channel."""

    type: MessageType = Field(default=MessageType.UNSUBSCRIBE)
    channel: str = Field(..., description="Channel to unsubscribe")


class ScheduleProgressData(BaseModel):
    """Schedule progress update data."""

    schedule_id: int = Field(..., description="Schedule ID")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    message: str | None = Field(None, description="Progress message")
    current_lot: str | None = Field(None, description="Current lot being processed")
    lots_completed: int | None = Field(None, description="Number of lots completed")
    lots_total: int | None = Field(None, description="Total number of lots")
    elapsed_time: float | None = Field(None, description="Elapsed time in seconds")
    estimated_remaining: float | None = Field(
        None, description="Estimated remaining time in seconds"
    )


class ScheduleCompletedData(BaseModel):
    """Schedule completion data."""

    schedule_id: int = Field(..., description="Schedule ID")
    status: str = Field(default="completed", description="Final status")
    makespan: float = Field(..., description="Schedule makespan")
    utilization: float = Field(..., description="Resource utilization")
    changeovers: int = Field(..., description="Number of changeovers")
    lots_scheduled: int = Field(..., description="Number of lots scheduled")
    execution_time: float = Field(..., description="Execution time in seconds")


class ScheduleFailedData(BaseModel):
    """Schedule failure data."""

    schedule_id: int = Field(..., description="Schedule ID")
    status: str = Field(default="failed", description="Final status")
    error: str = Field(..., description="Error message")
    error_type: str | None = Field(None, description="Error type")


class ComparisonProgressData(BaseModel):
    """Comparison progress update data."""

    comparison_id: int = Field(..., description="Comparison ID")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    message: str | None = Field(None, description="Progress message")
    strategies_completed: int | None = Field(None, description="Number of strategies completed")
    strategies_total: int | None = Field(None, description="Total strategies")
    current_strategy: str | None = Field(None, description="Current strategy being run")
    elapsed_time: float | None = Field(None, description="Elapsed time in seconds")


class ComparisonCompletedData(BaseModel):
    """Comparison completion data."""

    comparison_id: int = Field(..., description="Comparison ID")
    status: str = Field(default="completed", description="Final status")
    strategies_count: int = Field(..., description="Number of strategies compared")
    best_strategy: str = Field(..., description="Best performing strategy")
    best_makespan: float = Field(..., description="Best makespan achieved")
    execution_time: float = Field(..., description="Execution time in seconds")


def create_message(
    message_type: MessageType, data: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Create a WebSocket message.

    Args:
        message_type: Type of message
        data: Message payload

    Returns:
        Message dictionary ready for JSON serialization
    """
    message = WebSocketMessage(type=message_type, data=data or {})
    return message.to_dict()


def parse_message(message_str: str) -> WebSocketMessage | None:
    """
    Parse a WebSocket message from JSON string.

    Args:
        message_str: JSON string message

    Returns:
        Parsed WebSocketMessage or None if invalid
    """
    try:
        data = json.loads(message_str)
        return WebSocketMessage(**data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON message: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing message: {e}")
        return None


def create_error_message(error: str, error_code: str | None = None) -> dict[str, Any]:
    """
    Create an error message.

    Args:
        error: Error description
        error_code: Optional error code

    Returns:
        Error message dictionary
    """
    return create_message(
        MessageType.ERROR,
        {"error": error, "code": error_code} if error_code else {"error": error},
    )


def create_connected_message(connection_id: str, user_id: int) -> dict[str, Any]:
    """
    Create a connection confirmation message.

    Args:
        connection_id: Connection identifier
        user_id: User ID

    Returns:
        Connected message dictionary
    """
    return create_message(
        MessageType.CONNECTED,
        {
            "connection_id": connection_id,
            "user_id": user_id,
            "message": "WebSocket connected successfully",
        },
    )


def create_schedule_progress_message(
    schedule_id: int,
    progress: float,
    status: str = "running",
    message: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create a schedule progress message.

    Args:
        schedule_id: Schedule ID
        progress: Progress percentage (0-100)
        status: Current status
        message: Progress message
        **kwargs: Additional progress data

    Returns:
        Progress message dictionary
    """
    data = ScheduleProgressData(
        schedule_id=schedule_id,
        progress=progress,
        status=status,
        message=message,
        **kwargs,
    )
    return create_message(MessageType.SCHEDULE_PROGRESS, data.model_dump())


def create_schedule_completed_message(
    schedule_id: int,
    makespan: float,
    utilization: float,
    changeovers: int,
    lots_scheduled: int,
    execution_time: float,
) -> dict[str, Any]:
    """
    Create a schedule completion message.

    Args:
        schedule_id: Schedule ID
        makespan: Schedule makespan
        utilization: Resource utilization
        changeovers: Number of changeovers
        lots_scheduled: Number of lots scheduled
        execution_time: Execution time in seconds

    Returns:
        Completion message dictionary
    """
    data = ScheduleCompletedData(
        schedule_id=schedule_id,
        makespan=makespan,
        utilization=utilization,
        changeovers=changeovers,
        lots_scheduled=lots_scheduled,
        execution_time=execution_time,
    )
    return create_message(MessageType.SCHEDULE_COMPLETED, data.model_dump())


def create_schedule_failed_message(
    schedule_id: int, error: str, error_type: str | None = None
) -> dict[str, Any]:
    """
    Create a schedule failure message.

    Args:
        schedule_id: Schedule ID
        error: Error message
        error_type: Error type

    Returns:
        Failure message dictionary
    """
    data = ScheduleFailedData(schedule_id=schedule_id, error=error, error_type=error_type)
    return create_message(MessageType.SCHEDULE_FAILED, data.model_dump())


def create_comparison_progress_message(
    comparison_id: int,
    progress: float,
    status: str = "running",
    message: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create a comparison progress message.

    Args:
        comparison_id: Comparison ID
        progress: Progress percentage (0-100)
        status: Current status
        message: Progress message
        **kwargs: Additional progress data

    Returns:
        Progress message dictionary
    """
    data = ComparisonProgressData(
        comparison_id=comparison_id,
        progress=progress,
        status=status,
        message=message,
        **kwargs,
    )
    return create_message(MessageType.COMPARISON_PROGRESS, data.model_dump())
