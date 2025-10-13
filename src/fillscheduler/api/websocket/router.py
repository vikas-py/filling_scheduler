"""
WebSocket Router.

Provides WebSocket endpoints for real-time updates.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from fillscheduler.api.database.session import get_db
from fillscheduler.api.dependencies import get_current_user_from_token
from fillscheduler.api.models.database import User
from fillscheduler.api.websocket.manager import connection_manager
from fillscheduler.api.websocket.protocol import (
    MessageType,
    SubscribeMessage,
    UnsubscribeMessage,
    create_connected_message,
    create_error_message,
    create_message,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_current_user_ws(
    websocket: WebSocket,
    token: str | None = None,
    db: Session = Depends(get_db),
) -> User | None:
    """
    Get current user from WebSocket token parameter.

    Args:
        websocket: WebSocket instance
        token: Authentication token (query parameter)
        db: Database session

    Returns:
        User instance or None if authentication fails
    """
    if not token:
        return None

    try:
        return await get_current_user_from_token(token, db)
    except Exception as e:
        logger.warning(f"WebSocket authentication failed: {e}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str | None = None,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time updates.

    Authentication:
        Connect with token query parameter:
        ws://localhost:8000/api/ws?token=YOUR_TOKEN

    Protocol:
        Client sends:
        - {"type": "subscribe", "channel": "schedule:123"}
        - {"type": "unsubscribe", "channel": "schedule:123"}
        - {"type": "ping"}

        Server sends:
        - {"type": "connected", "data": {...}}
        - {"type": "pong"}
        - {"type": "schedule.progress", "data": {...}}
        - {"type": "schedule.completed", "data": {...}}
        - {"type": "error", "data": {"error": "..."}}

    Channels:
        - schedule:{id} - Subscribe to schedule updates
        - comparison:{id} - Subscribe to comparison updates
        - user:{id} - Subscribe to user-specific updates
    """
    # Authenticate user
    user = await get_current_user_ws(websocket, token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("WebSocket connection rejected: authentication failed")
        return

    # Generate unique connection ID
    connection_id = str(uuid.uuid4())

    # Connect to manager
    accepted = await connection_manager.connect(websocket, connection_id, user.id)
    if not accepted:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"WebSocket connection rejected: too many connections for user {user.id}")
        return

    # Send connected message
    connected_msg = create_connected_message(connection_id, user.id)
    await connection_manager.send_personal_message(connection_id, connected_msg)

    try:
        while True:
            # Receive message from client
            try:
                data = await websocket.receive_json()
            except Exception as e:
                logger.warning(f"Error receiving message: {e}")
                break

            # Parse message type
            message_type = data.get("type")
            if not message_type:
                error_msg = create_error_message("Missing message type")
                await connection_manager.send_personal_message(connection_id, error_msg)
                continue

            # Handle different message types
            if message_type == MessageType.PING:
                # Respond with pong
                pong_msg = create_message(MessageType.PONG)
                await connection_manager.send_personal_message(connection_id, pong_msg)

            elif message_type == MessageType.SUBSCRIBE:
                # Subscribe to channel
                try:
                    subscribe_msg = SubscribeMessage(**data)
                    channel = subscribe_msg.channel

                    # Validate channel ownership
                    if not await validate_channel_access(channel, user.id, db):
                        error_msg = create_error_message(
                            f"Access denied to channel: {channel}", "ACCESS_DENIED"
                        )
                        await connection_manager.send_personal_message(connection_id, error_msg)
                        continue

                    # Subscribe
                    success = await connection_manager.subscribe(connection_id, channel)
                    if success:
                        logger.info(
                            f"User {user.id} subscribed to {channel} "
                            f"(connection={connection_id})"
                        )
                    else:
                        error_msg = create_error_message(f"Failed to subscribe to {channel}")
                        await connection_manager.send_personal_message(connection_id, error_msg)

                except Exception as e:
                    error_msg = create_error_message(f"Invalid subscribe message: {e}")
                    await connection_manager.send_personal_message(connection_id, error_msg)

            elif message_type == MessageType.UNSUBSCRIBE:
                # Unsubscribe from channel
                try:
                    unsubscribe_msg = UnsubscribeMessage(**data)
                    channel = unsubscribe_msg.channel

                    success = await connection_manager.unsubscribe(connection_id, channel)
                    if success:
                        logger.info(
                            f"User {user.id} unsubscribed from {channel} "
                            f"(connection={connection_id})"
                        )

                except Exception as e:
                    error_msg = create_error_message(f"Invalid unsubscribe message: {e}")
                    await connection_manager.send_personal_message(connection_id, error_msg)

            else:
                # Unknown message type
                error_msg = create_error_message(
                    f"Unknown message type: {message_type}", "UNKNOWN_MESSAGE_TYPE"
                )
                await connection_manager.send_personal_message(connection_id, error_msg)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        await connection_manager.disconnect(connection_id)


async def validate_channel_access(channel: str, user_id: int, db: Session) -> bool:
    """
    Validate that user has access to a channel.

    Args:
        channel: Channel name (e.g., "schedule:123")
        user_id: User ID
        db: Database session

    Returns:
        True if user has access, False otherwise
    """
    try:
        # Parse channel
        parts = channel.split(":", 1)
        if len(parts) != 2:
            return False

        channel_type, resource_id = parts

        # Validate resource ID
        try:
            resource_id_int = int(resource_id)
        except ValueError:
            return False

        # Check access based on channel type
        if channel_type == "schedule":
            # Check if user owns the schedule
            from fillscheduler.api.models.database import Schedule

            schedule = (
                db.query(Schedule)
                .filter(Schedule.id == resource_id_int, Schedule.user_id == user_id)
                .first()
            )
            return schedule is not None

        elif channel_type == "comparison":
            # Check if user owns the comparison
            from fillscheduler.api.models.database import Comparison

            comparison = (
                db.query(Comparison)
                .filter(Comparison.id == resource_id_int, Comparison.user_id == user_id)
                .first()
            )
            return comparison is not None

        elif channel_type == "user":
            # User can only subscribe to their own channel
            return resource_id_int == user_id

        else:
            # Unknown channel type
            return False

    except Exception as e:
        logger.error(f"Error validating channel access: {e}")
        return False


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.

    Returns statistics about active connections, channels, and subscribers.
    Requires authentication (added by router dependencies).
    """
    return connection_manager.get_stats()
