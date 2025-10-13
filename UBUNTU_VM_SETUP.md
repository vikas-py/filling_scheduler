# Ubuntu VM Setup Instructions

Quick guide to get the Filling Scheduler running on your Ubuntu VirtualBox VM.

## Current Status
- ✅ Frontend API endpoints fixed (constants.ts has /api/v1 prefix)
- ✅ Backend .env file format corrected on Windows
- ❌ Need to pull changes and restart services on Ubuntu VM

---

## Step-by-Step Setup on Ubuntu VM

### 1. Pull Latest Changes
```bash
cd ~/filling_scheduler
git pull origin main
```

### 2. Verify Files Updated

**Check .env file format:**
```bash
cat .env
```

Should show:
```
# Database
DATABASE_URL=sqlite:///./fillscheduler.db

# JWT Authentication
SECRET_KEY=your-secret-key-change-this-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Comma-separated list (no quotes, no brackets)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://192.168.56.101:5173
```

**Check constants.ts has /api/v1 prefix:**
```bash
grep -A 5 "API_ENDPOINTS" frontend/src/utils/constants.ts
```

Should show `/api/v1/auth/login`, `/api/v1/auth/register`, etc.

**Check .env.development has your VM IP:**
```bash
cat frontend/.env.development
```

Should show:
```
VITE_API_URL=http://192.168.56.101:8000
VITE_WS_URL=ws://192.168.56.101:8000
```

### 3. Start Backend

**Terminal 1 - Backend:**
```bash
cd ~/filling_scheduler

# Activate virtual environment
source venv/bin/activate

# Start backend on all interfaces
python -m uvicorn fillscheduler.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4. Start Frontend

**Terminal 2 - Frontend:**
```bash
cd ~/filling_scheduler/frontend

# Start frontend on all interfaces
npm run dev -- --host 0.0.0.0
```

**Expected output:**
```
VITE v7.1.9  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.56.101:5173/
➜  press h + enter to show help
```

### 5. Test from Windows Browser

**Open:** http://192.168.56.101:5173

**Test flow:**
1. Click "Register"
2. Create an account (email + password)
3. Should auto-login after registration
4. Check DevTools Console - should see no CORS errors
5. Try logging out and logging back in

---

## If You Get Errors

### Error: "ModuleNotFoundError: No module named 'fillscheduler'"
**Solution:**
```bash
cd ~/filling_scheduler
pip install -e .
```

### Error: "CORS policy" or "No 'Access-Control-Allow-Origin'"
**Check backend is running with correct CORS:**
```bash
# Verify .env has correct format (no brackets, no quotes)
cat .env | grep CORS

# Should show: CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://192.168.56.101:5173
```

**Restart backend after fixing .env**

### Error: "ValidationError: Extra inputs are not permitted"
**Your .env file has wrong format. Recreate it:**
```bash
cd ~/filling_scheduler

cat > .env << 'EOF'
# Database
DATABASE_URL=sqlite:///./fillscheduler.db

# JWT Authentication
SECRET_KEY=your-secret-key-change-this-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Comma-separated list (no quotes, no brackets)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://192.168.56.101:5173
EOF
```

### Error: "crypto.hash is not a function"
**Node.js version too old. Upgrade to Node 20:**
```bash
# Remove old Node
sudo apt remove nodejs -y
sudo apt autoremove -y

# Install Node 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version  # Should show v20.x.x

# Reinstall frontend dependencies
cd ~/filling_scheduler/frontend
rm -rf node_modules package-lock.json
npm install
```

### Error: Can't access from Windows
**Check VirtualBox network settings:**
1. Power off VM
2. VirtualBox → VM Settings → Network
3. Adapter 1 → Change to "Bridged Adapter"
4. Start VM
5. Verify IP: `hostname -I | awk '{print $1}'`
6. Update frontend/.env.development with new IP if changed
7. Restart frontend

---

## Quick Commands Reference

### Backend (Terminal 1)
```bash
cd ~/filling_scheduler
source venv/bin/activate
python -m uvicorn fillscheduler.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Terminal 2)
```bash
cd ~/filling_scheduler/frontend
npm run dev -- --host 0.0.0.0
```

### Check if services are running
```bash
# Backend
ps aux | grep uvicorn

# Frontend
ps aux | grep vite

# Ports listening
sudo netstat -tlnp | grep -E '8000|5173'
```

### Test backend endpoint
```bash
# Health check
curl http://192.168.56.101:8000/health

# API docs (open in browser)
# http://192.168.56.101:8000/docs
```

---

## Success Criteria

✅ Backend starts without errors
✅ Frontend starts and shows Network URL
✅ Can access http://192.168.56.101:5173 from Windows
✅ Can register new account
✅ Can login
✅ No CORS errors in DevTools Console
✅ API requests go to http://192.168.56.101:8000/api/v1/auth/login

---

## Files Summary

**Fixed on Windows (already committed and pushed):**
- ✅ `.env` - CORS format corrected
- ✅ `frontend/src/utils/constants.ts` - API endpoints have /api/v1 prefix
- ✅ `HOW_TO_RUN.md` - Complete troubleshooting guide

**Need to be set on Ubuntu (environment-specific):**
- ⚠️ `frontend/.env.development` - Contains your VM IP (192.168.56.101:8000)
- ⚠️ This file may differ per environment

---

**Last updated:** 2025-10-13
**Your VM IP:** 192.168.56.101
**Access URLs:**
- Frontend: http://192.168.56.101:5173
- Backend: http://192.168.56.101:8000
- API Docs: http://192.168.56.101:8000/docs
