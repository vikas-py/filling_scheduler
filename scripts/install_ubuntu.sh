#!/bin/bash

# Filling Scheduler - Ubuntu Server Installation Script
# Run with: sudo bash install_ubuntu.sh

set -e  # Exit on error

echo "================================================"
echo "Filling Scheduler - Ubuntu Installation Script"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get the non-root user who invoked sudo
REAL_USER=${SUDO_USER:-$USER}

echo "📦 Step 1: Updating system packages..."
apt update && apt upgrade -y

echo ""
echo "🔧 Step 2: Installing core dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    curl \
    wget

echo ""
echo "📦 Step 3: Installing Node.js 18 LTS..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
else
    echo "Node.js already installed: $(node --version)"
fi

echo ""
echo "🖨️  Step 4: Installing WeasyPrint dependencies (for PDF generation)..."
apt install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

echo ""
echo "🌐 Step 5: Installing Nginx..."
apt install -y nginx

echo ""
echo "🐍 Step 6: Setting up Python virtual environment..."
cd /opt/filling_scheduler || exit 1

# Create venv as the real user
sudo -u $REAL_USER python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📊 Step 7: Installing frontend dependencies..."
cd frontend
sudo -u $REAL_USER npm install
sudo -u $REAL_USER npm run build
cd ..

echo ""
echo "🗄️  Step 8: Setting up database..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Application Settings
APP_NAME="Filling Scheduler"
APP_VERSION="1.0.0"
DEBUG=false

# Security - CHANGE THIS IN PRODUCTION!
SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL="sqlite:///./filling_scheduler.db"

# CORS - Update with your domain
CORS_ORIGINS="http://localhost:5173,http://localhost"

# Server
HOST="0.0.0.0"
PORT=8000

# Logging
LOG_LEVEL="INFO"
EOL
    chown $REAL_USER:$REAL_USER .env
    chmod 600 .env
    echo "✅ .env file created with auto-generated SECRET_KEY"
else
    echo "⚠️  .env file already exists, skipping..."
fi

# Run database migrations
source venv/bin/activate
alembic upgrade head

echo ""
echo "👤 Step 9: Creating admin user..."
echo "You will be prompted to create an admin user."
echo "Press Enter to continue or Ctrl+C to skip..."
read -r

sudo -u $REAL_USER bash << 'EOF'
source venv/bin/activate
python scripts/create_admin.py
EOF

echo ""
echo "🔧 Step 10: Creating systemd service..."
cat > /etc/systemd/system/filling-scheduler.service << 'EOL'
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
EOL

echo ""
echo "🔒 Step 11: Setting permissions..."
chown -R www-data:www-data /opt/filling_scheduler
chmod -R 755 /opt/filling_scheduler
chmod 600 /opt/filling_scheduler/.env
[ -f /opt/filling_scheduler/filling_scheduler.db ] && chmod 600 /opt/filling_scheduler/filling_scheduler.db

echo ""
echo "🚀 Step 12: Starting service..."
systemctl daemon-reload
systemctl enable filling-scheduler
systemctl start filling-scheduler

echo ""
echo "🔥 Step 13: Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo "y" | ufw enable
    ufw status
else
    echo "⚠️  UFW not installed, skipping firewall configuration"
fi

echo ""
echo "📝 Step 14: Configuring Nginx..."

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

cat > /etc/nginx/sites-available/filling-scheduler << EOL
server {
    listen 80;
    server_name $SERVER_IP _;

    root /opt/filling_scheduler/frontend/dist;
    index index.html;

    access_log /var/log/nginx/filling-scheduler-access.log;
    error_log /var/log/nginx/filling-scheduler-error.log;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOL

# Enable site
ln -sf /etc/nginx/sites-available/filling-scheduler /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
nginx -t
systemctl restart nginx

echo ""
echo "✅ Installation Complete!"
echo ""
echo "================================================"
echo "🎉 Filling Scheduler is now running!"
echo "================================================"
echo ""
echo "📍 Access your application at:"
echo "   http://$SERVER_IP"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status filling-scheduler    # Check service status"
echo "   sudo systemctl restart filling-scheduler   # Restart service"
echo "   sudo journalctl -u filling-scheduler -f    # View logs"
echo "   sudo tail -f /var/log/nginx/filling-scheduler-error.log  # Nginx errors"
echo ""
echo "📚 Documentation:"
echo "   - Deployment Guide: /opt/filling_scheduler/docs/UBUNTU_DEPLOYMENT_GUIDE.md"
echo "   - PDF Download Guide: /opt/filling_scheduler/docs/PDF_DOWNLOAD_GUIDE.md"
echo ""
echo "🔐 Security Recommendations:"
echo "   1. Change the SECRET_KEY in /opt/filling_scheduler/.env"
echo "   2. Setup SSL certificate with: sudo certbot --nginx"
echo "   3. Update CORS_ORIGINS in .env with your domain"
echo ""
echo "⚠️  Next Steps:"
echo "   1. Test the application in your browser"
echo "   2. Log in with the admin credentials you created"
echo "   3. Review logs: sudo journalctl -u filling-scheduler -n 50"
echo ""
