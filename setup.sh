#!/bin/bash

# Pinmaker Server Setup Script
# This script sets up the complete Pinmaker application environment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Configuration
APP_USER="pinmaker"
APP_DIR="/opt/Pinmaker"
APP_NAME="pinmaker"
DOMAIN="pinmaker.kraftysprouts.com"
GIT_REPO="https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"
GIT_BRANCH="main"
LOG_FILE="/var/log/pinmaker_setup.log"
ERROR_LOG="/var/log/pinmaker_setup_error.log"

# Redirect output to log files
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$ERROR_LOG" >&2)

log "Starting Pinmaker server setup..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root. Use: sudo $0"
fi

# Update system packages
log "Updating system packages..."
apt update && apt upgrade -y

# Install required system packages
log "Installing system dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    nginx \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config \
    certbot \
    python3-certbot-nginx \
    nodejs \
    npm

# Create application user
log "Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash "$APP_USER"
    log "User $APP_USER created"
else
    log "User $APP_USER already exists"
fi

# Create application directory
log "Setting up application directory..."
mkdir -p "$APP_DIR"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# Switch to application user for setup
log "Switching to application user for setup..."
sudo -u "$APP_USER" bash << EOF
set -e

# Navigate to application directory
cd "$APP_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    echo "Repository exists, pulling latest changes..."
    git fetch origin
    git reset --hard origin/$GIT_BRANCH
    git clean -fd
else
    echo "Cloning repository..."
    git clone "$GIT_REPO" .
fi

# Create Python virtual environment
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
fi
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch CPU version first
echo "Installing PyTorch CPU version..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found"
fi

# Verify critical packages
echo "Verifying critical packages..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"

# Create necessary directories
echo "Creating application directories..."
mkdir -p static logs uploads temp

# Install and build frontend if it exists
if [ -d "frontend" ]; then
    echo "Setting up frontend..."
    cd frontend
    
    if [ -f "package.json" ]; then
        echo "Installing Node.js dependencies..."
        npm install
        
        echo "Building frontend..."
        npm run build
        
        # Copy build to static directory
        if [ -d "dist" ]; then
            echo "Copying frontend build to static directory..."
            cp -r dist/* ../static/
        fi
    fi
    
    cd ..
fi

# Create .env file from template
if [ -f ".env.example" ]; then
    if [ ! -f ".env" ]; then
        echo "Creating .env file from template..."
        cp .env.example .env
        
        # Update .env with production values
        sed -i 's/DEBUG=true/DEBUG=false/' .env
        sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env
        sed -i "s/DOMAIN=localhost/DOMAIN=$DOMAIN/" .env
    fi
fi

EOF

# Set up systemd service
log "Setting up systemd service..."
cat > "/etc/systemd/system/$APP_NAME.service" << EOF
[Unit]
Description=Pinmaker FastAPI Application
After=network.target

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn -c $APP_DIR/gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Set up Nginx configuration
log "Setting up Nginx configuration..."
cp "$APP_DIR/nginx.conf" "/etc/nginx/sites-available/$DOMAIN"

# Enable the site
if [ -f "/etc/nginx/sites-enabled/$DOMAIN" ]; then
    rm "/etc/nginx/sites-enabled/$DOMAIN"
fi
ln -s "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"

# Remove default Nginx site
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    rm "/etc/nginx/sites-enabled/default"
fi

# Test Nginx configuration
log "Testing Nginx configuration..."
nginx -t

# Set up SSL certificate
log "Setting up SSL certificate..."
if ! certbot certificates | grep -q "$DOMAIN"; then
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@kraftysprouts.com
else
    log "SSL certificate already exists for $DOMAIN"
fi

# Set proper permissions
log "Setting proper permissions..."
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod +x "$APP_DIR/deploy.sh"

# Enable and start services
log "Enabling and starting services..."
systemctl daemon-reload
systemctl enable "$APP_NAME"
systemctl enable nginx

systemctl restart "$APP_NAME"
systemctl restart nginx

# Verify services are running
log "Verifying services..."
if systemctl is-active --quiet "$APP_NAME"; then
    log "✅ $APP_NAME service is running"
else
    error "❌ $APP_NAME service failed to start"
fi

if systemctl is-active --quiet nginx; then
    log "✅ Nginx service is running"
else
    error "❌ Nginx service failed to start"
fi

# Test application
log "Testing application..."
sleep 5
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    log "✅ Application health check passed"
else
    warn "⚠️ Application health check failed - check logs"
fi

# Final status
log "\n=== SETUP COMPLETE ==="
info "✅ Application: $APP_NAME"
info "✅ Domain: $DOMAIN"
info "✅ Directory: $APP_DIR"
info "✅ User: $APP_USER"
info "✅ Services: $APP_NAME, nginx"
info "✅ SSL: Configured with Let's Encrypt"

log "\n=== NEXT STEPS ==="
info "1. Check application: curl https://$DOMAIN/health"
info "2. View logs: journalctl -u $APP_NAME -f"
info "3. Deploy updates: sudo -u $APP_USER $APP_DIR/deploy.sh"

log "🎉 Pinmaker setup completed successfully!"
log "Your application should be available at: https://$DOMAIN"
