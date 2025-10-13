# How to Run - Filling Scheduler

Quick start guide to run the Filling Scheduler application (backend + frontend).

## Prerequisites

- **Python**: 3.9+ (3.10+ recommended)
- **Node.js**: 18+ (for frontend)
- **Git**: For cloning the repository

---

## Backend Setup (FastAPI)

### 1. Clone Repository
```bash
git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler
```

### 2. Create Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r filling_scheduler/requirements.txt
```

### 4. Run Backend Server
```bash
# From project root
python -m uvicorn fillscheduler.api.main:app --reload --port 8000
```

**Backend will be available at:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs (Swagger UI)

---

## Frontend Setup (React + Vite)

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Run Frontend Dev Server
```bash
npm run dev
```

**Frontend will be available at:** http://localhost:5173

---

## Quick Start (Both Services)

### Terminal 1 - Backend
```bash
# From project root
python -m uvicorn fillscheduler.api.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
# From project root
cd frontend
npm run dev
```

### Access Application
1. Open browser: http://localhost:5173
2. Click **Register** to create account
3. Login with your credentials
4. Start creating schedules!

---

## Running Tests

### Backend Tests
```bash
# From project root
pytest tests/ -v
```

### Frontend Tests
```bash
# From frontend directory
npm run test
```

---

## Sample Usage (CLI)

### Basic Schedule Generation
```python
# From project root
python -m filling_scheduler.main \
  --input filling_scheduler/examples/lots.csv \
  --output output/schedule.json \
  --strategy lpt \
  --num-lines 3
```

### Strategy Comparison
```bash
python -m filling_scheduler.compare_runs \
  --input filling_scheduler/examples/lots.csv \
  --num-lines 3
```

---

## Environment Variables

### Backend (.env in project root)
```bash
DATABASE_URL=sqlite:///./fillscheduler.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (frontend/.env.development)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## Troubleshooting

### Backend won't start
- **Check Python version:** `python --version` (must be 3.9+)
- **Reinstall dependencies:** `pip install -r filling_scheduler/requirements.txt --force-reinstall`
- **Delete database:** `rm fillscheduler.db` (will recreate on next run)

### Frontend won't start
- **Check Node version:** `node --version` (must be 18+)
- **Clear cache:** `rm -rf node_modules package-lock.json && npm install`
- **Check port 5173:** Make sure it's not already in use

### Database errors
```bash
# Delete and recreate database
rm fillscheduler.db
python -m uvicorn fillscheduler.api.main:app --reload --port 8000
```

### Authentication issues
- **Clear browser localStorage:** Open DevTools → Application → Local Storage → Clear All
- **Check backend is running:** http://localhost:8000/docs should load

---

## Default Login (If Database Initialized)

If you've run the backend before, you may have a test user:

- **Email:** test@example.com
- **Password:** test1234

Otherwise, register a new account via the frontend.

---

## API Testing with Postman

Import the Postman collection:

1. Open Postman
2. Import `postman/Filling_Scheduler_API.postman_collection.json`
3. Set base URL: http://localhost:8000
4. Use "Auth > Register" or "Auth > Login" to get token
5. Test all endpoints

See `postman/README.md` for detailed instructions.

---

## Production Build

### Backend
```bash
# Use production ASGI server
pip install gunicorn
gunicorn fillscheduler.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
npm run preview  # Preview production build
```

---

## Documentation

- **API Docs:** http://localhost:8000/docs (Swagger)
- **Phase Progress:** `docs/PHASE_2_PROGRESS.md`
- **Frontend README:** `frontend/README.md`
- **Postman Guide:** `postman/README.md`

---

## Support

For issues or questions:
1. Check `README.md` for detailed project information
2. Review API documentation at `/docs`
3. Check the `docs/` folder for phase-specific guides

---

**Enjoy scheduling!** 🚀
