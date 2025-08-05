#!/bin/bash

# Pinterest Template Generator - Complete VPS Setup Script
# Domain: pinmaker.kraftysprouts.com
# User: pinmaker
# App Directory: /opt/Pinmaker/

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Please run as a regular user with sudo privileges."
fi

# Configuration
APP_USER="pinmaker"
APP_DOMAIN="pinmaker.kraftysprouts.com"
APP_DIR="/opt/Pinmaker"
APP_NAME="pinmaker"
GIT_REPO="https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"  # Update with your repo
PYTHON_VERSION="3.11"
NODE_VERSION="18"

log "Starting Pinterest Template Generator VPS Setup"
log "Domain: $APP_DOMAIN"
log "User: $APP_USER"
log "Directory: $APP_DIR"

# Update system
log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
log "Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    unzip \
    htop \
    tree \
    vim \
    nano \
    supervisor \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban \
    logrotate

# Install Python 3.11
log "Installing Python $PYTHON_VERSION..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y \
    python$PYTHON_VERSION \
    python$PYTHON_VERSION-dev \
    python$PYTHON_VERSION-venv \
    python$PYTHON_VERSION-pip \
    python3-pip

# Install system dependencies for AI libraries
log "Installing system dependencies for AI/CV libraries..."
sudo apt install -y \
    libopencv-dev \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-doc \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio

# Install font-related dependencies
log "Installing font processing dependencies..."
sudo apt install -y \
    fontconfig \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    libfontconfig1-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev

# Install image processing dependencies
log "Installing image processing dependencies..."
sudo apt install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    liblcms2-dev \
    libzstd-dev \
    libmagickwand-dev \
    imagemagick \
    libheif-dev

# Install Node.js (for frontend build)
log "Installing Node.js $NODE_VERSION..."
curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
sudo apt install -y nodejs

# Create application user if doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    log "Creating user $APP_USER..."
    sudo useradd -m -s /bin/bash $APP_USER
    sudo usermod -aG sudo $APP_USER
else
    log "User $APP_USER already exists"
fi

# Create application directory structure
log "Creating application directory structure..."
sudo mkdir -p $APP_DIR/{app,logs,uploads,templates,previews,fonts,backups}
sudo chown -R $APP_USER:$APP_USER $APP_DIR

# Switch to app user for remaining operations
log "Switching to user $APP_USER for application setup..."

# Create a script to run as the app user
cat > /tmp/user_setup.sh << 'EOF'
#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

APP_USER="pinmaker"
APP_DIR="/home/$APP_USER"
GIT_REPO="https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"  # Update with your repo
PYTHON_VERSION="3.11"

cd $APP_DIR

# Clone or update repository
if [ -d "app/.git" ]; then
    log "Updating existing repository..."
    cd app
    git pull origin main
else
    log "Cloning repository..."
    git clone $GIT_REPO app
    cd app
fi

# Create Python virtual environment
log "Creating Python virtual environment..."
python$PYTHON_VERSION -m venv venv
source venv/bin/activate

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
log "Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies and build
if [ -d "frontend" ]; then
    log "Installing frontend dependencies..."
    cd frontend
    npm install
    
    log "Building frontend..."
    npm run build
    
    # Copy build files to static directory
    log "Copying frontend build to static directory..."
    mkdir -p ../static
    cp -r dist/* ../static/
    cd ..
fi

# Create environment file
log "Creating environment configuration..."
cat > .env << 'ENVEOF'
# Pinterest Template Generator Configuration
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Domain and URLs
DOMAIN=pinmaker.kraftysprouts.com
BASE_URL=https://pinmaker.kraftysprouts.com

# File paths
UPLOADS_DIR=/opt/Pinmaker/uploads
TEMPLATES_DIR=/opt/Pinmaker/templates
PREVIEWS_DIR=/opt/Pinmaker/previews
FONTS_DIR=/opt/Pinmaker/fonts
STATIC_DIR=/opt/Pinmaker/static

# File size limits (in MB)
MAX_UPLOAD_SIZE=50
MAX_IMAGE_SIZE=20
MAX_FONT_SIZE=10

# Stock photo API keys (add your keys)
# UNSPLASH_ACCESS_KEY=your_unsplash_key
# PEXELS_API_KEY=your_pexels_key
# PIXABAY_API_KEY=your_pixabay_key

# AI Model settings
MODEL_CACHE_DIR=/opt/Pinmaker/models
USE_GPU=true
BATCH_SIZE=1

# Logging
LOG_LEVEL=INFO
LOG_FILE=/opt/Pinmaker/logs/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=pinmaker.kraftysprouts.com,localhost,127.0.0.1
CORS_ORIGINS=https://pinmaker.kraftysprouts.com

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Cache settings
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Cleanup settings
CLEANUP_INTERVAL=3600
TEMP_FILE_MAX_AGE=86400
ENVEOF

# Create directories
mkdir -p models logs

# Download AI models (if needed)
log "Setting up AI models..."
python -c "
import torch
import ultralytics
from ultralytics import YOLO
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
# Download YOLOv8 model
model = YOLO('yolov8n.pt')
print('YOLOv8 model downloaded successfully')
"

log "User setup completed successfully!"
EOF

# Make the script executable and run it as the app user
chmod +x /tmp/user_setup.sh
sudo -u $APP_USER bash /tmp/user_setup.sh

# Create systemd service
log "Creating systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=Pinterest Template Generator
After=network.target

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR/app
Environment=PATH=$APP_DIR/app/venv/bin
EnvironmentFile=$APP_DIR/app/.env
ExecStart=$APP_DIR/app/venv/bin/gunicorn main:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

[Install]
WantedBy=multi-user.target
EOF

# Create Gunicorn configuration
log "Creating Gunicorn configuration..."
sudo -u $APP_USER tee $APP_DIR/app/gunicorn.conf.py > /dev/null << 'EOF'
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 120
keepalive = 2

# Logging
accesslog = "/opt/Pinmaker/logs/access.log"
errorlog = "/opt/Pinmaker/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "pinmaker"

# Server mechanics
daemon = False
pidfile = "/opt/Pinmaker/logs/gunicorn.pid"
user = "pinmaker"
group = "pinmaker"
tmp_upload_dir = None

# SSL (handled by nginx)
keyfile = None
certfile = None

# Environment
raw_env = [
    "ENVIRONMENT=production",
]

# Worker process lifecycle
def on_starting(server):
    server.log.info("Starting Pinterest Template Generator")

def on_reload(server):
    server.log.info("Reloading Pinterest Template Generator")

def when_ready(server):
    server.log.info("Pinterest Template Generator is ready")

def on_exit(server):
    server.log.info("Shutting down Pinterest Template Generator")
EOF

# Configure Nginx
log "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << EOF
server {
    listen 80;
    server_name $APP_DOMAIN;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $APP_DOMAIN;
    
    # SSL configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/$APP_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$APP_DOMAIN/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Client max body size for file uploads
    client_max_body_size 50M;
    
    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # Static files
    location /static/ {
        alias $APP_DIR/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Uploaded files
    location /uploads/ {
        alias $APP_DIR/uploads/;
        expires 1h;
        add_header Cache-Control "public";
    }
    
    # Templates
    location /templates/ {
        alias $APP_DIR/templates/;
        expires 1h;
        add_header Cache-Control "public";
    }
    
    # Previews
    location /previews/ {
        alias $APP_DIR/previews/;
        expires 1h;
        add_header Cache-Control "public";
    }
    
    # Fonts
    location /fonts/ {
        alias $APP_DIR/fonts/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # CORS for fonts
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, OPTIONS";
        add_header Access-Control-Allow-Headers "Range";
    }
    
    # API routes
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
    
    # Main application (React frontend)
    location / {
        try_files \$uri \$uri/ @app;
    }
    
    # Fallback to app
    location @app {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ /(requirements\.txt|setup\.sh|\.env|\.git) {
        deny all;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
log "Testing Nginx configuration..."
sudo nginx -t

# Configure firewall
log "Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Configure fail2ban
log "Configuring fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
logpath = /var/log/nginx/error.log
EOF

# Create log rotation configuration
log "Configuring log rotation..."
sudo tee /etc/logrotate.d/$APP_NAME > /dev/null << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload $APP_NAME
    endscript
}
EOF

# Create backup script
log "Creating backup script..."
sudo -u $APP_USER tee $APP_DIR/backup.sh > /dev/null << 'EOF'
#!/bin/bash

# Pinterest Template Generator Backup Script

APP_DIR="/opt/Pinmaker"
BACKUP_DIR="$APP_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="pinmaker_backup_$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
tar -czf $BACKUP_DIR/$BACKUP_NAME.tar.gz \
    --exclude='$APP_DIR/app/venv' \
    --exclude='$APP_DIR/app/node_modules' \
    --exclude='$APP_DIR/app/__pycache__' \
    --exclude='$APP_DIR/app/.git' \
    --exclude='$APP_DIR/backups' \
    $APP_DIR/app \
    $APP_DIR/uploads \
    $APP_DIR/templates \
    $APP_DIR/previews \
    $APP_DIR/fonts

# Keep only last 7 backups
cd $BACKUP_DIR
ls -t pinmaker_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup completed: $BACKUP_NAME.tar.gz"
EOF

chmod +x $APP_DIR/backup.sh

# Create monitoring script
log "Creating monitoring script..."
sudo -u $APP_USER tee $APP_DIR/monitor.sh > /dev/null << 'EOF'
#!/bin/bash

# Pinterest Template Generator Monitoring Script

APP_NAME="pinmaker"
LOG_FILE="/opt/Pinmaker/logs/monitor.log"

# Function to log with timestamp
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# Check if service is running
if ! systemctl is-active --quiet $APP_NAME; then
    log_message "ERROR: $APP_NAME service is not running. Attempting to restart..."
    sudo systemctl restart $APP_NAME
    sleep 10
    if systemctl is-active --quiet $APP_NAME; then
        log_message "SUCCESS: $APP_NAME service restarted successfully"
    else
        log_message "CRITICAL: Failed to restart $APP_NAME service"
    fi
fi

# Check disk usage
DISK_USAGE=$(df /opt/Pinmaker | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    log_message "WARNING: Disk usage is ${DISK_USAGE}%"
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    log_message "WARNING: Memory usage is ${MEM_USAGE}%"
fi

# Check if application is responding
if ! curl -f -s http://localhost:8000/health > /dev/null; then
    log_message "ERROR: Application health check failed"
fi

# Clean up old temporary files
find /opt/Pinmaker/uploads -type f -mtime +1 -delete 2>/dev/null
find /opt/Pinmaker/previews -type f -mtime +7 -delete 2>/dev/null
EOF

chmod +x $APP_DIR/monitor.sh

# Add cron jobs
log "Setting up cron jobs..."
(crontab -u $APP_USER -l 2>/dev/null; echo "# Pinterest Template Generator cron jobs") | crontab -u $APP_USER -
(crontab -u $APP_USER -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | crontab -u $APP_USER -
(crontab -u $APP_USER -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/monitor.sh") | crontab -u $APP_USER -

# Start and enable services
log "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl start $APP_NAME
sudo systemctl enable nginx
sudo systemctl restart nginx
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# Wait for services to start
sleep 5

# Check service status
log "Checking service status..."
if systemctl is-active --quiet $APP_NAME; then
    log "✓ $APP_NAME service is running"
else
    error "✗ $APP_NAME service failed to start"
fi

if systemctl is-active --quiet nginx; then
    log "✓ Nginx is running"
else
    error "✗ Nginx failed to start"
fi

# Get SSL certificate
log "Obtaining SSL certificate..."
sudo certbot --nginx -d $APP_DOMAIN --non-interactive --agree-tos --email admin@$APP_DOMAIN

# Test SSL renewal
log "Testing SSL certificate renewal..."
sudo certbot renew --dry-run

# Create deployment script for updates
log "Creating deployment script..."
sudo -u $APP_USER tee $APP_DIR/deploy.sh > /dev/null << 'EOF'
#!/bin/bash

# Pinterest Template Generator Deployment Script

set -e

APP_DIR="/opt/Pinmaker"
BACKUP_DIR="/opt/Pinmaker/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Starting deployment..."

# Create backup before deployment
echo "Creating backup..."
/opt/Pinmaker/backup.sh

# Navigate to app directory
cd $APP_DIR

# Pull latest changes
echo "Pulling latest changes..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update Python dependencies
echo "Updating Python dependencies..."
pip install -r requirements.txt

# Build frontend if changed
if [ -d "frontend" ]; then
    echo "Building frontend..."
    cd frontend
    npm install
    npm run build
    cp -r dist/* ../static/
    cd ..
fi

# Restart application
echo "Restarting application..."
sudo systemctl restart pinmaker

# Wait for service to start
sleep 5

# Check if service is running
if systemctl is-active --quiet pinmaker; then
    echo "✓ Deployment successful! Application is running."
else
    echo "✗ Deployment failed! Application is not running."
    echo "Checking logs..."
    sudo journalctl -u pinmaker --no-pager -n 20
    exit 1
fi

echo "Deployment completed successfully!"
EOF

chmod +x $APP_DIR/deploy.sh

# Final status check
log "Final system status check..."
echo "==========================================="
echo "Pinterest Template Generator Setup Complete"
echo "==========================================="
echo "Domain: $APP_DOMAIN"
echo "Application Directory: $APP_DIR"
echo "User: $APP_USER"
echo ""
echo "Service Status:"
systemctl status $APP_NAME --no-pager -l
echo ""
echo "Nginx Status:"
systemctl status nginx --no-pager -l
echo ""
echo "Application URL: https://$APP_DOMAIN"
echo "Health Check: https://$APP_DOMAIN/health"
echo "API Documentation: https://$APP_DOMAIN/docs"
echo ""
echo "Log Files:"
echo "  Application: $APP_DIR/logs/app.log"
echo "  Access: $APP_DIR/logs/access.log"
echo "  Error: $APP_DIR/logs/error.log"
echo "  Monitor: $APP_DIR/logs/monitor.log"
echo ""
echo "Management Commands:"
echo "  Deploy updates: $APP_DIR/deploy.sh"
echo "  Create backup: $APP_DIR/backup.sh"
echo "  Monitor system: $APP_DIR/monitor.sh"
echo "  View logs: sudo journalctl -u $APP_NAME -f"
echo "  Restart app: sudo systemctl restart $APP_NAME"
echo ""
echo "Next Steps:"
echo "1. Update the Git repository URL in this script"
echo "2. Add your stock photo API keys to $APP_DIR/app/.env"
echo "3. Test the application at https://$APP_DOMAIN"
echo "4. Set up monitoring alerts if needed"
echo ""
log "Setup completed successfully! 🎉"

# Clean up
rm -f /tmp/user_setup.sh

exit 0