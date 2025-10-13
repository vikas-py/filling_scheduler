# Phase 1.6 WebSocket Implementation - Quick Start

**Status:** Design Complete, Ready for Implementation
**Date:** October 13, 2025

---

## Overview

This guide provides a quick reference for implementing WebSocket real-time progress updates for the Filling Scheduler API.

**Full Design:** See [PHASE_1.6_WEBSOCKET_DESIGN.md](PHASE_1.6_WEBSOCKET_DESIGN.md)

---

## Implementation Priority

### Day 1: Core Infrastructure (6-8 hours) 🎯 START HERE

**Files to Create:**

```
src/fillscheduler/api/
└── websocket/
    ├── __init__.py
    ├── manager.py         # ConnectionManager class
    ├── protocol.py        # Message schemas (Pydantic)
    ├── tracker.py         # ProgressTracker class
    └── router.py          # WebSocket endpoint
```

**Key Classes:**

1. **ConnectionManager** (`manager.py`)
   ```python
   class ConnectionManager:
       active_connections: Dict[str, Set[WebSocket]] = {}

       async def connect(resource_id: str, websocket: WebSocket)
       async def disconnect(resource_id: str, websocket: WebSocket)
       async def send_message(resource_id: str, message: dict)
       async def disconnect_all(resource_id: str)
   ```

2. **Message Schemas** (`protocol.py`)
   ```python
   class ProgressMessage(BaseModel):
       type: Literal["progress"]
       step: str
       progress: int  # 0-100
       message: str
       timestamp: datetime

   class CompletionMessage(BaseModel):
       type: Literal["complete"]
       # ... includes result summary

   class ErrorMessage(BaseModel):
       type: Literal["error"]
       # ... includes error details
   ```

3. **WebSocket Endpoint** (`router.py`)
   ```python
   @router.websocket("/ws/schedule/{schedule_id}")
   async def schedule_websocket(
       websocket: WebSocket,
       schedule_id: int,
       token: str = Query(...),  # JWT in query param
       db: Session = Depends(get_db)
   ):
       # 1. Authenticate JWT
       # 2. Verify schedule ownership
       # 3. Accept connection
       # 4. Handle messages until close
   ```

**Tests to Write:**
- `tests/api/websocket/test_manager.py`
- `tests/api/websocket/test_protocol.py`
- `tests/api/websocket/test_router.py`

---

### Day 2: Schedule Integration (6-8 hours)

**Files to Modify:**

1. **`src/fillscheduler/api/routers/schedule.py`**

   Update `_run_schedule_background()`:
   ```python
   async def _run_schedule_background(...):
       manager = get_websocket_manager()

       # Step 1: Loading (10%)
       await manager.send_message(f"schedule:{schedule_id}", {
           "type": "progress",
           "step": "loading",
           "progress": 10,
           "message": "Loading and validating lots data..."
       })

       # Step 2: Validating (30%)
       await manager.send_message(f"schedule:{schedule_id}", {
           "type": "progress",
           "step": "validating",
           "progress": 30,
           "message": "Validating configuration..."
       })

       # Step 3: Planning (50%)
       await manager.send_message(f"schedule:{schedule_id}", {
           "type": "progress",
           "step": "planning",
           "progress": 50,
           "message": "Planning optimal schedule..."
       })
       result = await run_schedule(...)

       # Step 4: Saving (90%)
       await manager.send_message(f"schedule:{schedule_id}", {
           "type": "progress",
           "step": "saving",
           "progress": 90,
           "message": "Saving results..."
       })

       # Step 5: Complete (100%)
       await manager.send_message(f"schedule:{schedule_id}", {
           "type": "complete",
           "progress": 100,
           "message": "Schedule completed successfully!",
           "result": {
               "schedule_id": schedule_id,
               "makespan": result["makespan"],
               "kpis": result["kpis"]
           }
       })
   ```

2. **`src/fillscheduler/api/main.py`**

   Add WebSocket router:
   ```python
   from fillscheduler.api.websocket.router import router as websocket_router

   app.include_router(websocket_router, prefix="/ws", tags=["websocket"])
   ```

**Tests to Write:**
- `tests/api/test_websocket_schedule.py` (integration tests)

---

### Day 3: Comparison Integration (4-6 hours)

**Files to Modify:**

1. **`src/fillscheduler/api/routers/comparison.py`**

   Update `_run_comparison_background()`:
   ```python
   async def _run_comparison_background(...):
       manager = get_websocket_manager()

       # Dynamic progress based on strategy count
       strategies_count = len(strategies)
       progress_per_strategy = 60 // strategies_count

       base_progress = 15  # After loading/validating

       for i, strategy in enumerate(strategies):
           await manager.send_message(f"comparison:{comparison_id}", {
               "type": "progress",
               "step": f"strategy_{i+1}",
               "progress": base_progress + (i * progress_per_strategy),
               "message": f"Running strategy {i+1}/{strategies_count}: {strategy}..."
           })
           # Run strategy...
   ```

**Tests to Write:**
- `tests/api/test_websocket_comparison.py`

---

### Day 4: Client Features (6-8 hours)

**Tasks:**

1. **Connection Cleanup**
   ```python
   # In manager.py
   async def cleanup_stale_connections(self, timeout: int = 300):
       """Remove connections idle for > timeout seconds."""
   ```

2. **Reconnection Support**
   ```python
   # Track last message per resource
   last_message: Dict[str, dict] = {}

   async def get_last_message(self, resource_id: str) -> dict | None:
       """Get last message for reconnection."""
   ```

3. **Connection Limits**
   ```python
   MAX_CONNECTIONS_PER_RESOURCE = 10

   async def connect(self, resource_id: str, websocket: WebSocket):
       if len(self.active_connections.get(resource_id, set())) >= MAX_CONNECTIONS_PER_RESOURCE:
           await websocket.close(code=1008, reason="Too many connections")
           return False
   ```

**Tests to Write:**
- Load tests (100 concurrent connections)
- Reconnection tests
- Stale connection cleanup tests

---

### Day 5: Documentation & Polish (4-6 hours)

**Documentation to Create:**

1. **API Documentation Update**
   - Add WebSocket endpoint to OpenAPI docs
   - Message format examples
   - Connection flow diagrams

2. **Client Integration Guide**
   ```markdown
   # WebSocket Integration Guide

   ## JavaScript/TypeScript Example
   ## React Hook Example
   ## Error Handling Patterns
   ## Reconnection Strategy
   ```

3. **Performance Testing**
   - Run load tests
   - Document results
   - Memory leak detection

---

## Authentication Implementation

**WebSocket JWT Authentication:**

```python
from fillscheduler.api.utils.security import decode_access_token

@router.websocket("/ws/schedule/{schedule_id}")
async def schedule_websocket(
    websocket: WebSocket,
    schedule_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    # Decode JWT
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

    # Register connection
    manager = get_websocket_manager()
    await manager.connect(f"schedule:{schedule_id}", websocket)

    try:
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Handle client messages (e.g., pong)
    except WebSocketDisconnect:
        await manager.disconnect(f"schedule:{schedule_id}", websocket)
```

---

## Message Protocol Quick Reference

### Progress Message
```json
{
  "type": "progress",
  "step": "loading" | "validating" | "planning" | "saving",
  "progress": 50,
  "message": "Planning optimal schedule...",
  "timestamp": "2025-10-13T10:30:45.123Z"
}
```

### Completion Message
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
    "kpis": {...}
  }
}
```

### Error Message
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

---

## Testing Strategy

### Unit Tests (Day 1)
```bash
pytest tests/api/websocket/test_manager.py -v
pytest tests/api/websocket/test_protocol.py -v
```

### Integration Tests (Day 2-3)
```bash
pytest tests/api/test_websocket_schedule.py -v
pytest tests/api/test_websocket_comparison.py -v
```

### Load Tests (Day 4)
```bash
pytest tests/load/test_websocket_load.py -v --slow
```

---

## Dependencies to Add

Add to `requirements.txt`:
```
# WebSocket support (already included in FastAPI)
# No additional dependencies needed!
```

FastAPI includes WebSocket support via Starlette.

---

## Example Client Code

### JavaScript (Vanilla)
```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/schedule/123?token=${token}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'progress') {
    updateProgress(message.progress, message.message);
  } else if (message.type === 'complete') {
    showResults(message.result);
  }
};
```

### React Hook
```typescript
function useScheduleWebSocket(scheduleId: number, token: string) {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/schedule/${scheduleId}?token=${token}`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress);
      setMessage(data.message);
    };
    return () => ws.close();
  }, [scheduleId, token]);

  return { progress, message };
}
```

---

## Common Pitfalls & Solutions

### Problem: WebSocket closes immediately after accept

**Solution:** Keep the WebSocket alive with a receive loop:
```python
try:
    while True:
        await websocket.receive_text()
except WebSocketDisconnect:
    # Cleanup
```

### Problem: Multiple connections receive duplicate messages

**Solution:** Use a Set to track connections:
```python
active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
```

### Problem: Memory leaks from unclosed connections

**Solution:** Implement cleanup task:
```python
@app.on_event("startup")
async def startup_cleanup():
    asyncio.create_task(cleanup_task())
```

---

## Success Criteria

- [ ] WebSocket endpoint accepts authenticated connections
- [ ] Progress updates sent during schedule execution
- [ ] Completion message sent on success
- [ ] Error messages sent on failure
- [ ] Multiple clients can connect to same resource
- [ ] Connections cleaned up on completion
- [ ] JWT authentication works correctly
- [ ] User can only connect to their own schedules
- [ ] Integration tests pass
- [ ] Load tests show < 1MB per connection
- [ ] Documentation complete with examples

---

## Next Steps After Phase 1.6

1. **Phase 1.7:** Address critical bugs from code review
2. **Phase 2.0:** Frontend development (React + TypeScript)
3. **Phase 2.1:** Gantt chart visualization
4. **Phase 2.2:** Strategy comparison dashboard

---

**Ready to start? Begin with Day 1: Core Infrastructure** 🚀
