# How to Run - Filling Scheduler

Quick start guide to run the Filling Scheduler application (backend + frontend).

## TL;DR - Fastest Way to Run

**Requirements:** Python 3.10+, Node.js 20.19+/22.12+

```bash
# Terminal 1 - Backend
git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR: .\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -e .
python -m uvicorn fillscheduler.api.main:app --reload --port 8000

# Terminal 2 - Frontend (requires Node 20.19+)
cd frontend
npm install
npm run dev
```

**Access at:** http://localhost:5173

> **Important:** If you get `crypto.hash is not a function` error, upgrade Node.js to version 20.19+ or 22.12+

---

## Prerequisites

- **Python**: 3.10+ (required for backend)
- **Node.js**: 20.19+ or 22.12+ (required for Vite 7)
- **Git**: For cloning the repository

> **Note**: Vite 7 requires Node.js 20.19+ or 22.12+. If you have Node 18.x, you'll get a `crypto.hash is not a function` error.

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

### 3. Install Package in Editable Mode
```bash
# Install the package and all dependencies
pip install -e .

# OR if you also need MILP optimization support
pip install -e ".[milp]"
```

**Important:** The `-e` flag installs the package in "editable" mode, allowing Python to find the `fillscheduler` module.

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

## Expose to Local Network

Access the application from other devices on your network (phones, tablets, other computers).

### 1. Find Your IP Address

**Ubuntu/Linux:**
```bash
# Get your local IP address
hostname -I | awk '{print $1}'
# OR
ip addr show | grep "inet " | grep -v 127.0.0.1
```

**Windows (PowerShell):**
```powershell
# Get your local IP address
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"}).IPAddress
```

Example output: `192.168.1.100`

### 2. Start Backend with Host Binding

```bash
# Expose backend to all network interfaces
python -m uvicorn fillscheduler.api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be accessible at:
- **Local:** http://localhost:8000
- **Network:** http://192.168.1.100:8000 (use your actual IP)

### 3. Start Frontend with Host Binding

```bash
cd frontend
npm run dev -- --host
```

Frontend will be accessible at:
- **Local:** http://localhost:5173
- **Network:** http://192.168.1.100:5173 (use your actual IP)

### 4. Update Frontend Environment (Important!)

Edit `frontend/.env.development`:

```bash
# Change from localhost to your IP address
VITE_API_URL=http://192.168.1.100:8000
VITE_WS_URL=ws://192.168.1.100:8000
```

Then restart the frontend:
```bash
# Stop frontend (Ctrl+C), then restart
npm run dev -- --host
```

### 5. Access from Other Devices

From any device on the same network:
- **Frontend:** http://192.168.1.100:5173
- **Backend API Docs:** http://192.168.1.100:8000/docs

### Firewall Configuration (if needed)

**Ubuntu:**
```bash
# Allow incoming connections on ports 5173 and 8000
sudo ufw allow 5173/tcp
sudo ufw allow 8000/tcp
sudo ufw reload
```

**Windows:**
```powershell
# Allow Vite dev server
New-NetFirewallRule -DisplayName "Vite Dev Server" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow

# Allow FastAPI backend
New-NetFirewallRule -DisplayName "FastAPI Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### VirtualBox Network Settings (if needed)

If you're running in VirtualBox and can't access from host machine:

1. **Power off VM**
2. **VM Settings → Network**
3. **Adapter 1:** Change from "NAT" to **"Bridged Adapter"**
4. **Start VM** and repeat steps above

Your VM will get its own IP on the network (e.g., 192.168.1.101)

### Quick Test

```bash
# From another device, test if backend is reachable
curl http://192.168.1.100:8000/health

# Or open in browser:
# http://192.168.1.100:8000/docs
```

### Troubleshooting Network Access

#### Can't Access from Host Machine (VirtualBox)

**Step 1: Verify VM Network Mode**
```bash
# In VirtualBox, check your VM's network settings:
# Settings → Network → Adapter 1 → Should be "Bridged Adapter"
# (NOT "NAT" or "NAT Network")
```

**Step 2: Find VM's IP Address**
```bash
# In Ubuntu VM, run:
hostname -I | awk '{print $1}'

# OR check all network interfaces:
ip addr show

# Look for an IP like 192.168.1.xxx (same subnet as your Windows host)
```

**Step 3: Test Connectivity from VM**
```bash
# Ping your Windows host from Ubuntu VM
ping 192.168.1.x  # Use your Windows IP

# Check if services are listening on all interfaces:
sudo netstat -tlnp | grep 8000  # Should show 0.0.0.0:8000
sudo netstat -tlnp | grep 5173  # Should show 0.0.0.0:5173
```

**Step 4: Check Ubuntu Firewall**
```bash
# Check firewall status
sudo ufw status

# If active, allow the ports:
sudo ufw allow 5173/tcp
sudo ufw allow 8000/tcp
sudo ufw reload

# OR temporarily disable to test (not recommended for production):
sudo ufw disable
```

**Step 5: Test from Windows Host**
```powershell
# In Windows PowerShell, test connectivity:
Test-NetConnection -ComputerName 192.168.1.100 -Port 8000
Test-NetConnection -ComputerName 192.168.1.100 -Port 5173

# OR use curl:
curl http://192.168.1.100:8000/docs
```

**Step 6: Restart Services with Correct Binding**
```bash
# Make sure backend is bound to 0.0.0.0 (not 127.0.0.1):
python -m uvicorn fillscheduler.api.main:app --reload --host 0.0.0.0 --port 8000

# Make sure frontend is bound to 0.0.0.0:
cd frontend
npm run dev -- --host 0.0.0.0

# You should see output like:
# ➜  Network: http://192.168.1.100:5173/
```

**Step 7: Update Frontend API URL**
```bash
# Edit frontend/.env.development
# Change localhost to VM's IP:
VITE_API_URL=http://192.168.1.100:8000
VITE_WS_URL=ws://192.168.1.100:8000

# Then restart frontend:
npm run dev -- --host 0.0.0.0
```

**Common Issues:**

| Issue | Solution |
|-------|----------|
| "Connection refused" | Backend not running or not bound to 0.0.0.0 |
| "Connection timed out" | Firewall blocking or wrong network mode (use Bridged) |
| Frontend loads but API fails | Check VITE_API_URL in .env.development |
| Can ping but can't access port | Check if service is listening: `sudo netstat -tlnp` |
| VM has 10.0.x.x IP (NAT) | Change to Bridged Adapter in VirtualBox settings |

**Still Not Working?**

1. **Check if VM has correct IP:**
   ```bash
   ip addr show | grep "inet 192.168"
   ```
   Should show an IP in the same range as your Windows host (192.168.1.x)

2. **Verify Windows can reach VM:**
   ```powershell
   # From Windows
   ping 192.168.1.100
   ```

3. **Check both services are running:**
   ```bash
   # In Ubuntu VM
   ps aux | grep uvicorn    # Should show backend running
   ps aux | grep vite       # Should show frontend running
   ```

4. **Access URLs from Windows:**
   - Frontend: `http://192.168.1.100:5173`
   - Backend: `http://192.168.1.100:8000/docs`

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
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## Troubleshooting

### Backend won't start - "ModuleNotFoundError: No module named 'fillscheduler'"
**Solution:** Install the package in editable mode:
```bash
pip install -e .
```
This makes the `fillscheduler` module discoverable by Python.

### Backend won't start - Other issues
- **Check Python version:** `python --version` (must be 3.10+)
- **Reinstall package:** `pip install -e . --force-reinstall`
- **Delete database:** `rm fillscheduler.db` (will recreate on next run)

### Frontend won't start - "TypeError: crypto.hash is not a function"
**Cause:** Node.js version too old for Vite 7

**Solution:** Upgrade Node.js to 20.19+ or 22.12+

**For Ubuntu/VirtualBox Users (Recommended):**
```bash
# Remove old Node.js
sudo apt remove nodejs -y
sudo apt autoremove -y

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should show v20.x.x
```

**Alternative: Using nvm (Optional)**
```bash
# Install nvm first:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

# Then install Node 20:
nvm install 20
nvm use 20
node --version  # Should show v20.x.x
```

**After upgrading Node.js, clean and reinstall frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Frontend won't start - Other issues
- **Check Node version:** `node --version` (must be 20.19+ or 22.12+)
- **Clear cache:** `rm -rf node_modules package-lock.json && npm install`
- **Check port 5173:** Make sure it's not already in use
- **Permission issues:** Try running with `sudo` (Linux/Mac only if needed)

### Database errors
```bash
# Delete and recreate database
rm fillscheduler.db
python -m uvicorn fillscheduler.api.main:app --reload --port 8000
```

### Authentication issues
- **Clear browser localStorage:** Open DevTools → Application → Local Storage → Clear All
- **Check backend is running:** http://localhost:8000/docs should load

### Network Error on Login/Register

**Symptom:** "Network Error" or CORS error when clicking Login or Register button

**Error in Console:**
```
Access to XMLHttpRequest at 'http://192.168.56.101:8000/auth/login' from origin 'http://192.168.56.101:5173'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Root Cause:** Wrong API endpoint URL or backend not allowing CORS

**Critical Fix - Update API Endpoints:**

The backend API uses `/api/v1/` prefix but the frontend constants file is missing it!

**Fix in `frontend/src/utils/constants.ts`:**

```typescript
export const API_ENDPOINTS = {
  // Auth - ADD /api/v1 prefix
  LOGIN: '/api/v1/auth/login',        // Was: '/auth/login'
  REGISTER: '/api/v1/auth/register',  // Was: '/auth/register'
  ME: '/api/v1/auth/me',              // Was: '/auth/me'

  // Schedules - ADD /api/v1 prefix
  SCHEDULES: '/api/v1/schedules',
  // ... etc (add /api/v1 to all endpoints)
}
```

After fixing the file, restart the frontend!

**Quick Terminal Fix:**
```bash
# Navigate to frontend
cd ~/filling_scheduler/frontend

# Edit the constants file
nano src/utils/constants.ts

# Find the API_ENDPOINTS section and add '/api/v1' prefix to all endpoints
# Example: '/auth/login' -> '/api/v1/auth/login'

# Save and restart frontend
npm run dev -- --host 0.0.0.0
```

**Solution Steps:**

**1. Verify Backend is Running**
```bash
# Check if backend is running and test the correct endpoint
curl http://192.168.56.101:8000/api/v1/auth/login -X POST
# Should return: {"detail":"Method Not Allowed"} (this is okay, means endpoint exists)

# Test health endpoint
curl http://192.168.56.101:8000/health
# Should return: {"status":"healthy"}
```

**2. Check Frontend API Configuration**

If accessing frontend from **Windows host** (and backend is on Ubuntu VM):

Edit `frontend/.env.development`:
```bash
# Change from localhost to VM's actual IP (NO /api/v1 here!)
VITE_API_URL=http://192.168.56.101:8000  # Use your VM's IP
VITE_WS_URL=ws://192.168.56.101:8000
```

**Note:** Don't add `/api/v1` to VITE_API_URL - that goes in the constants.ts file!

**Important:** After changing `.env.development`, you MUST restart the frontend:
```bash
# Stop frontend (Ctrl+C)
npm run dev -- --host 0.0.0.0
```

**3. Verify API URL in Browser**

Open browser DevTools (F12) → Console tab → Try to login

Look for error like:
```
POST http://localhost:8000/api/auth/login net::ERR_CONNECTION_REFUSED
```

This means frontend is trying to reach `localhost:8000` but it should use your VM's IP.

**4. Test Backend Endpoint Directly**

From your Windows browser, visit:
```
http://192.168.1.100:8000/docs
```

If this doesn't load, the backend isn't accessible. Go back to the "Expose to Local Network" section.

**5. Check CORS Settings (if backend is accessible but login still fails)**

The backend should already have CORS configured for all origins in development. If you're still getting errors, check the backend console for CORS-related messages.

**Quick Fix Checklist:**

| Check | Command/Action | Expected Result |
|-------|---------------|-----------------|
| Backend running | `ps aux \| grep uvicorn` | Should show process |
| Backend bound to 0.0.0.0 | `sudo netstat -tlnp \| grep 8000` | Should show `0.0.0.0:8000` |
| Backend accessible | Visit `http://VM_IP:8000/docs` in Windows browser | Swagger UI loads |
| Frontend .env correct | `cat frontend/.env.development` | Shows `VITE_API_URL=http://VM_IP:8000` and `VITE_WS_URL` |
| Frontend restarted | After .env change | Must restart with Ctrl+C then `npm run dev -- --host 0.0.0.0` |

**Example: Working Configuration**

**Ubuntu VM (192.168.1.100):**
```bash
# Terminal 1 - Backend
python -m uvicorn fillscheduler.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
# Edit .env.development first!
npm run dev -- --host 0.0.0.0
```

**frontend/.env.development:**
```bash
VITE_API_URL=http://192.168.1.100:8000
VITE_WS_URL=ws://192.168.1.100:8000
```

**Windows Browser:**
```
http://192.168.1.100:5173
```

**Test Flow:**
1. Visit `http://192.168.1.100:5173` in Windows browser
2. Click "Register" or "Login"
3. Open DevTools → Network tab
4. Try to login
5. Check the POST request URL - should be `http://192.168.1.100:8000/api/auth/login`
6. If it shows `localhost:8000`, restart frontend after fixing .env

---

## Default Login (If Database Initialized)

If you've run the backend before, you may have a test user:

- **Email:** test@example.com
- **Password:** test1234

Otherwise, register a new account via the frontend.

---

## Committing Configuration Changes

After fixing the API endpoints and environment configuration, commit your changes:

```bash
# In Ubuntu VM
cd ~/filling_scheduler

# Check what changed
git status
# Should show:
#   modified:   frontend/.env.development
#   modified:   frontend/src/utils/constants.ts
#   modified:   HOW_TO_RUN.md

# Stage the frontend fixes
git add frontend/src/utils/constants.ts frontend/.env.development HOW_TO_RUN.md

# Commit with descriptive message
git commit -m "fix: Update API endpoints to include /api/v1 prefix

- Add /api/v1 prefix to all API endpoints in constants.ts
- Update .env.development with VM IP address for network access
- Fix CORS and 404 errors on login/register
- Update HOW_TO_RUN.md with troubleshooting guide"

# Push to GitHub
git push origin main
```

**Note:** If you have conflicts with changes made on Windows, handle them first:

```bash
# Check what's staged or modified
git status

# Option 1: Commit your changes first (recommended)
# Only commit constants.ts and HOW_TO_RUN.md (NOT .env.development)
git add frontend/src/utils/constants.ts HOW_TO_RUN.md
git commit -m "fix: Update API endpoints to include /api/v1 prefix"

# If you accidentally staged .env.development, unstage it:
git reset HEAD frontend/.env.development

# Now pull with rebase
git pull origin main --rebase

# If conflicts occur, resolve them in your editor, then:
git add .
git rebase --continue
git push origin main

# Option 2: Stash changes, pull, then apply
git stash
git pull origin main
git stash pop
# Resolve any conflicts, then commit and push

# Option 3: If .env.development should not be committed
# Add it to .gitignore instead (it's environment-specific)
echo "frontend/.env.development" >> .gitignore
git add .gitignore
git commit -m "chore: Ignore environment-specific .env files"
git pull origin main --rebase
git push origin main
```

**Best Practice:** The `.env.development` file should typically be in `.gitignore` since it contains environment-specific settings (like your VM's IP address). Only commit the `.env.example` template.

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
