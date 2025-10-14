# Ubuntu Server Quick Start

**For Ubuntu Server 20.04 LTS / 22.04 LTS / 24.04 LTS**

---

## 🚀 Automated Installation (Recommended)

### One-Command Install

```bash
# Clone repository
cd /opt
sudo git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler

# Run installation script
sudo bash scripts/install_ubuntu.sh
```

**What it does**:
- ✅ Installs all system dependencies (Python, Node.js, Nginx, WeasyPrint libs)
- ✅ Sets up Python virtual environment
- ✅ Installs Python packages (including PDF generation dependencies)
- ✅ Builds React frontend
- ✅ Creates systemd service
- ✅ Configures Nginx reverse proxy
- ✅ Sets up firewall rules
- ✅ Creates admin user
- ✅ Starts the application

**Installation time**: 10-15 minutes

**Access your application**: `http://your-server-ip`

---

## 📋 Manual Installation

See full step-by-step guide: [`docs/UBUNTU_DEPLOYMENT_GUIDE.md`](./UBUNTU_DEPLOYMENT_GUIDE.md)

---

## 🔒 Post-Installation Security

### 1. Setup SSL Certificate (HTTPS)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 2. Change Secret Key
```bash
sudo nano /opt/filling_scheduler/.env
# Update SECRET_KEY with a new random value
```

### 3. Update CORS Origins
```bash
sudo nano /opt/filling_scheduler/.env
# Update CORS_ORIGINS with your actual domain
CORS_ORIGINS="https://yourdomain.com"
```

### 4. Restart Service
```bash
sudo systemctl restart filling-scheduler
```

---

## 🔧 Management Commands

```bash
# Check service status
sudo systemctl status filling-scheduler

# View logs (live)
sudo journalctl -u filling-scheduler -f

# Restart service
sudo systemctl restart filling-scheduler

# Stop service
sudo systemctl stop filling-scheduler

# Start service
sudo systemctl start filling-scheduler
```

---

## 📊 Test Your Installation

### 1. Check Backend Health
```bash
curl http://localhost:8000/api/v1/health
```

Expected: `{"status":"healthy","version":"1.0.0"}`

### 2. Access Frontend
Open browser: `http://your-server-ip`

### 3. Test PDF Generation
1. Log in with admin credentials
2. Create a schedule
3. Click "PDF Report" button
4. Verify PDF downloads successfully

---

## 🐛 Troubleshooting

### Service won't start?
```bash
sudo journalctl -u filling-scheduler -n 50
```

### Nginx errors?
```bash
sudo tail -f /var/log/nginx/filling-scheduler-error.log
```

### PDF generation fails?
```bash
# Check WeasyPrint dependencies
python3 -c "from weasyprint import HTML; print('OK')"

# If error, reinstall:
sudo apt install --reinstall libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
```

---

## 📚 Full Documentation

- **Complete Deployment Guide**: [`docs/UBUNTU_DEPLOYMENT_GUIDE.md`](./UBUNTU_DEPLOYMENT_GUIDE.md)
- **PDF Download Guide**: [`docs/PDF_DOWNLOAD_GUIDE.md`](./PDF_DOWNLOAD_GUIDE.md)
- **Database Review**: [`docs/DATABASE_REVIEW.md`](./DATABASE_REVIEW.md)
- **Reporting Improvements**: [`docs/REPORTING_IMPROVEMENTS.md`](./REPORTING_IMPROVEMENTS.md)

---

## 🆘 Support

If you encounter issues:

1. Check service logs: `sudo journalctl -u filling-scheduler -f`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/filling-scheduler-error.log`
3. Verify dependencies: `source /opt/filling_scheduler/venv/bin/activate && pip list`
4. Test backend: `curl http://localhost:8000/api/v1/health`

---

**Version**: 1.0
**Status**: Production Ready ✅
