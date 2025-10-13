# Configuration Template API - Complete Reference

**Version:** 1.0
**Base URL:** `http://localhost:8000/api/v1`
**Authentication:** Bearer Token (JWT)

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Configuration Parameters](#configuration-parameters)
5. [Access Control](#access-control)
6. [Code Examples](#code-examples)
7. [Use Cases](#use-cases)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

---

## Overview

The Configuration Template API allows users to:

- **Create and manage** reusable configuration templates
- **Share** templates publicly or keep them private
- **Set defaults** for automatic configuration loading
- **Validate** configurations before saving
- **Import/Export** templates for backup or sharing
- **Search and filter** templates with pagination

### Key Features

✅ **Private & Public Templates** - Control who can see your configurations
✅ **Default Configuration** - Set one template as your default
✅ **Pre-flight Validation** - Validate before saving
✅ **Import/Export** - Portable configuration format
✅ **Pagination** - Efficient listing of large template collections
✅ **Access Control** - Owner-only operations for private templates

---

## Authentication

All endpoints require authentication using a Bearer token (JWT).

### Getting a Token

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## API Endpoints

### 1. Create Configuration Template

**POST** `/config`

Create a new configuration template (private or public).

**Request Body:**
```json
{
  "name": "My Custom Config",
  "description": "Configuration for high-priority lots",
  "config": {
    "max_clean_hours": 6.0,
    "default_changeover_hours": 3.0,
    "min_lot_spacing_hours": 1.0,
    "changeover_matrix": {
      "Product-A": {"Product-B": 4.0, "Product-C": 5.0},
      "Product-B": {"Product-A": 3.5, "Product-C": 4.5}
    },
    "window_penalty_weight": 100.0,
    "priority_levels": {
      "high": 3.0,
      "medium": 2.0,
      "low": 1.0
    }
  },
  "is_public": false
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 5,
  "name": "My Custom Config",
  "description": "Configuration for high-priority lots",
  "config": { /* configuration object */ },
  "is_public": false,
  "is_default": false,
  "created_at": "2025-10-13T10:30:00",
  "updated_at": "2025-10-13T10:30:00"
}
```

**Validation:**
- Configuration is validated before creation
- Returns `400 Bad Request` if configuration is invalid

---

### 2. Get Configuration Template by ID

**GET** `/config/{template_id}`

Retrieve a specific configuration template.

**Path Parameters:**
- `template_id` (integer) - Template ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 5,
  "name": "My Custom Config",
  "description": "Configuration for high-priority lots",
  "config": { /* configuration object */ },
  "is_public": false,
  "is_default": false,
  "created_at": "2025-10-13T10:30:00",
  "updated_at": "2025-10-13T10:30:00"
}
```

**Access Control:**
- ✅ Template owner can access
- ✅ Any user can access if `is_public: true`
- ❌ Returns `404 Not Found` if user doesn't have access

---

### 3. List Configuration Templates

**GET** `/configs`

List configuration templates with pagination.

**Query Parameters:**
- `page` (integer, default: 1) - Page number (≥1)
- `page_size` (integer, default: 20) - Items per page (1-100)
- `public_only` (boolean, default: false) - Show only public templates

**Response:** `200 OK`
```json
{
  "templates": [
    {
      "id": 1,
      "user_id": 5,
      "name": "My Custom Config",
      "config": { /* ... */ },
      "is_public": false,
      "is_default": true,
      "created_at": "2025-10-13T10:30:00",
      "updated_at": "2025-10-13T10:30:00"
    },
    {
      "id": 2,
      "user_id": 5,
      "name": "Standard Pharma Config",
      "config": { /* ... */ },
      "is_public": true,
      "is_default": false,
      "created_at": "2025-10-13T11:00:00",
      "updated_at": "2025-10-13T11:00:00"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

**Behavior:**
- By default: Returns user's own templates + all public templates
- With `public_only=true`: Returns only public templates

---

### 4. Update Configuration Template

**PUT** `/config/{template_id}`

Update an existing configuration template. All fields are optional.

**Path Parameters:**
- `template_id` (integer) - Template ID

**Request Body:**
```json
{
  "name": "Updated Config Name",
  "description": "Updated description",
  "config": {
    "max_clean_hours": 7.0
  },
  "is_public": true
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 5,
  "name": "Updated Config Name",
  "description": "Updated description",
  "config": { /* updated configuration */ },
  "is_public": true,
  "is_default": false,
  "created_at": "2025-10-13T10:30:00",
  "updated_at": "2025-10-13T12:00:00"
}
```

**Access Control:**
- ❌ Only the template owner can update
- Returns `404 Not Found` if not owner

---

### 5. Delete Configuration Template

**DELETE** `/config/{template_id}`

Delete a configuration template.

**Path Parameters:**
- `template_id` (integer) - Template ID

**Response:** `200 OK`
```json
{
  "message": "Configuration template deleted successfully",
  "detail": "Deleted template: My Custom Config"
}
```

**Behavior:**
- If the template is the user's default, it will be automatically unset
- Owner-only operation

---

### 6. Set Default Configuration

**POST** `/config/{template_id}/set-default`

Set a template as the user's default configuration.

**Path Parameters:**
- `template_id` (integer) - Template ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 5,
  "name": "My Custom Config",
  "config": { /* ... */ },
  "is_default": true,
  "created_at": "2025-10-13T10:30:00",
  "updated_at": "2025-10-13T12:00:00"
}
```

**Behavior:**
- Only ONE template can be default per user
- Setting a new default automatically unsets the previous one (atomic operation)
- Owner-only operation

---

### 7. Get User's Default Configuration

**GET** `/config/default`

Get the current user's default configuration template.

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 5,
  "name": "My Custom Config",
  "config": { /* ... */ },
  "is_default": true,
  "created_at": "2025-10-13T10:30:00",
  "updated_at": "2025-10-13T12:00:00"
}
```

**If no default is set:**
```json
null
```

---

### 8. Unset Default Configuration

**DELETE** `/config/default`

Remove the user's default configuration setting.

**Response:** `200 OK`
```json
{
  "message": "Default configuration template unset successfully"
}
```

**Behavior:**
- The template still exists, just no longer marked as default
- No error if no default was set

---

### 9. Validate Configuration

**POST** `/config/validate`

Validate a configuration without saving it (pre-flight validation).

**Request Body:**
```json
{
  "max_clean_hours": 6.0,
  "default_changeover_hours": 3.0,
  "changeover_matrix": {
    "Product-A": {"Product-B": 4.0}
  }
}
```

**Response:** `200 OK`

**Valid Configuration:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["max_clean_hours is quite high (6.0h), consider using 4-8 hours"]
}
```

**Invalid Configuration:**
```json
{
  "valid": false,
  "errors": [
    "max_clean_hours must be a positive number",
    "default_changeover_hours must be non-negative"
  ],
  "warnings": []
}
```

---

### 10. Get System Default Configuration

**GET** `/config/system/default`

Get the system's default configuration (used when no custom config is provided).

**Response:** `200 OK`
```json
{
  "max_clean_hours": 4.0,
  "default_changeover_hours": 2.0,
  "min_lot_spacing_hours": 0.5,
  "changeover_matrix": {},
  "window_penalty_weight": 100.0,
  "priority_levels": {
    "high": 3.0,
    "medium": 2.0,
    "low": 1.0
  },
  "milp_time_limit": 300.0,
  "allowed_strategies": [
    "smart_pack",
    "lpt_pack",
    "spt_pack",
    "cfs_pack",
    "hybrid_pack",
    "milp_opt"
  ]
}
```

---

### 11. Export Configuration Template

**GET** `/config/{template_id}/export`

Export a configuration template to a portable format for sharing or backup.

**Path Parameters:**
- `template_id` (integer) - Template ID

**Response:** `200 OK`
```json
{
  "name": "My Custom Config",
  "description": "Configuration for high-priority lots",
  "config": {
    "max_clean_hours": 6.0,
    "default_changeover_hours": 3.0
  },
  "created_at": "2025-10-13T10:30:00",
  "updated_at": "2025-10-13T12:00:00"
}
```

**Access Control:**
- ✅ Template owner can export
- ✅ Any user can export public templates

---

### 12. Import Configuration Template

**POST** `/config/import`

Import a configuration template from an exported format.

**Request Body:**
```json
{
  "name": "Imported Config",
  "description": "Imported from colleague",
  "config": {
    "max_clean_hours": 6.0,
    "default_changeover_hours": 3.0
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 5,
  "user_id": 7,
  "name": "Imported Config",
  "description": "Imported from colleague",
  "config": { /* ... */ },
  "is_public": false,
  "is_default": false,
  "created_at": "2025-10-13T13:00:00",
  "updated_at": "2025-10-13T13:00:00"
}
```

**Behavior:**
- Creates a new template owned by the importing user
- Configuration is validated before import
- Returns `400 Bad Request` if configuration is invalid

---

## Configuration Parameters

### Core Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `max_clean_hours` | float | No | 4.0 | Maximum hours for cleaning activities (must be positive) |
| `default_changeover_hours` | float | No | 2.0 | Default changeover time between products (must be ≥0) |
| `min_lot_spacing_hours` | float | No | 0.5 | Minimum spacing between lots (must be ≥0) |
| `changeover_matrix` | object | No | {} | Product-specific changeover times (dict of dicts) |
| `window_penalty_weight` | float | No | 100.0 | Penalty for time window violations (must be ≥0) |
| `priority_levels` | object | No | See below | Priority weights for scheduling |
| `milp_time_limit` | float | No | 300.0 | Time limit for MILP solver in seconds (must be positive) |
| `allowed_strategies` | array | No | All | List of allowed scheduling strategies |

### Default Priority Levels

```json
{
  "high": 3.0,
  "medium": 2.0,
  "low": 1.0
}
```

### Allowed Strategies

- `smart_pack` - Intelligent packing algorithm
- `lpt_pack` - Longest Processing Time first
- `spt_pack` - Shortest Processing Time first
- `cfs_pack` - Critical Ratio Scheduling
- `hybrid_pack` - Hybrid approach
- `milp_opt` - Mixed Integer Linear Programming optimization

### Changeover Matrix Example

```json
{
  "Product-A": {
    "Product-B": 4.0,
    "Product-C": 5.0
  },
  "Product-B": {
    "Product-A": 3.5,
    "Product-C": 4.5
  },
  "Product-C": {
    "Product-A": 5.5,
    "Product-B": 4.5
  }
}
```

### Validation Rules

✅ **max_clean_hours:**
- Must be a positive number
- Warning if > 24 hours

✅ **default_changeover_hours:**
- Must be non-negative (≥0)

✅ **changeover_matrix:**
- Must be a nested dictionary
- All values must be numeric and non-negative
- Inner keys should match outer keys for consistency

✅ **priority_levels:**
- Must be a dictionary with string keys and numeric values

✅ **milp_time_limit:**
- Must be positive
- Warning if > 3600 seconds (1 hour)

✅ **allowed_strategies:**
- Must be a list of valid strategy names

---

## Access Control

### Private Templates (`is_public: false`)

- ✅ **Owner** can: Read, Update, Delete, Set as Default, Export
- ❌ **Other users** cannot access

### Public Templates (`is_public: true`)

- ✅ **Owner** can: Read, Update, Delete, Set as Default, Export
- ✅ **Other users** can: Read, Export
- ❌ **Other users** cannot: Update, Delete, Set as Default

### Default Configuration

- Each user can have **ONE** default template
- Only the owner can set/unset their default
- Default templates must be owned by the user

---

## Code Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "user@example.com",
    "password": "password"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create a configuration template
config = {
    "name": "Production Config",
    "description": "Optimized for high-throughput",
    "config": {
        "max_clean_hours": 5.0,
        "default_changeover_hours": 2.5,
        "min_lot_spacing_hours": 1.0,
        "changeover_matrix": {
            "Product-A": {"Product-B": 3.0}
        }
    },
    "is_public": False
}
response = requests.post(f"{BASE_URL}/config", json=config, headers=headers)
template = response.json()
print(f"Created template ID: {template['id']}")

# Set as default
response = requests.post(
    f"{BASE_URL}/config/{template['id']}/set-default",
    headers=headers
)
print(f"Set as default: {response.json()['name']}")

# List templates
response = requests.get(f"{BASE_URL}/configs?page=1&page_size=10", headers=headers)
templates = response.json()
print(f"Total templates: {templates['total']}")

# Export template
response = requests.get(f"{BASE_URL}/config/{template['id']}/export", headers=headers)
exported = response.json()
print(f"Exported: {exported}")

# Import template (as another user or same user)
imported_config = {
    "name": "Imported Config",
    "description": "Imported from export",
    "config": exported["config"]
}
response = requests.post(f"{BASE_URL}/config/import", json=imported_config, headers=headers)
print(f"Imported template ID: {response.json()['id']}")
```

### TypeScript / JavaScript

```typescript
const BASE_URL = "http://localhost:8000/api/v1";

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    password: "password"
  })
});
const { access_token } = await loginResponse.json();
const headers = { Authorization: `Bearer ${access_token}` };

// Create configuration template
const config = {
  name: "Production Config",
  description: "Optimized for high-throughput",
  config: {
    max_clean_hours: 5.0,
    default_changeover_hours: 2.5,
    min_lot_spacing_hours: 1.0,
    changeover_matrix: {
      "Product-A": { "Product-B": 3.0 }
    }
  },
  is_public: false
};

const createResponse = await fetch(`${BASE_URL}/config`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify(config)
});
const template = await createResponse.json();
console.log(`Created template ID: ${template.id}`);

// Get user's default
const defaultResponse = await fetch(`${BASE_URL}/config/default`, { headers });
const defaultConfig = await defaultResponse.json();
if (defaultConfig) {
  console.log(`Default config: ${defaultConfig.name}`);
} else {
  console.log("No default config set");
}

// List public templates
const listResponse = await fetch(
  `${BASE_URL}/configs?public_only=true&page=1&page_size=20`,
  { headers }
);
const { templates, total } = await listResponse.json();
console.log(`Found ${total} public templates`);
```

### cURL

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Create template
curl -X POST http://localhost:8000/api/v1/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Config",
    "description": "High-throughput configuration",
    "config": {
      "max_clean_hours": 5.0,
      "default_changeover_hours": 2.5
    },
    "is_public": false
  }'

# List templates
curl -X GET "http://localhost:8000/api/v1/configs?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# Get default config
curl -X GET http://localhost:8000/api/v1/config/default \
  -H "Authorization: Bearer $TOKEN"

# Validate config
curl -X POST http://localhost:8000/api/v1/config/validate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "max_clean_hours": 6.0,
    "default_changeover_hours": 3.0
  }'

# Export template (ID=1)
curl -X GET http://localhost:8000/api/v1/config/1/export \
  -H "Authorization: Bearer $TOKEN"

# Delete template (ID=1)
curl -X DELETE http://localhost:8000/api/v1/config/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Use Cases

### 1. Personal Configuration Library

**Scenario:** User wants to maintain multiple configurations for different scenarios.

```python
# Create configurations for different scenarios
configs = [
    {
        "name": "High Priority Rush",
        "description": "For urgent orders",
        "config": {"max_clean_hours": 3.0, "priority_levels": {"high": 5.0}}
    },
    {
        "name": "Standard Production",
        "description": "Normal production schedule",
        "config": {"max_clean_hours": 4.0, "default_changeover_hours": 2.0}
    },
    {
        "name": "Long Campaign",
        "description": "Extended production runs",
        "config": {"max_clean_hours": 8.0, "min_lot_spacing_hours": 2.0}
    }
]

for config_data in configs:
    requests.post(f"{BASE_URL}/config", json=config_data, headers=headers)

# Set default for daily use
requests.post(f"{BASE_URL}/config/2/set-default", headers=headers)
```

### 2. Team Configuration Sharing

**Scenario:** Team lead creates a standard configuration and shares with team.

```python
# Team lead creates public template
team_config = {
    "name": "Team Standard Config",
    "description": "Standard configuration for all team members",
    "config": { /* ... */ },
    "is_public": True  # Make it public
}
response = requests.post(f"{BASE_URL}/config", json=team_config, headers=leader_headers)
template_id = response.json()["id"]

# Share the template ID with team
print(f"Share this template ID with your team: {template_id}")

# Team members can view and copy
response = requests.get(f"{BASE_URL}/config/{template_id}", headers=member_headers)
team_template = response.json()

# Export and import to create personal copy
exported = requests.get(f"{BASE_URL}/config/{template_id}/export", headers=member_headers).json()
imported = requests.post(f"{BASE_URL}/config/import", json=exported, headers=member_headers)
```

### 3. Configuration Validation Before Scheduling

**Scenario:** Validate configuration before creating a schedule.

```python
# Before creating a schedule, validate the config
config_to_test = {
    "max_clean_hours": 10.0,  # Might be too high
    "default_changeover_hours": -1.0  # Invalid!
}

validation = requests.post(
    f"{BASE_URL}/config/validate",
    json=config_to_test,
    headers=headers
).json()

if validation["valid"]:
    print("✓ Configuration is valid")
    if validation["warnings"]:
        print("Warnings:", validation["warnings"])
    # Proceed with scheduling
else:
    print("✗ Configuration is invalid")
    print("Errors:", validation["errors"])
    # Fix configuration before proceeding
```

### 4. Configuration Backup and Migration

**Scenario:** Backup all configurations or migrate to another environment.

```python
# Export all user's templates
response = requests.get(f"{BASE_URL}/configs?page_size=100", headers=headers)
templates = response.json()["templates"]

backups = []
for template in templates:
    exported = requests.get(
        f"{BASE_URL}/config/{template['id']}/export",
        headers=headers
    ).json()
    backups.append(exported)

# Save to file
import json
with open("config_backup.json", "w") as f:
    json.dump(backups, f, indent=2)

# Later, restore from backup (in new environment)
with open("config_backup.json", "r") as f:
    backups = json.load(f)

for backup in backups:
    requests.post(
        f"{BASE_URL}/config/import",
        json=backup,
        headers=new_headers
    )
```

### 5. Default Configuration Workflow

**Scenario:** Use default configuration for automatic schedule creation.

```python
# Get user's default config
default = requests.get(f"{BASE_URL}/config/default", headers=headers).json()

if default:
    # Use default config for scheduling
    schedule_request = {
        "name": "Daily Schedule",
        "lots_data": [...],
        "strategy": "smart_pack",
        "config": default["config"]  # Use default config
    }
    requests.post(f"{BASE_URL}/schedule", json=schedule_request, headers=headers)
else:
    # No default set, use system default
    system_default = requests.get(
        f"{BASE_URL}/config/system/default",
        headers=headers
    ).json()
    schedule_request["config"] = system_default
```

---

## Error Handling

### Common Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 400 | Bad Request | Invalid configuration, validation failed |
| 401 | Unauthorized | Missing or invalid token |
| 404 | Not Found | Template doesn't exist or no access |
| 422 | Unprocessable Entity | Invalid request format, type errors |
| 500 | Internal Server Error | Server-side issue |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "type": "ErrorType",
  "path": "/api/v1/config/123"
}
```

### Validation Error Example

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "config", "max_clean_hours"],
      "msg": "max_clean_hours must be a positive number",
      "input": -5.0
    }
  ]
}
```

### Handling Errors in Code

```python
try:
    response = requests.post(f"{BASE_URL}/config", json=config, headers=headers)
    response.raise_for_status()
    template = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        error = e.response.json()
        print(f"Validation error: {error['detail']}")
    elif e.response.status_code == 404:
        print("Template not found or no access")
    else:
        print(f"Error: {e}")
```

---

## Best Practices

### 1. Configuration Naming

✅ **Good:**
- "High Priority Rush Production"
- "Standard Pharma Config"
- "Long Campaign - Low Changeovers"

❌ **Avoid:**
- "Config 1"
- "Test"
- "Untitled"

### 2. Use Descriptions

Always provide meaningful descriptions:

```json
{
  "name": "Rush Production",
  "description": "Optimized for urgent orders with high priority weighting and minimal changeovers"
}
```

### 3. Validate Before Saving

Always use the `/config/validate` endpoint before creating templates:

```python
# Validate first
validation = requests.post(f"{BASE_URL}/config/validate", json=config, headers=headers).json()

if validation["valid"]:
    # Now create the template
    requests.post(f"{BASE_URL}/config", json=full_template, headers=headers)
else:
    print("Fix these errors:", validation["errors"])
```

### 4. Use Defaults Wisely

- Set one default configuration for your most common use case
- Update default when your workflow changes
- Don't delete your default without setting a new one

### 5. Public vs Private

**Use Public Templates for:**
- Team standards
- Best practices
- Reference configurations

**Use Private Templates for:**
- Experimental configurations
- Client-specific settings
- Work-in-progress

### 6. Regular Backups

Export important configurations regularly:

```python
# Monthly backup script
templates = get_all_templates()
for template in templates:
    export = requests.get(f"{BASE_URL}/config/{template['id']}/export", headers=headers).json()
    filename = f"backup_{template['name']}_{date.today()}.json"
    save_to_file(filename, export)
```

### 7. Pagination for Large Lists

Always use pagination when listing templates:

```python
# Good - paginated
page = 1
while True:
    response = requests.get(
        f"{BASE_URL}/configs?page={page}&page_size=50",
        headers=headers
    ).json()

    process_templates(response["templates"])

    if page >= response["pages"]:
        break
    page += 1
```

### 8. Error Handling

Always implement proper error handling:

```python
def create_config_safe(config_data):
    try:
        response = requests.post(f"{BASE_URL}/config", json=config_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to create config: {e.response.text}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to API server")
        return None
```

---

## FAQ

**Q: How many templates can I create?**
A: No hard limit, but use pagination when listing more than 100 templates.

**Q: Can I share a private template?**
A: Export it, share the JSON, and the recipient can import it (creates their own copy).

**Q: What happens if I delete my default template?**
A: The default will be automatically unset. Set a new default or use system defaults.

**Q: Can I have multiple defaults?**
A: No, only ONE template can be default per user.

**Q: Are public templates editable by others?**
A: No, only the owner can edit. Others can view and export to create their own copy.

**Q: What if validation warnings appear?**
A: Warnings are informational. The config is valid but you should review the warnings.

**Q: Can I revert to system defaults?**
A: Yes, use `GET /config/system/default` to retrieve system defaults anytime.

---

## Support

For issues or questions:
- Check the [API Documentation](http://localhost:8000/docs)
- Review [Known Issues](./KNOWN_ISSUES.md)
- See [Agent Development Guide](./AGENT_DEVELOPMENT_GUIDE.md)

---

*Last Updated: October 13, 2025*
*API Version: 1.0*
*Filling Scheduler Backend API*
