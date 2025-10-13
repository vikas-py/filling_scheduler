# Phase 1.6: WebSocket Real-Time Updates - Design Document

**Version:** 1.0
**Date:** October 13, 2025
**Status:** Design Phase
**Author:** AI Development Agent

---

## Table of Contents

1. [Overview](#overview)
2. [Goals & Requirements](#goals--requirements)
3. [Architecture Design](#architecture-design)
4. [WebSocket Protocol](#websocket-protocol)
5. [Implementation Plan](#implementation-plan)
6. [Security Considerations](#security-considerations)
7. [Testing Strategy](#testing-strategy)
8. [Performance & Scalability](#performance--scalability)
9. [Error Handling](#error-handling)
10. [Migration Path](#migration-path)

---

## Overview

### Purpose

Phase 1.6 adds WebSocket support to the Filling Scheduler API to provide real-time progress updates during long-running schedule and comparison operations. This enhances user experience by showing live progress instead of requiring polling.

### Current State

**Existing Behavior:**
- User creates schedule → receives 202 Accepted with `schedule_id`
- Background task runs scheduler asynchronously
- User must poll `GET /schedule/{id}` to check status
- No visibility into progress during execution

**Problems:**
- Poor UX: No progress indication during 10-60 second operations
- Inefficient: Polling creates unnecessary load
- No step-by-step visibility: Users don't know what's happening
- Resource waste: Multiple HTTP requests per second

### Target State

**New Behavior:**
- User creates schedule → receives 202 Accepted
- Frontend opens WebSocket connection: `WS /ws/schedule/{id}`
- Backend streams progress updates: 0% → 100%
- Real-time status changes and error notifications
- Connection automatically closed on completion
- Reconnection handling for network interruptions

---

## Goals & Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-1 | Send progress updates during schedule execution (0-100%) | MUST |
| FR-2 | Send step-by-step status messages | MUST |
| FR-3 | Send completion notification with results summary | MUST |
| FR-4 | Send error notifications with failure details | MUST |
| FR-5 | Support multiple concurrent connections per schedule | MUST |
| FR-6 | Authenticate WebSocket connections with JWT | MUST |
| FR-7 | Send progress updates for comparison operations | SHOULD |
| FR-8 | Support client reconnection with state recovery | SHOULD |
| FR-9 | Send periodic heartbeat/ping messages | MAY |
| FR-10 | Support cancellation via WebSocket | MAY |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR-1 | Message latency | < 100ms |
| NFR-2 | Max concurrent connections per schedule | 10 |
| NFR-3 | Connection memory overhead | < 1MB per connection |
| NFR-4 | Message size | < 10KB per message |
| NFR-5 | Heartbeat interval | 30 seconds |
| NFR-6 | Connection timeout | 300 seconds (5 min) |
| NFR-7 | Reconnection window | 60 seconds |

### Out of Scope (Future Phases)

- ❌ Broadcasting to all users (admin dashboards)
- ❌ Historical message replay
- ❌ Message persistence/queueing
- ❌ Load balancing across multiple servers (requires Redis pub/sub)
- ❌ Binary protocol (using JSON only)
- ❌ Compression

---

## Architecture Design

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Schedule   │    │  Comparison  │    │   WebSocket  │      │
│  │    Router    │    │    Router    │    │    Router    │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                    │                    │              │
│         │                    │                    │              │
│  ┌──────▼────────────────────▼────────────────────▼───────┐    │
│  │              WebSocket Connection Manager              │    │
│  │                                                         │    │
│  │  - Active connections: Dict[str, Set[WebSocket]]      │    │
│  │  - Connection locks: Dict[str, asyncio.Lock]          │    │
│  │  - Message queue: Optional[asyncio.Queue]             │    │
│  │                                                         │    │
│  │  Methods:                                              │    │
│  │  + connect(resource_id, websocket)                    │    │
│  │  + disconnect(resource_id, websocket)                 │    │
│  │  + send_progress(resource_id, message)                │    │
│  │  + send_error(resource_id, error)                     │    │
│  │  + send_completion(resource_id, result)               │    │
│  │  + cleanup_stale_connections()                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │            Progress Tracking Service                    │    │
│  │                                                         │    │
│  │  - Track current step for each operation              │    │
│  │  - Calculate progress percentage                       │    │
│  │  - Generate status messages                            │    │
│  │                                                         │    │
│  │  Methods:                                              │    │
│  │  + start_tracking(resource_id, total_steps)           │    │
│  │  + update_progress(resource_id, step, message)        │    │
│  │  + complete_tracking(resource_id)                     │    │
│  │  + fail_tracking(resource_id, error)                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Background Tasks                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  async def _run_schedule_background():                           │
│      tracker = get_progress_tracker()                            │
│      manager = get_websocket_manager()                           │
│                                                                   │
│      # Step 1: Load data                                         │
│      await manager.send_progress(schedule_id, {                  │
│          "step": "loading",                                      │
│          "progress": 10,                                         │
│          "message": "Loading and validating lots data..."        │
│      })                                                          │
│                                                                   │
│      # Step 2: Validate                                          │
│      await manager.send_progress(schedule_id, {                  │
│          "step": "validating",                                   │
│          "progress": 30,                                         │
│          "message": "Validating configuration..."                │
│      })                                                          │
│                                                                   │
│      # Step 3: Run scheduler                                     │
│      await manager.send_progress(schedule_id, {                  │
│          "step": "planning",                                     │
│          "progress": 50,                                         │
│          "message": "Planning optimal schedule..."               │
│      })                                                          │
│      result = await run_schedule(...)                            │
│                                                                   │
│      # Step 4: Save results                                      │
│      await manager.send_progress(schedule_id, {                  │
│          "step": "saving",                                       │
│          "progress": 90,                                         │
│          "message": "Saving results..."                          │
│      })                                                          │
│                                                                   │
│      # Step 5: Complete                                          │
│      await manager.send_completion(schedule_id, {                │
│          "step": "complete",                                     │
│          "progress": 100,                                        │
│          "message": "Schedule completed successfully!",          │
│          "schedule_id": schedule_id,                             │
│          "makespan": result["makespan"],                         │
│          "kpis": result["kpis"]                                  │
│      })                                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

```
src/fillscheduler/api/
├── websocket/
│   ├── __init__.py
│   ├── manager.py          # WebSocket connection manager
│   ├── protocol.py         # Message schemas and types
│   ├── tracker.py          # Progress tracking service
│   └── router.py           # WebSocket endpoints
├── routers/
│   ├── schedule.py         # Updated with progress updates
│   ├── comparison.py       # Updated with progress updates
│   └── ...
└── main.py                 # Updated to include WebSocket router
```

---

## WebSocket Protocol

### Connection Flow

```
1. Client → Server: HTTP Upgrade Request
   GET /ws/schedule/123?token=<jwt_token>
   Upgrade: websocket
   Connection: Upgrade

2. Server: Authenticate JWT token
   - Extract user_id from token
   - Verify schedule belongs to user
   - Accept or reject connection

3. Server → Client: Upgrade Response (if authenticated)
   HTTP 101 Switching Protocols

4. Client ↔ Server: WebSocket Messages (JSON)

5. Server → Client: Close Connection
   When operation completes or errors
```

### Message Types

#### 1. Progress Update

**Direction:** Server → Client

```json
{
  "type": "progress",
  "step": "loading" | "validating" | "planning" | "saving" | "complete",
  "progress": 50,
  "message": "Planning optimal schedule...",
  "timestamp": "2025-10-13T10:30:45.123Z"
}
```

**Fields:**
- `type`: Always "progress"
- `step`: Current execution step (enum)
- `progress`: Percentage complete (0-100)
- `message`: Human-readable status message
- `timestamp`: ISO 8601 timestamp

#### 2. Completion Message

**Direction:** Server → Client

```json
{
  "type": "complete",
  "step": "complete",
  "progress": 100,
  "message": "Schedule completed successfully!",
  "timestamp": "2025-10-13T10:31:00.456Z",
  "result": {
    "schedule_id": 123,
    "makespan": 145.5,
    "utilization": 0.87,
    "changeovers": 12,
    "kpis": {
      "makespan_hours": 145.5,
      "utilization_percent": 87.0,
      "changeover_count": 12,
      "avg_lot_duration": 12.1
    }
  }
}
```

**Fields:**
- All progress fields, plus:
- `result`: Summary of execution results

#### 3. Error Message

**Direction:** Server → Client

```json
{
  "type": "error",
  "step": "planning",
  "progress": 50,
  "message": "Scheduling failed: Invalid lot configuration",
  "timestamp": "2025-10-13T10:30:55.789Z",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": "Lot 'LOT-001' has invalid fill_hours: -5"
  }
}
```

**Fields:**
- All progress fields, plus:
- `error.code`: Error code (enum)
- `error.details`: Detailed error message

#### 4. Heartbeat/Ping (Optional)

**Direction:** Server → Client

```json
{
  "type": "ping",
  "timestamp": "2025-10-13T10:30:30.000Z"
}
```

**Client Response (Pong):**

```json
{
  "type": "pong",
  "timestamp": "2025-10-13T10:30:30.100Z"
}
```

### Progress Steps

#### Schedule Execution Steps

| Step | Progress | Description | Duration |
|------|----------|-------------|----------|
| `loading` | 10% | Load and parse lots data | 1-2s |
| `validating` | 30% | Validate configuration and data | 2-3s |
| `planning` | 50% | Run scheduling algorithm | 10-50s |
| `saving` | 90% | Save results to database | 1-2s |
| `complete` | 100% | Operation completed | - |

#### Comparison Execution Steps

| Step | Progress | Description | Duration |
|------|----------|-------------|----------|
| `loading` | 5% | Load and parse lots data | 1-2s |
| `validating` | 10% | Validate configuration | 2-3s |
| `preparing` | 15% | Prepare strategy execution | 1s |
| `strategy_1` | 25% | Running strategy 1/N | 10-50s |
| `strategy_2` | 45% | Running strategy 2/N | 10-50s |
| `strategy_N` | 75% | Running strategy N/N | 10-50s |
| `analyzing` | 90% | Analyzing and comparing results | 2-3s |
| `saving` | 95% | Saving results | 1-2s |
| `complete` | 100% | Comparison completed | - |

### Error Codes

| Code | Description | HTTP Equivalent |
|------|-------------|-----------------|
| `VALIDATION_ERROR` | Invalid input data | 400 |
| `AUTHENTICATION_ERROR` | Invalid JWT token | 401 |
| `AUTHORIZATION_ERROR` | User doesn't own resource | 403 |
| `NOT_FOUND` | Schedule/comparison not found | 404 |
| `EXECUTION_ERROR` | Scheduler execution failed | 500 |
| `TIMEOUT_ERROR` | Operation timed out | 504 |
| `CONNECTION_ERROR` | WebSocket connection issue | - |

---

## Implementation Plan

### Phase 1: Core Infrastructure (Day 1)

**Tasks:**

1. ✅ Create design document
2. ⏳ Create `websocket/manager.py` - Connection manager
   - `ConnectionManager` class
   - `connect()` / `disconnect()` methods
   - `send_message()` method
   - Active connections tracking
3. ⏳ Create `websocket/protocol.py` - Message schemas
   - Pydantic models for each message type
   - Enums for steps and error codes
4. ⏳ Create `websocket/tracker.py` - Progress tracking
   - `ProgressTracker` class
   - Step-to-progress mapping
5. ⏳ Create `websocket/router.py` - WebSocket endpoint
   - `GET /ws/schedule/{id}` endpoint
   - JWT authentication
   - Connection lifecycle management

**Deliverables:**
- 4 new files in `websocket/` package
- Unit tests for `ConnectionManager`
- Unit tests for message schemas

**Estimated Time:** 6-8 hours

### Phase 2: Schedule Integration (Day 2)

**Tasks:**

1. ⏳ Update `routers/schedule.py`
   - Import WebSocket manager
   - Add progress updates to `_run_schedule_background()`
   - 5 progress checkpoints: loading, validating, planning, saving, complete
2. ⏳ Update `services/scheduler.py`
   - Add optional progress callback parameter
   - Emit progress during execution
3. ⏳ Add authentication middleware
   - Validate JWT in WebSocket handshake
   - Check user ownership of schedule
4. ⏳ Add error handling
   - Catch exceptions in background task
   - Send error messages via WebSocket

**Deliverables:**
- Updated schedule router with WebSocket support
- Integration tests for schedule + WebSocket
- Error handling tests

**Estimated Time:** 6-8 hours

### Phase 3: Comparison Integration (Day 3)

**Tasks:**

1. ⏳ Update `routers/comparison.py`
   - Import WebSocket manager
   - Add progress updates to `_run_comparison_background()`
   - Dynamic progress based on strategy count
2. ⏳ Update `services/comparison.py`
   - Add progress callback to `run_comparison()`
   - Emit per-strategy progress updates
3. ⏳ Add completion summary
   - Send comparison results summary
   - Include best strategy recommendation

**Deliverables:**
- Updated comparison router with WebSocket support
- Integration tests for comparison + WebSocket

**Estimated Time:** 4-6 hours

### Phase 4: Client Features (Day 4)

**Tasks:**

1. ⏳ Add connection cleanup
   - Background task to close stale connections
   - Timeout handling (5 min)
2. ⏳ Add reconnection support
   - Track last message timestamp
   - Allow reconnection within 60s window
   - Resume from last known state
3. ⏳ Add heartbeat/ping (optional)
   - Send ping every 30s
   - Detect dead connections
4. ⏳ Add connection limits
   - Max 10 connections per schedule
   - Reject excess connections gracefully

**Deliverables:**
- Robust connection management
- Reconnection tests
- Load tests (100 concurrent connections)

**Estimated Time:** 6-8 hours

### Phase 5: Documentation & Polish (Day 5)

**Tasks:**

1. ⏳ Update API documentation
   - Add WebSocket endpoint docs
   - Message format examples
   - Connection flow diagrams
2. ⏳ Create client integration guide
   - JavaScript/TypeScript examples
   - React hook example
   - Error handling patterns
3. ⏳ Add monitoring/logging
   - Log connection events
   - Log message counts
   - Track connection duration
4. ⏳ Performance testing
   - Load test with 100 schedules
   - Stress test with 1000 connections
   - Memory leak detection

**Deliverables:**
- Complete documentation
- Client integration examples
- Performance test results
- Production-ready code

**Estimated Time:** 4-6 hours

---

## Security Considerations

### Authentication

**JWT Token in Query Parameter:**

```
GET /ws/schedule/123?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Rationale:**
- WebSocket handshake doesn't support custom headers in browsers
- Query parameter is standard approach for WebSocket auth
- Token is validated before accepting connection

**Implementation:**

```python
@router.websocket("/ws/schedule/{schedule_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    schedule_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    # Decode and validate JWT
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Verify schedule ownership
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == user_id
    ).first()

    if not schedule:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    # Accept connection
    await websocket.accept()
    # ... handle messages ...
```

### Authorization

**Resource Ownership Check:**
- Verify user owns the schedule before accepting connection
- Check on every reconnection attempt
- Close connection if ownership changes (admin deletion)

### Rate Limiting

**Connection Limits:**
- Max 10 concurrent connections per schedule
- Max 100 concurrent connections per user
- Max 1000 concurrent connections globally

**Message Rate Limiting:**
- Max 100 messages per second per connection
- Disconnect abusive clients

### Input Validation

**Message Validation:**
- Validate all client messages (pong responses)
- Reject malformed JSON
- Sanitize error messages before sending

### Data Leakage Prevention

**Scope Isolation:**
- Never broadcast to all connections
- Only send messages to specific schedule connections
- Don't include sensitive data in error messages

---

## Testing Strategy

### Unit Tests

**`tests/api/websocket/test_manager.py`:**

```python
def test_connection_manager_connect():
    """Test adding a connection."""

def test_connection_manager_disconnect():
    """Test removing a connection."""

def test_connection_manager_send_message():
    """Test sending message to all connections."""

def test_connection_manager_multiple_connections():
    """Test multiple connections for same resource."""

def test_connection_manager_cleanup_stale():
    """Test cleanup of stale connections."""
```

**`tests/api/websocket/test_protocol.py`:**

```python
def test_progress_message_schema():
    """Test ProgressMessage validation."""

def test_completion_message_schema():
    """Test CompletionMessage validation."""

def test_error_message_schema():
    """Test ErrorMessage validation."""

def test_message_serialization():
    """Test JSON serialization/deserialization."""
```

### Integration Tests

**`tests/api/test_websocket_schedule.py`:**

```python
@pytest.mark.asyncio
async def test_schedule_websocket_connection():
    """Test WebSocket connection establishment."""

@pytest.mark.asyncio
async def test_schedule_websocket_progress_updates():
    """Test receiving progress updates during schedule."""

@pytest.mark.asyncio
async def test_schedule_websocket_completion():
    """Test receiving completion message."""

@pytest.mark.asyncio
async def test_schedule_websocket_error():
    """Test receiving error message on failure."""

@pytest.mark.asyncio
async def test_schedule_websocket_authentication():
    """Test JWT authentication."""

@pytest.mark.asyncio
async def test_schedule_websocket_authorization():
    """Test user must own schedule."""

@pytest.mark.asyncio
async def test_schedule_websocket_reconnection():
    """Test reconnection after disconnect."""
```

### Load Tests

**`tests/load/test_websocket_load.py`:**

```python
@pytest.mark.asyncio
async def test_100_concurrent_connections():
    """Test 100 simultaneous WebSocket connections."""

@pytest.mark.asyncio
async def test_1000_message_throughput():
    """Test sending 1000 messages per second."""

@pytest.mark.asyncio
async def test_memory_leak_detection():
    """Test no memory leaks over 1 hour."""
```

### Manual Testing

**Test Scenarios:**

1. **Happy Path:**
   - Create schedule
   - Connect WebSocket
   - Receive all progress updates
   - Receive completion message
   - Connection closes automatically

2. **Error Path:**
   - Create schedule with invalid data
   - Connect WebSocket
   - Receive progress updates up to error
   - Receive error message
   - Connection closes

3. **Reconnection:**
   - Create schedule
   - Connect WebSocket
   - Disconnect after 50% progress
   - Reconnect within 60s
   - Continue receiving updates from last position

4. **Multiple Clients:**
   - Create schedule
   - Open 5 WebSocket connections
   - All receive same progress updates
   - All close on completion

5. **Authentication Failure:**
   - Connect without token → Rejected
   - Connect with invalid token → Rejected
   - Connect with expired token → Rejected
   - Connect to other user's schedule → Rejected

---

## Performance & Scalability

### Single Server Limits

**Expected Capacity:**
- 1000 concurrent WebSocket connections
- 100 schedules executing simultaneously
- 10,000 messages per second

**Memory Requirements:**
- ~1MB per WebSocket connection
- ~1GB for 1000 connections
- ~2GB server minimum recommended

**CPU Requirements:**
- WebSocket overhead: minimal (<5% CPU)
- Message serialization: <1ms per message
- Broadcasting to 10 clients: <10ms

### Multi-Server Scaling (Future)

**Current Limitation:**
- WebSocket connections are in-memory
- Connections tied to specific server instance
- No state sharing between servers

**Future Solution (Phase 2.0):**

Use Redis Pub/Sub for distributed WebSocket:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Server 1 │────▶│  Redis   │◀────│ Server 2 │
│ (WS)     │     │ Pub/Sub  │     │ (WS)     │
└──────────┘     └──────────┘     └──────────┘
     │                                   │
     ▼                                   ▼
┌─────────┐                         ┌─────────┐
│ Client A│                         │ Client B│
└─────────┘                         └─────────┘
```

**Implementation:**

```python
# server1: Publish message
await redis.publish(f"schedule:{schedule_id}", json.dumps(message))

# server2: Subscribe and forward to local connections
async for message in redis.subscribe(f"schedule:{schedule_id}"):
    for websocket in local_connections:
        await websocket.send_json(message)
```

### Connection Pool Management

**Strategy:**
- Reuse WebSocket connections (no need for pooling)
- Close idle connections after 5 minutes
- Background task to cleanup every 60 seconds

**Implementation:**

```python
async def cleanup_stale_connections():
    """Background task to cleanup stale connections."""
    while True:
        await asyncio.sleep(60)  # Run every minute
        manager = get_websocket_manager()
        await manager.cleanup_stale()
```

---

## Error Handling

### Connection Errors

| Error | Status Code | Action |
|-------|-------------|--------|
| Invalid JWT token | 1008 (Policy Violation) | Close connection |
| Unauthorized access | 1008 (Policy Violation) | Close connection |
| Schedule not found | 1008 (Policy Violation) | Close connection |
| Too many connections | 1008 (Policy Violation) | Reject connection |
| Internal server error | 1011 (Internal Error) | Close connection |

### Execution Errors

**Graceful Degradation:**

```python
try:
    # Run scheduler
    result = await run_schedule(...)
except ValidationError as e:
    # Send error message
    await manager.send_error(schedule_id, {
        "type": "error",
        "step": "validating",
        "message": "Validation failed",
        "error": {"code": "VALIDATION_ERROR", "details": str(e)}
    })
except Exception as e:
    # Generic error
    await manager.send_error(schedule_id, {
        "type": "error",
        "step": "unknown",
        "message": "Unexpected error occurred",
        "error": {"code": "EXECUTION_ERROR", "details": str(e)}
    })
finally:
    # Always close connections
    await manager.disconnect_all(schedule_id)
```

### Network Errors

**Client-Side Handling:**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/schedule/123?token=...');

ws.onclose = (event) => {
  if (event.code === 1000) {
    // Normal closure (completed)
    console.log('Schedule completed');
  } else if (event.code === 1006) {
    // Abnormal closure (network error)
    console.log('Connection lost, attempting reconnect...');
    setTimeout(() => reconnect(), 5000);
  } else {
    // Other error
    console.error(`WebSocket closed: ${event.code} - ${event.reason}`);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## Migration Path

### Backward Compatibility

**Polling Still Supported:**
- `GET /schedule/{id}` endpoint remains unchanged
- Old clients can continue polling
- WebSocket is optional enhancement

**Graceful Degradation:**
- If WebSocket connection fails, fall back to polling
- Frontend should handle both methods

### Deprecation Plan

**Phase 1.6:** WebSocket added (current)
- Polling and WebSocket both supported
- Documentation recommends WebSocket

**Phase 1.7:** (Future)
- WebSocket is primary method
- Polling still available for compatibility

**Phase 2.0:** (Future, 6 months)
- Consider deprecating polling
- Add deprecation warnings
- Provide 3-month sunset notice

---

## Appendix

### A. Example Client Implementation (JavaScript)

```javascript
class ScheduleWebSocket {
  constructor(scheduleId, token) {
    this.scheduleId = scheduleId;
    this.token = token;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const url = `ws://localhost:8000/ws/schedule/${this.scheduleId}?token=${this.token}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = (event) => {
      console.log(`WebSocket closed: ${event.code}`);
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => this.reconnect(), 5000);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'progress':
        console.log(`Progress: ${message.progress}% - ${message.message}`);
        this.onProgress?.(message.progress, message.message);
        break;
      case 'complete':
        console.log('Schedule completed!', message.result);
        this.onComplete?.(message.result);
        break;
      case 'error':
        console.error('Schedule failed:', message.error);
        this.onError?.(message.error);
        break;
      case 'ping':
        this.ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
        break;
    }
  }

  reconnect() {
    this.reconnectAttempts++;
    console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
    this.connect();
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Client closing');
    }
  }
}

// Usage
const ws = new ScheduleWebSocket(123, 'jwt_token_here');
ws.onProgress = (progress, message) => {
  document.getElementById('progress-bar').style.width = `${progress}%`;
  document.getElementById('status-message').textContent = message;
};
ws.onComplete = (result) => {
  console.log('Makespan:', result.makespan);
  window.location.href = `/schedule/${ws.scheduleId}`;
};
ws.onError = (error) => {
  alert(`Error: ${error.details}`);
};
ws.connect();
```

### B. Example Client Implementation (React Hook)

```typescript
// useScheduleWebSocket.ts
import { useEffect, useState, useCallback } from 'react';

interface ProgressMessage {
  type: 'progress';
  step: string;
  progress: number;
  message: string;
  timestamp: string;
}

interface CompleteMessage {
  type: 'complete';
  progress: number;
  message: string;
  result: {
    schedule_id: number;
    makespan: number;
    utilization: number;
    kpis: Record<string, any>;
  };
}

interface ErrorMessage {
  type: 'error';
  message: string;
  error: {
    code: string;
    details: string;
  };
}

type WebSocketMessage = ProgressMessage | CompleteMessage | ErrorMessage;

export function useScheduleWebSocket(scheduleId: number, token: string) {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('Connecting...');
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const connect = useCallback(() => {
    const url = `ws://localhost:8000/ws/schedule/${scheduleId}?token=${token}`;
    const websocket = new WebSocket(url);

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setMessage('Connected');
    };

    websocket.onmessage = (event) => {
      const data: WebSocketMessage = JSON.parse(event.data);

      switch (data.type) {
        case 'progress':
          setProgress(data.progress);
          setMessage(data.message);
          break;
        case 'complete':
          setProgress(100);
          setMessage(data.message);
          setIsComplete(true);
          break;
        case 'error':
          setError(data.error.details);
          break;
      }
    };

    websocket.onclose = (event) => {
      if (event.code !== 1000) {
        setError('Connection lost');
      }
    };

    websocket.onerror = () => {
      setError('WebSocket error');
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [scheduleId, token]);

  useEffect(() => {
    const cleanup = connect();
    return cleanup;
  }, [connect]);

  return { progress, message, isComplete, error, reconnect: connect };
}

// Usage in component
function ScheduleProgress({ scheduleId, token }: { scheduleId: number; token: string }) {
  const { progress, message, isComplete, error } = useScheduleWebSocket(scheduleId, token);

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (isComplete) {
    return <div className="success">Schedule completed!</div>;
  }

  return (
    <div className="progress-container">
      <div className="progress-bar" style={{ width: `${progress}%` }} />
      <p>{message}</p>
    </div>
  );
}
```

### C. Performance Benchmarks (Projected)

| Metric | Target | Acceptable | Unacceptable |
|--------|--------|------------|--------------|
| Message latency | < 50ms | < 100ms | > 200ms |
| Connection overhead | < 500KB | < 1MB | > 2MB |
| Concurrent connections | 1000+ | 500+ | < 100 |
| Messages per second | 10,000+ | 5,000+ | < 1,000 |
| CPU usage (idle) | < 5% | < 10% | > 20% |
| Memory per connection | < 500KB | < 1MB | > 2MB |

---

**End of Design Document**

**Next Steps:**
1. Review and approve design
2. Create GitHub issue/project board
3. Begin Phase 1 implementation
4. Update progress in todo list

**Questions for Review:**
- Should we support cancellation via WebSocket?
- Should we implement Redis pub/sub now or defer to Phase 2?
- What should the max connection limit be per schedule?
- Should we add message compression?
