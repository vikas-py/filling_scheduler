"""
WebSocket real-time updates module.

Provides real-time progress updates for:
- Schedule execution
- Comparison runs
- Long-running operations

Components:
- manager: ConnectionManager for managing WebSocket connections
- protocol: Message schemas and protocol handlers
- tracker: Progress tracking for schedules and comparisons
- router: WebSocket endpoints
"""

from fillscheduler.api.websocket.manager import ConnectionManager
from fillscheduler.api.websocket.protocol import (
    MessageType,
    WebSocketMessage,
    create_message,
    parse_message,
)
from fillscheduler.api.websocket.tracker import (
    ComparisonProgress,
    ProgressTracker,
    ScheduleProgress,
)

__all__ = [
    "ConnectionManager",
    "MessageType",
    "WebSocketMessage",
    "parse_message",
    "create_message",
    "ProgressTracker",
    "ScheduleProgress",
    "ComparisonProgress",
]
