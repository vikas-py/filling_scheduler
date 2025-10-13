# API & Frontend Architecture Overview

**Related Documents**:
- [API_FRONTEND_TODO.md](API_FRONTEND_TODO.md) - Complete implementation plan (172 items)
- [Restructuring_TODO.md](Restructuring_TODO.md) - Main project TODO (Section 10)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         React Frontend                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Dashboard  │  │  Schedule   │  │  Compare    │             │
│  │             │  │  Creation   │  │  Strategies │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────┐        │
│  │  Gantt Chart | KPI Cards | Config Editor            │        │
│  └─────────────────────────────────────────────────────┘        │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     │ HTTP/REST + WebSocket
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│                      FastAPI Backend                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  API Routers                                         │       │
│  │  /api/v1/schedule | /compare | /config | /auth      │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Business Logic (Existing Scheduler Code)            │       │
│  │  plan_schedule() | compare_strategies() | validate() │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Database Layer (SQLAlchemy)                         │       │
│  └──────────────────────────────────────────────────────┘       │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│                    PostgreSQL Database                            │
│  Tables: users | schedules | schedule_results | config_templates │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints Overview

### Authentication
```
POST   /api/v1/auth/register     Create new user account
POST   /api/v1/auth/login        Login and get JWT token
POST   /api/v1/auth/refresh      Refresh access token
GET    /api/v1/auth/me           Get current user info
```

### Schedule Management
```
POST   /api/v1/schedule          Create new schedule
GET    /api/v1/schedule/{id}     Get schedule details
GET    /api/v1/schedules         List user's schedules (paginated)
DELETE /api/v1/schedule/{id}     Delete schedule
GET    /api/v1/schedule/{id}/export?format=csv|excel|pdf
POST   /api/v1/schedule/validate Validate lots data
GET    /api/v1/strategies        List available strategies
```

### Strategy Comparison
```
POST   /api/v1/compare           Compare multiple strategies
GET    /api/v1/compare/{id}      Get comparison results
GET    /api/v1/comparisons       List user's comparisons
POST   /api/v1/compare/all       Compare all strategies
```

### Configuration
```
GET    /api/v1/config/default    Get default configuration
GET    /api/v1/config/templates  List saved templates
POST   /api/v1/config/templates  Save new template
GET    /api/v1/config/templates/{id}
DELETE /api/v1/config/templates/{id}
POST   /api/v1/config/validate   Validate configuration
```

### File Upload
```
POST   /api/v1/upload/lots       Upload CSV file
POST   /api/v1/upload/config     Upload config file (YAML/JSON)
```

### Real-time Updates
```
WS     /ws/schedule/{id}         WebSocket for progress updates
```

---

## 🎨 Frontend Components

### Pages
```
/                    Dashboard (recent schedules, quick stats)
/login               Login page
/register            Registration page
/schedule/new        Create new schedule
/schedule/:id        Schedule detail (Gantt, KPIs, activities)
/compare             Strategy comparison
/config              Configuration management
/profile             User profile
```

### Key Components

#### Schedule Creation Flow
```
1. FileUpload component (drag-and-drop CSV)
2. DataPreview component (validate & preview data)
3. StrategySelector component (choose strategy)
4. ConfigEditor component (tune parameters)
5. Submit → WebSocket connection for real-time progress
6. Redirect to ScheduleDetail page
```

#### Schedule Visualization
```
┌─────────────────────────────────────────────────────────────┐
│ Schedule Header                                              │
│ Strategy: smart-pack | Created: 2025-10-12 | Status: ✓     │
├─────────────────────────────────────────────────────────────┤
│ KPI Cards                                                    │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│ │ Makespan │ │Utilization│ │Changeovers│ │   Lots  │       │
│ │ 156.75h  │ │   87.3%   │ │     3    │ │    15   │       │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│ Gantt Chart                                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Lot 1  ████████████                                      │ │
│ │ Lot 2    ██████████                                      │ │
│ │ Lot 3               ███████████                          │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Activity List (Table)                                        │
│ Start       | End         | Type      | Lot ID | Duration  │
│ 08:00:00    | 14:30:00    | Filling   | LOT001 | 6.5h     │
│ 14:30:00    | 15:30:00    | Cleaning  | -      | 1.0h     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Real-time Progress Flow

```
User Clicks "Create Schedule"
         │
         ▼
Frontend POST /api/v1/schedule
         │
         ▼
Backend Creates Task & Returns schedule_id
         │
         ▼
Frontend Opens WebSocket /ws/schedule/{id}
         │
         ▼
Backend Sends Progress Updates:
  { "step": "loading", "progress": 10, "message": "Loading lots..." }
  { "step": "validating", "progress": 30, "message": "Validating..." }
  { "step": "planning", "progress": 50, "message": "Planning schedule..." }
  { "step": "writing", "progress": 90, "message": "Writing outputs..." }
  { "step": "complete", "progress": 100, "schedule": {...} }
         │
         ▼
Frontend Shows Progress Bar + Messages
         │
         ▼
On Completion: Navigate to /schedule/{id}
```

---

## 💾 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Schedules Table
```sql
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255),
    strategy VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    config_json JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

### Schedule Results Table
```sql
CREATE TABLE schedule_results (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER REFERENCES schedules(id) ON DELETE CASCADE,
    makespan FLOAT,
    utilization FLOAT,
    changeovers INTEGER,
    lots_scheduled INTEGER,
    kpis_json JSONB,
    activities_json JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Config Templates Table
```sql
CREATE TABLE config_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config_json JSONB NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 Authentication Flow

```
1. User Registration
   POST /api/v1/auth/register { email, password }
   → Backend hashes password with bcrypt
   → Store user in database
   → Return success message

2. User Login
   POST /api/v1/auth/login { email, password }
   → Backend verifies password
   → Generate JWT token (expires in 24h)
   → Return { access_token, token_type: "bearer" }

3. Authenticated Requests
   Frontend stores token in memory/localStorage
   Include in headers: Authorization: Bearer <token>
   Backend middleware validates token
   Inject user into request context

4. Token Refresh
   POST /api/v1/auth/refresh
   → Validate old token
   → Issue new token
   → Return new access_token
```

---

## 📊 Data Flow Example: Create Schedule

### 1. User Uploads CSV
```javascript
// Frontend
const formData = new FormData();
formData.append('file', csvFile);
const response = await axios.post('/api/v1/upload/lots', formData);
const lotsData = response.data.lots;
```

### 2. User Configures & Submits
```javascript
// Frontend
const scheduleRequest = {
  lots: lotsData,
  strategy: 'smart-pack',
  config: { CLEAN_HOURS: 24.0, WINDOW_HOURS: 120.0 },
  start_time: '2025-01-01T08:00:00'
};
const response = await axios.post('/api/v1/schedule', scheduleRequest);
const scheduleId = response.data.id;
```

### 3. Backend Processes
```python
# Backend (FastAPI)
@router.post("/schedule")
async def create_schedule(
    request: ScheduleRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    # Create schedule record
    schedule = Schedule(user_id=current_user.id, status="pending")
    db.add(schedule)
    db.commit()

    # Run scheduler in background
    background_tasks.add_task(
        run_scheduler,
        schedule_id=schedule.id,
        lots=request.lots,
        config=request.config
    )

    return {"id": schedule.id, "status": "pending"}
```

### 4. Real-time Updates via WebSocket
```python
# Backend (WebSocket)
async def run_scheduler(schedule_id, lots, config):
    manager = get_websocket_manager()

    await manager.send_message(schedule_id, {
        "step": "loading", "progress": 10
    })

    # Run actual scheduler
    activities, makespan, kpis = plan_schedule(lots, config)

    await manager.send_message(schedule_id, {
        "step": "complete", "progress": 100,
        "schedule": { "activities": activities, "kpis": kpis }
    })

    # Save to database
    save_schedule_result(schedule_id, activities, kpis)
```

### 5. Frontend Displays Results
```javascript
// Frontend
const ws = new WebSocket(`ws://api.example.com/ws/schedule/${scheduleId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.step === 'complete') {
    navigate(`/schedule/${scheduleId}`);
  } else {
    setProgress(data.progress);
    setMessage(data.message);
  }
};
```

---

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
│                      (HTTPS / SSL)                           │
└────────────┬────────────────────────────────────┬────────────┘
             │                                    │
    ┌────────▼────────┐                  ┌────────▼────────┐
    │  Frontend       │                  │  Frontend       │
    │  (Nginx)        │                  │  (Nginx)        │
    │  Port 80        │                  │  Port 80        │
    └────────┬────────┘                  └────────┬────────┘
             │                                    │
             └────────────────┬───────────────────┘
                              │
                     ┌────────▼────────┐
                     │  Backend API    │
                     │  (FastAPI)      │
                     │  Port 8000      │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │  PostgreSQL     │
                     │  Port 5432      │
                     └─────────────────┘
```

### Docker Compose Setup
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/fillscheduler
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=fillscheduler
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=fillscheduler

volumes:
  postgres_data:
```

---

## 📈 MVP vs Full Feature Comparison

### MVP (8 weeks)
- ✅ User authentication
- ✅ Schedule creation (basic)
- ✅ Strategy comparison
- ✅ Configuration management
- ✅ Gantt chart visualization
- ✅ KPI display
- ✅ File upload (CSV)
- ✅ Real-time progress (WebSocket)
- ✅ Basic dashboard
- ✅ Docker deployment

### Full Version (12+ weeks)
- All MVP features, plus:
- ✅ Advanced scheduling (templates, constraints)
- ✅ Comprehensive analytics
- ✅ Custom reports & exports
- ✅ Email/Slack notifications
- ✅ Multi-user collaboration
- ✅ Role-based access control
- ✅ API keys for programmatic access
- ✅ ERP integrations
- ✅ Calendar integrations
- ✅ Advanced visualizations
- ✅ Performance optimization
- ✅ Security hardening
- ✅ Cost calculations
- ✅ Forecasting & planning

---

## 🎯 Success Metrics

### Technical Metrics
- API response time: < 200ms (P95)
- Schedule generation: < 30s for 100 lots
- Frontend load time: < 3s
- Test coverage: > 80%
- Uptime: > 99.5%

### User Metrics
- Time to first schedule: < 5 minutes
- User satisfaction: > 4/5 stars
- Active users: Track monthly
- Schedules created: Track weekly

---

*For detailed implementation steps, see [API_FRONTEND_TODO.md](API_FRONTEND_TODO.md)*
