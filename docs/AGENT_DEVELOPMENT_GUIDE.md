# Agent Development Guide - Filling Scheduler

**Project:** Filling Scheduler API
**Last Updated:** October 13, 2025
**Target Audience:** AI Coding Agents (Claude, GitHub Copilot, etc.)

---

## ⚠️ CRITICAL BEST PRACTICES

### 🔴 Rule #1: ALWAYS Use Virtual Environment

```bash
# Activate BEFORE any Python command
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # Linux/Mac

# Verify - prompt should show (venv)
```

**Why?** Prevents dependency conflicts, ensures consistent package versions.

### 🔴 Rule #2: ALWAYS Use Separate Terminals for Server and Tests

```bash
# TERMINAL 1: Server (keep running)
.\venv\Scripts\Activate.ps1
python -m uvicorn fillscheduler.api.main:app --reload --port 8000

# TERMINAL 2: Tests (open separate terminal)
.\venv\Scripts\Activate.ps1
python test_schedule_api.py
```

**Why?** Server is a blocking process. Tests need to send HTTP requests to running server.

### 🔴 Rule #3: Never Run Tests in Same Terminal as Server

❌ **WRONG:**
```bash
python -m uvicorn ... &  # Background job
python test_schedule_api.py  # Won't work reliably
```

✅ **CORRECT:**
- Terminal 1: Server (visible logs)
- Terminal 2: Tests (visible test output)

---

## 🚀 Quick Setup Checklist

**First Time Setup:**
```bash
# 1. Clone repository
git clone <repo-url>
cd filling_scheduler

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python -c "from fillscheduler.api.main import app; print('✓ Setup complete!')"
```

**Every Development Session:**
```bash
# TERMINAL 1 (Server)
cd d:\GitHub\filling_scheduler
.\venv\Scripts\Activate.ps1
python -m uvicorn fillscheduler.api.main:app --reload --port 8000

# TERMINAL 2 (Tests/Development)
cd d:\GitHub\filling_scheduler
.\venv\Scripts\Activate.ps1
# Now run tests, edit code, etc.
python test_schedule_api.py
```

**Checklist:**
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] Server running in Terminal 1 (see "Application startup complete")
- [ ] Tests run in Terminal 2 (separate from server)
- [ ] Both terminals in project root directory

---

## Table of Contents

0. [⚠️ CRITICAL BEST PRACTICES](#️-critical-best-practices) ← **READ THIS FIRST**
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Technology Stack](#technology-stack)
4. [Development Workflow](#development-workflow)
5. [Architecture Patterns](#architecture-patterns)
6. [Database Schema](#database-schema)
7. [API Design Patterns](#api-design-patterns)
8. [Testing Guidelines](#testing-guidelines)
9. [Common Tasks](#common-tasks)
10. [Code Style & Conventions](#code-style--conventions)
11. [Known Issues](#known-issues)
12. [Quick Reference](#quick-reference)

---

## Project Overview

### What is Filling Scheduler?

A pharmaceutical manufacturing scheduling system that optimizes the sequencing of lot fills in a filling suite. The system uses multiple algorithms (strategies) to find optimal schedules that minimize makespan, maximize utilization, and reduce changeover time.

### Project Goals

- ✅ **Backend API**: FastAPI-based REST API with JWT authentication
- ✅ **Multiple Strategies**: 6 scheduling algorithms available
- ✅ **Async Processing**: Background task execution for long-running schedules
- ✅ **Comparison System**: Run multiple strategies in parallel and compare results
- 🚧 **Configuration Management**: Template system for reusable configurations
- 🚧 **Real-time Updates**: WebSocket for progress broadcasting
- 🚧 **Frontend**: React + TypeScript UI with Gantt charts and dashboards

### Current Status (Phase 1.4 Complete)

**Completed:**
- ✅ Phase 1.1: Project Setup (SQLite database, FastAPI structure)
- ✅ Phase 1.2: Authentication System (JWT, bcrypt password hashing)
- ✅ Phase 1.3: Schedule Endpoints (7 endpoints, background processing)
- ✅ Phase 1.4: Comparison Endpoints (4 endpoints, parallel execution)

**In Progress:**
- 🚧 Bug fixes from code review (7 critical issues)
- 🚧 Phase 1.5: Configuration Endpoints
- 🚧 Phase 1.6: WebSocket support

---

## Project Structure

```
filling_scheduler/
├── filling_scheduler/              # Original CLI tool (legacy)
│   ├── scheduler.py               # Core scheduling engine
│   ├── models.py                  # Lot, Activity models
│   ├── strategies/                # 6 scheduling algorithms
│   │   ├── smart_pack.py
│   │   ├── spt_pack.py
│   │   ├── lpt_pack.py
│   │   ├── cfs_pack.py
│   │   ├── hybrid_pack.py
│   │   └── milp_opt.py
│   └── ...
│
├── src/fillscheduler/api/         # FastAPI Backend (NEW)
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Settings (Pydantic BaseSettings)
│   ├── dependencies.py            # FastAPI dependencies
│   │
│   ├── database/
│   │   └── session.py            # SQLAlchemy session management
│   │
│   ├── models/
│   │   ├── database.py           # SQLAlchemy ORM models
│   │   └── schemas.py            # Pydantic request/response schemas
│   │
│   ├── routers/
│   │   ├── auth.py              # Authentication endpoints (4)
│   │   ├── schedule.py          # Schedule endpoints (7)
│   │   └── comparison.py        # Comparison endpoints (4)
│   │
│   └── services/
│       ├── auth.py              # Auth business logic
│       ├── scheduler.py         # Scheduling service (async wrapper)
│       └── comparison.py        # Comparison service (parallel execution)
│
├── tests/                        # Unit tests for core scheduler
├── docs/                         # Documentation
│   ├── SCHEDULE_ENDPOINTS_SUMMARY.md
│   ├── COMPARISON_ENDPOINTS_SUMMARY.md
│   ├── AGENT_DEVELOPMENT_GUIDE.md (this file)
│   └── codereviews/
│       └── router_integration_bugs_13Oct2025.md
│
├── test_*.py                    # Integration tests (API)
├── fillscheduler.db            # SQLite database
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Dependencies
└── README.md                   # Project README
```

### Key Files to Know

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `src/fillscheduler/api/main.py` | FastAPI app, router registration | 125 | ✅ Stable |
| `src/fillscheduler/api/models/database.py` | SQLAlchemy models (6 tables) | 170 | ✅ Stable |
| `src/fillscheduler/api/models/schemas.py` | Pydantic schemas | 290 | ✅ Stable |
| `src/fillscheduler/api/routers/schedule.py` | Schedule endpoints | 437 | ⚠️ Has bugs |
| `src/fillscheduler/api/routers/comparison.py` | Comparison endpoints | 350 | ✅ Tested |
| `src/fillscheduler/api/services/scheduler.py` | Async scheduler wrapper | 330 | ⚠️ Has bugs |
| `src/fillscheduler/api/services/comparison.py` | Parallel execution service | 230 | ✅ Tested |
| `fillscheduler/scheduler.py` | Core scheduling engine | 500+ | ✅ Stable (legacy) |

---

## Technology Stack

### Backend

- **Framework**: FastAPI 0.104.0+ (async support, automatic OpenAPI docs)
- **Database**: SQLAlchemy 2.0+ ORM with SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT tokens (python-jose), bcrypt password hashing (passlib)
- **Async Processing**: ThreadPoolExecutor for CPU-bound scheduling, FastAPI BackgroundTasks
- **Validation**: Pydantic 2.0+ (request/response validation, settings management)

### Core Scheduler (Legacy)

- **Language**: Python 3.10+
- **Optimization**: PuLP (MILP solver, optional for milp-opt strategy)
- **Data Models**: dataclasses (Lot, Activity, AppConfig)

### Development Tools

- **Testing**: pytest, requests (integration tests)
- **Code Quality**: (not yet configured - TODO)
- **Documentation**: Markdown, FastAPI automatic docs

### Database

- **Current**: SQLite (file-based, `fillscheduler.db`)
- **Schema**: 6 tables (users, schedules, schedule_results, comparisons, comparison_results, config_templates)
- **Migrations**: Manual (no Alembic yet - schemas created via `Base.metadata.create_all()`)

### Environment Variables

Create a `.env` file in the project root for configuration:

```env
# Database
DATABASE_URL=sqlite:///./fillscheduler.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
DEBUG=True
HOST=0.0.0.0
PORT=8000

# CORS (for frontend development)
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

**Generate a secure SECRET_KEY:**
```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -hex 32
```

**⚠️ IMPORTANT:**
- Add `.env` to `.gitignore` (never commit secrets!)
- Use different SECRET_KEY for production
- Change DATABASE_URL for PostgreSQL in production

---

## Development Workflow

### ⚠️ CRITICAL: Virtual Environment

**ALWAYS use a virtual environment for all Python commands!**

```bash
# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows CMD:
.\venv\Scripts\activate.bat

# On Linux/Mac:
source venv/bin/activate

# Install dependencies in virtual environment
pip install -r requirements.txt

# Verify you're in virtual environment
# Prompt should show (venv) prefix
```

**Why?** Virtual environments prevent dependency conflicts and ensure consistent behavior across different machines.

### Starting the Server

**⚠️ CRITICAL: Always run server in a SEPARATE terminal from tests!**

**Terminal 1 (Server):**
```bash
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Start server in development mode (auto-reload)
python -m uvicorn fillscheduler.api.main:app --reload --port 8000

# Or production mode
python -m uvicorn fillscheduler.api.main:app --host 0.0.0.0 --port 8000

# Keep this terminal open - server runs continuously
```

**Server URLs:**
- API Base: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Running Tests

**⚠️ CRITICAL: Run tests in a DIFFERENT terminal from the server!**

**Terminal 2 (Tests):**
```bash
# Integration tests (require server running)
python test_auth_api.py
python test_schedule_api.py
python test_comparison_api.py

# Unit tests (legacy scheduler)
pytest tests/
```

**Why separate terminals?**
- Server runs as a blocking process (keeps running)
- Tests need to send HTTP requests to the running server
- Easier to monitor server logs while tests run
- Can stop/restart server independently

### Database Management

```bash
# Database is auto-created on first startup
# Location: ./fillscheduler.db

# Reset database (delete and restart server)
rm fillscheduler.db
python -m uvicorn fillscheduler.api.main:app
```

### Adding New Dependencies

```bash
# Add to requirements.txt
pip install <package>
pip freeze | grep <package> >> requirements.txt

# Install all dependencies
pip install -r requirements.txt
```

---

## Architecture Patterns

### 1. Layered Architecture

```
┌─────────────────────────────────────┐
│  Routers (HTTP Endpoints)           │  ← Request validation, response formatting
├─────────────────────────────────────┤
│  Services (Business Logic)          │  ← Async wrappers, parallel execution
├─────────────────────────────────────┤
│  Core Scheduler (Algorithms)        │  ← CPU-bound scheduling logic
├─────────────────────────────────────┤
│  Database (SQLAlchemy ORM)          │  ← Data persistence
└─────────────────────────────────────┘
```

**Key Principles:**
- Routers handle HTTP concerns only (validation, status codes, responses)
- Services contain business logic (async operations, coordination)
- Core scheduler is synchronous (CPU-bound, runs in ThreadPoolExecutor)
- Database operations use SQLAlchemy ORM (no raw SQL)

### 2. Background Task Pattern

**Used by:** Schedule endpoints, Comparison endpoints

```python
# Pattern: Create record → Start background task → Return immediately

@router.post("/schedule", status_code=202)
async def create_schedule(
    request: ScheduleRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 1. Validate input
    validation = await validate_lots_data(request.lots_data)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["errors"])

    # 2. Create database record with status="pending"
    schedule = Schedule(user_id=current_user.id, status="pending", ...)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    # 3. Start background task (non-blocking)
    background_tasks.add_task(
        _run_schedule_background,
        schedule.id,
        request.lots_data,
        ...
    )

    # 4. Return immediately with 202 Accepted
    return ScheduleResponse(id=schedule.id, status="pending", ...)
```

**Background Task Function:**
```python
async def _run_schedule_background(schedule_id: int, ...):
    # CRITICAL: Create own database session (request session closes after 202 response)
    db = SessionLocal()

    try:
        # Update status to "running"
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        schedule.status = "running"
        db.commit()

        # Run long operation (in ThreadPoolExecutor for CPU-bound work)
        result = await run_schedule(...)

        # Save results
        schedule_result = ScheduleResult(...)
        db.add(schedule_result)
        schedule.status = "completed"
        db.commit()

    except Exception as e:
        # Update with error
        schedule.status = "failed"
        schedule.error_message = str(e)
        db.commit()
    finally:
        db.close()
```

### 3. Async Wrapper Pattern

**Used by:** Services wrapping synchronous core scheduler

```python
# Core scheduler is synchronous (CPU-bound)
def plan_schedule(lots, start_time, strategy, config):
    # Heavy computation...
    return activities, makespan, kpis

# Service wraps in async function
async def run_schedule(lots_data, start_time, strategy, config_data):
    # Convert input to core scheduler format
    lots = [_convert_lot_dict_to_lot(lot) for lot in lots_data]
    config = _create_config_from_dict(config_data)

    # Run in thread pool (don't block event loop)
    loop = asyncio.get_event_loop()
    activities, makespan, kpis = await loop.run_in_executor(
        _executor,  # ThreadPoolExecutor(max_workers=4)
        _run_scheduler_sync,  # Wrapper around plan_schedule
        lots,
        start_time,
        strategy,
        config
    )

    # Convert output to API format
    return {
        "activities": [_convert_activity_to_dict(a) for a in activities],
        "makespan": makespan,
        "kpis": kpis
    }
```

### 4. Parallel Execution Pattern

**Used by:** Comparison service

```python
async def run_comparison(lots_data, strategies, start_time, config_data):
    # Create task for each strategy
    tasks = [
        run_single_strategy(lots_data, start_time, strategy, config_data)
        for strategy in strategies
    ]

    # Run all in parallel (asyncio.gather handles concurrent execution)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Convert exceptions to error results
    strategy_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            strategy_results.append({
                "strategy": strategies[i],
                "status": "failed",
                "error_message": str(result),
                ...
            })
        else:
            strategy_results.append({
                "strategy": strategies[i],
                **result
            })

    return {"results": strategy_results}
```

### 5. JSON Storage Pattern (SQLite)

**Used by:** Storing complex data in SQLite TEXT columns

```python
# Database model (SQLite doesn't have native JSON type)
class Schedule(Base):
    config_json = Column(Text, nullable=True)  # Store as JSON string

# Writing to database
schedule = Schedule(
    config_json=json.dumps(request.config or {})  # Convert dict to JSON string
)

# Reading from database
config = json.loads(schedule.config_json) if schedule.config_json else {}
```

**⚠️ Important:** Always use `json.dumps()` when saving and `json.loads()` when reading.

### 6. Owner-Based Access Control

**Pattern:** All resources belong to users, check ownership on access

```python
@router.get("/schedule/{schedule_id}")
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Query with user_id filter (prevents accessing other users' data)
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id  # Ownership check
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return schedule
```

---

## Database Schema

### Tables Overview

```sql
users (5 columns, primary auth table)
  ├── schedules (1:N)
  │   └── schedule_results (1:1)
  ├── comparisons (1:N)
  │   └── comparison_results (1:N)
  └── config_templates (1:N)
```

### User Table

```python
class User(Base):
    __tablename__ = "users"

    id: int (PK)
    email: str (unique, indexed)
    hashed_password: str
    is_active: bool (default=True)
    is_superuser: bool (default=False)
    created_at: datetime
    updated_at: datetime
```

### Schedule Tables

```python
class Schedule(Base):
    __tablename__ = "schedules"

    id: int (PK)
    user_id: int (FK → users.id)
    name: str
    strategy: str  # "smart-pack", "spt-pack", etc.
    status: str    # "pending", "running", "completed", "failed"
    error_message: str (nullable)
    config_json: str (JSON serialized)
    created_at: datetime
    started_at: datetime (nullable)
    completed_at: datetime (nullable)

class ScheduleResult(Base):
    __tablename__ = "schedule_results"

    id: int (PK)
    schedule_id: int (FK → schedules.id, unique, CASCADE DELETE)
    makespan: float
    utilization: float
    changeovers: int
    lots_scheduled: int
    window_violations: int
    kpis_json: str (JSON serialized)
    activities_json: str (JSON serialized)
    created_at: datetime
```

### Comparison Tables

```python
class Comparison(Base):
    __tablename__ = "comparisons"

    id: int (PK)
    user_id: int (FK → users.id)
    name: str
    lots_data_hash: str (SHA256, indexed, for caching)
    lots_data_json: str (JSON serialized, for reproducibility)
    strategies: str (JSON list: ["smart-pack", "spt-pack", ...])
    status: str
    error_message: str (nullable)
    config_json: str (JSON serialized)
    best_strategy: str (nullable, recommendation)
    created_at: datetime
    started_at: datetime (nullable)
    completed_at: datetime (nullable)

class ComparisonResult(Base):
    __tablename__ = "comparison_results"

    id: int (PK)
    comparison_id: int (FK → comparisons.id, CASCADE DELETE)
    strategy: str
    status: str
    error_message: str (nullable)
    makespan: float (nullable)
    utilization: float (nullable)
    changeovers: int (nullable)
    lots_scheduled: int (nullable)
    window_violations: int (nullable)
    kpis_json: str (JSON serialized, nullable)
    activities_json: str (JSON serialized, nullable)
    execution_time: float (seconds, nullable)
    created_at: datetime
```

### Config Template Table (Not Yet Implemented)

```python
class ConfigTemplate(Base):
    __tablename__ = "config_templates"

    id: int (PK)
    user_id: int (FK → users.id)
    name: str
    description: str (nullable)
    config_json: str (JSON serialized)
    is_public: bool (default=False)
    created_at: datetime
    updated_at: datetime
```

---

## API Design Patterns

### Endpoint Naming Convention

```
POST   /api/v1/resource         → Create (201 Created or 202 Accepted)
GET    /api/v1/resource/{id}    → Read one (200 OK or 404 Not Found)
GET    /api/v1/resources         → Read many (200 OK, may be empty list)
PUT    /api/v1/resource/{id}    → Update (200 OK or 404 Not Found)
DELETE /api/v1/resource/{id}    → Delete (200 OK or 404 Not Found)
POST   /api/v1/resource/action  → Custom action (varies)
```

### Status Code Usage

| Code | Usage | Example |
|------|-------|---------|
| 200 OK | Successful GET, DELETE | GET /schedule/1 |
| 201 Created | Resource created immediately | POST /auth/register |
| 202 Accepted | Request accepted, processing async | POST /schedule (background task) |
| 400 Bad Request | Validation error, invalid input | Invalid lots data |
| 401 Unauthorized | Missing or invalid auth token | No Authorization header |
| 403 Forbidden | Valid auth but no permission | Accessing another user's schedule |
| 404 Not Found | Resource doesn't exist | GET /schedule/999 |
| 422 Unprocessable Entity | Pydantic validation error | Missing required field |
| 500 Internal Server Error | Unexpected server error | Unhandled exception |

### Response Schema Patterns

**Single Resource:**
```python
class ResourceResponse(BaseModel):
    id: int
    name: str
    status: str
    created_at: datetime
    # ... other fields
```

**List with Pagination:**
```python
class ResourceListResponse(BaseModel):
    resources: List[ResourceResponse]
    total: int           # Total count (all pages)
    page: int            # Current page (1-indexed)
    page_size: int       # Items per page
    pages: int           # Total pages
```

**Detail with Nested Data:**
```python
class ResourceDetailResponse(ResourceResponse):
    result: Optional[ResultData] = None  # Nested data
    metadata: Optional[Dict] = None
```

**Simple Message:**
```python
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
```

### Pydantic Field Aliases

**Problem:** SQLAlchemy column name differs from JSON field name

**Solution:** Use Pydantic field aliases

```python
class ScheduleResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode

    # Database column: kpis_json (Text)
    # JSON field: kpis (Dict)
    kpis: Dict[str, Any] = Field(..., alias="kpis_json")
    activities: List[Dict] = Field(..., alias="activities_json")
```

**Usage:**
```python
# Creating response (use alias names for constructor)
response = ScheduleResultResponse(
    kpis_json=json.loads(result.kpis_json),  # Pass with alias name
    activities_json=json.loads(result.activities_json)
)

# JSON output will have "kpis" and "activities" (without _json suffix)
```

---

## Testing Guidelines

### Integration Test Structure

**⚠️ PREREQUISITE: Server must be running in separate terminal!**

```bash
# Terminal 1: Start server
.\venv\Scripts\Activate.ps1
python -m uvicorn fillscheduler.api.main:app --reload --port 8000

# Terminal 2: Run tests (in different terminal)
.\venv\Scripts\Activate.ps1
python test_<feature>_api.py
```

```python
# Test file: test_<feature>_api.py

import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
TEST_PASSWORD = "testpass123"

def test_feature_api():
    # 1. Setup: Authentication
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert register_response.status_code == 201

    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test: Create resource
    create_response = requests.post(
        f"{BASE_URL}/resource",
        headers=headers,
        json={...}
    )
    assert create_response.status_code == 202
    resource_id = create_response.json()["id"]

    # 3. Test: Wait for completion (if background task)
    import time
    max_wait = 30
    start_time = time.time()
    while time.time() - start_time < max_wait:
        get_response = requests.get(
            f"{BASE_URL}/resource/{resource_id}",
            headers=headers
        )
        result = get_response.json()
        if result["status"] == "completed":
            break
        time.sleep(2)

    assert result["status"] == "completed"

    # 4. Test: Verify results
    assert result["some_field"] == expected_value

    # 5. Cleanup: Delete resource
    delete_response = requests.delete(
        f"{BASE_URL}/resource/{resource_id}",
        headers=headers
    )
    assert delete_response.status_code == 200
```

### Test Data

**Sample Lots:**
```python
sample_lots = [
    {
        "lot_id": "LOT001",
        "lot_type": "Product-A",
        "vials": 1000,
        "fill_hours": 2.5,
        "target_start": "2025-10-15T08:00:00",
        "target_end": "2025-10-15T18:00:00"
    },
    {
        "lot_id": "LOT002",
        "lot_type": "Product-B",
        "vials": 1500,
        "fill_hours": 2.5
    }
]
```

### Running Tests

**⚠️ CRITICAL: Use TWO separate terminals with virtual environment activated in BOTH!**

```bash
# TERMINAL 1: Start server (keep running)
.\venv\Scripts\Activate.ps1  # Activate virtual environment
python -m uvicorn fillscheduler.api.main:app --port 8000

# TERMINAL 2: Run tests (in different terminal)
.\venv\Scripts\Activate.ps1  # Activate virtual environment
python test_auth_api.py
python test_schedule_api.py
python test_comparison_api.py

# All tests should output:
# ============================================================
# ALL <FEATURE> TESTS PASSED!
# ============================================================
```

**Common Mistake:** Running tests in same terminal as server → Tests won't run because server is blocking!

**Common Mistake:** Not activating virtual environment → Import errors or wrong package versions!

---

## Common Tasks

### Task 1: Add a New Endpoint

**Example:** Add GET /api/v1/schedule/{id}/summary

**Steps:**

1. **Add schema to `schemas.py`:**
```python
class ScheduleSummaryResponse(BaseModel):
    id: int
    name: str
    makespan: Optional[float] = None
    lots_count: int
    completed: bool
```

2. **Add endpoint to router:**
```python
# In src/fillscheduler/api/routers/schedule.py

@router.get("/schedule/{schedule_id}/summary", response_model=ScheduleSummaryResponse)
async def get_schedule_summary(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get schedule (with ownership check)
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Get result if exists
    result = db.query(ScheduleResult).filter(
        ScheduleResult.schedule_id == schedule_id
    ).first()

    return ScheduleSummaryResponse(
        id=schedule.id,
        name=schedule.name,
        makespan=result.makespan if result else None,
        lots_count=result.lots_scheduled if result else 0,
        completed=(schedule.status == "completed")
    )
```

3. **Test the endpoint:**
```python
# Add to test_schedule_api.py

def test_schedule_summary():
    # ... authentication ...

    # Create schedule
    schedule = create_schedule(headers, lots_data)
    schedule_id = schedule["id"]

    # Wait for completion
    wait_for_completion(headers, schedule_id)

    # Get summary
    summary_response = requests.get(
        f"{BASE_URL}/schedule/{schedule_id}/summary",
        headers=headers
    )
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["completed"] == True
    assert summary["makespan"] > 0
```

4. **Update documentation:**
- Add endpoint to `docs/SCHEDULE_ENDPOINTS_SUMMARY.md`
- Update OpenAPI docs (automatic via FastAPI)

### Task 2: Add a New Database Table

**Example:** Add ActivityLog table

**Steps:**

1. **Define model in `database.py`:**
```python
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # "create_schedule", "delete_schedule"
    resource_type = Column(String(50), nullable=False)  # "schedule", "comparison"
    resource_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="activity_logs")
```

2. **Add relationship to User model:**
```python
class User(Base):
    # ... existing fields ...

    # Add to relationships
    activity_logs = relationship("ActivityLog", back_populates="user")
```

3. **Create schema in `schemas.py`:**
```python
class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    resource_type: str
    resource_id: int
    timestamp: datetime
```

4. **Restart server (tables auto-created):**
```bash
# Tables created on startup via init_db()
python -m uvicorn fillscheduler.api.main:app
```

5. **Use in routers:**
```python
@router.post("/schedule")
async def create_schedule(...):
    # ... create schedule ...

    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="create_schedule",
        resource_type="schedule",
        resource_id=schedule.id
    )
    db.add(log)
    db.commit()

    return schedule
```

### Task 3: Add a New Service Function

**Example:** Add validation for configuration

**Steps:**

1. **Create function in appropriate service file:**
```python
# In src/fillscheduler/api/services/scheduler.py

def validate_config(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration parameters.

    Returns:
        Dict with 'valid', 'errors', 'warnings' keys
    """
    errors = []
    warnings = []

    # Check max_clean_hours
    if "max_clean_hours" in config_data:
        max_clean = config_data["max_clean_hours"]
        if not isinstance(max_clean, (int, float)):
            errors.append("max_clean_hours must be a number")
        elif max_clean < 0:
            errors.append("max_clean_hours must be positive")
        elif max_clean > 24:
            warnings.append("max_clean_hours > 24 is unusual")

    # Check changeover_matrix
    if "changeover_matrix" in config_data:
        matrix = config_data["changeover_matrix"]
        if not isinstance(matrix, dict):
            errors.append("changeover_matrix must be a dictionary")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
```

2. **Use in router:**
```python
@router.post("/schedule")
async def create_schedule(request: ScheduleRequest, ...):
    # Validate config
    if request.config:
        config_validation = validate_config(request.config)
        if not config_validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid configuration",
                    "errors": config_validation["errors"]
                }
            )

    # ... continue with schedule creation ...
```

3. **Add tests:**
```python
def test_config_validation():
    from fillscheduler.api.services.scheduler import validate_config

    # Valid config
    result = validate_config({"max_clean_hours": 4.0})
    assert result["valid"] == True

    # Invalid config
    result = validate_config({"max_clean_hours": "invalid"})
    assert result["valid"] == False
    assert len(result["errors"]) > 0
```

### Task 4: Fix a Bug

**Example:** Fix Bug #5 - Duplicate lot_id check

**Location:** `src/fillscheduler/api/services/scheduler.py:218-222`

**Current (buggy) code:**
```python
async def validate_lots_data(lots_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    errors = []
    warnings = []

    # Validate each lot
    for i, lot in enumerate(lots_data):  # INSIDE LOOP!
        # ... field validation ...

        # Check lot_id uniqueness - WRONG: runs N times!
        lot_ids = [lot.get("lot_id") for lot in lots_data]
        duplicates = [lid for lid in set(lot_ids) if lot_ids.count(lid) > 1]
        if duplicates:
            warnings.append(f"Duplicate lot_ids found: {duplicates}")
```

**Fixed code:**
```python
async def validate_lots_data(lots_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    errors = []
    warnings = []

    if not lots_data:
        errors.append("No lots provided")
        return {"valid": False, "errors": errors, "warnings": warnings, "lots_count": 0}

    # Check duplicate lot_ids ONCE, BEFORE loop
    lot_ids = [lot.get("lot_id") for lot in lots_data]
    seen = set()
    duplicates = []
    for lid in lot_ids:
        if lid in seen:
            duplicates.append(lid)
        seen.add(lid)

    if duplicates:
        # Make it an ERROR (not warning) - duplicates cause problems
        errors.append(f"Duplicate lot_ids found: {list(set(duplicates))}")

    # Validate each lot
    for i, lot in enumerate(lots_data):
        # ... field validation (unchanged) ...
        pass

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "lots_count": len(lots_data)
    }
```

**Test the fix:**
```python
def test_duplicate_lot_ids():
    from fillscheduler.api.services.scheduler import validate_lots_data

    lots = [
        {"lot_id": "A", "lot_type": "X", "vials": 100, "fill_hours": 1.0},
        {"lot_id": "B", "lot_type": "X", "vials": 100, "fill_hours": 1.0},
        {"lot_id": "A", "lot_type": "Y", "vials": 200, "fill_hours": 2.0}  # Duplicate!
    ]

    result = await validate_lots_data(lots)
    assert result["valid"] == False
    assert any("Duplicate" in error for error in result["errors"])
    assert "A" in str(result["errors"])
```

---

## Code Style & Conventions

### Python Style

- **PEP 8**: Follow standard Python style guide
- **Line length**: 100 characters (not 80)
- **Imports**: Group by standard library, third-party, local (separated by blank lines)
- **Docstrings**: Use for all public functions, classes, modules

**Example:**
```python
"""
Module docstring explaining purpose.
"""

# Standard library
import json
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local
from fillscheduler.api.dependencies import get_current_active_user
from fillscheduler.api.models.database import Schedule


async def function_name(
    param1: int,
    param2: str,
    optional_param: Optional[dict] = None
) -> dict:
    """
    Short description of function.

    Args:
        param1: Description of param1
        param2: Description of param2
        optional_param: Description of optional_param

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is negative
    """
    if param1 < 0:
        raise ValueError("param1 must be positive")

    # Implementation
    result = {"key": "value"}
    return result
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `schedule_id`, `lots_data` |
| Functions | snake_case | `create_schedule()`, `validate_lots_data()` |
| Classes | PascalCase | `Schedule`, `ScheduleResponse` |
| Constants | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE`, `DEFAULT_STRATEGY` |
| Private functions | _leading_underscore | `_run_schedule_background()` |
| Database tables | snake_case (plural) | `schedules`, `comparison_results` |
| API endpoints | kebab-case | `/api/v1/schedule-summary` |

### FastAPI Patterns

**Router organization:**
```python
router = APIRouter()

# Group endpoints by resource
@router.post("/resource")          # Create
@router.get("/resource/{id}")      # Read one
@router.get("/resources")           # Read many
@router.put("/resource/{id}")      # Update
@router.delete("/resource/{id}")   # Delete
@router.post("/resource/action")   # Custom action
```

**Dependency injection:**
```python
# Always use Depends() for dependencies
current_user: User = Depends(get_current_active_user)
db: Session = Depends(get_db)

# Not:
# current_user = get_current_active_user()  # WRONG
```

**Error handling:**
```python
# Use HTTPException for expected errors
if not schedule:
    raise HTTPException(status_code=404, detail="Schedule not found")

# Let unexpected errors propagate (FastAPI will handle with 500)
```

### Database Patterns

**Always use ORM (no raw SQL):**
```python
# Good
schedules = db.query(Schedule).filter(Schedule.user_id == user_id).all()

# Bad
# db.execute("SELECT * FROM schedules WHERE user_id = ?", (user_id,))
```

**Always check ownership:**
```python
# Good
schedule = db.query(Schedule).filter(
    Schedule.id == schedule_id,
    Schedule.user_id == current_user.id  # Ownership check
).first()

# Bad
# schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
# # Missing ownership check - security vulnerability!
```

**Close sessions in background tasks:**
```python
async def _background_task():
    db = SessionLocal()  # Create own session
    try:
        # ... work ...
        db.commit()
    finally:
        db.close()  # Always close
```

---

## Known Issues

### Critical Bugs (Production Blockers)

See `docs/codereviews/router_integration_bugs_13Oct2025.md` for detailed analysis.

**Quick Reference:**

| Bug # | Issue | Location | Severity |
|-------|-------|----------|----------|
| #1 | Race condition in background task DB session | schedule.py:41-100 | 🔴 Critical |
| #2 | Unsafe cascade delete (no transaction) | schedule.py:287-314 | 🔴 Critical |
| #4 | Timezone bug in start_time parsing | schedule.py:149-156 | 🔴 Critical |
| #5 | Duplicate lot_id check inefficiency | scheduler.py:218-222 | 🔴 Critical |
| #6 | Background task exception swallowing | schedule.py:93-98 | 🔴 Critical |
| #11 | No strategy validation before creation | schedule.py:103-177 | 🟡 High |

**Quick Fixes:**

1. **Bug #5 (Duplicate check):** Move check outside loop, make it an error
2. **Bug #11 (Strategy validation):** Add strategy validation before creating schedule
3. **Bug #2 (Cascade delete):** Remove manual deletion, rely on ORM cascade

### Minor Issues

- Thread pool executor never cleaned up (memory leak on restart)
- No rate limiting on API endpoints
- No request ID tracking for logging
- Missing indexes on some foreign keys

---

## Quick Reference

### Common Commands

**⚠️ ALWAYS activate virtual environment first!**

```bash
# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Verify virtual environment is active (should show "(venv)")
# Your prompt should look like: (venv) PS D:\GitHub\filling_scheduler>

# Start server (Terminal 1)
python -m uvicorn fillscheduler.api.main:app --reload

# Run tests (Terminal 2 - SEPARATE from server)
python test_schedule_api.py
python test_comparison_api.py

# Reset database
rm fillscheduler.db

# Install dependencies (in virtual environment)
pip install -r requirements.txt

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Deactivate virtual environment (when done)
deactivate
```

### Git Workflow Commands

```bash
# Check current status
git status

# Create feature branch
git checkout -b feature/new-endpoint
git checkout -b fix/bug-5-duplicate-check

# Stage and commit changes
git add src/fillscheduler/api/routers/new_file.py
git commit -m "feat: add new endpoint for X functionality"

# For bug fixes
git commit -m "fix: move duplicate lot_id check outside loop (Bug #5)"

# Push to remote
git push origin feature/new-endpoint

# Update from main
git checkout main
git pull origin main
git checkout feature/new-endpoint
git merge main

# View commit history
git log --oneline --graph --decorate
```

**Commit Message Convention:**
- `feat:` New feature (e.g., "feat: add comparison endpoints")
- `fix:` Bug fix (e.g., "fix: race condition in background task")
- `docs:` Documentation (e.g., "docs: update API reference")
- `test:` Tests (e.g., "test: add comparison API tests")
- `refactor:` Code improvement (e.g., "refactor: extract validation logic")
- `style:` Formatting (e.g., "style: fix indentation")
- `chore:` Maintenance (e.g., "chore: update dependencies")

### API Endpoints Summary

**Authentication (4 endpoints):**
- POST /api/v1/auth/register - Register user (201)
- POST /api/v1/auth/login - Login (200)
- GET /api/v1/auth/me - Get current user (200)
- POST /api/v1/auth/refresh - Refresh token (200)

**Schedules (7 endpoints):**
- POST /api/v1/schedule - Create schedule (202)
- GET /api/v1/schedule/{id} - Get schedule details (200)
- GET /api/v1/schedules - List schedules (200)
- DELETE /api/v1/schedule/{id} - Delete schedule (200)
- GET /api/v1/schedule/{id}/export?format=json|csv - Export (200)
- POST /api/v1/schedule/validate - Validate lots (200)
- GET /api/v1/strategies - List strategies (200)

**Comparisons (4 endpoints):**
- POST /api/v1/compare - Create comparison (202)
- GET /api/v1/compare/{id} - Get comparison results (200)
- GET /api/v1/comparisons - List comparisons (200)
- DELETE /api/v1/compare/{id} - Delete comparison (200)

### Available Strategies

1. **smart-pack** (default) - Intelligent type-aware packing
2. **spt-pack** - Shortest Processing Time first
3. **lpt-pack** - Longest Processing Time first
4. **cfs-pack** - Customer First Scheduling
5. **hybrid-pack** - Hybrid approach combining multiple strategies
6. **milp-opt** - MILP optimization (requires PuLP)

### File Locations

```
# Models
src/fillscheduler/api/models/database.py   # SQLAlchemy ORM
src/fillscheduler/api/models/schemas.py    # Pydantic schemas

# Routers
src/fillscheduler/api/routers/auth.py       # Auth endpoints
src/fillscheduler/api/routers/schedule.py   # Schedule endpoints
src/fillscheduler/api/routers/comparison.py # Comparison endpoints

# Services
src/fillscheduler/api/services/auth.py       # Auth logic
src/fillscheduler/api/services/scheduler.py  # Scheduler wrapper
src/fillscheduler/api/services/comparison.py # Parallel execution

# Core
fillscheduler/scheduler.py  # Core scheduling engine
fillscheduler/strategies/   # 6 scheduling algorithms

# Tests
test_auth_api.py        # Auth integration tests
test_schedule_api.py    # Schedule integration tests
test_comparison_api.py  # Comparison integration tests

# Docs
docs/SCHEDULE_ENDPOINTS_SUMMARY.md
docs/COMPARISON_ENDPOINTS_SUMMARY.md
docs/AGENT_DEVELOPMENT_GUIDE.md
```

### Environment Variables

```bash
# .env file (create if needed)
DATABASE_URL=sqlite:///./fillscheduler.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Useful SQL Queries

```sql
-- Count schedules by status
SELECT status, COUNT(*) FROM schedules GROUP BY status;

-- Recent schedules
SELECT id, name, strategy, status, created_at
FROM schedules
ORDER BY created_at DESC
LIMIT 10;

-- Comparison results
SELECT c.id, c.name, c.best_strategy, COUNT(cr.id) as result_count
FROM comparisons c
LEFT JOIN comparison_results cr ON c.id = cr.comparison_id
GROUP BY c.id;

-- User activity
SELECT u.email, COUNT(s.id) as schedule_count, COUNT(c.id) as comparison_count
FROM users u
LEFT JOIN schedules s ON u.id = s.user_id
LEFT JOIN comparisons c ON u.id = c.user_id
GROUP BY u.id;
```

---

## Troubleshooting

### Virtual Environment Not Activated

**Symptom:** Import errors, module not found, or wrong package versions

**Solution:**
```bash
# Activate virtual environment first!
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Verify - prompt should show (venv)
# Example: (venv) PS D:\GitHub\filling_scheduler>

# If virtual environment doesn't exist, create it:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Server Won't Start

**Symptom:** Import errors or module not found

**Solution:**
```bash
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Check Python path includes project root
cd d:/GitHub/filling_scheduler
python -c "import sys; print('\n'.join(sys.path))"

# Should show: d:\GitHub\filling_scheduler

# 3. If not, set PYTHONPATH
$env:PYTHONPATH = "d:\GitHub\filling_scheduler"

# 4. Reinstall dependencies in virtual environment
pip install -r requirements.txt
```

### Tests Fail with Connection Refused

**Symptom:** `ConnectionRefusedError: [WinError 10061]`

**Solution:**
```bash
# Problem: Server not running or tests running in same terminal as server

# TERMINAL 1: Start server (keep this running)
.\venv\Scripts\Activate.ps1
python -m uvicorn fillscheduler.api.main:app --port 8000

# TERMINAL 2: Run tests (open NEW terminal)
.\venv\Scripts\Activate.ps1
python test_schedule_api.py

# DO NOT run tests in same terminal as server!
```

### Database Locked Error

**Symptom:** `database is locked`

**Solution:**
```bash
# SQLite has a lock - close all connections
# Kill server (Ctrl+C)
# Restart server
python -m uvicorn fillscheduler.api.main:app --port 8000
```

### Import Errors from Core Scheduler

**Symptom:** `ModuleNotFoundError: No module named 'fillscheduler.scheduler'`

**Solution:**
```python
# Use absolute imports from project root
from fillscheduler.scheduler import plan_schedule  # Good
from fillscheduler.models import Lot, Activity    # Good

# Not relative imports
# from ..scheduler import plan_schedule  # Bad
```

---

## Next Steps

### Immediate Tasks (Bug Fixes)

1. Fix Bug #5 (duplicate lot_id check) - 10 minutes
2. Fix Bug #11 (strategy validation) - 15 minutes
3. Fix Bug #2 (unsafe cascade delete) - 10 minutes
4. Test fixes with integration tests - 15 minutes

### Phase 1.5: Configuration Endpoints (3-5 days)

- Create config template CRUD endpoints
- Add template sharing (public/private)
- Implement default configs
- Configuration validation
- Import/export functionality

### Phase 1.6: WebSocket Support (3-5 days)

- WebSocket connection manager
- Progress broadcasting during execution
- Client reconnection handling
- Testing WebSocket functionality

### Phase 2: Frontend (2-3 weeks)

- React + Vite + TypeScript setup
- Material-UI component library
- Authentication flow
- Schedule creation wizard
- Gantt chart visualization
- KPIs dashboard
- Comparison results view

---

## Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

### Internal Docs

- `docs/SCHEDULE_ENDPOINTS_SUMMARY.md` - Schedule API reference
- `docs/COMPARISON_ENDPOINTS_SUMMARY.md` - Comparison API reference
- `docs/codereviews/router_integration_bugs_13Oct2025.md` - Known bugs
- `README.md` - Project overview

### Code Examples

- `test_auth_api.py` - Authentication examples
- `test_schedule_api.py` - Schedule API examples
- `test_comparison_api.py` - Comparison API examples

---

**Last Updated:** October 13, 2025
**Maintainer:** AI Development Team
**Version:** 1.0

**Status:** ✅ Complete - Ready for agent use

---

## Appendix: Agent Workflow

### When Starting a New Task

1. **Activate virtual environment** - `.\venv\Scripts\Activate.ps1`
2. **Read this guide** - Understand project structure
3. **Check todo list** - See what's in progress
4. **Review existing code** - Look at similar implementations
5. **Read bug report** - Check for known issues in the area
6. **Write tests first** - Define expected behavior
7. **Implement feature** - Follow patterns in this guide
8. **Test thoroughly** - Run integration tests (separate terminal!)
9. **Update documentation** - Add to summary docs
10. **Update todo list** - Mark task complete

### When Debugging

1. **Activate virtual environment** - First thing always!
2. **Read error message** - Understand what failed
3. **Check server logs** - Look for SQL queries, exceptions (in server terminal)
4. **Check database** - Verify data state
5. **Check known issues** - See if bug is documented
6. **Add logging** - Use print() or logger.debug()
7. **Test fix** - Verify with integration test (separate terminal!)
8. **Document fix** - Update bug report if applicable

### When Adding Features

1. **Activate virtual environment** - `.\venv\Scripts\Activate.ps1`
2. **Design schema** - Database model, Pydantic schema
3. **Create service** - Business logic layer
4. **Create router** - HTTP endpoint layer
5. **Create test** - Integration test
6. **Start server** - Terminal 1: `python -m uvicorn fillscheduler.api.main:app --reload`
7. **Run test** - Terminal 2: `python test_<feature>_api.py`
8. **Document** - Add to summary doc
9. **Update todo** - Mark complete

---

**END OF GUIDE**
