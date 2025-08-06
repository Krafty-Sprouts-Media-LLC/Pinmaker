#!/bin/bash

# Complete Fix Script for Pinmaker Server Setup
# This script will completely fix the /opt/Pinmaker directory and set up everything properly

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
GIT_REPO="https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"
GIT_BRANCH="main"

log "Starting complete Pinmaker server fix..."

# Check if running as correct user
if [ "$(whoami)" != "$APP_USER" ]; then
    error "This script must be run as user $APP_USER. Run: sudo su - $APP_USER"
fi

# Step 1: Fix the repository issue
log "Step 1: Fixing repository setup..."

if [ -d "$APP_DIR" ]; then
    info "Checking existing directory..."
    
    # Check if it has the main.py file (indicator of proper clone)
    if [ ! -f "$APP_DIR/main.py" ]; then
        warn "Directory exists but missing application files - fixing..."
        
        # Backup any existing content
        if [ "$(ls -A $APP_DIR)" ]; then
            log "Backing up existing content..."
            sudo mv "$APP_DIR" "${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        else
            log "Directory is empty, removing..."
            sudo rm -rf "$APP_DIR"
        fi
    else
        log "Repository files found, checking git status..."
        cd "$APP_DIR"
        
        # If it's a git repo, pull latest changes
        if [ -d ".git" ]; then
            log "Updating existing repository..."
            git fetch origin
            git reset --hard origin/$GIT_BRANCH
            git clean -fd
        fi
    fi
fi

# Create/recreate directory if needed
if [ ! -d "$APP_DIR" ]; then
    log "Creating application directory..."
    sudo mkdir -p "$APP_DIR"
    sudo chown -R $APP_USER:$APP_USER "$APP_DIR"
    
    log "Cloning repository..."
    git clone "$GIT_REPO" "$APP_DIR"
    
    # Verify clone was successful
    if [ ! -f "$APP_DIR/main.py" ]; then
        error "Git clone failed - main.py not found after clone"
    fi
    
    log "✅ Repository cloned successfully"
fi

# Ensure we're in the app directory
cd "$APP_DIR"

# Step 2: Set up Python virtual environment
log "Step 2: Setting up Python virtual environment..."

if [ -d "venv" ]; then
    warn "Virtual environment exists, recreating for clean setup..."
    rm -rf venv
fi

log "Creating virtual environment..."
python3 -m venv venv

log "Activating virtual environment..."
source venv/bin/activate

# Verify virtual environment
if [ "$VIRTUAL_ENV" != "$APP_DIR/venv" ]; then
    error "Failed to activate virtual environment"
fi

log "✅ Virtual environment activated: $VIRTUAL_ENV"

# Step 3: Install Python dependencies
log "Step 3: Installing Python dependencies..."

# Upgrade pip first
log "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch CPU version first (to avoid conflicts)
log "Installing PyTorch CPU version..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
if [ -f "requirements.txt" ]; then
    log "Installing requirements from requirements.txt..."
    pip install -r requirements.txt
else
    warn "requirements.txt not found, installing essential packages..."
    pip install fastapi uvicorn gunicorn python-multipart jinja2 aiofiles
fi

# Verify critical packages
log "Verifying critical packages..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"

log "✅ Python dependencies installed"

# Step 4: Set up frontend
log "Step 4: Setting up frontend..."

if [ -d "frontend" ]; then
    cd frontend
    
    # Install Node.js dependencies
    if [ -f "package.json" ]; then
        log "Installing Node.js dependencies..."
        npm install
        
        log "Building frontend..."
        npm run build
        
        if [ ! -d "dist" ]; then
            error "Frontend build failed - dist directory not created"
        fi
        
        log "✅ Frontend built successfully"
    else
        warn "No package.json found in frontend directory"
    fi
    
    cd ..
else
    warn "No frontend directory found"
fi

# Step 5: Create necessary directories
log "Step 5: Creating necessary directories..."

mkdir -p static
mkdir -p logs
mkdir -p uploads
mkdir -p temp

# Copy frontend build to static if it exists
if [ -d "frontend/dist" ]; then
    log "Copying frontend build to static directory..."
    cp -r frontend/dist/* static/
fi

log "✅ Directories created"

# Step 6: Set up configuration
log "Step 6: Setting up configuration..."

if [ -f ".env.template" ]; then
    if [ ! -f ".env" ]; then
        log "Creating .env from template..."
        cp .env.template .env
        
        # Update .env with production values
        sed -i 's/DEBUG=true/DEBUG=false/' .env
        sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env
        sed -i 's/HOST=127.0.0.1/HOST=0.0.0.0/' .env
        sed -i 's/PORT=8000/PORT=8000/' .env
        
        log "✅ .env file configured"
    else
        log "✅ .env file already exists"
    fi
else
    warn "No .env.template found, creating basic .env..."
    cat > .env << EOF
DEBUG=false
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DOMAIN=pinmaker.kraftysprouts.com
EOF
fi

# Step 7: Set proper permissions
log "Step 7: Setting proper permissions..."

sudo chown -R $APP_USER:$APP_USER "$APP_DIR"
chmod +x deploy.sh
chmod +x setup.sh

log "✅ Permissions set"

# Step 8: Test the setup
log "Step 8: Testing the setup..."

# Test Python application
log "Testing Python application..."
python -c "import sys; sys.path.append('$APP_DIR'); import main; print('✅ Main application imports successfully')"

# Test virtual environment is working
log "Testing virtual environment..."
which python
which pip
python --version

log "✅ Setup testing completed"

# Final summary
log "\n=== SETUP COMPLETE ==="
info "✅ Repository: $(git remote get-url origin)"
info "✅ Branch: $(git branch --show-current)"
info "✅ Virtual environment: $VIRTUAL_ENV"
info "✅ Python: $(python --version)"
info "✅ Application directory: $APP_DIR"

if [ -d "frontend/dist" ]; then
    info "✅ Frontend: Built and ready"
else
    warn "⚠️  Frontend: Not built (may not be needed)"
fi

if [ -f ".env" ]; then
    info "✅ Configuration: .env file ready"
else
    warn "⚠️  Configuration: .env file missing"
fi

log "\n=== NEXT STEPS ==="
info "1. Virtual environment is activated and ready"
info "2. Run deployment: ./deploy.sh"
info "3. Check logs: tail -f logs/pinmaker.log"
info "4. Test application: curl http://localhost:8000/health"

log "\n🎉 Complete fix finished successfully!"
log "You can now run: ./deploy.sh"