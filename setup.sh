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

# Check if running directly as root (not via sudo)
if [[ $EUID -eq 0 && -z "$SUDO_USER" ]]; then
   error "This script should not be run directly as root. Please run as a regular user with sudo privileges."
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    error "sudo is required but not installed. Please install sudo first."
fi

# Configuration
APP_USER="pinmaker"
APP_DOMAIN="pinmaker.kraftysprouts.com"
APP_DIR="/opt/Pinmaker"
APP_NAME="pinmaker"
GIT_REPO="https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"
PYTHON_VERSION="3.12"
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

# Install Python 3.12
log "Installing Python $PYTHON_VERSION..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y \
    python$PYTHON_VERSION \
    python$PYTHON_VERSION-dev \
    python$PYTHON_VERSION-venv \
    python3-pip

# Install pip for Python 3.12 manually
log "Installing pip for Python $PYTHON_VERSION..."
wget https://bootstrap.pypa.io/get-pip.py
sudo python$PYTHON_VERSION get-pip.py --break-system-packages --no-warn-script-location --ignore-installed
rm get-pip.py

# Install system dependencies for AI libraries
log "Installing system dependencies for AI/CV libraries..."
sudo apt install -y \
    libopencv-dev \
    python3-opencv \
    libgl1-mesa-dri \
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
sudo mkdir -p $APP_DIR/{logs,uploads,templates,previews,fonts,backups,static}
sudo chown -R $APP_USER:$APP_USER $APP_DIR

# Clone repository to correct location
log "Cloning repository..."
if [ -d "$APP_DIR/.git" ]; then
    log "Repository already exists, pulling latest changes..."
    sudo -u $APP_USER git -C $APP_DIR pull origin main
else
    log "Cloning fresh repository..."
    sudo -u $APP_USER git clone $GIT_REPO $APP_DIR
fi

# Switch to app directory and setup as app user
log "Setting up application as user $APP_USER..."
sudo -u $APP_USER bash << 'EOF'
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

APP_DIR="/opt/Pinmaker"
PYTHON_VERSION="3.12"

cd $APP_DIR

# Create Python virtual environment
log "Creating Python virtual environment..."
python$PYTHON_VERSION -m venv venv
source venv/bin/activate

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install PyTorch with CPU support first
log "Installing PyTorch CPU version..."
pip install torch==2.5.1+cpu torchvision==0.20.1+cpu torchaudio==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
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
WORKERS=2

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

# AI Model settings
MODEL_CACHE_DIR=/opt/Pinmaker/models
USE_GPU=false
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

# Temp directories
TEMP=/tmp
TMPDIR=/tmp
ENVEOF

# Create directories
mkdir -p models logs

log "Application setup completed successfully!"
EOF

# Create systemd service
log "Creating systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=Pinterest Template Generator - AI-powered template creation service
After=network.target
Wants=network.target

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
WatchdogSec=60
KillMode=mixed
TimeoutStopSec=30

# Security settings
NoNewPrivileges=true
PrivateTmp=false
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=$APP_DIR /home/$APP_USER /tmp
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
log "Configuring Nginx..."
sudo cp $APP_DIR/nginx.conf /etc/nginx/sites-available/$APP_DOMAIN
sudo ln -sf /etc/nginx/sites-available/$APP_DOMAIN /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Configure firewall
log "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Configure fail2ban
log "Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Setup SSL certificate
log "Setting up SSL certificate..."
sudo certbot --nginx -d $APP_DOMAIN --non-interactive --agree-tos --email admin@$APP_DOMAIN

# Enable and start services
log "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl enable nginx
sudo systemctl restart nginx
sudo systemctl start $APP_NAME

# Wait for service to start
sleep 10

# Check service status
log "Checking service status..."
sudo systemctl status $APP_NAME --no-pager

# Test the application
log "Testing application..."
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    log "✅ Application is running successfully!"
else
    warn "⚠️ Application health check failed. Check logs with: sudo journalctl -u $APP_NAME -f"
fi

log "🎉 Setup completed successfully!"
log "Your application should be available at: https://$APP_DOMAIN"
log "To check logs: sudo journalctl -u $APP_NAME -f"
log "To restart service: sudo systemctl restart $APP_NAME"