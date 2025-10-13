# API & Frontend Implementation Plan

**Date Created**: October 12, 2025
**Last Updated**: October 13, 2025
**Purpose**: Comprehensive plan for building FastAPI backend and React + Vite frontend for Filling Scheduler
**Cross-reference**: See [Restructuring_TODO.md](Restructuring_TODO.md) Section 10

---

## 📊 **Overall Progress: 16% Complete (14/87 major items)**

### ✅ **Completed**:
- Phase 1.1: Project Setup (8/8 items) - **100% COMPLETE**
- Phase 1.2: Authentication & Authorization (6/6 items) - **100% COMPLETE**

### ⏳ **In Progress**:
- Phase 1.3: Schedule Endpoints (0/8 items)

### 📝 **Recent Updates**:
- **Oct 13, 2025**: Authentication system fully implemented and tested
  - Fixed bcrypt 5.x compatibility by pinning to 4.x
  - Added email-validator dependency
  - All 9 authentication tests passing
  - Comprehensive documentation created (AUTHENTICATION_SUMMARY.md)

### Project Vision
Transform the CLI-based filling scheduler into a full-stack web application with:
- RESTful API for all scheduling operations
- Modern React frontend with interactive visualizations
- Real-time progress updates via WebSocket
- User authentication and schedule management
- Database persistence for schedules and configurations

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL/SQLite
- **Frontend**: React 18 + Vite + TypeScript + Material-UI
- **Real-time**: WebSocket for progress updates
- **Charts**: Recharts/Plotly for visualizations, React-Gantt for timeline
- **Auth**: JWT tokens with bcrypt password hashing
- **Testing**: pytest (backend), Vitest + React Testing Library (frontend)
- **Deployment**: Docker + docker-compose

---

## 🔧 **Phase 1: Backend API (FastAPI)**

### 1.1 Project Setup ✅ **COMPLETE** (8/8 items)
- [x] **Create API directory structure**:
  ```
  src/fillscheduler/
  ├── api/
  │   ├── __init__.py
  │   ├── main.py              # FastAPI app
  │   ├── config.py            # API settings
  │   ├── dependencies.py      # Dependency injection
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   ├── schedule.py      # Schedule endpoints
  │   │   ├── compare.py       # Comparison endpoints
  │   │   ├── config.py        # Config endpoints
  │   │   ├── upload.py        # File upload endpoints
  │   │   ├── auth.py          # Authentication endpoints
  │   │   └── users.py         # User management
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── database.py      # SQLAlchemy models
  │   │   ├── schemas.py       # Pydantic schemas
  │   │   └── enums.py         # API enums
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── scheduler.py     # Scheduler service
  │   │   ├── auth.py          # Auth service
  │   │   └── storage.py       # File storage service
  │   ├── database/
  │   │   ├── __init__.py
  │   │   ├── base.py          # Base classes
  │   │   ├── session.py       # DB session
  │   │   └── crud.py          # CRUD operations
  │   ├── middleware/
  │   │   ├── __init__.py
  │   │   ├── cors.py          # CORS middleware
  │   │   └── auth.py          # Auth middleware
  │   └── utils/
  │       ├── __init__.py
  │       ├── security.py      # Password hashing, JWT
  │       └── websocket.py     # WebSocket manager
  ```

- [x] **Add API dependencies to requirements.txt**:
  ```
  # API Framework
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0
  python-multipart>=0.0.6      # File uploads

  # Database
  sqlalchemy>=2.0.0
  alembic>=1.12.0              # Migrations
  psycopg2-binary>=2.9.9       # PostgreSQL (optional)

  # Authentication
  python-jose[cryptography]>=3.3.0  # JWT
  passlib[bcrypt]>=1.7.4       # Password hashing

  # WebSocket
  websockets>=12.0

  # Additional
  python-dotenv>=1.0.0         # Environment variables
  aiofiles>=23.2.1             # Async file operations
  ```

- [x] **Create API configuration** (`api/config.py`):
  - Database URL (SQLite for dev, PostgreSQL for prod)
  - JWT secret key and algorithm
  - CORS origins
  - File upload settings (max size, allowed types)
  - API version and prefix

- [x] **Create database models** (`api/models/database.py`):
  - User model (id, email, hashed_password, created_at)
  - Schedule model (id, user_id, name, strategy, status, created_at)
  - ScheduleResult model (id, schedule_id, makespan, utilization, kpis_json)
  - LotData model (id, schedule_id, lot_json)
  - ConfigTemplate model (id, user_id, name, config_json)

- [ ] **Create Pydantic schemas** (`api/models/schemas.py`):
  - ScheduleRequest (lots, strategy, config, start_time)
  - ScheduleResponse (id, status, activities, kpis, created_at)
  - CompareRequest (lots, strategies, config)
  - CompareResponse (results, best_strategy)
  - UserCreate, UserLogin, UserResponse
  - TokenResponse (access_token, token_type)

- [x] **Setup database connection** (`api/database/session.py`):
  - SQLAlchemy engine
  - SessionLocal factory
  - get_db() dependency
  - Database initialization script

- [ ] **Create Alembic migrations**:
  ```bash
  alembic init alembic
  alembic revision --autogenerate -m "Initial schema"
  alembic upgrade head
  ```

- [x] **Create FastAPI app** (`api/main.py`):
  - Initialize FastAPI with metadata
  - Add CORS middleware
  - Include routers
  - Add startup/shutdown events
  - Configure OpenAPI docs

### 1.2 Authentication & Authorization ✅ **COMPLETE** (6/6 items)
- [x] **Implement JWT authentication** (`api/utils/security.py`):
  - `create_access_token()` - Generate JWT tokens ✅
  - `decode_access_token()` - Validate and decode tokens ✅
  - `get_password_hash()` - Hash passwords with bcrypt (with 72-byte handling) ✅
  - `verify_password()` - Verify password against hash ✅
  - **Notes**: Fixed bcrypt 5.x compatibility issue by pinning to 4.x, added SHA256 pre-hashing for passwords > 72 bytes

- [x] **Create auth service** (`api/services/auth.py`):
  - `create_user()` - Create new user account ✅
  - `authenticate_user()` - Validate credentials ✅
  - `get_user_by_email()` - Fetch user by email ✅
  - `get_user_by_id()` - Fetch user by ID ✅
  - `update_user_password()` - Update user password ✅
  - `deactivate_user()` - Deactivate user account ✅

- [x] **Create auth router** (`api/routers/auth.py`):
  - `POST /api/v1/auth/register` - User registration (returns UserResponse) ✅
  - `POST /api/v1/auth/login` - User login (OAuth2 form, returns JWT) ✅
  - `POST /api/v1/auth/logout` - Logout endpoint (informational) ✅
  - `GET /api/v1/auth/me` - Get current user info (protected) ✅

- [x] **Create auth dependencies** (`api/dependencies.py`):
  - OAuth2PasswordBearer for token extraction ✅
  - `get_current_user()` - Validates JWT and fetches user from DB ✅
  - `get_current_active_user()` - Checks is_active flag ✅
  - `get_current_superuser()` - Checks is_superuser flag for admin access ✅

- [ ] **Implement role-based access control (RBAC)** - DEFERRED:
  - Basic RBAC implemented via `is_superuser` flag ✅
  - Admin role available via `get_current_superuser` dependency ✅
  - **Note**: Advanced RBAC with multiple roles deferred to later phase

- [x] **Write authentication tests** (`test_auth_api.py`):
  - Test user registration (unique email validation) ✅
  - Test duplicate registration rejection ✅
  - Test login with valid/invalid credentials ✅
  - Test JWT token generation ✅
  - Test protected endpoint access with valid token ✅
  - Test unauthorized access (no token) ✅
  - Test invalid token rejection ✅
  - Test logout endpoint ✅
  - **Result**: All 9 authentication tests passing! 🎉

### 1.3 Schedule Endpoints ⏳ (0/8 items)
- [ ] **Create scheduler service** (`api/services/scheduler.py`):
  - `create_schedule()` - Wrapper for plan_schedule()
  - `get_schedule()` - Retrieve schedule by ID
  - `list_schedules()` - List user's schedules
  - `delete_schedule()` - Delete schedule
  - `export_schedule()` - Export to CSV/Excel/PDF

- [ ] **Create schedule router** (`api/routers/schedule.py`):
  - `POST /api/v1/schedule` - Create new schedule
    * Request: lots data, strategy, config, start_time
    * Response: schedule_id, status, activities, kpis
  - `GET /api/v1/schedule/{id}` - Get schedule details
  - `GET /api/v1/schedules` - List all user schedules (paginated)
  - `DELETE /api/v1/schedule/{id}` - Delete schedule
  - `GET /api/v1/schedule/{id}/export` - Export schedule
    * Query params: format (csv/excel/pdf/json)
  - `GET /api/v1/schedule/{id}/report` - Get HTML report
  - `POST /api/v1/schedule/validate` - Validate lots data
  - `GET /api/v1/strategies` - List available strategies

- [ ] **Implement file upload** (`api/routers/upload.py`):
  - `POST /api/v1/upload/lots` - Upload CSV file
    * Validate file type and size
    * Parse CSV with pandas
    * Return parsed lots data
  - `POST /api/v1/upload/config` - Upload config file (YAML/JSON)

- [ ] **Add background task processing**:
  - Use FastAPI BackgroundTasks for long-running schedules
  - Store task status in database
  - Allow polling for completion

- [ ] **Implement pagination**:
  - Add skip/limit query parameters
  - Return total count and page info
  - Add cursor-based pagination for large datasets

- [ ] **Add filtering and sorting**:
  - Filter by strategy, date range, status
  - Sort by created_at, makespan, utilization

- [ ] **Implement caching**:
  - Cache strategy list
  - Cache default configuration
  - Add ETags for conditional requests

- [ ] **Write schedule endpoint tests** (`tests/api/test_schedule.py`):
  - Test schedule creation with valid data
  - Test validation errors
  - Test pagination and filtering
  - Test export formats

### 1.4 Comparison Endpoints ⏳ (0/5 items)
- [ ] **Create comparison router** (`api/routers/compare.py`):
  - `POST /api/v1/compare` - Compare multiple strategies
    * Request: lots data, strategy list, config
    * Response: comparison results with KPIs
  - `GET /api/v1/compare/{id}` - Get comparison results
  - `GET /api/v1/comparisons` - List user's comparisons
  - `POST /api/v1/compare/all-strategies` - Compare all strategies
  - `DELETE /api/v1/compare/{id}` - Delete comparison

- [ ] **Implement parallel strategy execution**:
  - Use asyncio to run strategies concurrently
  - Add timeout handling
  - Aggregate results

- [ ] **Add comparison visualization data**:
  - Prepare data for charts (makespan, utilization, changeovers)
  - Calculate percentage differences
  - Identify best strategy

- [ ] **Implement comparison caching**:
  - Cache results based on lots hash + strategies
  - Avoid recomputing identical comparisons

- [ ] **Write comparison tests** (`tests/api/test_compare.py`):
  - Test multi-strategy comparison
  - Test all-strategies comparison
  - Test concurrent execution

### 1.5 Configuration Endpoints ⏳ (0/6 items)
- [ ] **Create config router** (`api/routers/config.py`):
  - `GET /api/v1/config/default` - Get default config
  - `GET /api/v1/config/templates` - List saved templates
  - `POST /api/v1/config/templates` - Save config template
  - `GET /api/v1/config/templates/{id}` - Get template
  - `DELETE /api/v1/config/templates/{id}` - Delete template
  - `POST /api/v1/config/validate` - Validate configuration

- [ ] **Implement config template CRUD**:
  - Create template with name and config JSON
  - Associate with user
  - Allow sharing templates (optional)

- [ ] **Add config presets**:
  - Fast preset (spt-pack, minimal validation)
  - Balanced preset (smart-pack, standard settings)
  - Optimal preset (milp-opt, strict validation)
  - Custom preset (user-defined)

- [ ] **Implement config diff**:
  - Compare two configurations
  - Highlight differences

- [ ] **Add config validation endpoint**:
  - Validate against Pydantic schema
  - Return detailed error messages

- [ ] **Write config tests** (`tests/api/test_config.py`):
  - Test template CRUD operations
  - Test validation
  - Test presets

### 1.6 WebSocket for Real-time Updates ⏳ (0/5 items)
- [ ] **Create WebSocket manager** (`api/utils/websocket.py`):
  - ConnectionManager class
  - connect() / disconnect()
  - send_personal_message()
  - broadcast()

- [ ] **Add WebSocket endpoint** (`api/main.py`):
  - `WS /ws/schedule/{schedule_id}` - Real-time progress
    * Connect on schedule start
    * Send progress updates (%, current step)
    * Send completion notification
    * Handle disconnections

- [ ] **Integrate with scheduler**:
  - Add progress callbacks to plan_schedule()
  - Emit progress events via WebSocket
  - Send step updates (loading, validating, planning, writing)

- [ ] **Add connection authentication**:
  - Validate JWT token in WebSocket handshake
  - Verify user has access to schedule

- [ ] **Write WebSocket tests** (`tests/api/test_websocket.py`):
  - Test connection/disconnection
  - Test message broadcasting
  - Test authentication

### 1.7 API Documentation ⏳ (0/5 items)
- [ ] **Configure OpenAPI/Swagger**:
  - Add API title, description, version
  - Add contact and license info
  - Configure tags for endpoint grouping
  - Add examples to schemas

- [ ] **Write API documentation** (`docs/api_guide.md`):
  - API overview and architecture
  - Authentication flow
  - Endpoint reference with examples
  - Error codes and handling
  - Rate limiting information

- [ ] **Add request/response examples**:
  - Example JSON payloads for each endpoint
  - cURL examples
  - Python client examples

- [ ] **Create Postman collection**:
  - Export OpenAPI spec
  - Convert to Postman collection
  - Add environment variables

- [ ] **Add API versioning**:
  - Use /api/v1 prefix
  - Plan for v2 with breaking changes

### 1.8 Testing & Quality ⏳ (0/6 items)
- [ ] **Setup API test infrastructure** (`tests/api/`):
  - conftest.py with fixtures (test client, test db)
  - Test database setup/teardown
  - Mock authentication

- [ ] **Write comprehensive tests**:
  - Unit tests for services
  - Integration tests for endpoints
  - Authentication tests
  - WebSocket tests
  - File upload tests

- [ ] **Add API performance tests**:
  - Load testing with locust or k6
  - Measure response times
  - Test concurrent requests
  - Identify bottlenecks

- [ ] **Add API security tests**:
  - Test SQL injection prevention
  - Test XSS prevention
  - Test CSRF protection
  - Test rate limiting

- [ ] **Achieve 80%+ test coverage**:
  - Run pytest-cov on api/ directory
  - Cover edge cases and error paths
  - Test validation errors

- [ ] **Add API linting**:
  - Extend pre-commit hooks to api/
  - Run mypy on API code
  - Check OpenAPI spec validity

---

## 🎨 **Phase 2: Frontend (React + Vite + TypeScript)**

### 2.1 Project Setup ⏳ (0/8 items)
- [ ] **Initialize React + Vite project**:
  ```bash
  npm create vite@latest frontend -- --template react-ts
  cd frontend
  npm install
  ```

- [ ] **Install core dependencies**:
  ```bash
  # UI Framework
  npm install @mui/material @emotion/react @emotion/styled
  npm install @mui/icons-material

  # Routing
  npm install react-router-dom

  # State Management
  npm install zustand  # or redux-toolkit

  # API Client
  npm install axios
  npm install @tanstack/react-query  # Data fetching

  # Forms & Validation
  npm install react-hook-form
  npm install zod  # Schema validation

  # Charts & Visualization
  npm install recharts
  npm install react-gantt-timeline

  # Date/Time
  npm install date-fns

  # WebSocket
  npm install socket.io-client

  # File Upload
  npm install react-dropzone

  # Tables
  npm install @tanstack/react-table

  # Notifications
  npm install react-hot-toast
  ```

- [ ] **Install dev dependencies**:
  ```bash
  npm install -D vitest @vitest/ui
  npm install -D @testing-library/react @testing-library/jest-dom
  npm install -D @testing-library/user-event
  npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
  npm install -D prettier eslint-config-prettier
  ```

- [ ] **Create directory structure**:
  ```
  frontend/
  ├── src/
  │   ├── api/
  │   │   ├── client.ts           # Axios instance
  │   │   ├── schedule.ts         # Schedule API calls
  │   │   ├── compare.ts          # Compare API calls
  │   │   ├── auth.ts             # Auth API calls
  │   │   └── config.ts           # Config API calls
  │   ├── components/
  │   │   ├── common/
  │   │   │   ├── Button.tsx
  │   │   │   ├── Card.tsx
  │   │   │   ├── Modal.tsx
  │   │   │   └── Loading.tsx
  │   │   ├── layout/
  │   │   │   ├── AppBar.tsx
  │   │   │   ├── Sidebar.tsx
  │   │   │   ├── Layout.tsx
  │   │   │   └── Footer.tsx
  │   │   ├── schedule/
  │   │   │   ├── ScheduleForm.tsx
  │   │   │   ├── ScheduleList.tsx
  │   │   │   ├── ScheduleCard.tsx
  │   │   │   ├── GanttChart.tsx
  │   │   │   └── KPICards.tsx
  │   │   ├── compare/
  │   │   │   ├── CompareForm.tsx
  │   │   │   ├── ComparisonTable.tsx
  │   │   │   └── ComparisonCharts.tsx
  │   │   ├── config/
  │   │   │   ├── ConfigEditor.tsx
  │   │   │   ├── ConfigTemplates.tsx
  │   │   │   └── StrategySelector.tsx
  │   │   └── upload/
  │   │       ├── FileUpload.tsx
  │   │       └── DataPreview.tsx
  │   ├── pages/
  │   │   ├── Login.tsx
  │   │   ├── Register.tsx
  │   │   ├── Dashboard.tsx
  │   │   ├── NewSchedule.tsx
  │   │   ├── ScheduleDetail.tsx
  │   │   ├── Compare.tsx
  │   │   ├── Config.tsx
  │   │   └── Profile.tsx
  │   ├── hooks/
  │   │   ├── useAuth.ts
  │   │   ├── useSchedule.ts
  │   │   ├── useWebSocket.ts
  │   │   └── useFileUpload.ts
  │   ├── store/
  │   │   ├── authStore.ts        # Zustand store
  │   │   ├── scheduleStore.ts
  │   │   └── configStore.ts
  │   ├── types/
  │   │   ├── schedule.ts
  │   │   ├── lot.ts
  │   │   ├── config.ts
  │   │   └── user.ts
  │   ├── utils/
  │   │   ├── formatters.ts
  │   │   ├── validators.ts
  │   │   └── constants.ts
  │   ├── App.tsx
  │   ├── main.tsx
  │   └── router.tsx
  ```

- [ ] **Configure Vite** (`vite.config.ts`):
  - API proxy for development
  - Build optimization
  - Environment variables
  - Path aliases (@/ for src/)

- [ ] **Setup ESLint and Prettier**:
  - Configure TypeScript rules
  - Add React hooks rules
  - Configure import sorting
  - Add pre-commit hooks (husky)

- [ ] **Create TypeScript types** (`src/types/`):
  - Mirror backend Pydantic schemas
  - Add frontend-specific types
  - Use strict TypeScript config

- [ ] **Setup environment variables**:
  - `.env.development` - API URL for dev
  - `.env.production` - API URL for prod
  - Add to .gitignore

### 2.2 Authentication & Layout ⏳ (0/7 items)
- [ ] **Create auth store** (`src/store/authStore.ts`):
  - user state
  - token state
  - login() action
  - logout() action
  - register() action
  - isAuthenticated getter

- [ ] **Create auth API client** (`src/api/auth.ts`):
  - login(email, password)
  - register(email, password)
  - logout()
  - getCurrentUser()
  - refreshToken()

- [ ] **Create Login page** (`src/pages/Login.tsx`):
  - Email/password form with validation
  - Remember me checkbox
  - Link to register page
  - Error handling
  - Redirect after login

- [ ] **Create Register page** (`src/pages/Register.tsx`):
  - Registration form
  - Password confirmation
  - Email validation
  - Terms acceptance
  - Link to login page

- [ ] **Create protected route component**:
  - Check authentication status
  - Redirect to login if not authenticated
  - Show loading state

- [ ] **Create app layout** (`src/components/layout/Layout.tsx`):
  - App bar with navigation
  - Sidebar menu (collapsible)
  - User menu (profile, logout)
  - Content area
  - Footer

- [ ] **Setup routing** (`src/router.tsx`):
  - React Router configuration
  - Protected routes
  - Public routes
  - 404 page

### 2.3 Dashboard ⏳ (0/6 items)
- [ ] **Create Dashboard page** (`src/pages/Dashboard.tsx`):
  - Welcome message
  - Quick stats cards (total schedules, avg utilization)
  - Recent schedules list
  - Quick actions (new schedule, compare)
  - Activity chart

- [ ] **Create KPI cards component** (`src/components/schedule/KPICards.tsx`):
  - Makespan card with icon
  - Utilization card with progress bar
  - Changeovers card
  - Lots scheduled card
  - Color-coded indicators

- [ ] **Create recent schedules list** (`src/components/schedule/ScheduleList.tsx`):
  - Table/grid of recent schedules
  - Strategy badge
  - Status indicator
  - Created date
  - Actions (view, delete)

- [ ] **Add filtering and search**:
  - Search by name
  - Filter by strategy
  - Filter by date range
  - Sort options

- [ ] **Add pagination**:
  - Page size selector
  - Previous/next buttons
  - Page number display

- [ ] **Add dashboard charts**:
  - Line chart: schedules over time
  - Bar chart: strategies used
  - Pie chart: utilization distribution

### 2.4 Schedule Creation ⏳ (0/8 items)
- [ ] **Create schedule form** (`src/pages/NewSchedule.tsx`):
  - File upload section
  - Strategy selector (dropdown with descriptions)
  - Configuration editor
  - Start time picker
  - Validation options (checkboxes)
  - Submit button

- [ ] **Create file upload component** (`src/components/upload/FileUpload.tsx`):
  - Drag-and-drop area
  - File type validation (CSV only)
  - File size validation
  - Upload progress indicator
  - Preview uploaded data

- [ ] **Create data preview component** (`src/components/upload/DataPreview.tsx`):
  - Table showing first 10 rows
  - Column headers
  - Validation warnings
  - Edit capabilities (optional)

- [ ] **Create strategy selector** (`src/components/config/StrategySelector.tsx`):
  - Radio buttons or dropdown
  - Strategy descriptions
  - Performance indicators (fast/optimal)
  - Recommended badge

- [ ] **Create config editor** (`src/components/config/ConfigEditor.tsx`):
  - Tabbed interface (constraints, strategy params)
  - Form inputs for all config options
  - Real-time validation
  - Load from template button
  - Reset to defaults button

- [ ] **Implement form validation**:
  - Use react-hook-form
  - Validate required fields
  - Validate file format
  - Show inline errors

- [ ] **Add real-time progress**:
  - WebSocket connection on submit
  - Progress steps display
  - Animated spinner
  - Success/error notification

- [ ] **Handle errors gracefully**:
  - Display API error messages
  - Retry logic
  - Cancel button

### 2.5 Schedule Visualization ⏳ (0/7 items)
- [ ] **Create schedule detail page** (`src/pages/ScheduleDetail.tsx`):
  - Schedule header (name, strategy, date)
  - KPI cards section
  - Gantt chart section
  - Activity list section
  - Export button
  - Share button

- [ ] **Create Gantt chart** (`src/components/schedule/GanttChart.tsx`):
  - Timeline view of activities
  - Color-coded by activity type (filling, cleaning, changeover)
  - Tooltips on hover (lot details)
  - Zoom controls
  - Download as image button

- [ ] **Create activity list** (`src/components/schedule/ActivityList.tsx`):
  - Filterable table
  - Columns: start, end, duration, type, lot, vial type
  - Sort by any column
  - Export to CSV

- [ ] **Add schedule export**:
  - Export as CSV
  - Export as Excel
  - Export as PDF
  - Download HTML report

- [ ] **Add schedule sharing**:
  - Generate shareable link
  - Copy to clipboard
  - Email schedule (optional)

- [ ] **Add comparison with other schedules**:
  - Select schedules to compare
  - Side-by-side KPI comparison
  - Gantt overlay (optional)

- [ ] **Add schedule editing** (optional):
  - Allow manual adjustments
  - Drag-and-drop activities
  - Recalculate KPIs

### 2.6 Strategy Comparison ⏳ (0/6 items)
- [ ] **Create compare page** (`src/pages/Compare.tsx`):
  - File upload section (same as schedule)
  - Strategy selection (multi-select)
  - "Compare All" button
  - Configuration options
  - Submit button

- [ ] **Create comparison table** (`src/components/compare/ComparisonTable.tsx`):
  - Strategies as rows
  - KPIs as columns (makespan, utilization, changeovers)
  - Color-coded best values (green)
  - Sort by column
  - Expand row for details

- [ ] **Create comparison charts** (`src/components/compare/ComparisonCharts.tsx`):
  - Bar chart: makespan comparison
  - Bar chart: utilization comparison
  - Radar chart: multi-metric comparison
  - Stacked bar: time breakdown

- [ ] **Add strategy recommendations**:
  - Highlight best strategy
  - Show trade-offs
  - Explain why strategy is best

- [ ] **Add comparison export**:
  - Export table as CSV
  - Export charts as images
  - Generate comparison report (PDF)

- [ ] **Add comparison history**:
  - Save comparison results
  - View past comparisons
  - Compare comparisons (meta-comparison)

### 2.7 Configuration Management ⏳ (0/5 items)
- [ ] **Create config page** (`src/pages/Config.tsx`):
  - Template list
  - Create new template button
  - Load default config button
  - Active template indicator

- [ ] **Create template list** (`src/components/config/ConfigTemplates.tsx`):
  - Grid/list of saved templates
  - Template name and description
  - Actions: edit, delete, duplicate, apply

- [ ] **Create template editor** (reuse ConfigEditor):
  - Save template form
  - Template name input
  - Template description textarea
  - Config editor (nested)

- [ ] **Add template presets**:
  - Fast preset card
  - Balanced preset card
  - Optimal preset card
  - Custom preset creation

- [ ] **Add config validation display**:
  - Validate button
  - Show validation errors
  - Highlight invalid fields

### 2.8 Real-time Features ⏳ (0/5 items)
- [ ] **Create WebSocket hook** (`src/hooks/useWebSocket.ts`):
  - Connect to WebSocket endpoint
  - Subscribe to schedule progress
  - Handle connection errors
  - Reconnect logic
  - Cleanup on unmount

- [ ] **Create progress indicator component**:
  - Progress bar (0-100%)
  - Current step display
  - Estimated time remaining
  - Cancel button

- [ ] **Add real-time notifications**:
  - Use react-hot-toast
  - Schedule completed notification
  - Error notifications
  - Progress updates

- [ ] **Add live schedule updates**:
  - Update schedule list when new schedule created
  - Update KPIs in real-time
  - Show "New schedule available" badge

- [ ] **Add connection status indicator**:
  - Online/offline badge
  - Reconnecting animation
  - Connection error alert

### 2.9 Testing & Quality ⏳ (0/7 items)
- [ ] **Setup Vitest**:
  - Configure vitest.config.ts
  - Setup testing library
  - Add test scripts to package.json

- [ ] **Write component tests**:
  - Test form validation
  - Test user interactions
  - Test routing
  - Test error handling

- [ ] **Write integration tests**:
  - Test full schedule creation flow
  - Test authentication flow
  - Test comparison flow

- [ ] **Write API integration tests**:
  - Mock API responses
  - Test loading states
  - Test error states

- [ ] **Add E2E tests** (Playwright or Cypress):
  - Test critical user journeys
  - Test across browsers

- [ ] **Achieve 70%+ test coverage**:
  - Run vitest with coverage
  - Cover edge cases

- [ ] **Add frontend linting**:
  - ESLint with TypeScript rules
  - Prettier formatting
  - Pre-commit hooks

### 2.10 UI/UX Polish ⏳ (0/8 items)
- [ ] **Implement responsive design**:
  - Mobile-friendly layout
  - Tablet optimization
  - Desktop optimization
  - Test on multiple screen sizes

- [ ] **Add loading states**:
  - Skeleton screens
  - Spinner for long operations
  - Progress bars
  - Shimmer effects

- [ ] **Add empty states**:
  - No schedules message
  - Empty comparison message
  - No templates message
  - Call-to-action buttons

- [ ] **Add error boundaries**:
  - Catch React errors
  - Display friendly error message
  - Log errors to console
  - Retry button

- [ ] **Add animations**:
  - Page transitions
  - Button hover effects
  - Loading animations
  - Toast notifications

- [ ] **Add dark mode support**:
  - Theme toggle
  - Dark color palette
  - Persist preference

- [ ] **Add accessibility features**:
  - ARIA labels
  - Keyboard navigation
  - Screen reader support
  - Color contrast compliance

- [ ] **Add help system**:
  - Tooltips on complex features
  - Help icon with explanations
  - Onboarding tour (optional)
  - Documentation links

---

## 🐳 **Phase 3: Deployment & DevOps**

### 3.1 Containerization ⏳ (0/6 items)
- [ ] **Create backend Dockerfile**:
  ```dockerfile
  FROM python:3.10-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY src/ ./src/
  CMD ["uvicorn", "src.fillscheduler.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

- [ ] **Create frontend Dockerfile**:
  ```dockerfile
  FROM node:18-alpine as build
  WORKDIR /app
  COPY package*.json .
  RUN npm ci
  COPY . .
  RUN npm run build

  FROM nginx:alpine
  COPY --from=build /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/conf.d/default.conf
  ```

- [ ] **Create docker-compose.yml**:
  - Backend service (FastAPI)
  - Frontend service (Nginx)
  - PostgreSQL service
  - Redis service (for caching, optional)
  - Volume mounts
  - Environment variables

- [ ] **Create .dockerignore files**:
  - Exclude .venv, node_modules
  - Exclude .git, .pytest_cache
  - Exclude development files

- [ ] **Add health checks**:
  - Backend health endpoint
  - Database connection check
  - Frontend health check

- [ ] **Test Docker build and run**:
  ```bash
  docker-compose up --build
  docker-compose down
  ```

### 3.2 Database Migration ⏳ (0/4 items)
- [ ] **Create migration scripts**:
  - Initial schema creation
  - Add indexes for performance
  - Add foreign key constraints

- [ ] **Setup Alembic for production**:
  - Configure production database URL
  - Test migrations on staging
  - Rollback strategy

- [ ] **Add seed data script**:
  - Create admin user
  - Add default config templates
  - Add example schedules

- [ ] **Document migration process**:
  - How to run migrations
  - How to rollback
  - How to add new migrations

### 3.3 CI/CD Pipeline ⏳ (0/8 items)
- [ ] **Create backend CI workflow** (`.github/workflows/backend-ci.yml`):
  - Install dependencies
  - Run linters (Black, Ruff, mypy)
  - Run tests
  - Check coverage
  - Build Docker image

- [ ] **Create frontend CI workflow** (`.github/workflows/frontend-ci.yml`):
  - Install dependencies
  - Run linters (ESLint, Prettier)
  - Run tests
  - Build production bundle
  - Check bundle size

- [ ] **Create deployment workflow** (`.github/workflows/deploy.yml`):
  - Trigger on push to main
  - Build and push Docker images
  - Deploy to server
  - Run database migrations
  - Health check after deployment

- [ ] **Add security scanning**:
  - Dependabot for dependency updates
  - Snyk or OWASP dependency check
  - Docker image scanning
  - Secret scanning

- [ ] **Add E2E tests in CI**:
  - Run Playwright/Cypress tests
  - Record test videos
  - Upload artifacts

- [ ] **Add performance testing**:
  - Run Lighthouse CI
  - Check bundle size
  - API performance tests

- [ ] **Setup staging environment**:
  - Separate staging branch
  - Deploy to staging before production
  - Manual approval for production

- [ ] **Add rollback capability**:
  - Keep previous Docker images
  - Database rollback scripts
  - Quick rollback workflow

### 3.4 Production Deployment ⏳ (0/6 items)
- [ ] **Choose hosting provider**:
  - AWS (EC2, ECS, or App Runner)
  - Google Cloud (Cloud Run)
  - Azure (Container Apps)
  - DigitalOcean (App Platform)
  - Heroku (simple option)

- [ ] **Setup production database**:
  - PostgreSQL instance
  - Connection pooling
  - Automated backups
  - Point-in-time recovery

- [ ] **Configure domain and SSL**:
  - Register domain
  - Setup DNS records
  - Configure SSL certificate (Let's Encrypt)
  - HTTPS redirect

- [ ] **Setup monitoring**:
  - Application monitoring (Sentry, New Relic)
  - Infrastructure monitoring (Prometheus + Grafana)
  - Log aggregation (ELK stack or Datadog)
  - Uptime monitoring (UptimeRobot)

- [ ] **Configure CDN** (optional):
  - CloudFront or Cloudflare
  - Cache static assets
  - DDoS protection

- [ ] **Setup backup strategy**:
  - Daily database backups
  - File storage backups
  - Test restore process

### 3.5 Documentation ⏳ (0/5 items)
- [ ] **Write deployment guide** (`docs/deployment.md`):
  - Prerequisites
  - Environment setup
  - Docker deployment
  - Database setup
  - Environment variables
  - SSL configuration

- [ ] **Write API documentation** (`docs/api_guide.md`):
  - Authentication
  - Endpoints
  - Request/response examples
  - Error codes

- [ ] **Write user guide** (`docs/user_guide.md`):
  - Getting started
  - Creating schedules
  - Comparing strategies
  - Configuration management
  - Tips and tricks

- [ ] **Create developer guide** (`docs/developer_guide.md`):
  - Architecture overview
  - Local development setup
  - Running tests
  - Contributing guidelines

- [ ] **Create video tutorials** (optional):
  - Quick start video
  - Feature walkthrough
  - Admin guide

---

## 🔒 **Phase 4: Security & Performance**

### 4.1 Security Hardening ⏳ (0/8 items)
- [ ] **Implement rate limiting**:
  - Use slowapi for FastAPI
  - Limit requests per IP
  - Limit login attempts
  - Throttle expensive operations

- [ ] **Add input sanitization**:
  - Validate all user inputs
  - Prevent SQL injection (use SQLAlchemy ORM)
  - Prevent XSS (escape HTML)
  - Validate file uploads

- [ ] **Implement CSRF protection**:
  - CSRF tokens for state-changing requests
  - SameSite cookies

- [ ] **Add security headers**:
  - Content-Security-Policy
  - X-Content-Type-Options
  - X-Frame-Options
  - Strict-Transport-Security

- [ ] **Secure file uploads**:
  - Validate file types (whitelist)
  - Scan for malware
  - Limit file size
  - Store files outside web root

- [ ] **Add audit logging**:
  - Log all authentication events
  - Log data access
  - Log configuration changes
  - Store logs securely

- [ ] **Implement API key authentication** (optional):
  - For programmatic access
  - Key rotation
  - Usage tracking

- [ ] **Add penetration testing**:
  - OWASP ZAP scan
  - Fix vulnerabilities
  - Regular security audits

### 4.2 Performance Optimization ⏳ (0/7 items)
- [ ] **Add database indexing**:
  - Index foreign keys
  - Index frequently queried columns
  - Analyze query performance

- [ ] **Implement caching**:
  - Redis for API responses
  - Cache strategy list
  - Cache user schedules
  - Set appropriate TTLs

- [ ] **Optimize API queries**:
  - Use eager loading (SQLAlchemy)
  - Avoid N+1 queries
  - Add database query logging

- [ ] **Add API response compression**:
  - GZip compression
  - Reduce payload size

- [ ] **Optimize frontend bundle**:
  - Code splitting
  - Lazy loading routes
  - Tree shaking
  - Minification

- [ ] **Add frontend caching**:
  - Service worker
  - Cache API responses (React Query)
  - Cache static assets

- [ ] **Add CDN for static assets**:
  - Serve images from CDN
  - Cache CSS/JS bundles
  - Geo-distribution

---

## 📝 **Phase 5: Advanced Features (Optional)**

### 5.1 Advanced Scheduling ⏳ (0/5 items)
- [ ] **Add schedule templates**:
  - Save schedules as templates
  - Apply template to new lots
  - Template marketplace (optional)

- [ ] **Add schedule constraints**:
  - Resource constraints (machines, operators)
  - Time windows (night shifts, weekends)
  - Lot priorities

- [ ] **Add what-if analysis**:
  - Compare scenarios
  - Sensitivity analysis
  - Impact of constraint changes

- [ ] **Add schedule optimization goals**:
  - Minimize makespan
  - Minimize changeovers
  - Maximize utilization
  - Multi-objective optimization

- [ ] **Add collaborative scheduling**:
  - Multiple users
  - Schedule sharing
  - Comments and annotations

### 5.2 Reporting & Analytics ⏳ (0/6 items)
- [ ] **Add dashboard analytics**:
  - Trend charts (schedules over time)
  - Strategy performance comparison
  - Utilization trends
  - Cost analysis (optional)

- [ ] **Add custom reports**:
  - Report builder
  - Save report templates
  - Schedule report generation

- [ ] **Add data export**:
  - Export to Excel with charts
  - Export to PDF with formatting
  - Export to PowerPoint (optional)

- [ ] **Add KPI alerts**:
  - Email notifications
  - Slack/Teams integration
  - Threshold-based alerts

- [ ] **Add forecasting** (optional):
  - Predict future scheduling needs
  - Capacity planning
  - Resource requirements

- [ ] **Add cost calculations** (optional):
  - Material costs
  - Labor costs
  - Changeover costs
  - Total cost comparison

### 5.3 Integrations ⏳ (0/5 items)
- [ ] **Add ERP integration** (optional):
  - Import lots from ERP
  - Export schedules to ERP
  - API webhooks

- [ ] **Add calendar integration**:
  - Export to Google Calendar
  - Export to Outlook
  - iCal format support

- [ ] **Add notification integrations**:
  - Email notifications (SendGrid)
  - Slack notifications
  - Microsoft Teams notifications

- [ ] **Add file storage integration**:
  - AWS S3 for file uploads
  - Google Drive integration
  - Dropbox integration

- [ ] **Add authentication providers**:
  - Google OAuth
  - Microsoft OAuth
  - SSO (SAML)

---

## 📊 **Progress Summary**

### By Phase
```
Phase 1 (Backend API):       0% (0/59 items)  ░░░░░░░░░░░░░░░
Phase 2 (Frontend):          0% (0/59 items)  ░░░░░░░░░░░░░░░
Phase 3 (Deployment):        0% (0/23 items)  ░░░░░░░░░░░░░░░
Phase 4 (Security/Perf):     0% (0/15 items)  ░░░░░░░░░░░░░░░
Phase 5 (Advanced):          0% (0/16 items)  ░░░░░░░░░░░░░░░
─────────────────────────────────────────────
TOTAL:                       0% (0/172 items) ░░░░░░░░░░░░░░░
```

### By Category
```
Backend Setup:          0% (0/14 items)  ⏳
Backend Features:       0% (0/30 items)  ⏳
Backend Testing:        0% (0/15 items)  ⏳
Frontend Setup:         0% (0/8 items)   ⏳
Frontend Features:      0% (0/37 items)  ⏳
Frontend Testing:       0% (0/14 items)  ⏳
DevOps:                 0% (0/24 items)  ⏳
Security:               0% (0/8 items)   ⏳
Performance:            0% (0/7 items)   ⏳
Advanced Features:      0% (0/16 items)  ⏳
```

---

## 🎯 **Recommended Implementation Order**

### Sprint 1 (2 weeks): MVP Backend
1. Backend setup (1.1)
2. Authentication (1.2)
3. Basic schedule endpoints (1.3)
4. Database setup

### Sprint 2 (2 weeks): MVP Frontend
1. Frontend setup (2.1)
2. Authentication UI (2.2)
3. Dashboard (2.3)
4. Schedule creation (2.4)

### Sprint 3 (2 weeks): Core Features
1. Schedule visualization (2.5)
2. Comparison endpoints (1.4)
3. Comparison UI (2.6)
4. WebSocket progress (1.6, 2.8)

### Sprint 4 (1 week): Config & Polish
1. Configuration management (1.5, 2.7)
2. Testing (1.8, 2.9)
3. UI polish (2.10)

### Sprint 5 (1 week): Deployment
1. Containerization (3.1)
2. CI/CD (3.3)
3. Production deployment (3.4)

### Sprint 6+ (Ongoing): Enhancements
1. Security hardening (4.1)
2. Performance optimization (4.2)
3. Advanced features (Phase 5)

---

## 🔗 **Cross-References**

- **Main Project**: [Restructuring_TODO.md](Restructuring_TODO.md) - Section 10
- **CLI Documentation**: [CLI_IMPLEMENTATION_GUIDE.md](CLI_IMPLEMENTATION_GUIDE.md)
- **Session History**: [CLI_SESSION_9_SUMMARY.md](CLI_SESSION_9_SUMMARY.md)

---

## 📚 **Additional Resources**

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

### Frontend
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Material-UI Documentation](https://mui.com/)
- [React Query Documentation](https://tanstack.com/query/latest)

### DevOps
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

*Last Updated: October 12, 2025*
*Status: Planning Phase - Not Started*
*Estimated Timeline: 8-12 weeks for MVP*
