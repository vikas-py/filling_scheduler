# Filling Scheduler: System Architecture

**Version:** 1.0
**Date:** October 15, 2025
**Document Purpose:** Comprehensive system architecture documentation with Mermaid diagrams

---

## Table of Contents

1. [High-Level Architecture](#1-high-level-architecture)
2. [Component Architecture](#2-component-architecture)
3. [Backend Architecture](#3-backend-architecture)
4. [Frontend Architecture](#4-frontend-architecture)
5. [Data Flow Diagrams](#5-data-flow-diagrams)
6. [Database Schema](#6-database-schema)
7. [API Architecture](#7-api-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Security Architecture](#9-security-architecture)
10. [Algorithm Execution Flow](#10-algorithm-execution-flow)

---

## 1. High-Level Architecture

### 1.1 System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        CLI[Command Line Interface]
    end

    subgraph "Application Layer"
        Frontend[React Frontend<br/>TypeScript + Material-UI<br/>Port 5173]
        API[FastAPI Backend<br/>Python 3.10+<br/>Port 8000]
    end

    subgraph "Business Logic Layer"
        Scheduler[Core Scheduler Engine]
        Strategies[Algorithm Strategies<br/>6 Algorithms]
        Validator[Validation Engine]
        Reporter[Report Generator<br/>PDF/Excel/CSV]
    end

    subgraph "Data Layer"
        Database[(SQLite/PostgreSQL<br/>Database)]
        FileSystem[File System<br/>CSV/Config Files]
    end

    subgraph "External Services"
        WebSocket[WebSocket Server<br/>Real-time Updates]
    end

    Browser -->|HTTP/HTTPS| Frontend
    Browser -->|WebSocket| WebSocket
    CLI -->|Direct Call| Scheduler

    Frontend -->|REST API| API
    API --> Scheduler
    API --> Validator
    API --> Reporter
    API --> WebSocket

    Scheduler --> Strategies
    Scheduler --> Database
    Scheduler --> FileSystem

    API --> Database
    Reporter --> Database
    Reporter --> FileSystem

    style Frontend fill:#61dafb,stroke:#333,stroke-width:2px
    style API fill:#009688,stroke:#333,stroke-width:2px
    style Scheduler fill:#ff9800,stroke:#333,stroke-width:2px
    style Database fill:#4caf50,stroke:#333,stroke-width:2px
```

### 1.2 Technology Stack

```mermaid
graph LR
    subgraph "Frontend Stack"
        React[React 18]
        TS[TypeScript 5]
        MUI[Material-UI 5]
        Vite[Vite 5]
        Zustand[Zustand State]
        ReactRouter[React Router 6]
    end

    subgraph "Backend Stack"
        Python[Python 3.10+]
        FastAPI[FastAPI 0.104+]
        Pydantic[Pydantic 2.0+]
        SQLAlchemy[SQLAlchemy 2.0+]
        Uvicorn[Uvicorn ASGI]
    end

    subgraph "Algorithm Stack"
        Pandas[Pandas 2.0+]
        PuLP[PuLP 2.7+]
        NumPy[NumPy]
    end

    subgraph "Reporting Stack"
        WeasyPrint[WeasyPrint PDF]
        OpenPyXL[OpenPyXL Excel]
        Plotly[Plotly Charts]
        Jinja2[Jinja2 Templates]
    end

    subgraph "Infrastructure"
        Nginx[Nginx Reverse Proxy]
        Systemd[Systemd Service]
        SQLite[(SQLite/PostgreSQL)]
    end

    style React fill:#61dafb
    style FastAPI fill:#009688
    style Python fill:#3776ab
    style Nginx fill:#269539
```

### 1.3 Communication Patterns

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant W as WebSocket
    participant S as Scheduler
    participant D as Database

    U->>F: Create Schedule
    F->>A: POST /api/v1/schedule
    A->>D: Create Schedule Record (pending)
    A->>W: Subscribe to Progress
    A-->>F: 202 Accepted + Schedule ID
    F->>W: WebSocket Connect

    par Background Processing
        A->>S: Run Algorithm (async)
        S->>S: Execute Strategy
        loop Progress Updates
            S->>W: Emit Progress (10%, 20%, ...)
            W->>F: Progress Event
            F->>U: Update UI
        end
        S->>D: Save Results
        S->>W: Emit Complete (100%)
    end

    W->>F: Schedule Complete
    F->>U: Show Results
    U->>F: View Details
    F->>A: GET /api/v1/schedule/{id}
    A->>D: Fetch Results
    D-->>A: Schedule + Activities
    A-->>F: Full Schedule Data
    F->>U: Display Gantt Chart
```

---

## 2. Component Architecture

### 2.1 System Components

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[UI Components]
        Pages[Page Components]
        Charts[Visualization Components]
    end

    subgraph "State Management"
        AuthStore[Auth Store<br/>Zustand]
        ScheduleStore[Schedule Cache]
        WSManager[WebSocket Manager]
    end

    subgraph "API Layer"
        APIClient[API Client<br/>Axios]
        AuthInterceptor[Auth Interceptor]
        ErrorHandler[Error Handler]
    end

    subgraph "Backend Services"
        AuthService[Authentication Service]
        SchedulerService[Scheduler Service]
        ComparisonService[Comparison Service]
        ConfigService[Config Service]
    end

    subgraph "Core Engine"
        StrategyFactory[Strategy Factory]
        ValidationEngine[Validation Engine]
        SchedulingEngine[Scheduling Engine]
        ReportingEngine[Reporting Engine]
    end

    subgraph "Data Access"
        ORM[SQLAlchemy ORM]
        SessionManager[Session Manager]
        Models[Database Models]
    end

    UI --> Pages
    Pages --> Charts
    Pages --> AuthStore
    Pages --> APIClient

    APIClient --> AuthInterceptor
    APIClient --> ErrorHandler
    APIClient --> AuthService
    APIClient --> SchedulerService

    AuthService --> ORM
    SchedulerService --> ValidationEngine
    SchedulerService --> SchedulingEngine
    SchedulingEngine --> StrategyFactory

    SchedulerService --> ReportingEngine
    SchedulerService --> ORM
    ORM --> SessionManager
    SessionManager --> Models

    style UI fill:#e3f2fd
    style AuthService fill:#fff9c4
    style SchedulingEngine fill:#ffccbc
    style ORM fill:#c8e6c9
```

### 2.2 Module Dependencies

```mermaid
graph LR
    subgraph "Core Modules"
        Config[config.py]
        Models[models.py]
        Rules[rules.py]
        Scheduler[scheduler.py]
        Validate[validate.py]
        IOUtils[io_utils.py]
        Reporting[reporting.py]
    end

    subgraph "Strategy Modules"
        StrategyBase[strategies/__init__.py]
        SmartPack[smart_pack.py]
        SPTPack[spt_pack.py]
        LPTPack[lpt_pack.py]
        CFSPack[cfs_pack.py]
        HybridPack[hybrid_pack.py]
        MILPOpt[milp_opt.py]
    end

    subgraph "API Modules"
        APIMain[api/main.py]
        APIConfig[api/config.py]
        Dependencies[api/dependencies.py]
        Security[api/utils/security.py]
    end

    subgraph "API Routers"
        AuthRouter[routers/auth.py]
        ScheduleRouter[routers/schedule.py]
        CompareRouter[routers/comparison.py]
        ConfigRouter[routers/config.py]
    end

    Scheduler --> Models
    Scheduler --> Rules
    Scheduler --> Config
    Scheduler --> StrategyBase

    StrategyBase --> SmartPack
    StrategyBase --> SPTPack
    StrategyBase --> LPTPack
    StrategyBase --> CFSPack
    StrategyBase --> HybridPack
    StrategyBase --> MILPOpt

    SmartPack --> Models
    SmartPack --> Rules
    SmartPack --> Config

    APIMain --> APIConfig
    APIMain --> AuthRouter
    APIMain --> ScheduleRouter
    APIMain --> CompareRouter
    APIMain --> ConfigRouter

    AuthRouter --> Security
    AuthRouter --> Dependencies
    ScheduleRouter --> Scheduler
    ScheduleRouter --> Validate
    ScheduleRouter --> Reporting

    style Scheduler fill:#ffab91
    style StrategyBase fill:#ce93d8
    style APIMain fill:#80cbc4
```

---

## 3. Backend Architecture

### 3.1 FastAPI Application Structure

```mermaid
graph TB
    subgraph "FastAPI Application"
        App[FastAPI App Instance]

        subgraph "Middleware Stack"
            CORS[CORS Middleware]
            ErrorHandler[Exception Handlers]
            RequestID[Request ID Middleware]
        end

        subgraph "Routers"
            AuthAPI[Auth Router<br/>/api/v1/auth]
            ScheduleAPI[Schedule Router<br/>/api/v1/schedule]
            CompareAPI[Comparison Router<br/>/api/v1/comparisons]
            ConfigAPI[Config Router<br/>/api/v1/config]
            WSAPI[WebSocket Router<br/>/api/v1/ws]
        end

        subgraph "Dependencies"
            GetDB[get_db<br/>Session Factory]
            GetUser[get_current_user<br/>JWT Validation]
            GetActiveUser[get_current_active_user<br/>Status Check]
        end

        subgraph "Services"
            AuthSvc[Auth Service]
            SchedulerSvc[Scheduler Service]
            ComparisonSvc[Comparison Service]
            ConfigSvc[Config Service]
        end
    end

    App --> CORS
    CORS --> ErrorHandler
    ErrorHandler --> RequestID

    App --> AuthAPI
    App --> ScheduleAPI
    App --> CompareAPI
    App --> ConfigAPI
    App --> WSAPI

    AuthAPI --> GetDB
    ScheduleAPI --> GetDB
    ScheduleAPI --> GetActiveUser
    CompareAPI --> GetActiveUser

    GetActiveUser --> GetUser

    AuthAPI --> AuthSvc
    ScheduleAPI --> SchedulerSvc
    CompareAPI --> ComparisonSvc
    ConfigAPI --> ConfigSvc

    style App fill:#009688,color:#fff
    style AuthAPI fill:#4caf50
    style ScheduleAPI fill:#2196f3
    style CompareAPI fill:#ff9800
```

### 3.2 Service Layer Architecture

```mermaid
graph TB
    subgraph "API Layer"
        Router[API Router]
    end

    subgraph "Service Layer"
        Service[Service Class]
        Validation[Input Validation]
        BusinessLogic[Business Logic]
        DataTransform[Data Transformation]
    end

    subgraph "Core Layer"
        Scheduler[Scheduler Engine]
        Strategy[Strategy Implementation]
        Validator[Core Validator]
    end

    subgraph "Data Layer"
        ORM[SQLAlchemy ORM]
        Models[Database Models]
        DB[(Database)]
    end

    Router --> Service
    Service --> Validation
    Validation --> BusinessLogic
    BusinessLogic --> DataTransform

    BusinessLogic --> Scheduler
    Scheduler --> Strategy
    BusinessLogic --> Validator

    Service --> ORM
    ORM --> Models
    Models --> DB

    style Service fill:#fff59d
    style Scheduler fill:#ffab91
    style ORM fill:#a5d6a7
```

### 3.3 Background Task Processing

```mermaid
sequenceDiagram
    participant API as API Endpoint
    participant BG as Background Tasks
    participant Worker as Task Worker
    participant DB as Database
    participant WS as WebSocket
    participant Scheduler as Scheduler Engine

    API->>DB: Create Schedule (status=pending)
    DB-->>API: Schedule ID
    API->>BG: Add Background Task
    API-->>Client: 202 Accepted

    par Background Execution
        BG->>Worker: Execute Task
        Worker->>DB: Update status=running
        Worker->>Scheduler: Run Algorithm

        loop Progress Updates
            Scheduler->>Worker: Progress Callback
            Worker->>WS: Broadcast Progress
        end

        Scheduler-->>Worker: Result
        Worker->>DB: Save Results
        Worker->>DB: Update status=completed
        Worker->>WS: Broadcast Complete
    end

    Note over Worker,WS: All updates sent via WebSocket
```

---

## 4. Frontend Architecture

### 4.1 React Application Structure

```mermaid
graph TB
    subgraph "Application Root"
        Main[main.tsx<br/>App Entry]
        App[App.tsx<br/>Router Setup]
        Theme[Theme Provider]
    end

    subgraph "Routing"
        Router[React Router]
        ProtectedRoute[Protected Route<br/>Auth Guard]
        PublicRoute[Public Route]
    end

    subgraph "Pages"
        Login[Login Page]
        Dashboard[Dashboard Page]
        ScheduleCreate[Schedule Create]
        ScheduleDetail[Schedule Detail]
        SchedulesList[Schedules List]
        Compare[Compare Page]
        Config[Config Page]
    end

    subgraph "Components"
        Layout[Layout Component]
        Header[Header/Nav]
        Charts[Chart Components]
        Forms[Form Components]
        Tables[Table Components]
    end

    subgraph "State Management"
        AuthStore[Auth Store<br/>Zustand]
        API[API Client]
        WSContext[WebSocket Context]
    end

    Main --> App
    App --> Theme
    App --> Router

    Router --> PublicRoute
    Router --> ProtectedRoute

    PublicRoute --> Login
    ProtectedRoute --> Dashboard
    ProtectedRoute --> ScheduleCreate
    ProtectedRoute --> ScheduleDetail
    ProtectedRoute --> SchedulesList
    ProtectedRoute --> Compare
    ProtectedRoute --> Config

    Dashboard --> Layout
    ScheduleCreate --> Layout
    Layout --> Header
    Layout --> Charts
    Layout --> Forms

    ProtectedRoute --> AuthStore
    Pages --> API
    Pages --> WSContext

    API --> AuthStore

    style Main fill:#61dafb
    style AuthStore fill:#764abc
    style API fill:#ff6b6b
```

### 4.2 State Management Flow

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated

    Unauthenticated --> Authenticating: Login Request
    Authenticating --> Authenticated: Success
    Authenticating --> Unauthenticated: Failure

    Authenticated --> LoadingSchedules: Fetch Schedules
    LoadingSchedules --> SchedulesLoaded: Success
    LoadingSchedules --> Error: Failure

    SchedulesLoaded --> CreatingSchedule: Create New
    CreatingSchedule --> SchedulePending: Submitted
    SchedulePending --> ScheduleRunning: Started
    ScheduleRunning --> ScheduleCompleted: Success
    ScheduleRunning --> ScheduleFailed: Error

    SchedulesLoaded --> ViewingSchedule: Select Schedule
    ViewingSchedule --> SchedulesLoaded: Back

    Authenticated --> [*]: Logout
    Error --> SchedulesLoaded: Retry

    note right of ScheduleRunning
        WebSocket updates
        provide real-time
        progress
    end note
```

### 4.3 Component Hierarchy

```mermaid
graph TB
    subgraph "Layout Components"
        Layout[Layout]
        Header[Header]
        Sidebar[Sidebar]
        Footer[Footer]
    end

    subgraph "Dashboard Components"
        DashboardKPIs[KPI Cards]
        DashboardCharts[Dashboard Charts]
        RecentSchedules[Recent Schedules Table]
        QuickActions[Quick Actions]
    end

    subgraph "Schedule Components"
        ScheduleForm[Schedule Form]
        CSVUpload[CSV Upload]
        DataPreview[Data Preview]
        StrategySelector[Strategy Selector]
        ConfigEditor[Config Editor]
        ProgressIndicator[Progress Indicator]
    end

    subgraph "Visualization Components"
        TimelineGantt[Timeline Gantt Chart]
        ActivityList[Activity List]
        ScheduleStats[Schedule Statistics]
        ComparisonCharts[Comparison Charts]
    end

    subgraph "Common Components"
        LoadingButton[Loading Button]
        EmptyState[Empty State]
        ErrorBoundary[Error Boundary]
        ConnectionStatus[Connection Status]
        HelpDialog[Help Dialog]
    end

    Layout --> Header
    Layout --> Sidebar
    Layout --> Footer

    Dashboard --> DashboardKPIs
    Dashboard --> DashboardCharts
    Dashboard --> RecentSchedules
    Dashboard --> QuickActions

    ScheduleCreate --> ScheduleForm
    ScheduleForm --> CSVUpload
    ScheduleForm --> DataPreview
    ScheduleForm --> StrategySelector
    ScheduleForm --> ConfigEditor
    ScheduleForm --> ProgressIndicator

    ScheduleDetail --> TimelineGantt
    ScheduleDetail --> ActivityList
    ScheduleDetail --> ScheduleStats

    Compare --> ComparisonCharts

    style Layout fill:#e1f5fe
    style Dashboard fill:#fff9c4
    style ScheduleCreate fill:#f3e5f5
    style Common fill:#e8f5e9
```

---

## 5. Data Flow Diagrams

### 5.1 Schedule Creation Flow

```mermaid
flowchart TD
    Start([User Clicks Create Schedule]) --> Upload[Upload CSV File]
    Upload --> ParseCSV{Parse CSV}
    ParseCSV -->|Success| Preview[Preview Lots Data]
    ParseCSV -->|Error| ErrorMsg[Show Error Message]
    ErrorMsg --> Upload

    Preview --> SelectStrategy[Select Strategy]
    SelectStrategy --> ConfigParams[Configure Parameters]
    ConfigParams --> ValidateInput{Validate Input}

    ValidateInput -->|Invalid| ShowErrors[Display Validation Errors]
    ShowErrors --> ConfigParams

    ValidateInput -->|Valid| Submit[Submit to API]
    Submit --> CreateRecord[Create Schedule Record DB]
    CreateRecord --> StartBG[Start Background Task]
    StartBG --> WSConnect[WebSocket Connect]

    WSConnect --> ShowProgress[Show Progress Bar]

    subgraph "Background Processing"
        RunAlgo[Run Scheduling Algorithm]
        RunAlgo --> EmitProgress[Emit Progress Updates]
        EmitProgress --> CheckComplete{Complete?}
        CheckComplete -->|No| RunAlgo
        CheckComplete -->|Yes| SaveResults[Save Results to DB]
    end

    StartBG --> RunAlgo

    SaveResults --> NotifyComplete[Notify via WebSocket]
    NotifyComplete --> ShowProgress
    ShowProgress --> DisplayResults[Display Schedule Results]
    DisplayResults --> End([End])

    style Start fill:#4caf50,color:#fff
    style Submit fill:#2196f3,color:#fff
    style RunAlgo fill:#ff9800,color:#fff
    style End fill:#4caf50,color:#fff
```

### 5.2 Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend
    participant API as Auth API
    participant DB as Database
    participant JWT as JWT Service

    User->>UI: Enter Credentials
    UI->>API: POST /api/v1/auth/login
    API->>DB: Query User by Email
    DB-->>API: User Record

    alt User Exists
        API->>API: Verify Password (bcrypt)
        alt Password Valid
            API->>JWT: Generate Token
            JWT-->>API: JWT Token
            API-->>UI: 200 OK + Token
            UI->>UI: Store Token in localStorage
            UI->>UI: Update Auth State
            UI-->>User: Redirect to Dashboard
        else Password Invalid
            API-->>UI: 401 Unauthorized
            UI-->>User: Show Error
        end
    else User Not Found
        API-->>UI: 401 Unauthorized
        UI-->>User: Show Error
    end

    Note over UI,API: Subsequent Requests
    User->>UI: Access Protected Route
    UI->>API: Request + Authorization Header
    API->>JWT: Validate Token
    alt Token Valid
        JWT-->>API: User Info
        API-->>UI: Protected Data
    else Token Invalid/Expired
        JWT-->>API: Invalid
        API-->>UI: 401 Unauthorized
        UI->>UI: Clear Auth State
        UI-->>User: Redirect to Login
    end
```

### 5.3 Real-time Progress Updates

```mermaid
sequenceDiagram
    participant Client as Frontend
    participant WSRouter as WebSocket Router
    participant WSManager as Connection Manager
    participant Tracker as Progress Tracker
    participant Worker as Background Worker
    participant Scheduler as Scheduler Engine

    Client->>WSRouter: WebSocket Connect + JWT Token
    WSRouter->>WSRouter: Validate Token
    WSRouter->>WSManager: Register Connection
    WSManager-->>Client: Connected (connection_id)

    Client->>WSRouter: Subscribe to schedule:{id}
    WSRouter->>WSManager: Add to Channel
    WSManager-->>Client: Subscribed

    Worker->>Scheduler: Run Algorithm
    Scheduler->>Scheduler: Process Lots

    loop Every Progress Update
        Scheduler->>Tracker: Update Progress (30%)
        Tracker->>WSManager: Broadcast to Channel
        WSManager->>Client: Progress Event {percent: 30}
        Client->>Client: Update Progress Bar
    end

    Scheduler-->>Worker: Complete
    Worker->>Tracker: Mark Complete
    Tracker->>WSManager: Broadcast Complete
    WSManager->>Client: Complete Event
    Client->>Client: Fetch Results
    Client->>Client: Display Schedule

    Client->>WSRouter: Disconnect
    WSRouter->>WSManager: Remove Connection
```

### 5.4 Comparison Workflow

```mermaid
flowchart TD
    Start([Start Comparison]) --> SelectStrategies[Select Multiple Strategies]
    SelectStrategies --> UploadData[Upload Lots Data]
    UploadData --> ConfigureAll[Configure Shared Settings]
    ConfigureAll --> Submit[Submit Comparison]

    Submit --> CreateComparison[Create Comparison Record]
    CreateComparison --> StartTasks[Start Background Tasks]

    subgraph "Parallel Execution"
        Task1[Run Strategy 1]
        Task2[Run Strategy 2]
        Task3[Run Strategy 3]
        Task4[Run Strategy N]
    end

    StartTasks --> Task1
    StartTasks --> Task2
    StartTasks --> Task3
    StartTasks --> Task4

    Task1 --> Save1[Save Result 1]
    Task2 --> Save2[Save Result 2]
    Task3 --> Save3[Save Result 3]
    Task4 --> Save4[Save Result N]

    Save1 --> Aggregate[Aggregate Results]
    Save2 --> Aggregate
    Save3 --> Aggregate
    Save4 --> Aggregate

    Aggregate --> Analyze[Analyze Metrics]
    Analyze --> DetermineBest[Determine Best Strategy]
    DetermineBest --> Display[Display Comparison Table]
    Display --> Charts[Show Comparison Charts]
    Charts --> End([End])

    style Start fill:#4caf50,color:#fff
    style Task1 fill:#2196f3,color:#fff
    style Task2 fill:#2196f3,color:#fff
    style Task3 fill:#2196f3,color:#fff
    style Task4 fill:#2196f3,color:#fff
    style End fill:#4caf50,color:#fff
```

---

## 6. Database Schema

### 6.1 Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Schedule : creates
    User ||--o{ ConfigTemplate : owns
    User ||--o{ Comparison : creates
    Schedule ||--|| ScheduleResult : has
    Comparison ||--o{ ComparisonResult : contains

    User {
        int id PK
        string email UK
        string hashed_password
        boolean is_active
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    Schedule {
        int id PK
        int user_id FK
        string name
        string strategy
        string status
        text error_message
        text config_json
        datetime created_at
        datetime started_at
        datetime completed_at
    }

    ScheduleResult {
        int id PK
        int schedule_id FK,UK
        float makespan
        float utilization
        int changeovers
        int lots_scheduled
        int window_violations
        text kpis_json
        text activities_json
        datetime created_at
    }

    ConfigTemplate {
        int id PK
        int user_id FK
        string name
        text description
        text config_json
        boolean is_public
        boolean is_default
        datetime created_at
        datetime updated_at
    }

    Comparison {
        int id PK
        int user_id FK
        string name
        string lots_data_hash
        text lots_data_json
        text strategies
        string status
        text error_message
        text config_json
        string best_strategy
        datetime created_at
        datetime started_at
        datetime completed_at
    }

    ComparisonResult {
        int id PK
        int comparison_id FK
        string strategy
        string status
        text error_message
        float makespan
        float utilization
        int changeovers
        int lots_scheduled
        int window_violations
        text kpis_json
        text activities_json
        float execution_time
        datetime created_at
    }
```

### 6.2 Database Relationships

```mermaid
graph TB
    subgraph "User Domain"
        User[User]
    end

    subgraph "Schedule Domain"
        Schedule[Schedule]
        ScheduleResult[Schedule Result]
    end

    subgraph "Comparison Domain"
        Comparison[Comparison]
        ComparisonResult[Comparison Result]
    end

    subgraph "Config Domain"
        ConfigTemplate[Config Template]
    end

    User -->|"1:N<br/>creates"| Schedule
    User -->|"1:N<br/>owns"| ConfigTemplate
    User -->|"1:N<br/>creates"| Comparison

    Schedule -->|"1:1<br/>has"| ScheduleResult
    Comparison -->|"1:N<br/>contains"| ComparisonResult

    style User fill:#e3f2fd
    style Schedule fill:#fff9c4
    style Comparison fill:#f3e5f5
    style ConfigTemplate fill:#e8f5e9
```

---

## 7. API Architecture

### 7.1 API Endpoint Structure

```mermaid
graph TB
    Root["/"]
    Health["/health"]

    subgraph "Authentication /api/v1/auth"
        AuthRegister[POST /register]
        AuthLogin[POST /login]
        AuthMe[GET /me]
        AuthLogout[POST /logout]
    end

    subgraph "Schedules /api/v1"
        ScheduleCreate[POST /schedule]
        ScheduleCreateJSON[POST /schedule/json]
        ScheduleGet[GET /schedule/:id]
        SchedulesList[GET /schedules]
        SchedulesStats[GET /schedules/stats]
        ScheduleDelete[DELETE /schedule/:id]
        ScheduleExport[GET /schedule/:id/export]
        ScheduleValidate[POST /schedule/validate]
        StrategiesList[GET /strategies]
    end

    subgraph "Comparisons /api/v1"
        ComparisonCreate[POST /compare]
        ComparisonCreateJSON[POST /comparisons]
        ComparisonGet[GET /comparisons/:id]
        ComparisonsList[GET /comparisons]
        ComparisonDelete[DELETE /comparisons/:id]
    end

    subgraph "Config /api/v1/config"
        ConfigCreate[POST /config]
        ConfigList[GET /config]
        ConfigGet[GET /config/:id]
        ConfigUpdate[PUT /config/:id]
        ConfigDelete[DELETE /config/:id]
        ConfigDefault[GET /config/default]
        ConfigSetDefault[POST /config/:id/set-default]
        ConfigValidate[POST /config/validate]
        ConfigSystemDefault[GET /config/system-default]
    end

    subgraph "WebSocket /api/v1/ws"
        WSScheduleProgress[WS /ws/schedules/:id/progress]
        WSComparisonProgress[WS /ws/comparisons/:id/progress]
    end

    style AuthLogin fill:#4caf50
    style ScheduleCreate fill:#2196f3
    style ComparisonCreate fill:#ff9800
    style WSScheduleProgress fill:#9c27b0
```

### 7.2 Request/Response Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant R as Router
    participant D as Dependency
    participant S as Service
    participant DB as Database

    C->>M: HTTP Request

    rect rgb(200, 230, 255)
        Note over M: Middleware Layer
        M->>M: CORS Check
        M->>M: Request ID Generation
        M->>M: Logging
    end

    M->>R: Validated Request

    rect rgb(255, 240, 200)
        Note over R,D: Authentication
        R->>D: Check Dependencies
        D->>D: Extract JWT Token
        D->>D: Validate Token
        D->>DB: Get User from DB
        DB-->>D: User Object
    end

    D-->>R: Authenticated User

    rect rgb(230, 255, 230)
        Note over R,S: Business Logic
        R->>S: Call Service Method
        S->>S: Validate Input
        S->>S: Execute Business Logic
        S->>DB: Query/Update Database
        DB-->>S: Data
        S->>S: Transform Response
    end

    S-->>R: Result
    R-->>M: Response

    rect rgb(255, 230, 230)
        Note over M: Response Middleware
        M->>M: Add Headers
        M->>M: Logging
    end

    M-->>C: HTTP Response
```

### 7.3 Authentication & Authorization

```mermaid
flowchart TD
    Request[Incoming Request] --> HasAuth{Has Authorization<br/>Header?}

    HasAuth -->|No| Public{Public<br/>Endpoint?}
    Public -->|Yes| Allow[Allow Access]
    Public -->|No| Reject401[401 Unauthorized]

    HasAuth -->|Yes| ExtractToken[Extract Bearer Token]
    ExtractToken --> ValidateToken{Valid JWT?}

    ValidateToken -->|No| Reject401
    ValidateToken -->|Yes| GetUser[Get User from Database]

    GetUser --> UserExists{User<br/>Exists?}
    UserExists -->|No| Reject401
    UserExists -->|Yes| CheckActive{User<br/>Active?}

    CheckActive -->|No| Reject400[400 Inactive User]
    CheckActive -->|Yes| CheckPermissions{Required<br/>Permissions?}

    CheckPermissions -->|Admin Required| IsAdmin{Is<br/>Superuser?}
    IsAdmin -->|No| Reject403[403 Forbidden]
    IsAdmin -->|Yes| Allow

    CheckPermissions -->|User Access| CheckOwnership{Owns<br/>Resource?}
    CheckOwnership -->|No| Reject403
    CheckOwnership -->|Yes| Allow

    CheckPermissions -->|No Check| Allow

    Allow --> ProcessRequest[Process Request]
    ProcessRequest --> Success[200-299 Response]

    style Request fill:#e3f2fd
    style Allow fill:#c8e6c9
    style Success fill:#4caf50,color:#fff
    style Reject401 fill:#ef5350,color:#fff
    style Reject403 fill:#ef5350,color:#fff
    style Reject400 fill:#ff9800,color:#fff
```

---

## 8. Deployment Architecture

### 8.1 Production Deployment (Ubuntu Server)

```mermaid
graph TB
    subgraph "Internet"
        Client[Web Browser]
        Mobile[Mobile Client]
    end

    subgraph "Ubuntu Server"
        subgraph "Nginx Layer"
            Nginx[Nginx Reverse Proxy<br/>Port 80/443]
            SSL[SSL/TLS Termination]
        end

        subgraph "Application Layer"
            Uvicorn1[Uvicorn Worker 1<br/>Port 8001]
            Uvicorn2[Uvicorn Worker 2<br/>Port 8002]
            Uvicorn3[Uvicorn Worker 3<br/>Port 8003]
            Uvicorn4[Uvicorn Worker 4<br/>Port 8004]
        end

        subgraph "Static Files"
            Frontend[React Build<br/>/opt/filling_scheduler/frontend/dist]
        end

        subgraph "Data Layer"
            DB[(SQLite/PostgreSQL<br/>Database)]
            Files[File System<br/>CSV/Reports]
        end

        subgraph "System Services"
            Systemd[Systemd Service<br/>filling-scheduler.service]
            Logs[Logs<br/>/var/log]
        end
    end

    Client -->|HTTPS| Nginx
    Mobile -->|HTTPS| Nginx

    Nginx --> SSL
    SSL -->|Static Files| Frontend
    SSL -->|/api/*| Uvicorn1
    SSL -->|/api/*| Uvicorn2
    SSL -->|/api/*| Uvicorn3
    SSL -->|/api/*| Uvicorn4

    Uvicorn1 --> DB
    Uvicorn2 --> DB
    Uvicorn3 --> DB
    Uvicorn4 --> DB

    Uvicorn1 --> Files

    Systemd -.->|Manages| Uvicorn1
    Systemd -.->|Manages| Uvicorn2
    Systemd -.->|Manages| Uvicorn3
    Systemd -.->|Manages| Uvicorn4

    Uvicorn1 -.->|Writes| Logs

    style Client fill:#e3f2fd
    style Nginx fill:#66bb6a,color:#fff
    style Frontend fill:#61dafb
    style DB fill:#4caf50,color:#fff
```

### 8.2 Development Environment

```mermaid
graph LR
    subgraph "Developer Machine"
        subgraph "Frontend Dev"
            ViteDev[Vite Dev Server<br/>Port 5173<br/>Hot Reload]
            ReactApp[React Application]
        end

        subgraph "Backend Dev"
            UvicornDev[Uvicorn<br/>Port 8000<br/>--reload]
            FastAPIApp[FastAPI Application]
        end

        subgraph "Local Data"
            SQLiteDev[(SQLite DB<br/>fillscheduler.db)]
            LocalFiles[Local CSV Files<br/>examples/]
        end

        subgraph "Development Tools"
            VSCode[VS Code<br/>+ Extensions]
            Git[Git Version Control]
            VirtualEnv[Python venv]
            NodeModules[node_modules]
        end
    end

    ViteDev --> ReactApp
    ReactApp -->|Proxy| UvicornDev
    UvicornDev --> FastAPIApp
    FastAPIApp --> SQLiteDev
    FastAPIApp --> LocalFiles

    VSCode -.->|Edits| ReactApp
    VSCode -.->|Edits| FastAPIApp
    Git -.->|Version Control| ReactApp
    Git -.->|Version Control| FastAPIApp

    VirtualEnv -.->|Python Deps| UvicornDev
    NodeModules -.->|JS Deps| ViteDev

    style ViteDev fill:#646cff
    style UvicornDev fill:#009688
    style VSCode fill:#007acc
```

### 8.3 Container Deployment (Future)

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/Traefik<br/>Port 80/443]
    end

    subgraph "Docker Compose Stack"
        subgraph "Frontend Container"
            FrontendC[Nginx + React Build<br/>filling-scheduler-frontend]
        end

        subgraph "Backend Containers"
            API1[FastAPI Container 1<br/>filling-scheduler-api]
            API2[FastAPI Container 2<br/>filling-scheduler-api]
            API3[FastAPI Container 3<br/>filling-scheduler-api]
        end

        subgraph "Database Container"
            PostgreSQL[(PostgreSQL 15<br/>filling-scheduler-db)]
        end

        subgraph "Cache Container (Future)"
            Redis[(Redis<br/>Session/Cache)]
        end

        subgraph "Shared Volumes"
            Uploads[Uploads Volume]
            Reports[Reports Volume]
        end
    end

    LB --> FrontendC
    LB --> API1
    LB --> API2
    LB --> API3

    API1 --> PostgreSQL
    API2 --> PostgreSQL
    API3 --> PostgreSQL

    API1 --> Redis
    API2 --> Redis
    API3 --> Redis

    API1 --> Uploads
    API1 --> Reports

    style LB fill:#66bb6a,color:#fff
    style FrontendC fill:#61dafb
    style API1 fill:#009688,color:#fff
    style API2 fill:#009688,color:#fff
    style API3 fill:#009688,color:#fff
    style PostgreSQL fill:#336791,color:#fff
    style Redis fill:#dc382d,color:#fff
```

---

## 9. Security Architecture

### 9.1 Security Layers

```mermaid
graph TB
    subgraph "Network Security"
        Firewall[Firewall<br/>UFW]
        SSL[SSL/TLS<br/>HTTPS Only]
        CORS[CORS Policy<br/>Allowed Origins]
    end

    subgraph "Application Security"
        JWT[JWT Authentication]
        CSRF[CSRF Protection<br/>TODO]
        RateLimit[Rate Limiting<br/>TODO]
        InputVal[Input Validation<br/>Pydantic]
        OutputSan[Output Sanitization]
    end

    subgraph "Data Security"
        Encryption[Password Hashing<br/>bcrypt]
        DBPerms[Database Permissions]
        FilePerms[File System Permissions]
        SQLInject[SQL Injection Prevention<br/>ORM]
    end

    subgraph "Infrastructure Security"
        Isolation[Process Isolation<br/>systemd]
        LeastPriv[Least Privilege<br/>www-data user]
        Logging[Audit Logging]
        Backup[Regular Backups]
    end

    Internet[Internet Traffic] --> Firewall
    Firewall --> SSL
    SSL --> CORS

    CORS --> JWT
    JWT --> RateLimit
    RateLimit --> CSRF
    CSRF --> InputVal
    InputVal --> OutputSan

    OutputSan --> Encryption
    Encryption --> DBPerms
    DBPerms --> FilePerms

    FilePerms --> Isolation
    Isolation --> LeastPriv
    LeastPriv --> Logging
    Logging --> Backup

    style Firewall fill:#ef5350,color:#fff
    style JWT fill:#66bb6a,color:#fff
    style Encryption fill:#42a5f5,color:#fff
    style Isolation fill:#ab47bc,color:#fff
```

### 9.2 Authentication Flow Security

```mermaid
sequenceDiagram
    participant C as Client
    participant F as Frontend
    participant N as Nginx
    participant A as API
    participant DB as Database

    Note over C,DB: Registration (Secure)
    C->>F: Enter Password (plain)
    F->>N: HTTPS POST /register
    N->>A: Encrypted Transport
    A->>A: Validate Input (Pydantic)
    A->>A: Hash Password (bcrypt, rounds=12)
    A->>DB: Store Hashed Password
    DB-->>A: Success
    A-->>N: 201 Created
    N-->>F: Response
    F-->>C: Success Message

    Note over C,DB: Login (Secure)
    C->>F: Enter Credentials
    F->>N: HTTPS POST /login
    N->>A: Encrypted Transport
    A->>DB: Query User by Email
    DB-->>A: User + Hashed Password
    A->>A: Verify Password (bcrypt.verify)
    alt Password Valid
        A->>A: Generate JWT (HS256)
        A->>A: Set Expiry (24h)
        A-->>N: JWT Token
        N-->>F: Token
        F->>F: Store in localStorage (HttpOnly TODO)
        F-->>C: Redirect to Dashboard
    else Invalid
        A-->>N: 401 Unauthorized
        N-->>F: Error
        F-->>C: Show Error (generic message)
    end

    Note over C,DB: Authenticated Request
    C->>F: Access Protected Resource
    F->>F: Get Token from localStorage
    F->>N: HTTPS Request + Bearer Token
    N->>A: Forward with Token
    A->>A: Decode JWT
    A->>A: Verify Signature (SECRET_KEY)
    A->>A: Check Expiry
    alt Token Valid
        A->>DB: Get User Details
        DB-->>A: User Object
        A->>A: Check is_active
        A-->>N: Protected Data
    else Token Invalid
        A-->>N: 401 Unauthorized
        N-->>F: Error
        F->>F: Clear localStorage
        F-->>C: Redirect to Login
    end
```

---

## 10. Algorithm Execution Flow

### 10.1 Strategy Selection & Execution

```mermaid
flowchart TD
    Start([Receive Schedule Request]) --> ParseInput[Parse Lots Data]
    ParseInput --> Validate[Validate Input]
    Validate --> SelectStrategy{Select<br/>Strategy}

    SelectStrategy -->|smart-pack| Smart[Smart-Pack Strategy]
    SelectStrategy -->|spt-pack| SPT[SPT-Pack Strategy]
    SelectStrategy -->|lpt-pack| LPT[LPT-Pack Strategy]
    SelectStrategy -->|cfs-pack| CFS[CFS-Pack Strategy]
    SelectStrategy -->|hybrid-pack| Hybrid[Hybrid-Pack Strategy]
    SelectStrategy -->|milp-opt| MILP[MILP-Opt Strategy]

    Smart --> Preorder1[Preorder: No Sort]
    SPT --> Preorder2[Preorder: Type Cluster + SPT]
    LPT --> Preorder3[Preorder: Global LPT Sort]
    CFS --> Preorder4[Preorder: Cluster by Type]
    Hybrid --> Preorder5[Preorder: No Sort]
    MILP --> Preorder6[Preorder: MILP Solve]

    Preorder1 --> SchedulingLoop
    Preorder2 --> SchedulingLoop
    Preorder3 --> SchedulingLoop
    Preorder4 --> SchedulingLoop
    Preorder5 --> SchedulingLoop
    Preorder6 --> SchedulingLoop

    SchedulingLoop[Main Scheduling Loop]
    SchedulingLoop --> PickNext{Pick Next Lot}

    PickNext -->|smart/hybrid| BeamSearch[Beam Search + Lookahead]
    PickNext -->|spt/lpt/cfs| GreedyFit[Greedy Fit]
    PickNext -->|milp| FollowOrder[Follow MILP Order]

    BeamSearch --> FitsWindow{Fits Current<br/>Window?}
    GreedyFit --> FitsWindow
    FollowOrder --> FitsWindow

    FitsWindow -->|Yes| AddToBlock[Add to Current Block]
    FitsWindow -->|No| StartNewBlock[Start New Block]

    AddToBlock --> MoreLots{More Lots<br/>Remaining?}
    StartNewBlock --> MoreLots

    MoreLots -->|Yes| SchedulingLoop
    MoreLots -->|No| EmitActivities[Emit Activities]

    EmitActivities --> ValidateSchedule[Validate Schedule]
    ValidateSchedule --> CalcMetrics[Calculate Metrics]
    CalcMetrics --> SaveResults[Save Results to DB]
    SaveResults --> End([Return Schedule])

    style Start fill:#4caf50,color:#fff
    style Smart fill:#ff9800,color:#fff
    style SPT fill:#2196f3,color:#fff
    style LPT fill:#2196f3,color:#fff
    style CFS fill:#9c27b0,color:#fff
    style Hybrid fill:#ff9800,color:#fff
    style MILP fill:#f44336,color:#fff
    style End fill:#4caf50,color:#fff
```

### 10.2 Smart-Pack Algorithm Flow (Detailed)

```mermaid
flowchart TD
    Start([Smart-Pack Execution]) --> Init[Initialize State]
    Init --> RemainingCheck{Lots<br/>Remaining?}

    RemainingCheck -->|No| Done[Complete]
    RemainingCheck -->|Yes| ScoreAll[Score All Candidates]

    ScoreAll --> CalcBase[Calculate Base Scores]
    CalcBase --> CalcSwitch[Apply Switch Penalty]
    CalcSwitch --> CalcSlack[Calculate Slack Waste]
    CalcSlack --> CalcStreak[Apply Streak Bonus]
    CalcStreak --> FilterFeasible[Filter Feasible Lots]

    FilterFeasible --> AnyFeasible{Any<br/>Feasible?}
    AnyFeasible -->|No| NewBlock[Start New Block]
    AnyFeasible -->|Yes| SelectTop[Select Top K Candidates]

    SelectTop --> BeamLoop[For Each Beam Candidate]
    BeamLoop --> SimulateSchedule[Simulate Scheduling]
    SimulateSchedule --> ScoreFollowers[Score All Followers]
    ScoreFollowers --> BestFollower[Find Best Follower]
    BestFollower --> ComboScore[Combo = Base + 0.25×Follower]

    ComboScore --> MoreBeam{More in<br/>Beam?}
    MoreBeam -->|Yes| BeamLoop
    MoreBeam -->|No| SelectBest[Select Best Combo]

    SelectBest --> CheckFit{Fits<br/>Window?}
    CheckFit -->|No| NewBlock
    CheckFit -->|Yes| AddLot[Add Lot to Block]

    AddLot --> UpdateState[Update State]
    UpdateState --> EmitProgress[Emit Progress]
    EmitProgress --> RemainingCheck

    NewBlock --> EmitClean[Emit CLEAN Activity]
    EmitClean --> ResetState[Reset Window State]
    ResetState --> RemainingCheck

    Done --> Return([Return Activities])

    style Start fill:#ff9800,color:#fff
    style ScoreAll fill:#fff59d
    style BeamLoop fill:#ffccbc
    style SelectBest fill:#c8e6c9
    style Return fill:#4caf50,color:#fff
```

### 10.3 MILP Optimization Process

```mermaid
sequenceDiagram
    participant API as API Service
    participant MILP as MILP Strategy
    participant Model as PuLP Model
    participant Solver as CBC Solver
    participant Result as Result Extractor

    API->>MILP: Run MILP-Opt
    MILP->>MILP: Check Size (n ≤ 30)

    alt Too Large
        MILP-->>API: RuntimeError (too many lots)
    else Acceptable Size
        MILP->>Model: Create LP Problem
        Model->>Model: Define Variables (y, u, s, e, z, p)
        Model->>Model: Set Objective (minimize blocks + changeovers)
        Model->>Model: Add Constraints

        Note over Model: Constraints:<br/>- Assignment (each lot once)<br/>- Block usage<br/>- Path structure<br/>- MTZ subtour elimination<br/>- Capacity limits

        Model->>Solver: Solve (timeLimit=60s)
        Solver->>Solver: Branch and Bound

        loop Until Optimal or Timeout
            Solver->>Solver: Explore Solution Space
            Solver->>Solver: Prune Branches
        end

        alt Optimal Found
            Solver-->>Model: Optimal Solution
            Model->>Result: Extract Variable Values
            Result->>Result: Build Block Sequences
            Result->>Result: Flatten to Lot Order
            Result-->>MILP: Ordered Lots
            MILP-->>API: Success
        else Timeout
            Solver-->>Model: Best Feasible Solution
            Model->>Result: Extract Values
            Result-->>MILP: Best Found Order
            MILP-->>API: Success (not proven optimal)
        else Infeasible
            Solver-->>Model: Infeasible
            Model-->>MILP: Error
            MILP-->>API: RuntimeError
        end
    end
```

---

## Appendix: Technology Details

### Component Versions

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Backend runtime |
| FastAPI | 0.104+ | Web framework |
| React | 18 | Frontend framework |
| TypeScript | 5 | Type safety |
| SQLAlchemy | 2.0+ | ORM |
| PuLP | 2.7+ | MILP solver |
| Uvicorn | 0.24+ | ASGI server |
| Nginx | Latest | Reverse proxy |
| Vite | 5 | Build tool |

### Port Allocations

| Service | Port | Protocol |
|---------|------|----------|
| Vite Dev | 5173 | HTTP |
| FastAPI | 8000 | HTTP |
| Nginx | 80 | HTTP |
| Nginx SSL | 443 | HTTPS |
| WebSocket | 8000 | WS/WSS |

---

**Document Version:** 1.0
**Last Updated:** October 15, 2025
**Maintained By:** Filling Scheduler Development Team
**License:** GNU GPL v3.0
