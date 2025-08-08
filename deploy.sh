#!/bin/bash

# Pinmaker Deployment Script
# This script handles deployment of updates to the Pinmaker application

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$ERROR_LOG"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Configuration
APP_USER="pinmaker"
APP_DIR="/opt/Pinmaker"
APP_NAME="pinmaker"
DOMAIN="pinmaker.kraftysprouts.com"
GIT_REPO="https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"
GIT_BRANCH="main"
LOG_FILE="$APP_DIR/logs/deploy.log"
ERROR_LOG="$APP_DIR/logs/deploy_error.log"

# Ensure log directory exists
mkdir -p "$APP_DIR/logs"

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as correct user
    if [ "$(whoami)" != "$APP_USER" ]; then
        error "This script must be run as user $APP_USER. Run: sudo su - $APP_USER"
    fi
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        error "Git is not installed"
    fi
    
    # Check if we're in the right directory
    if [ "$(pwd)" != "$APP_DIR" ]; then
        error "Script must be run from $APP_DIR directory"
    fi
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed"
    fi
    
    # Check if Python virtual environment exists
    if [ ! -d "venv" ]; then
        error "Python virtual environment not found. Run setup.sh first."
    fi
    
    log "✅ Prerequisites check passed"
}

# Enable maintenance mode
enable_maintenance() {
    log "Enabling maintenance mode..."
    
    # Create maintenance page
    cat > /tmp/maintenance.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pinmaker - Under Maintenance</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .container {
            text-align: center;
            max-width: 600px;
            padding: 2rem;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .message {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }
        
        .submessage {
            font-size: 1rem;
            opacity: 0.7;
            margin-bottom: 2rem;
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .eta {
            margin-top: 1rem;
            font-size: 0.9rem;
            opacity: 0.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📌 Pinmaker</div>
        <div class="message">We're updating our service</div>
        <div class="submessage">We'll be back online shortly with exciting new features!</div>
        <div class="spinner"></div>
        <div class="eta">Estimated time: 2-3 minutes</div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            window.location.reload();
        }, 30000);
    </script>
</body>
</html>
EOF

    # Create temporary Nginx config for maintenance
    sudo tee /etc/nginx/sites-available/maintenance > /dev/null << EOF
server {
    listen 80;
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        root /tmp;
        try_files /maintenance.html =503;
    }
    
    location /health {
        return 503;
    }
}
EOF

    # Enable maintenance mode
    if sudo ln -sf /etc/nginx/sites-available/maintenance /etc/nginx/sites-enabled/pinmaker.kraftysprouts.com 2>/dev/null; then
        sudo nginx -s reload
        log "✅ Maintenance mode enabled"
    else
        warn "⚠️ Could not enable maintenance mode, continuing anyway"
    fi
}

# Disable maintenance mode
disable_maintenance() {
    log "Disabling maintenance mode..."
    
    # Restore original Nginx config
    if sudo ln -sf /etc/nginx/sites-available/pinmaker.kraftysprouts.com /etc/nginx/sites-enabled/pinmaker.kraftysprouts.com 2>/dev/null; then
        sudo nginx -s reload
        log "✅ Maintenance mode disabled"
    else
        warn "⚠️ Could not disable maintenance mode properly"
    fi
    
    # Clean up maintenance files
    sudo rm -f /tmp/maintenance.html /etc/nginx/sites-available/maintenance
}

# Fetch latest code
fetch_code() {
    log "Fetching latest code..."
    
    # Stash any local changes
    if git diff --quiet && git diff --staged --quiet; then
        log "No local changes to stash"
    else
        log "Stashing local changes..."
        git stash push -m "Auto-stash before deployment $(date)"
    fi
    
    # Handle private repository authentication
    if [ -n "$GITHUB_TOKEN" ]; then
        log "Using GitHub token for authentication"
        git remote set-url origin "https://$GITHUB_TOKEN@github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"
    fi
    
    # Fetch and reset to latest
    git fetch origin "$GIT_BRANCH"
    
    local current_commit=$(git rev-parse HEAD)
    local latest_commit=$(git rev-parse "origin/$GIT_BRANCH")
    
    if [ "$current_commit" = "$latest_commit" ]; then
        log "Already up to date (commit: ${current_commit:0:8})"
    else
        log "Updating from ${current_commit:0:8} to ${latest_commit:0:8}"
        git reset --hard "origin/$GIT_BRANCH"
        git clean -fd
        log "✅ Code updated successfully"
    fi
}

# Install/update Python dependencies
install_python_deps() {
    log "Installing/updating Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install PyTorch CPU version first
    log "Installing PyTorch CPU version..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    
    # Install/update requirements
    if [ -f "requirements.txt" ]; then
        log "Installing requirements from requirements.txt..."
        pip install -r requirements.txt
    else
        warn "requirements.txt not found"
    fi
    
    # Install Black for code formatting
    log "Installing Black code formatter..."
    pip install black
    
    # Auto-format code with Black
    log "Auto-formatting code with Black..."
    black . || warn "Black formatting failed, continuing deployment"
    
    # Verify critical libraries
    log "Verifying critical libraries..."
    python -c "import easyocr; print('✅ EasyOCR available')" || warn "⚠️ EasyOCR not available"
    python -c "import fastapi; print('✅ FastAPI available')" || error "❌ FastAPI not available"
    python -c "import uvicorn; print('✅ Uvicorn available')" || error "❌ Uvicorn not available"
    
    log "✅ Python dependencies updated"
}

# Install/update frontend dependencies and build
install_frontend_deps() {
    log "Installing/updating frontend dependencies..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        # Install dependencies
        if [ -f "package.json" ]; then
            log "Installing Node.js dependencies..."
            npm ci --production=false
            
            log "Building frontend..."
            npm run build
            
            if [ -d "dist" ]; then
                log "Copying frontend build to static directory..."
                rm -rf ../static/*
                cp -r dist/* ../static/
                log "✅ Frontend built and deployed"
            else
                error "❌ Frontend build failed - dist directory not found"
            fi
        else
            warn "⚠️ No package.json found in frontend directory"
        fi
        
        cd ..
    else
        warn "⚠️ No frontend directory found"
    fi
}

# Intelligent test caching
test_cache_key() {
    # Create cache key based on relevant files
    find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" -exec stat -c "%Y" {} \; | sort | md5sum | cut -d' ' -f1
}

# Run tests
run_tests() {
    log "Running tests..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if we can skip tests based on cache
    local cache_key=$(test_cache_key)
    local cache_file=".test_cache"
    
    if [ -f "$cache_file" ] && [ "$(cat $cache_file)" = "$cache_key" ]; then
        log "✅ Tests skipped (no changes detected)"
        return 0
    fi
    
    # Run Python tests
    if [ -f "test_main.py" ] || [ -d "tests" ]; then
        log "Running Python tests..."
        python -m pytest tests/ -v || {
            error "❌ Python tests failed"
        }
    else
        log "No Python tests found, skipping"
    fi
    
    # Run frontend tests
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        cd frontend
        if npm run test --if-present; then
            log "✅ Frontend tests passed"
        else
            warn "⚠️ Frontend tests failed or not configured"
        fi
        cd ..
    fi
    
    # Cache successful test run
    echo "$cache_key" > "$cache_file"
    log "✅ Tests completed successfully"
}

# Update configuration
update_config() {
    log "Updating configuration..."
    
    # Update .env from template if template is newer
    if [ -f ".env.template" ]; then
        if [ ! -f ".env" ] || [ ".env.template" -nt ".env" ]; then
            log "Updating .env from template..."
            
            # Backup existing .env
            if [ -f ".env" ]; then
                cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
            fi
            
            # Create new .env from template
            cp .env.template .env
            
            # Set production values
            sed -i 's/DEBUG=true/DEBUG=false/' .env
            sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env
            sed -i "s/DOMAIN=localhost/DOMAIN=$DOMAIN/" .env
            
            log "✅ Configuration updated"
        else
            log "Configuration is up to date"
        fi
    fi
}

# Restart services
restart_services() {
    log "Restarting services..."
    
    # Reload systemd daemon
    sudo systemctl daemon-reload
    
    # Restart application
    log "Restarting $APP_NAME service..."
    sudo systemctl restart "$APP_NAME"
    
    # Wait for service to start
    sleep 3
    
    # Check if service started successfully
    if sudo systemctl is-active --quiet "$APP_NAME"; then
        log "✅ $APP_NAME service restarted successfully"
    else
        error "❌ $APP_NAME service failed to start"
    fi
    
    # Restart Nginx
    log "Restarting Nginx..."
    sudo systemctl restart nginx
    
    if sudo systemctl is-active --quiet nginx; then
        log "✅ Nginx restarted successfully"
    else
        error "❌ Nginx failed to start"
    fi
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Wait for application to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log "✅ Health check passed (attempt $attempt)"
            break
        else
            if [ $attempt -eq $max_attempts ]; then
                error "❌ Health check failed after $max_attempts attempts"
            fi
            log "Health check failed, retrying in 2 seconds... (attempt $attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    # Test main page
    if curl -f -s https://pinmaker.kraftysprouts.com >/dev/null 2>&1; then
        log "✅ Main page accessible"
    else
        warn "⚠️ Main page not accessible via HTTPS"
    fi
    
    log "✅ Deployment verification completed"
}

# Send deployment notification
send_notification() {
    local status="$1"
    local message="$2"
    
    log "Sending deployment notification..."
    
    # Email notification (if configured)
    if command -v mail &> /dev/null && [ -n "$NOTIFICATION_EMAIL" ]; then
        echo "$message" | mail -s "Pinmaker Deployment $status" "$NOTIFICATION_EMAIL"
    fi
    
    # Slack notification (if configured)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"Pinmaker Deployment $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" >/dev/null 2>&1
    fi
}

# Main deployment function
deploy() {
    local start_time=$(date +%s)
    
    log "🚀 Starting deployment process..."
    
    # Run deployment steps
    check_prerequisites
    enable_maintenance
    
    # Trap to ensure maintenance mode is disabled on exit
    trap 'disable_maintenance' EXIT
    
    fetch_code
    install_python_deps
    install_frontend_deps
    update_config
    run_tests
    restart_services
    
    # Disable maintenance mode
    disable_maintenance
    trap - EXIT
    
    verify_deployment
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "🎉 Deployment completed successfully in ${duration}s"
    send_notification "SUCCESS" "Deployment completed in ${duration}s"
}

# Handle different commands
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "status")
        log "Checking application status..."
        sudo systemctl status "$APP_NAME" --no-pager
        sudo systemctl status nginx --no-pager
        ;;
    "logs")
        log "Showing recent logs..."
        sudo journalctl -u "$APP_NAME" -n 50 --no-pager
        ;;
    "maintenance")
        case "${2:-}" in
            "on")
                enable_maintenance
                ;;
            "off")
                disable_maintenance
                ;;
            *)
                echo "Usage: $0 maintenance [on|off]"
                exit 1
                ;;
        esac
        ;;
    "help")
        echo "Pinmaker Deployment Script"
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy      - Run full deployment (default)"
        echo "  status      - Show service status"
        echo "  logs        - Show recent application logs"
        echo "  maintenance - Control maintenance mode [on|off]"
        echo "  help        - Show this help message"
        ;;
    *)
        error "Unknown command: $1. Use '$0 help' for usage information."
        ;;
esac
