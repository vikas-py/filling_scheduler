# Filling Scheduler API - Postman Collection

This directory contains Postman collection and environment files for the Filling Scheduler API.

## 📁 Files

- **`Filling_Scheduler_API.postman_collection.json`** - Complete API collection with all endpoints
- **`Filling_Scheduler_Dev.postman_environment.json`** - Development environment variables
- **`Filling_Scheduler_Prod.postman_environment.json`** - Production environment variables

---

## 🚀 Quick Start

### 1. Import Collection

1. Open Postman
2. Click **Import** button (top left)
3. Drag and drop `Filling_Scheduler_API.postman_collection.json`
4. Or click **Choose Files** and select the file

### 2. Import Environment

1. Click the **Environments** icon (gear icon) in top right
2. Click **Import**
3. Select `Filling_Scheduler_Dev.postman_environment.json`
4. Optionally import `Filling_Scheduler_Prod.postman_environment.json`

### 3. Select Environment

1. Click the environment dropdown (top right)
2. Select **Filling Scheduler - Development**

### 4. Configure Environment Variables

1. Click the **Environments** icon
2. Click **Filling Scheduler - Development**
3. Update the following variables:
   - `userEmail` - Your test user email (default: test@example.com)
   - `userPassword` - Your test user password (default: TestPassword123!)
   - `baseUrl` - API base URL (default: http://localhost:8000)

### 5. Authenticate

1. Expand the **Authentication** folder
2. Click **Login** request
3. Click **Send**
4. The access token is automatically saved to the environment
5. All subsequent requests will use this token

---

## 📚 Collection Structure

```
Filling Scheduler API/
├── Authentication/
│   ├── Login
│   └── Get Current User
├── Schedules/
│   ├── Create Schedule
│   ├── Get Schedule
│   ├── List Schedules
│   ├── Delete Schedule
│   ├── Export Schedule (JSON)
│   ├── Export Schedule (CSV)
│   ├── Validate Lots Data
│   └── List Available Strategies
├── Comparisons/
│   ├── Create Comparison
│   ├── Get Comparison
│   ├── List Comparisons
│   └── Delete Comparison
├── Configuration/
│   ├── Create Config Template
│   ├── List Config Templates
│   ├── Get Config Template
│   ├── Update Config Template
│   ├── Delete Config Template
│   ├── Set Default Config
│   ├── Get Default Config
│   ├── Validate Configuration
│   └── Get System Default Config
└── Health & Info/
    ├── Root
    └── Health Check
```

---

## 🔐 Authentication

The collection uses **Bearer Token** authentication. The token is automatically:
1. Obtained from the **Login** request
2. Saved to the `accessToken` environment variable
3. Included in all subsequent requests via the collection-level auth

### Manual Token Setup

If you already have a token:
1. Go to Environments
2. Set the `accessToken` variable to your token value
3. All requests will use it automatically

---

## 🎯 Common Workflows

### Workflow 1: Create and Monitor a Schedule

1. **Login** → Saves token
2. **Create Schedule** → Saves schedule ID
3. **Get Schedule** → Check status (pending → running → completed)
4. Poll **Get Schedule** until status is "completed"
5. **Export Schedule (JSON)** → Download results

### Workflow 2: Compare Strategies

1. **Login** → Saves token
2. **Create Comparison** → Saves comparison ID
3. **Get Comparison** → View results for all strategies
4. Analyze which strategy performed best

### Workflow 3: Save Configuration Template

1. **Login** → Saves token
2. **Create Config Template** → Saves template ID
3. **Set Default Config** → Make it your default
4. **Get Default Config** → Verify it's set

### Workflow 4: Using Configuration in Schedule

1. **Login** → Saves token
2. **Get Default Config** → Get your config
3. **Create Schedule** → Use config in request body
4. **Get Schedule** → View results

---

## 📋 Environment Variables

### Required Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `baseUrl` | API base URL | `http://localhost:8000` |
| `userEmail` | User email for login | `test@example.com` |
| `userPassword` | User password | `TestPassword123!` |

### Auto-Populated Variables

These are automatically set by request scripts:

| Variable | Description | Set By |
|:---------|:------------|:-------|
| `accessToken` | JWT access token | Login request |
| `scheduleId` | Last created schedule ID | Create Schedule |
| `comparisonId` | Last created comparison ID | Create Comparison |
| `configTemplateId` | Last created config template ID | Create Config Template |

---

## 🔧 Request Examples

### Create Schedule

```json
POST /api/v1/schedule

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
  }
}
```

### Compare Strategies

```json
POST /api/v1/compare

{
  "name": "Strategy Comparison",
  "lots_data": [...],
  "strategies": ["smart-pack", "lpt-pack", "spt-pack"],
  "config": {
    "line_count": 3
  }
}
```

### Create Config Template

```json
POST /api/v1/config

{
  "name": "High-Priority Production",
  "description": "Configuration for high-priority lots",
  "config": {
    "line_count": 5,
    "changeover_time": 30,
    "priority_weight": 2.0
  },
  "is_public": false
}
```

---

## 🧪 Testing Scripts

The collection includes test scripts that:

1. **Auto-save tokens** after login
2. **Auto-save resource IDs** after creation
3. **Log request/response info** to console
4. **Validate response status** codes

### View Test Results

1. Click **Runner** (top right)
2. Select the collection or folder
3. Click **Run**
4. View test results in the runner

---

## 🌐 Switching Environments

### Development → Production

1. Click environment dropdown
2. Select **Filling Scheduler - Production**
3. Update `userEmail` and `userPassword`
4. Run **Login** to get production token

### Create Custom Environment

1. Click **Environments**
2. Click **+** to create new environment
3. Add all required variables
4. Select your new environment

---

## 🔍 Tips & Tricks

### 1. View Generated Code

- Click any request
- Click **Code** button (</> icon, top right)
- Select your language (Python, JavaScript, cURL, etc.)
- Copy generated code

### 2. Use Variables in Requests

Variables are referenced with `{{variableName}}`:
- URL: `{{baseUrl}}/api/v1/schedule/{{scheduleId}}`
- Headers: `Authorization: Bearer {{accessToken}}`
- Body: Use JSON editor with variable syntax

### 3. Bulk Run Requests

1. Click **Runner**
2. Select a folder (e.g., "Schedules")
3. Click **Run**
4. All requests in folder execute sequentially

### 4. Export Modified Collection

1. Right-click collection
2. Click **Export**
3. Choose format (Collection v2.1)
4. Save file

### 5. View Request History

- Click **History** tab (left sidebar)
- View all past requests
- Re-run any request by clicking it

---

## 📖 Additional Resources

- **API Documentation**: [docs/API_GUIDE.md](../docs/API_GUIDE.md)
- **OpenAPI/Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub Repository**: https://github.com/vikas-py/filling_scheduler

---

## 🐛 Troubleshooting

### Issue: "Could not validate credentials"

**Solution:**
1. Run **Login** request again
2. Verify `userEmail` and `userPassword` are correct
3. Check that token is saved in `accessToken` variable

### Issue: "Schedule not found"

**Solution:**
1. Verify `scheduleId` variable is set
2. Check that you created a schedule first
3. Confirm you're using the correct environment

### Issue: "Connection refused"

**Solution:**
1. Verify API server is running: `python -m uvicorn fillscheduler.api.main:app --reload --port 8000`
2. Check `baseUrl` in environment matches server URL
3. Test with **Health Check** request

### Issue: Variables not auto-populating

**Solution:**
1. Check test scripts are enabled (Collection → Edit → Tests)
2. View Console (bottom left) for script errors
3. Manually set variables if needed

---

## 🔄 Updating the Collection

To update the collection after API changes:

### Option 1: Re-import
1. Export modified collection (with your customizations)
2. Import new collection version
3. Merge your customizations

### Option 2: Manual Updates
1. Edit requests in Postman
2. Export modified collection
3. Replace file in repository

### Option 3: From OpenAPI Spec
```bash
# Generate from OpenAPI spec
curl http://localhost:8000/openapi.json -o openapi.json

# Use online converter or CLI tool
# https://www.postman.com/postman/workspace/postman-open-technologies/documentation/13479-e361c89c-b38e-4c81-81ea-8e39c8e8cc33
```

---

## 📝 Contributing

To contribute improvements to the collection:

1. Make changes in Postman
2. Export collection (Collection v2.1 format)
3. Replace file in `postman/` directory
4. Update this README if needed
5. Submit pull request

---

## 📄 License

This Postman collection is part of the Filling Scheduler project and is licensed under the MIT License.

---

## 💬 Support

- **Issues**: https://github.com/vikas-py/filling_scheduler/issues
- **Documentation**: See [API_GUIDE.md](../docs/API_GUIDE.md)
- **Email**: support@fillscheduler.example.com

---

**Happy Testing! 🚀**
