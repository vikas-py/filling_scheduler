"""
Tests for WebSocket ConnectionManager.

Tests the connection lifecycle, subscription management, and broadcasting.
"""

import pytest

from fillscheduler.api.websocket.manager import ConnectionManager


@pytest.fixture
def manager():
    """Create a fresh ConnectionManager for each test."""
    return ConnectionManager(max_connections_per_user=3)


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self):
        self.accepted = False
        self.messages = []
        self.closed = False

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.messages.append(data)


@pytest.mark.asyncio
async def test_connection_lifecycle(manager):
    """Test connecting and disconnecting a WebSocket."""
    ws = MockWebSocket()
    connection_id = "conn1"
    user_id = 1

    # Connect
    accepted = await manager.connect(ws, connection_id, user_id)
    assert accepted is True
    assert ws.accepted is True
    assert connection_id in manager.active_connections
    assert user_id in manager.user_connections
    assert connection_id in manager.user_connections[user_id]

    # Disconnect
    await manager.disconnect(connection_id)
    assert connection_id not in manager.active_connections
    assert user_id not in manager.user_connections


@pytest.mark.asyncio
async def test_connection_limit_per_user(manager):
    """Test that connection limit per user is enforced."""
    user_id = 1

    # Connect up to limit (3)
    for i in range(3):
        ws = MockWebSocket()
        accepted = await manager.connect(ws, f"conn{i}", user_id)
        assert accepted is True

    # Try to connect beyond limit
    ws = MockWebSocket()
    accepted = await manager.connect(ws, "conn4", user_id)
    assert accepted is False
    assert ws.accepted is False


@pytest.mark.asyncio
async def test_multiple_users_can_connect(manager):
    """Test that different users can each have connections."""
    # User 1 connects
    ws1 = MockWebSocket()
    await manager.connect(ws1, "conn1", user_id=1)

    # User 2 connects
    ws2 = MockWebSocket()
    await manager.connect(ws2, "conn2", user_id=2)

    assert len(manager.active_connections) == 2
    assert len(manager.user_connections) == 2


@pytest.mark.asyncio
async def test_subscribe_to_channel(manager):
    """Test subscribing a connection to a channel."""
    ws = MockWebSocket()
    await manager.connect(ws, "conn1", user_id=1)

    # Subscribe to channel
    result = await manager.subscribe("conn1", "schedule:123")
    assert result is True
    assert "schedule:123" in manager.channel_subscriptions
    assert "conn1" in manager.channel_subscriptions["schedule:123"]

    # Check metadata
    metadata = manager.get_connection_info("conn1")
    assert "schedule:123" in metadata["channels"]


@pytest.mark.asyncio
async def test_subscribe_unknown_connection(manager):
    """Test subscribing an unknown connection fails gracefully."""
    result = await manager.subscribe("unknown", "schedule:123")
    assert result is False


@pytest.mark.asyncio
async def test_unsubscribe_from_channel(manager):
    """Test unsubscribing from a channel."""
    ws = MockWebSocket()
    await manager.connect(ws, "conn1", user_id=1)
    await manager.subscribe("conn1", "schedule:123")

    # Unsubscribe
    result = await manager.unsubscribe("conn1", "schedule:123")
    assert result is True
    assert "schedule:123" not in manager.channel_subscriptions

    # Check metadata
    metadata = manager.get_connection_info("conn1")
    assert "schedule:123" not in metadata["channels"]


@pytest.mark.asyncio
async def test_send_personal_message(manager):
    """Test sending a message to a specific connection."""
    ws = MockWebSocket()
    await manager.connect(ws, "conn1", user_id=1)

    message = {"type": "test", "data": "hello"}
    result = await manager.send_personal_message("conn1", message)

    assert result is True
    assert len(ws.messages) == 1
    assert ws.messages[0] == message


@pytest.mark.asyncio
async def test_send_personal_message_to_unknown_connection(manager):
    """Test sending to unknown connection fails gracefully."""
    message = {"type": "test"}
    result = await manager.send_personal_message("unknown", message)
    assert result is False


@pytest.mark.asyncio
async def test_broadcast_to_channel(manager):
    """Test broadcasting a message to all channel subscribers."""
    # Connect two clients and subscribe to same channel
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    await manager.connect(ws1, "conn1", user_id=1)
    await manager.connect(ws2, "conn2", user_id=2)
    await manager.subscribe("conn1", "schedule:123")
    await manager.subscribe("conn2", "schedule:123")

    # Broadcast message
    message = {"type": "update", "data": "progress"}
    count = await manager.broadcast_to_channel("schedule:123", message)

    assert count == 2
    assert len(ws1.messages) == 1
    assert len(ws2.messages) == 1
    assert ws1.messages[0] == message
    assert ws2.messages[0] == message


@pytest.mark.asyncio
async def test_broadcast_to_empty_channel(manager):
    """Test broadcasting to a channel with no subscribers."""
    message = {"type": "test"}
    count = await manager.broadcast_to_channel("empty:999", message)
    assert count == 0


@pytest.mark.asyncio
async def test_broadcast_to_user(manager):
    """Test broadcasting to all connections of a user."""
    # User has two connections
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    user_id = 1
    await manager.connect(ws1, "conn1", user_id)
    await manager.connect(ws2, "conn2", user_id)

    # Broadcast to user
    message = {"type": "notification", "data": "hello"}
    count = await manager.broadcast_to_user(user_id, message)

    assert count == 2
    assert len(ws1.messages) == 1
    assert len(ws2.messages) == 1


@pytest.mark.asyncio
async def test_disconnect_cleans_up_subscriptions(manager):
    """Test that disconnecting removes all subscriptions."""
    ws = MockWebSocket()
    await manager.connect(ws, "conn1", user_id=1)
    await manager.subscribe("conn1", "schedule:123")
    await manager.subscribe("conn1", "comparison:456")

    # Disconnect
    await manager.disconnect("conn1")

    # Subscriptions should be cleaned up
    assert "schedule:123" not in manager.channel_subscriptions
    assert "comparison:456" not in manager.channel_subscriptions
    assert "conn1" not in manager.active_connections


@pytest.mark.asyncio
async def test_get_channel_subscribers(manager):
    """Test getting list of subscribers for a channel."""
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    await manager.connect(ws1, "conn1", user_id=1)
    await manager.connect(ws2, "conn2", user_id=2)
    await manager.subscribe("conn1", "schedule:123")
    await manager.subscribe("conn2", "schedule:123")

    subscribers = manager.get_channel_subscribers("schedule:123")
    assert len(subscribers) == 2
    assert "conn1" in subscribers
    assert "conn2" in subscribers


@pytest.mark.asyncio
async def test_get_user_connections(manager):
    """Test getting list of connections for a user."""
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    user_id = 1
    await manager.connect(ws1, "conn1", user_id)
    await manager.connect(ws2, "conn2", user_id)

    connections = manager.get_user_connections(user_id)
    assert len(connections) == 2
    assert "conn1" in connections
    assert "conn2" in connections


@pytest.mark.asyncio
async def test_get_stats(manager):
    """Test getting connection statistics."""
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    await manager.connect(ws1, "conn1", user_id=1)
    await manager.connect(ws2, "conn2", user_id=2)
    await manager.subscribe("conn1", "schedule:123")
    await manager.subscribe("conn2", "schedule:123")

    stats = manager.get_stats()
    assert stats["total_connections"] == 2
    assert stats["total_channels"] == 1
    assert stats["total_users"] == 2
    assert "schedule:123" in stats["channels"]
    assert stats["channels"]["schedule:123"] == 2
