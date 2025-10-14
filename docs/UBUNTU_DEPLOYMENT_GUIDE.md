# Ubuntu Server Deployment Guide

**Last Updated**: October 14, 2025
**Target OS**: Ubuntu Server 20.04 LTS / 22.04 LTS / 24.04 LTS
**Status**: Production Ready

---

## 📋 Prerequisites

### System Requirements
- **Ubuntu Server**: 20.04 LTS, 22.04 LTS, or 24.04 LTS
- **RAM**: Minimum 2GB, Recommended 4GB+
- **CPU**: 2+ cores recommended
- **Storage**: 10GB+ free space
- **Python**: 3.9+ (Python 3.11 recommended)
- **Node.js**: 18+ LTS

---

## 🚀 Quick Start Installation

### Step 1: Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install System Dependencies

#### Core Dependencies
```bash
# Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Node.js and npm (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Git
sudo apt install -y git

# Build essentials
sudo apt install -y build-essential
```

#### WeasyPrint Dependencies (for PDF generation)
```bash
sudo apt install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info
```

#### Optional: PostgreSQL (recommended for production)
```bash
sudo apt install -y postgresql postgresql-contrib libpq-dev
```

---

## 📦 Application Installation

### Step 3: Clone Repository
```bash
cd /opt
sudo git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler
sudo chown -R $USER:$USER /opt/filling_scheduler
```

### Step 4: Setup Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

**Expected installation time**: 5-10 minutes (includes WeasyPrint and dependencies)

### Step 5: Setup Frontend
```bash
cd frontend

# Install Node.js dependencies
npm install

# Build for production
npm run build

cd ..
```

**Expected build time**: 2-5 minutes

---

## ⚙️ Configuration

### Step 6: Environment Variables

Create `.env` file in project root:
```bash
nano .env
```

Add the following configuration:
```bash
# Application Settings
APP_NAME="Filling Scheduler"
APP_VERSION="1.0.0"
DEBUG=false

# Security
SECRET_KEY="your-secret-key-here-change-this-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (SQLite - default)
DATABASE_URL="sqlite:///./filling_scheduler.db"

# OR PostgreSQL (production recommended)
# DATABASE_URL="postgresql://user:password@localhost/filling_scheduler"

# CORS (adjust for your domain)
CORS_ORIGINS="http://localhost:5173,http://your-domain.com,https://your-domain.com"

# Server
HOST="0.0.0.0"
PORT=8000

# Logging
LOG_LEVEL="INFO"
```

**Generate a secure SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 7: Initialize Database
```bash
source venv/bin/activate

# Run database migrations
alembic upgrade head

# Create admin user
python scripts/create_admin.py
```

Enter admin credentials when prompted:
- Username: `admin`
- Email: `admin@yourdomain.com`
- Password: (choose a strong password)

---

## 🔧 Running the Application

### Development Mode

#### Terminal 1: Backend
```bash
source venv/bin/activate
uvicorn src.fillscheduler.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Frontend Dev Server
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

Access at: `http://your-server-ip:5173`

### Production Mode with Nginx

This is the **recommended** setup for production.

---

## 🌐 Production Setup with Nginx

### Step 8: Install Nginx
```bash
sudo apt install -y nginx
```

### Step 9: Configure Systemd Service for Backend

Create service file:
```bash
sudo nano /etc/systemd/system/filling-scheduler.service
```

Add the following:
```ini
[Unit]
Description=Filling Scheduler FastAPI Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/filling_scheduler
Environment="PATH=/opt/filling_scheduler/venv/bin"
ExecStart=/opt/filling_scheduler/venv/bin/uvicorn src.fillscheduler.api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Configure permissions**:
```bash
sudo chown -R www-data:www-data /opt/filling_scheduler
sudo chmod -R 755 /opt/filling_scheduler
```

**Enable and start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable filling-scheduler
sudo systemctl start filling-scheduler
sudo systemctl status filling-scheduler
```

### Step 10: Configure Nginx

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/filling-scheduler
```

Add the following:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend - serve built React app
    root /opt/filling_scheduler/frontend/dist;
    index index.html;

    # Logs
    access_log /var/log/nginx/filling-scheduler-access.log;
    error_log /var/log/nginx/filling-scheduler-error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml+rss;

    # Frontend routes (React Router)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts (important for PDF generation)
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable the site**:
```bash
sudo ln -s /etc/nginx/sites-available/filling-scheduler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 11: Setup SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is configured by default
# Test renewal:
sudo certbot renew --dry-run
```

After SSL setup, Nginx will automatically redirect HTTP to HTTPS.

---

## 🔒 Security Hardening

### Firewall Configuration
```bash
# Install UFW
sudo apt install -y ufw

# Allow SSH (IMPORTANT: do this first!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### Secure Permissions
```bash
# Set proper ownership
sudo chown -R www-data:www-data /opt/filling_scheduler

# Secure sensitive files
chmod 600 /opt/filling_scheduler/.env
chmod 600 /opt/filling_scheduler/filling_scheduler.db
```

### Database Backup Script
```bash
sudo nano /opt/filling_scheduler/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/opt/filling_scheduler/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup SQLite database
cp /opt/filling_scheduler/filling_scheduler.db "$BACKUP_DIR/filling_scheduler_$DATE.db"

# Keep only last 30 days of backups
find $BACKUP_DIR -name "filling_scheduler_*.db" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make executable and add to cron:
```bash
chmod +x /opt/filling_scheduler/backup.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add line:
0 2 * * * /opt/filling_scheduler/backup.sh
```

---

## 📊 Monitoring & Maintenance

### View Application Logs
```bash
# Backend service logs
sudo journalctl -u filling-scheduler -f

# Nginx access logs
sudo tail -f /var/log/nginx/filling-scheduler-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/filling-scheduler-error.log
```

### Service Management Commands
```bash
# Start service
sudo systemctl start filling-scheduler

# Stop service
sudo systemctl stop filling-scheduler

# Restart service
sudo systemctl restart filling-scheduler

# Check status
sudo systemctl status filling-scheduler

# View recent logs
sudo journalctl -u filling-scheduler -n 100 --no-pager
```

### Update Application
```bash
cd /opt/filling_scheduler

# Pull latest changes
git pull origin main

# Update Python dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Rebuild frontend
cd frontend
npm install
npm run build
cd ..

# Restart service
sudo systemctl restart filling-scheduler
```

---

## 🧪 Testing the Deployment

### Test Backend API
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{"status":"healthy","version":"1.0.0"}
```

### Test PDF Generation
```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}' \
  | jq -r '.access_token')

# Create a test schedule
SCHEDULE_ID=$(curl -X POST http://localhost:8000/api/v1/schedules \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sample_schedule.json \
  | jq -r '.id')

# Download PDF
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/schedule/$SCHEDULE_ID/export?format=pdf" \
  -o test_report.pdf

# Verify PDF was created
file test_report.pdf
```

### Test Frontend
Open browser to `http://your-server-ip` or `https://your-domain.com`

---

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check service status
sudo systemctl status filling-scheduler

# Check logs
sudo journalctl -u filling-scheduler -n 50

# Common issues:
# 1. Port 8000 already in use
sudo netstat -tlnp | grep 8000

# 2. Permission issues
sudo chown -R www-data:www-data /opt/filling_scheduler

# 3. Missing dependencies
source /opt/filling_scheduler/venv/bin/activate
pip install -r /opt/filling_scheduler/requirements.txt
```

### PDF Generation Fails
```bash
# Verify WeasyPrint dependencies
dpkg -l | grep -E 'libcairo|libpango|libgdk-pixbuf'

# If missing, reinstall:
sudo apt install --reinstall \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0

# Test WeasyPrint
python3 -c "from weasyprint import HTML; print('WeasyPrint OK')"
```

### Nginx 502 Bad Gateway
```bash
# Check if backend is running
sudo systemctl status filling-scheduler

# Check backend is listening on port 8000
sudo netstat -tlnp | grep 8000

# Check Nginx error logs
sudo tail -f /var/log/nginx/filling-scheduler-error.log
```

### Database Issues
```bash
# Check database permissions
ls -la /opt/filling_scheduler/filling_scheduler.db

# Should be owned by www-data
sudo chown www-data:www-data /opt/filling_scheduler/filling_scheduler.db

# Recreate database (WARNING: deletes all data)
rm /opt/filling_scheduler/filling_scheduler.db
source /opt/filling_scheduler/venv/bin/activate
alembic upgrade head
python /opt/filling_scheduler/scripts/create_admin.py
```

---

## 📈 Performance Tuning

### Increase Worker Processes
Edit service file:
```bash
sudo nano /etc/systemd/system/filling-scheduler.service
```

Change:
```ini
ExecStart=/opt/filling_scheduler/venv/bin/uvicorn src.fillscheduler.api.main:app --host 127.0.0.1 --port 8000 --workers 4
```

To (for 4-core CPU):
```ini
ExecStart=/opt/filling_scheduler/venv/bin/uvicorn src.fillscheduler.api.main:app --host 127.0.0.1 --port 8000 --workers 8
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart filling-scheduler
```

### Enable Redis Caching (Optional)
```bash
# Install Redis
sudo apt install -y redis-server

# Add to requirements.txt
echo "redis>=5.0.0" >> requirements.txt
pip install redis

# Configure in .env
echo "REDIS_URL=redis://localhost:6379" >> .env
```

### PostgreSQL for Large Deployments
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
```

In PostgreSQL:
```sql
CREATE DATABASE filling_scheduler;
CREATE USER scheduler_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE filling_scheduler TO scheduler_user;
\q
```

Update `.env`:
```bash
DATABASE_URL="postgresql://scheduler_user:secure_password@localhost/filling_scheduler"
```

---

## 🔄 Backup & Recovery

### Full Backup
```bash
#!/bin/bash
# Save as /opt/filling_scheduler/full_backup.sh

BACKUP_DIR="/backup/filling_scheduler"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
cp /opt/filling_scheduler/filling_scheduler.db "$BACKUP_DIR/db_$DATE.db"

# Backup uploads (if any)
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" /opt/filling_scheduler/uploads/

# Backup .env
cp /opt/filling_scheduler/.env "$BACKUP_DIR/env_$DATE"

echo "Full backup completed: $DATE"
```

### Restore from Backup
```bash
# Stop service
sudo systemctl stop filling-scheduler

# Restore database
cp /backup/filling_scheduler/db_YYYYMMDD_HHMMSS.db /opt/filling_scheduler/filling_scheduler.db

# Restore uploads
tar -xzf /backup/filling_scheduler/uploads_YYYYMMDD_HHMMSS.tar.gz -C /

# Set permissions
sudo chown -R www-data:www-data /opt/filling_scheduler

# Start service
sudo systemctl start filling-scheduler
```

---

## 📞 Support & Resources

### Useful Commands Cheatsheet
```bash
# Service management
sudo systemctl status filling-scheduler
sudo systemctl restart filling-scheduler
sudo journalctl -u filling-scheduler -f

# Nginx management
sudo nginx -t
sudo systemctl restart nginx
sudo tail -f /var/log/nginx/filling-scheduler-error.log

# Application update
cd /opt/filling_scheduler && git pull && systemctl restart filling-scheduler

# Database backup
cp filling_scheduler.db backups/backup_$(date +%Y%m%d).db

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep uvicorn
```

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
- [Let's Encrypt Guide](https://certbot.eff.org/)

---

**Version**: 1.0
**Last Updated**: October 14, 2025
**Status**: Production Ready ✅
