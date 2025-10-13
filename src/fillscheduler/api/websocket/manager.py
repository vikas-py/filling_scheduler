"""
WebSocket Connection Manager.

Manages active WebSocket connections, handles subscription/unsubscription,
and broadcasts messages to connected clients.
"""

import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.

    Features:
    - Connection lifecycle management
    - Channel-based subscriptions (schedule:{id}, comparison:{id}, user:{id})
    - Broadcast messages to subscribers
    - Automatic cleanup on disconnect
    - Connection limit per user
    """

    def __init__(self, max_connections_per_user: int = 10):
        """
        Initialize connection manager.

        Args:
            max_connections_per_user: Maximum WebSocket connections per user
        """
        # Active connections: {connection_id: WebSocket}
        self.active_connections: dict[str, WebSocket] = {}

        # Connection metadata: {connection_id: {"user_id": int, "channels": set()}}
        self.connection_metadata: dict[str, dict[str, Any]] = {}

        # Channel subscriptions: {channel: {connection_id1, connection_id2, ...}}
        self.channel_subscriptions: dict[str, set[str]] = {}

        # User connections: {user_id: {connection_id1, connection_id2, ...}}
        self.user_connections: dict[int, set[str]] = {}

        self.max_connections_per_user = max_connections_per_user

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: int,
    ) -> bool:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket instance
            connection_id: Unique connection identifier
            user_id: User ID owning this connection

        Returns:
            True if connection accepted, False if rejected (too many connections)
        """
        # Check connection limit per user
        user_connection_count = len(self.user_connections.get(user_id, set()))
        if user_connection_count >= self.max_connections_per_user:
            logger.warning(
                f"User {user_id} exceeded max connections ({self.max_connections_per_user})"
            )
            return False

        await websocket.accept()

        # Store connection
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "channels": set(),
        }

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)

        logger.info(
            f"WebSocket connected: {connection_id} (user={user_id}, "
            f"total={len(self.active_connections)})"
        )
        return True

    async def disconnect(self, connection_id: str) -> None:
        """
        Disconnect a WebSocket and cleanup subscriptions.

        Args:
            connection_id: Connection identifier to disconnect
        """
        if connection_id not in self.active_connections:
            return

        # Get metadata
        metadata = self.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")
        channels = metadata.get("channels", set())

        # Unsubscribe from all channels
        for channel in channels:
            if channel in self.channel_subscriptions:
                self.channel_subscriptions[channel].discard(connection_id)
                if not self.channel_subscriptions[channel]:
                    del self.channel_subscriptions[channel]

        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove connection
        del self.active_connections[connection_id]
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]

        logger.info(
            f"WebSocket disconnected: {connection_id} " f"(total={len(self.active_connections)})"
        )

    async def subscribe(self, connection_id: str, channel: str) -> bool:
        """
        Subscribe a connection to a channel.

        Args:
            connection_id: Connection identifier
            channel: Channel name (e.g., "schedule:123", "user:456")

        Returns:
            True if subscribed, False if connection not found
        """
        if connection_id not in self.connection_metadata:
            logger.warning(f"Cannot subscribe unknown connection: {connection_id}")
            return False

        # Add to channel subscriptions
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(connection_id)

        # Update metadata
        self.connection_metadata[connection_id]["channels"].add(channel)

        logger.debug(
            f"Connection {connection_id} subscribed to {channel} "
            f"(subscribers={len(self.channel_subscriptions[channel])})"
        )
        return True

    async def unsubscribe(self, connection_id: str, channel: str) -> bool:
        """
        Unsubscribe a connection from a channel.

        Args:
            connection_id: Connection identifier
            channel: Channel name

        Returns:
            True if unsubscribed, False if not subscribed
        """
        if connection_id not in self.connection_metadata:
            return False

        # Remove from channel subscriptions
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(connection_id)
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]

        # Update metadata
        self.connection_metadata[connection_id]["channels"].discard(channel)

        logger.debug(f"Connection {connection_id} unsubscribed from {channel}")
        return True

    async def send_personal_message(self, connection_id: str, message: dict) -> bool:
        """
        Send a message to a specific connection.

        Args:
            connection_id: Connection identifier
            message: Message dictionary to send

        Returns:
            True if sent, False if connection not found or send failed
        """
        if connection_id not in self.active_connections:
            return False

        try:
            websocket = self.active_connections[connection_id]
            await websocket.send_json(message)
            return True
        except WebSocketDisconnect:
            logger.warning(f"Connection {connection_id} disconnected during send")
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"Error sending to {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False

    async def broadcast_to_channel(self, channel: str, message: dict) -> int:
        """
        Broadcast a message to all subscribers of a channel.

        Args:
            channel: Channel name
            message: Message dictionary to broadcast

        Returns:
            Number of successful sends
        """
        if channel not in self.channel_subscriptions:
            logger.debug(f"No subscribers for channel: {channel}")
            return 0

        subscribers = self.channel_subscriptions[channel].copy()
        successful_sends = 0
        failed_connections = []

        for connection_id in subscribers:
            if await self.send_personal_message(connection_id, message):
                successful_sends += 1
            else:
                failed_connections.append(connection_id)

        # Cleanup failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)

        logger.debug(f"Broadcast to {channel}: {successful_sends}/{len(subscribers)} sent")
        return successful_sends

    async def broadcast_to_user(self, user_id: int, message: dict) -> int:
        """
        Broadcast a message to all connections of a user.

        Args:
            user_id: User ID
            message: Message dictionary to broadcast

        Returns:
            Number of successful sends
        """
        if user_id not in self.user_connections:
            logger.debug(f"No connections for user: {user_id}")
            return 0

        connections = self.user_connections[user_id].copy()
        successful_sends = 0

        for connection_id in connections:
            if await self.send_personal_message(connection_id, message):
                successful_sends += 1

        logger.debug(f"Broadcast to user {user_id}: {successful_sends}/{len(connections)} sent")
        return successful_sends

    def get_channel_subscribers(self, channel: str) -> list[str]:
        """
        Get list of connection IDs subscribed to a channel.

        Args:
            channel: Channel name

        Returns:
            List of connection IDs
        """
        return list(self.channel_subscriptions.get(channel, set()))

    def get_user_connections(self, user_id: int) -> list[str]:
        """
        Get list of connection IDs for a user.

        Args:
            user_id: User ID

        Returns:
            List of connection IDs
        """
        return list(self.user_connections.get(user_id, set()))

    def get_connection_info(self, connection_id: str) -> dict[str, Any] | None:
        """
        Get metadata about a connection.

        Args:
            connection_id: Connection identifier

        Returns:
            Connection metadata dict or None if not found
        """
        return self.connection_metadata.get(connection_id)

    def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about active connections.

        Returns:
            Stats dictionary with connection counts
        """
        return {
            "total_connections": len(self.active_connections),
            "total_channels": len(self.channel_subscriptions),
            "total_users": len(self.user_connections),
            "channels": {
                channel: len(subs) for channel, subs in self.channel_subscriptions.items()
            },
        }


# Global connection manager instance
connection_manager = ConnectionManager()
