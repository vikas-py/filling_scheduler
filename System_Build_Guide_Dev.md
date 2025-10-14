# System Build Guide (Developer)

This guide provides step-by-step instructions for developers to build, run, and test the Filling Scheduler system (backend + frontend).

---

## 1. Prerequisites

- **Python**: 3.10+
- **Node.js**: 20.19+ or 22.12+ (required for Vite 7)
- **Git**: For cloning the repository
- **pip**: Python package manager

---

## 2. Clone the Repository

```bash
git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler
```

---

## 3. Backend Setup (FastAPI)

### a. Create and Activate Virtual Environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### b. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development/testing
pip install -e .  # Editable install for CLI
```

### c. Environment Configuration

- Copy `.env.example` to `.env` and update values as needed.
- Ensure all variables use the `API_` prefix (see `UBUNTU_VM_SETUP.md`).
- Example:
  ```env
  API_DATABASE_URL=sqlite:///./fillscheduler.db
  API_SECRET_KEY=your-secret-key
  API_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://192.168.56.101:5173
  ```

### d. Run Backend Server

```bash
python -m uvicorn fillscheduler.api.main:app --reload --port 8000
```

---

## 4. Frontend Setup (React + Vite)

### a. Install Node.js Dependencies

```bash
cd frontend
npm install
```

### b. Environment Configuration

- Copy `.env.example` to `.env.development` and update API URL:
  ```env
  VITE_API_URL=http://localhost:8000/api/v1
  VITE_ENABLE_WEBSOCKET=false
  ```

### c. Run Frontend Dev Server

```bash
npm run dev
```

- Access the app at: [http://localhost:5173](http://localhost:5173)

---

## 5. Running Tests

### Backend
```bash
pytest
pytest --cov  # With coverage
```

### Frontend
```bash
npm run test
npm run test:coverage
```

---

## 6. Building for Production

### Backend
- Use a production WSGI/ASGI server (e.g., gunicorn, uvicorn with workers)

### Frontend
```bash
npm run build
```
- Output in `frontend/dist/`

---

## 7. Useful Scripts & Commands

- **Backend CLI**: `fillscheduler --help`
- **Database Migrations**: `alembic upgrade head`
- **Linting**: `npm run lint` (frontend), `ruff .` (backend)
- **Formatting**: `black .` (backend)

---

## 8. Troubleshooting

- **Node.js version error**: Upgrade to Node.js 20.19+ or 22.12+
- **CORS issues**: Check `API_CORS_ORIGINS` in `.env`
- **Auth errors**: Ensure correct token key (`auth_token`) in localStorage
- **Database errors**: Verify `API_DATABASE_URL` and run migrations

---

## 9. References

- See `README.md`, `HOW_TO_RUN.md`, `UBUNTU_VM_SETUP.md`, and `docs/` for more details.
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

**For further help, see the documentation in the `docs/` folder or contact the maintainers.**
