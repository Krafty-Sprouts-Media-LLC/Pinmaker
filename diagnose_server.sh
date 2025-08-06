#!/bin/bash

# Diagnostic Script for Pinmaker Server Setup
# This script will check the current state and fix any issues

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
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Configuration
APP_USER="pinmaker"
APP_DIR="/opt/Pinmaker"
GIT_REPO="https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"

log "Starting Pinmaker server diagnosis..."

# Check current user
info "Current user: $(whoami)"
info "Current directory: $(pwd)"

# Check if /opt/Pinmaker exists
if [ -d "$APP_DIR" ]; then
    log "Directory $APP_DIR exists"
    
    # Show detailed directory contents
    info "Contents of $APP_DIR:"
    ls -la "$APP_DIR"
    
    # Check if it's a git repository
    if [ -d "$APP_DIR/.git" ]; then
        log "Git repository found"
        cd "$APP_DIR"
        info "Git status:"
        git status
        info "Git remote:"
        git remote -v
    else
        warn "No git repository found in $APP_DIR"
        
        # Check if directory is empty or has only folders
        file_count=$(find "$APP_DIR" -maxdepth 1 -type f | wc -l)
        dir_count=$(find "$APP_DIR" -maxdepth 1 -type d | wc -l)
        
        info "Files in root: $file_count"
        info "Directories in root: $dir_count"
        
        if [ "$file_count" -eq 0 ]; then
            warn "No files found in $APP_DIR - this explains the issue!"
            
            # Check if we're the right user to fix this
            if [ "$(whoami)" = "$APP_USER" ]; then
                log "Attempting to fix by cloning repository..."
                
                # Remove existing directory and recreate
                cd /opt
                sudo rm -rf Pinmaker
                sudo mkdir -p Pinmaker
                sudo chown -R $APP_USER:$APP_USER Pinmaker
                
                # Clone repository
                log "Cloning repository..."
                git clone "$GIT_REPO" Pinmaker
                
                # Verify clone
                if [ -f "$APP_DIR/main.py" ]; then
                    log "✅ Repository cloned successfully!"
                    info "New contents of $APP_DIR:"
                    ls -la "$APP_DIR"
                else
                    error "❌ Repository clone failed"
                fi
            else
                error "Need to run as user $APP_USER to fix this issue"
                info "Run: sudo su - $APP_USER"
                info "Then run this script again"
            fi
        fi
    fi
else
    error "Directory $APP_DIR does not exist!"
    
    if [ "$(whoami)" = "$APP_USER" ]; then
        log "Creating directory and cloning repository..."
        sudo mkdir -p "$APP_DIR"
        sudo chown -R $APP_USER:$APP_USER "$APP_DIR"
        git clone "$GIT_REPO" "$APP_DIR"
    else
        error "Need to run as user $APP_USER to create directory"
    fi
fi

# Check for required files
log "Checking for required files..."
required_files=("main.py" "requirements.txt" "gunicorn.conf.py" "nginx.conf" "setup.sh" "deploy.sh")

for file in "${required_files[@]}"; do
    if [ -f "$APP_DIR/$file" ]; then
        info "✅ $file found"
    else
        warn "❌ $file missing"
    fi
done

# Check for virtual environment
if [ -d "$APP_DIR/venv" ]; then
    log "✅ Virtual environment found"
    
    # Test virtual environment
    if [ -f "$APP_DIR/venv/bin/activate" ]; then
        info "Virtual environment appears to be properly set up"
    else
        warn "Virtual environment directory exists but activate script missing"
    fi
else
    warn "❌ Virtual environment not found - this needs to be created"
fi

# Check for frontend build
if [ -d "$APP_DIR/frontend" ]; then
    log "✅ Frontend directory found"
    
    if [ -d "$APP_DIR/frontend/dist" ]; then
        info "✅ Frontend build directory found"
    else
        warn "❌ Frontend not built yet"
    fi
else
    warn "❌ Frontend directory missing"
fi

# Check for static directory
if [ -d "$APP_DIR/static" ]; then
    log "✅ Static directory found"
    static_files=$(find "$APP_DIR/static" -type f | wc -l)
    info "Static files count: $static_files"
else
    warn "❌ Static directory missing"
fi

# Summary and recommendations
log "\n=== DIAGNOSIS SUMMARY ==="

if [ ! -f "$APP_DIR/main.py" ]; then
    error "CRITICAL: Repository files are missing!"
    info "SOLUTION: The git clone failed. You need to:"
    info "1. Remove the empty directory: sudo rm -rf $APP_DIR"
    info "2. Create it fresh: sudo mkdir -p $APP_DIR && sudo chown -R $APP_USER:$APP_USER $APP_DIR"
    info "3. Clone repository: git clone $GIT_REPO $APP_DIR"
else
    log "Repository files are present"
fi

if [ ! -d "$APP_DIR/venv" ]; then
    warn "Virtual environment needs to be created"
    info "SOLUTION: Run the fix_setup.sh script"
fi

if [ ! -d "$APP_DIR/static" ] || [ ! -d "$APP_DIR/frontend/dist" ]; then
    warn "Frontend needs to be built"
    info "SOLUTION: This will be handled by the fix_setup.sh script"
fi

log "\n=== NEXT STEPS ==="
info "1. If repository files are missing, fix the git clone first"
info "2. Run the fix_setup.sh script to create virtual environment"
info "3. Activate virtual environment: source $APP_DIR/venv/bin/activate"
info "4. Run deploy script: $APP_DIR/deploy.sh"

log "Diagnosis completed!"
