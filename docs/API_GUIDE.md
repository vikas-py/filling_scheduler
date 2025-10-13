# Filling Scheduler API - Complete Guide

**Version:** 0.1.0
**Base URL:** `http://localhost:8000` (Development) | `https://api.fillscheduler.example.com` (Production)
**Documentation:** http://localhost:8000/docs (Swagger UI) | http://localhost:8000/redoc (ReDoc)
**Postman Collection:** [Download](../postman/Filling_Scheduler_API.postman_collection.json) | [Guide](../postman/README.md)

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start with Postman](#quick-start-with-postman)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
5. [Request/Response Examples](#requestresponse-examples)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [WebSocket Real-Time Updates](#websocket-real-time-updates)
9. [Client Libraries](#client-libraries)
10. [Best Practices](#best-practices)

---

## Overview

The Filling Scheduler API is a RESTful API for creating and managing production schedules. It provides endpoints for:

- **Authentication** - User registration, login, and token management
- **Schedules** - Create, retrieve, and manage production schedules
- **Comparisons** - Compare multiple scheduling strategies side-by-side
- **Configuration** - Manage configuration templates for scheduling parameters
- **WebSocket** - Real-time progress updates during schedule execution

### Key Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 📊 **Multiple Strategies** - Smart-pack, LPT, SPT, CFS, Hybrid, MILP optimization
- ⚡ **Real-Time Updates** - WebSocket progress notifications
- 🎯 **Strategy Comparison** - Find the best scheduling approach
- 📝 **Configuration Templates** - Save and reuse scheduling configurations
- 🔄 **Async Processing** - Background task execution for long-running schedules

### Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTPS/WSS
       ▼
┌─────────────┐
│  FastAPI    │
│   Server    │
└──────┬──────┘
       │
       ├──► JWT Auth
       ├──► SQLAlchemy ORM
       ├──► Background Tasks
       └──► WebSocket Manager
              │
              ▼
       ┌─────────────┐
       │  SQLite DB  │
       └─────────────┘
```

---

## Quick Start with Postman

The fastest way to explore the API is using our Postman collection:

### 1. Import Collection & Environment

1. Download the collection: [Filling_Scheduler_API.postman_collection.json](../postman/Filling_Scheduler_API.postman_collection.json)
2. Download the environment: [Filling_Scheduler_Dev.postman_environment.json](../postman/Filling_Scheduler_Dev.postman_environment.json)
3. Import both files into Postman
4. Select "Filling Scheduler - Development" environment

### 2. Authenticate

1. Open the **Authentication** folder
2. Run the **Login** request
3. Access token is automatically saved

### 3. Create Your First Schedule

1. Open the **Schedules** folder
2. Run **Create Schedule**
3. Run **Get Schedule** to see results

### 4. Compare Strategies

1. Open the **Comparisons** folder
2. Run **Create Comparison**
3. Run **Get Comparison** to see which strategy performed best

📖 **Full Postman Guide:** [postman/README.md](../postman/README.md)

---

## Authentication

The API uses **JWT (JSON Web Tokens)** for authentication. All protected endpoints require a valid access token in the `Authorization` header.

### Authentication Flow

```
1. User registers or logs in
   └─► POST /api/v1/auth/login

2. Server returns access token
   └─► {"access_token": "eyJ0eXAiOiJ...", "token_type": "bearer"}

3. Client includes token in requests
   └─► Authorization: Bearer eyJ0eXAiOiJ...

4. Server validates token
   └─► Allows access to protected resources
```

### Endpoints

#### Register (Not Yet Implemented)
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123!
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-10-13T10:00:00"
}
```

### Token Storage

**Recommended approach:**
- Store token in memory (React state, Zustand store)
- For persistence, use `httpOnly` cookies or secure storage
- Never store tokens in localStorage (XSS vulnerability)

### Token Expiration

- Access tokens expire after **30 minutes** (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Implement token refresh logic in your client
- Handle 401 Unauthorized responses by redirecting to login

---

## API Endpoints

### Base URL Structure

All API endpoints follow the pattern: `/api/v1/{resource}`

| Resource | Base Path | Description |
|:---------|:----------|:------------|
| Authentication | `/api/v1/auth` | User authentication |
| Schedules | `/api/v1/schedules` | Schedule CRUD operations |
| Comparisons | `/api/v1/compare` | Strategy comparisons |
| Configuration | `/api/v1/config` | Configuration templates |
| WebSocket | `/api/v1/ws` | Real-time connections |

### Schedules

#### Create Schedule
```http
POST /api/v1/schedule
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Production Schedule - Week 42",
  "lots_data": [
    {
      "lot_id": "LOT001",
      "product": "ProductA",
      "quantity": 1000,
      "priority": 1,
      "start_window": "2024-10-14T08:00:00",
      "end_window": "2024-10-14T16:00:00"
    }
  ],
  "strategy": "smart-pack",
  "config": {
    "line_count": 3,
    "changeover_time": 30
  },
  "start_time": "2024-10-14T08:00:00"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Production Schedule - Week 42",
  "strategy": "smart-pack",
  "status": "pending",
  "created_at": "2024-10-13T10:00:00",
  "started_at": null,
  "completed_at": null,
  "error_message": null
}
```

#### Get Schedule
```http
GET /api/v1/schedule/{id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "name": "Production Schedule - Week 42",
  "strategy": "smart-pack",
  "status": "completed",
  "created_at": "2024-10-13T10:00:00",
  "started_at": "2024-10-13T10:00:05",
  "completed_at": "2024-10-13T10:02:30",
  "error_message": null,
  "result": {
    "makespan": 450.5,
    "utilization": 0.85,
    "changeovers": 12,
    "lots_scheduled": 50,
    "window_violations": 0,
    "kpis": {
      "total_production_time": 450.5,
      "average_line_utilization": 0.85,
      "on_time_delivery_rate": 1.0
    },
    "activities": [
      {
        "lot_id": "LOT001",
        "line": 1,
        "start": "2024-10-14T08:00:00",
        "end": "2024-10-14T10:30:00",
        "duration": 150.0
      }
    ]
  }
}
```

#### List Schedules
```http
GET /api/v1/schedules?page=1&page_size=20&status=completed
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 20) - Items per page
- `status` (string, optional) - Filter by status: `pending`, `running`, `completed`, `failed`

**Response:**
```json
{
  "schedules": [
    {
      "id": 1,
      "name": "Production Schedule - Week 42",
      "strategy": "smart-pack",
      "status": "completed",
      "created_at": "2024-10-13T10:00:00",
      "started_at": "2024-10-13T10:00:05",
      "completed_at": "2024-10-13T10:02:30",
      "error_message": null
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

#### Delete Schedule
```http
DELETE /api/v1/schedule/{id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Schedule deleted successfully"
}
```

#### Export Schedule
```http
GET /api/v1/schedule/{id}/export?format=json
Authorization: Bearer <token>
```

**Query Parameters:**
- `format` (string) - Export format: `json` or `csv`

#### Validate Lots Data
```http
POST /api/v1/schedule/validate
Authorization: Bearer <token>
Content-Type: application/json

{
  "lots_data": [
    {
      "lot_id": "LOT001",
      "product": "ProductA",
      "quantity": 1000
    }
  ]
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Missing 'priority' field for lot LOT001, defaulting to 0"]
}
```

#### List Available Strategies
```http
GET /api/v1/strategies
Authorization: Bearer <token>
```

**Response:**
```json
{
  "strategies": [
    {
      "id": "smart-pack",
      "name": "Smart Pack",
      "description": "Intelligent packing with priority optimization"
    },
    {
      "id": "lpt-pack",
      "name": "Longest Processing Time",
      "description": "Schedule largest lots first"
    },
    {
      "id": "spt-pack",
      "name": "Shortest Processing Time",
      "description": "Schedule smallest lots first"
    },
    {
      "id": "cfs-pack",
      "name": "Critical First Strategy",
      "description": "Priority-based scheduling"
    },
    {
      "id": "hybrid-pack",
      "name": "Hybrid Strategy",
      "description": "Combination of multiple strategies"
    },
    {
      "id": "milp-opt",
      "name": "MILP Optimization",
      "description": "Mixed Integer Linear Programming optimization"
    }
  ]
}
```

### Comparisons

#### Create Comparison
```http
POST /api/v1/compare
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Strategy Comparison - October 2024",
  "lots_data": [
    {
      "lot_id": "LOT001",
      "product": "ProductA",
      "quantity": 1000,
      "priority": 1
    }
  ],
  "strategies": ["smart-pack", "lpt-pack", "spt-pack"],
  "config": {
    "line_count": 3
  }
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Strategy Comparison - October 2024",
  "strategies": ["smart-pack", "lpt-pack", "spt-pack"],
  "status": "pending",
  "created_at": "2024-10-13T10:00:00",
  "started_at": null,
  "completed_at": null
}
```

#### Get Comparison
```http
GET /api/v1/compare/{id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "name": "Strategy Comparison - October 2024",
  "strategies": ["smart-pack", "lpt-pack", "spt-pack"],
  "status": "completed",
  "created_at": "2024-10-13T10:00:00",
  "started_at": "2024-10-13T10:00:05",
  "completed_at": "2024-10-13T10:05:30",
  "best_strategy": "smart-pack",
  "results": [
    {
      "strategy": "smart-pack",
      "status": "completed",
      "makespan": 450.5,
      "utilization": 0.85,
      "changeovers": 12,
      "lots_scheduled": 50,
      "window_violations": 0,
      "execution_time": 2.5
    },
    {
      "strategy": "lpt-pack",
      "status": "completed",
      "makespan": 480.0,
      "utilization": 0.80,
      "changeovers": 15,
      "lots_scheduled": 50,
      "window_violations": 2,
      "execution_time": 1.8
    }
  ]
}
```

#### List Comparisons
```http
GET /api/v1/comparisons?page=1&page_size=20
Authorization: Bearer <token>
```

#### Delete Comparison
```http
DELETE /api/v1/compare/{id}
Authorization: Bearer <token>
```

### Configuration

#### Create Configuration Template
```http
POST /api/v1/config
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "High-Priority Production",
  "description": "Configuration for high-priority lots",
  "config": {
    "line_count": 5,
    "changeover_time": 30,
    "min_batch_size": 100,
    "max_makespan": 480,
    "priority_weight": 2.0
  },
  "is_public": false
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "High-Priority Production",
  "description": "Configuration for high-priority lots",
  "config": {
    "line_count": 5,
    "changeover_time": 30,
    "min_batch_size": 100,
    "max_makespan": 480,
    "priority_weight": 2.0
  },
  "is_public": false,
  "is_default": false,
  "created_at": "2024-10-13T10:00:00",
  "updated_at": "2024-10-13T10:00:00"
}
```

#### List Configuration Templates
```http
GET /api/v1/configs?page=1&page_size=20&include_public=true
Authorization: Bearer <token>
```

#### Get Configuration Template
```http
GET /api/v1/config/{id}
Authorization: Bearer <token>
```

#### Update Configuration Template
```http
PUT /api/v1/config/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "config": {
    "line_count": 6
  }
}
```

#### Delete Configuration Template
```http
DELETE /api/v1/config/{id}
Authorization: Bearer <token>
```

#### Set Default Configuration
```http
POST /api/v1/config/{id}/set-default
Authorization: Bearer <token>
```

#### Get Default Configuration
```http
GET /api/v1/config/default
Authorization: Bearer <token>
```

#### Validate Configuration
```http
POST /api/v1/config/validate
Authorization: Bearer <token>
Content-Type: application/json

{
  "config": {
    "line_count": 3,
    "changeover_time": 30
  }
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

---

## Request/Response Examples

### cURL Examples

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123!"
```

#### Create Schedule
```bash
curl -X POST "http://localhost:8000/api/v1/schedule" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Schedule",
    "lots_data": [
      {
        "lot_id": "LOT001",
        "product": "ProductA",
        "quantity": 1000,
        "priority": 1
      }
    ],
    "strategy": "smart-pack"
  }'
```

#### Get Schedule
```bash
curl -X GET "http://localhost:8000/api/v1/schedule/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Python Client Examples

#### Basic Usage
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "user@example.com",
        "password": "SecurePass123!"
    }
)
token = response.json()["access_token"]

# Create schedule
headers = {"Authorization": f"Bearer {token}"}
schedule_data = {
    "name": "Test Schedule",
    "lots_data": [
        {
            "lot_id": "LOT001",
            "product": "ProductA",
            "quantity": 1000,
            "priority": 1
        }
    ],
    "strategy": "smart-pack"
}

response = requests.post(
    "http://localhost:8000/api/v1/schedule",
    json=schedule_data,
    headers=headers
)
schedule_id = response.json()["id"]

# Get schedule
response = requests.get(
    f"http://localhost:8000/api/v1/schedule/{schedule_id}",
    headers=headers
)
schedule = response.json()
print(f"Schedule status: {schedule['status']}")
```

#### With Error Handling
```python
import requests
from requests.exceptions import HTTPError

class SchedulerClient:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.token = None
        self.login(email, password)

    def login(self, email, password):
        """Login and store access token."""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": email, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def _get_headers(self):
        """Get authorization headers."""
        return {"Authorization": f"Bearer {self.token}"}

    def create_schedule(self, name, lots_data, strategy="smart-pack", config=None):
        """Create a new schedule."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/schedule",
                json={
                    "name": name,
                    "lots_data": lots_data,
                    "strategy": strategy,
                    "config": config
                },
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"Error creating schedule: {e.response.json()}")
            raise

    def get_schedule(self, schedule_id):
        """Get schedule by ID."""
        response = requests.get(
            f"{self.base_url}/api/v1/schedule/{schedule_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def wait_for_completion(self, schedule_id, poll_interval=2):
        """Poll schedule until completion."""
        import time

        while True:
            schedule = self.get_schedule(schedule_id)
            status = schedule["status"]

            if status == "completed":
                return schedule
            elif status == "failed":
                raise Exception(f"Schedule failed: {schedule['error_message']}")

            time.sleep(poll_interval)

# Usage
client = SchedulerClient(
    "http://localhost:8000",
    "user@example.com",
    "SecurePass123!"
)

schedule = client.create_schedule(
    name="Production Schedule",
    lots_data=[
        {"lot_id": "LOT001", "product": "A", "quantity": 1000}
    ],
    strategy="smart-pack"
)

print(f"Created schedule {schedule['id']}")
result = client.wait_for_completion(schedule["id"])
print(f"Makespan: {result['result']['makespan']}")
```

### JavaScript/TypeScript Examples

#### Using Fetch API
```javascript
// Login
async function login(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  const data = await response.json();
  return data.access_token;
}

// Create schedule
async function createSchedule(token, scheduleData) {
  const response = await fetch('http://localhost:8000/api/v1/schedule', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(scheduleData),
  });

  return await response.json();
}

// Usage
const token = await login('user@example.com', 'SecurePass123!');
const schedule = await createSchedule(token, {
  name: 'Test Schedule',
  lots_data: [
    { lot_id: 'LOT001', product: 'A', quantity: 1000 }
  ],
  strategy: 'smart-pack',
});
```

#### Using Axios
```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with interceptor
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await axios.post(
    `${API_BASE_URL}/api/v1/auth/login`,
    formData,
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }
  );

  return response.data.access_token;
}

// Create schedule
export async function createSchedule(scheduleData: ScheduleRequest) {
  const response = await api.post('/api/v1/schedule', scheduleData);
  return response.data;
}

// Get schedule
export async function getSchedule(id: number) {
  const response = await api.get(`/api/v1/schedule/${id}`);
  return response.data;
}

// Usage with React
function App() {
  const handleCreateSchedule = async () => {
    try {
      const schedule = await createSchedule({
        name: 'Test Schedule',
        lots_data: [
          { lot_id: 'LOT001', product: 'A', quantity: 1000 }
        ],
        strategy: 'smart-pack',
      });
      console.log('Created schedule:', schedule);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return <button onClick={handleCreateSchedule}>Create Schedule</button>;
}
```

---

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "lots_data", 0, "lot_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### HTTP Status Codes

| Code | Name | Description |
|:-----|:-----|:------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 204 | No Content | Resource deleted |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Common Error Scenarios

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

**Cause:** Invalid or expired token
**Solution:** Re-authenticate and get a new token

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions to access this resource"
}
```

**Cause:** User doesn't have access to the resource
**Solution:** Check if user owns the resource or has admin privileges

#### 404 Not Found
```json
{
  "detail": "Schedule not found"
}
```

**Cause:** Resource doesn't exist or user doesn't have access
**Solution:** Verify the resource ID

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "strategy"],
      "msg": "Invalid strategy: must be one of [smart-pack, lpt-pack, spt-pack, cfs-pack, hybrid-pack, milp-opt]",
      "type": "value_error"
    }
  ]
}
```

**Cause:** Invalid input data
**Solution:** Fix the validation errors and retry

### Error Handling Best Practices

```python
import requests
from requests.exceptions import HTTPError

def create_schedule_safe(token, schedule_data):
    """Create schedule with proper error handling."""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/schedule",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()

    except HTTPError as e:
        if e.response.status_code == 401:
            print("Authentication failed - please login again")
            # Re-authenticate
        elif e.response.status_code == 422:
            print("Validation error:")
            for error in e.response.json()["detail"]:
                print(f"  - {error['loc']}: {error['msg']}")
        else:
            print(f"Error {e.response.status_code}: {e.response.json()}")
        raise

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

---

## Rate Limiting

**Status:** Not yet implemented

**Planned limits:**
- 100 requests per minute per user
- 10 concurrent schedule executions per user
- 5 MB maximum request body size

**Response headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634145600
```

**Error response (429 Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded. Please try again in 30 seconds."
}
```

---

## WebSocket Real-Time Updates

The API provides WebSocket connections for real-time progress updates during schedule and comparison execution.

### Connection

```javascript
const token = 'YOUR_ACCESS_TOKEN';
const scheduleId = 1;

const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/schedule/${scheduleId}?token=${token}`
);

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);

  switch (message.type) {
    case 'progress':
      console.log(`Progress: ${message.progress}% - ${message.message}`);
      break;
    case 'complete':
      console.log('Schedule completed!', message.result);
      break;
    case 'error':
      console.log('Error:', message.message);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

### Message Types

#### Progress Update
```json
{
  "type": "progress",
  "step": "planning",
  "progress": 50,
  "message": "Planning optimal schedule...",
  "timestamp": "2024-10-13T10:01:00"
}
```

#### Completion
```json
{
  "type": "complete",
  "progress": 100,
  "message": "Schedule completed successfully!",
  "result": {
    "schedule_id": 1,
    "makespan": 450.5,
    "kpis": {
      "utilization": 0.85
    }
  },
  "timestamp": "2024-10-13T10:02:00"
}
```

#### Error
```json
{
  "type": "error",
  "code": "VALIDATION_ERROR",
  "message": "Invalid lot data: duplicate lot_id found",
  "timestamp": "2024-10-13T10:00:30"
}
```

### React Hook Example

```typescript
import { useEffect, useState } from 'react';

interface ProgressUpdate {
  type: string;
  step?: string;
  progress?: number;
  message?: string;
}

function useScheduleProgress(scheduleId: number, token: string) {
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/ws/schedule/${scheduleId}?token=${token}`
    );

    ws.onopen = () => setIsConnected(true);
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setProgress(message);
    };
    ws.onerror = (error) => console.error('WebSocket error:', error);
    ws.onclose = () => setIsConnected(false);

    return () => ws.close();
  }, [scheduleId, token]);

  return { progress, isConnected };
}

// Usage in component
function ScheduleProgress({ scheduleId }: { scheduleId: number }) {
  const token = localStorage.getItem('token') || '';
  const { progress, isConnected } = useScheduleProgress(scheduleId, token);

  if (!isConnected) return <div>Connecting...</div>;
  if (!progress) return <div>Waiting for updates...</div>;

  return (
    <div>
      <div>Step: {progress.step}</div>
      <div>Progress: {progress.progress}%</div>
      <div>Message: {progress.message}</div>
    </div>
  );
}
```

---

## Client Libraries

### Python
```bash
pip install requests websockets
```

See [Python Client Examples](#python-client-examples)

### JavaScript/TypeScript
```bash
npm install axios
```

See [JavaScript/TypeScript Examples](#javascripttypescript-examples)

### Future Libraries (Planned)
- Official Python SDK
- Official TypeScript SDK
- CLI tool for API interaction

---

## Best Practices

### 1. **Authentication**
- ✅ Store tokens securely (not in localStorage)
- ✅ Implement token refresh logic
- ✅ Handle 401 errors gracefully
- ❌ Don't include tokens in URLs (use headers)

### 2. **Error Handling**
- ✅ Check HTTP status codes
- ✅ Parse error responses
- ✅ Implement retry logic for transient errors
- ✅ Log errors for debugging

### 3. **Performance**
- ✅ Use pagination for large lists
- ✅ Cache configuration templates
- ✅ Use WebSocket for real-time updates (avoid polling)
- ✅ Compress request bodies for large lot data

### 4. **Data Validation**
- ✅ Validate data on client side before sending
- ✅ Use the `/schedule/validate` endpoint
- ✅ Handle validation errors gracefully

### 5. **Scheduling**
- ✅ Use meaningful schedule names
- ✅ Test with `/compare` before production
- ✅ Monitor schedule execution via WebSocket
- ✅ Handle failures and retries

### 6. **Configuration**
- ✅ Create reusable configuration templates
- ✅ Set a default configuration
- ✅ Validate configurations before use
- ✅ Document configuration parameters

---

## Next Steps

1. **Explore the Interactive Docs** - http://localhost:8000/docs
2. **Try the Examples** - Run the code snippets above
3. **Build Your Client** - Use the provided examples as a starting point
4. **Report Issues** - https://github.com/vikas-py/filling_scheduler/issues

---

**Questions?** Check the [FAQ](FAQ.md) or [open an issue](https://github.com/vikas-py/filling_scheduler/issues).

**License:** MIT
**Repository:** https://github.com/vikas-py/filling_scheduler
