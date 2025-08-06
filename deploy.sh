#!/bin/bash

# Pinterest Template Generator - Git Deployment Script
# This script handles automated deployment from GitHub to VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
APP_NAME="pinmaker"
DOMAIN="pinmaker.kraftysprouts.com"
GIT_REPO="https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git"  # HTTPS for password auth
GIT_BRANCH="main"
DEPLOY_LOG="/opt/Pinmaker/logs/deploy.log"
MAINTENANCE_FILE="/opt/Pinmaker/maintenance.html"

# Test configuration - set to "skip" to always skip, empty for intelligent caching, or any value to always run
TEST="smart"

# Test cache file to track last successful test run
TEST_CACHE_FILE="$APP_DIR/.test_cache"

# Ensure log directory exists
mkdir -p "$(dirname $DEPLOY_LOG)"

# Deployment functions
log_deploy() {
    echo "[$(date -Iseconds)] $1" >> "$DEPLOY_LOG"
    log "$1"
}

check_prerequisites() {
    log_deploy "Checking deployment prerequisites..."
    
    # Check if running as correct user
    if [ "$(whoami)" != "$APP_USER" ]; then
        error "This script must be run as user: $APP_USER"
        exit 1
    fi
    
    # Check if git is installed
    if ! command -v git >/dev/null 2>&1; then
        error "Git is not installed"
        exit 1
    fi
    
    # Check if node is installed
    if ! command -v node >/dev/null 2>&1; then
        error "Node.js is not installed"
        exit 1
    fi
    
    # Check if python virtual environment exists
    if [ ! -d "$APP_DIR/venv" ]; then
        error "Python virtual environment not found at $APP_DIR/venv"
        exit 1
    fi
    
    log_deploy "Prerequisites check passed"
}

enable_maintenance_mode() {
    log_deploy "Enabling maintenance mode..."
    
    # Check if we can use sudo without password
    if ! sudo -n true 2>/dev/null; then
        log_deploy "Warning: Cannot enable maintenance mode - sudo requires password"
        log_deploy "Skipping maintenance mode and proceeding with deployment..."
        return 0
    fi
    
    # Create maintenance page
    cat > "$MAINTENANCE_FILE" << 'MAINTENANCE_EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pinterest Template Generator - Maintenance</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            font-weight: 300;
        }
        
        p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            line-height: 1.6;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .eta {
            font-size: 0.9rem;
            opacity: 0.7;
            margin-top: 1rem;
        }
        
        .features {
            margin-top: 3rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            text-align: left;
        }
        
        .feature {
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        
        .feature h3 {
            font-size: 1rem;
            margin-bottom: 0.5rem;
            color: #feca57;
        }
        
        .feature p {
            font-size: 0.9rem;
            margin: 0;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📌 PinMaker</div>
        <h1>We're Updating!</h1>
        <p>We're currently deploying new features and improvements to make your Pinterest template creation experience even better.</p>
        
        <div class="spinner"></div>
        
        <p class="eta">This usually takes just a few minutes. Please check back shortly!</p>
        
        <div class="features">
            <div class="feature">
                <h3>🤖 AI-Powered Analysis</h3>
                <p>Advanced computer vision for accurate template recreation</p>
            </div>
            <div class="feature">
                <h3>🎨 Custom Fonts</h3>
                <p>Upload and use your own fonts in generated templates</p>
            </div>
            <div class="feature">
                <h3>⚡ Real-time Preview</h3>
                <p>See your templates come to life instantly</p>
            </div>
            <div class="feature">
                <h3>📱 Modern Interface</h3>
                <p>Beautiful, responsive design that works everywhere</p>
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            window.location.reload();
        }, 30000);
    </script>
</body>
</html>
MAINTENANCE_EOF
    
    # Update nginx to serve maintenance page
    sudo tee /etc/nginx/sites-available/pinmaker-maintenance > /dev/null << 'NGINX_MAINTENANCE_EOF'
server {
    listen 80;
    listen [::]:80;
    server_name pinmaker.kraftysprouts.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Serve maintenance page
    location / {
        root /opt/Pinmaker;
        try_files /maintenance.html =503;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "maintenance mode";
        add_header Content-Type text/plain;
    }
}
NGINX_MAINTENANCE_EOF
    
    # Enable maintenance site
    sudo ln -sf /etc/nginx/sites-available/pinmaker-maintenance /etc/nginx/sites-enabled/pinmaker-maintenance
    sudo rm -f /etc/nginx/sites-enabled/pinmaker
    sudo nginx -t && sudo systemctl reload nginx
    
    log_deploy "Maintenance mode enabled"
}

disable_maintenance_mode() {
    log_deploy "Disabling maintenance mode..."
    
    # Check if we can use sudo without password
    if ! sudo -n true 2>/dev/null; then
        log_deploy "Warning: Cannot disable maintenance mode - sudo requires password"
        log_deploy "Skipping maintenance mode cleanup..."
        # Still remove maintenance file if it exists
        rm -f "$MAINTENANCE_FILE"
        return 0
    fi
    
    # Restore original nginx configuration
    sudo rm -f /etc/nginx/sites-enabled/pinmaker-maintenance
    sudo ln -sf /etc/nginx/sites-available/pinmaker /etc/nginx/sites-enabled/pinmaker
    sudo nginx -t && sudo systemctl reload nginx
    
    # Remove maintenance file
    rm -f "$MAINTENANCE_FILE"
    
    log_deploy "Maintenance mode disabled"
}

# Backup functionality removed for simplified deployment

fetch_latest_code() {
    log_deploy "Fetching latest code from repository..."
    
    cd "$APP_DIR"
    
    # Stash any local changes
    if [ -n "$(git status --porcelain)" ]; then
        log_deploy "Stashing local changes..."
        git stash push -m "Auto-stash before deployment $(date -Iseconds)"
    fi
    
    # Get current commit before update
    local current_commit=$(git rev-parse HEAD)
    
    # Use git pull for private repository with token authentication
    log_deploy "Pulling latest changes from $GIT_REPO..."
    
    # Check if GitHub token is configured
    if ! git config --get credential.helper >/dev/null 2>&1; then
        log_deploy "Setting up Git credential helper for private repository..."
        git config --global credential.helper store
    fi
    
    if ! git pull origin "$GIT_BRANCH"; then
        error "Failed to pull latest changes from private repository. Please:"
        error "1. Generate a GitHub Personal Access Token at: https://github.com/settings/tokens"
        error "2. Use token as password when prompted (username: your-github-username)"
        error "3. Or configure git with: git config --global credential.helper store"
        error "4. Then run: git pull origin main (enter token when prompted)"
        return 1
    fi
    
    # Get target commit after update
    local target_commit=$(git rev-parse HEAD)
    
    if [ "$current_commit" = "$target_commit" ]; then
        log_deploy "Already up to date with origin/$GIT_BRANCH"
        return 0
    fi
    
    log_deploy "Updated from $current_commit to $target_commit"
    
    # Log changes
    log_deploy "Changes in this deployment:"
    git log --oneline "$current_commit..$target_commit" >> "$DEPLOY_LOG"
    
    log_deploy "Code updated successfully"
}

install_dependencies() {
    log_deploy "Installing/updating dependencies..."
    
    cd "$APP_DIR"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Update Python dependencies
    log_deploy "Updating Python dependencies..."
    pip install --upgrade pip
    
    # Install PyTorch with CPU support first (prevents CUDA issues)
    log_deploy "Installing PyTorch CPU version..."
    pip install torch==2.5.1+cpu torchvision==0.20.1+cpu torchaudio==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu
    
    # Install remaining dependencies
    log_deploy "Installing remaining dependencies..."
    pip install -r requirements.txt
    
    # Verify critical dependencies
    log_deploy "Verifying critical dependencies..."
    python -c "import torch; print(f'PyTorch {torch.__version__} installed successfully')" || error "PyTorch import failed"
    python -c "import easyocr; print('EasyOCR imported successfully')" || error "EasyOCR import failed"
    python -c "import fastapi; print('FastAPI imported successfully')" || error "FastAPI import failed"
    
    # Install/update Node.js dependencies for frontend
    if [ -f "frontend/package.json" ]; then
        log_deploy "Installing Node.js dependencies..."
        cd frontend
        
        # Always use npm install to ensure all dependencies are properly installed
        log_deploy "Installing all dependencies..."
        npm install
        
        # Install additional required dependencies for Vite build
        npm install vite@^5.4.0 @vitejs/plugin-react@^4.3.0 tailwindcss autoprefixer postcss @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio terser --save-dev
        
        cd ..
    fi
    
    log_deploy "Dependencies updated successfully"
}

build_frontend() {
    log_deploy "Building frontend application..."
    
    cd "$APP_DIR/frontend"
    
    # Ensure dependencies are installed
    if [ ! -d "node_modules" ] || [ ! "$(ls -A node_modules)" ]; then
        log_deploy "Node modules not found, installing dependencies..."
        npm install
    fi
    
    # Build production frontend
    npm run build
    
    # Verify build output (Vite uses 'dist' directory)
    if [ ! -d "dist" ] || [ ! "$(ls -A dist)" ]; then
        error "Frontend build failed - no dist directory or empty"
        return 1
    fi
    
    log_deploy "Frontend built successfully"
    
    # The built files are already in the correct location for nginx
    # Nginx is configured to serve from /opt/Pinmaker/app/frontend/dist
    # which matches our build output directory
    log_deploy "Frontend files are ready for nginx serving from $APP_DIR/frontend/dist"
    
    cd "$APP_DIR"
}

check_test_cache() {
    local current_commit=$(git rev-parse HEAD)
    
    # Check if test cache file exists and contains current commit
    if [ -f "$TEST_CACHE_FILE" ]; then
        local cached_commit=$(cat "$TEST_CACHE_FILE" 2>/dev/null || echo "")
        if [ "$cached_commit" = "$current_commit" ]; then
            log_deploy "Tests already passed for commit $current_commit - skipping tests"
            return 0
        else
            log_deploy "New commit detected ($current_commit vs cached $cached_commit) - tests required"
            return 1
        fi
    else
        log_deploy "No test cache found - tests required"
        return 1
    fi
}

update_test_cache() {
    local current_commit=$(git rev-parse HEAD)
    echo "$current_commit" > "$TEST_CACHE_FILE"
    log_deploy "Updated test cache with successful commit: $current_commit"
}

run_tests() {
    cd "$APP_DIR"
    
    # Skip tests completely if TEST variable is set to "skip"
    if [ "$TEST" = "skip" ]; then
        log_deploy "Skipping tests (TEST variable set to skip)"
        return 0
    fi
    
    # Use intelligent test caching for empty TEST or "smart" mode
    if [ -z "$TEST" ] || [ "$TEST" = "smart" ]; then
        if check_test_cache; then
            return 0
        fi
    fi
    
    log_deploy "Running tests..."
    
    source venv/bin/activate
    
    local test_failed=false
    
    # Run Python tests if they exist
    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
        log_deploy "Running Python tests..."
        if ! python -m pytest tests/ -v; then
            warn "Python tests failed"
            test_failed=true
        fi
    fi
    
    # Run frontend tests if they exist
    if [ -f "frontend/package.json" ] && grep -q '"test"' frontend/package.json; then
        log_deploy "Running frontend tests..."
        cd frontend
        if ! npm test -- --watchAll=false; then
            warn "Frontend tests failed"
            test_failed=true
        fi
        cd ..
    fi
    
    if [ "$test_failed" = "true" ]; then
        warn "Some tests failed, but continuing deployment"
    else
        log_deploy "All tests passed - updating test cache"
        update_test_cache
    fi
    
    log_deploy "Tests completed"
}

update_configuration() {
    log_deploy "Updating configuration..."
    
    cd "$APP_DIR"
    
    # Update environment file if template exists
    if [ -f ".env.example" ] && [ ! -f ".env" ]; then
        log_deploy "Creating .env file from template..."
        cp .env.example .env
        
        # Update with production values
        sed -i "s/DOMAIN=.*/DOMAIN=$DOMAIN/g" .env
        sed -i "s/DEBUG=.*/DEBUG=False/g" .env
        sed -i "s/ENVIRONMENT=.*/ENVIRONMENT=production/g" .env
    fi
    
    # Set proper permissions
    chmod 600 .env 2>/dev/null || true
    
    log_deploy "Configuration updated"
}

restart_services() {
    log_deploy "Restarting application services..."
    
    # Check if user has passwordless sudo for systemctl
    if ! sudo -n systemctl daemon-reload 2>/dev/null; then
        log_deploy "Warning: Cannot restart services - sudo requires password"
        log_deploy "Services will need to be restarted manually after deployment"
        log_deploy "Please run: sudo systemctl restart pinmaker nginx"
        return 0
    fi
    
    # Install/update systemd service file
    if [ -f "$APP_DIR/pinmaker.service" ]; then
        log_deploy "Installing systemd service file..."
        sudo cp "$APP_DIR/pinmaker.service" /etc/systemd/system/
        sudo systemctl enable pinmaker
    fi
    
    # Reload systemd configuration
    sudo systemctl daemon-reload
    
    # Restart application
    sudo systemctl restart pinmaker
    
    # Wait for service to start
    sleep 5
    
    # Check if service started successfully
    if ! sudo systemctl is-active --quiet pinmaker; then
        error "Failed to start pinmaker service"
        sudo systemctl status pinmaker --no-pager
        return 1
    fi
    
    # Restart nginx
    sudo systemctl restart nginx
    
    log_deploy "Services restarted successfully"
}

verify_deployment() {
    log_deploy "Verifying deployment..."
    
    # Wait for application to be ready
    sleep 10
    
    # Check health endpoint
    local health_url="http://$DOMAIN/health"
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s --max-time 10 "$health_url" >/dev/null; then
            log_deploy "Health check passed"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "Health check failed after $max_attempts attempts"
            return 1
        fi
        
        log_deploy "Health check attempt $attempt/$max_attempts failed, retrying..."
        sleep 5
        ((attempt++))
    done
    
    # Check main page
    if curl -f -s --max-time 15 "http://$DOMAIN" >/dev/null; then
        log_deploy "Main page check passed"
    else
        warn "Main page check failed, but health endpoint is working"
    fi
    
    # Check service status
    if sudo -n systemctl is-active --quiet pinmaker 2>/dev/null; then
        log_deploy "Service status check passed"
    else
        warn "Cannot check service status (sudo required), but health endpoint is working"
    fi
    
    log_deploy "Deployment verification completed successfully"
}

# Rollback functionality removed - no backups available

# Backup cleanup functionality removed

send_deployment_notification() {
    local status="$1"
    local message="$2"
    
    # Log deployment result
    log_deploy "Deployment $status: $message"
    
    # Send email notification if mail is configured
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "[$status] Pinterest Template Generator Deployment" admin@kraftysprouts.com 2>/dev/null || true
    fi
    
    # Send Slack notification if webhook is configured
    local slack_webhook=""  # Add your Slack webhook URL
    if [ -n "$slack_webhook" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$status] Pinterest Template Generator Deployment: $message\"}" \
            "$slack_webhook" >/dev/null 2>&1 || true
    fi
}

# Main deployment function
deploy() {
    local start_time=$(date +%s)
    
    log_deploy "Starting deployment of Pinterest Template Generator"
    log_deploy "Target: $DOMAIN"
    log_deploy "Branch: $GIT_BRANCH"
    log_deploy "User: $(whoami)"
    
    # Check prerequisites
    check_prerequisites
    
    # Enable maintenance mode
    enable_maintenance_mode
    
    # Deployment steps
    if fetch_latest_code && \
       install_dependencies && \
       build_frontend && \
       update_configuration && \
       run_tests && \
       restart_services && \
       verify_deployment; then
        
        # Disable maintenance mode
        disable_maintenance_mode
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_deploy "Deployment completed successfully in ${duration}s"
        send_deployment_notification "SUCCESS" "Deployment completed successfully in ${duration}s"
        
    else
        # Deployment failed
        log_deploy "Deployment failed!"
        disable_maintenance_mode
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        error "Deployment failed in ${duration}s"
        send_deployment_notification "FAILED" "Deployment failed in ${duration}s"
        
        exit 1
    fi
}

# Script commands
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    
    "rollback")
        error "Rollback functionality has been removed"
        error "To revert changes, manually reset git or redeploy previous version"
        exit 1
        ;;
    
    "status")
        echo "Pinterest Template Generator Deployment Status"
        echo "============================================="
        echo "Domain: $DOMAIN"
        echo "App Directory: $APP_DIR"
        echo "Current User: $(whoami)"
        echo ""
        
        if [ -d "$APP_DIR/.git" ]; then
            cd "$APP_DIR"
            echo "Git Status:"
            echo "  Branch: $(git branch --show-current)"
            echo "  Commit: $(git rev-parse --short HEAD)"
            echo "  Status: $(git status --porcelain | wc -l) modified files"
        fi
        echo ""
        
        echo "Service Status:"
        printf "  Pinmaker: "
        if sudo systemctl is-active --quiet pinmaker; then
            echo "✓ Running"
        else
            echo "✗ Stopped"
        fi
        
        printf "  Nginx: "
        if sudo systemctl is-active --quiet nginx; then
            echo "✓ Running"
        else
            echo "✗ Stopped"
        fi
        echo ""
        
        echo "Recent Deployments:"
        if [ -f "$DEPLOY_LOG" ]; then
            grep "Deployment completed\|Deployment failed" "$DEPLOY_LOG" | tail -5
        else
            echo "  No deployment history found"
        fi
        ;;
    
    "logs")
        if [ -f "$DEPLOY_LOG" ]; then
            tail -f "$DEPLOY_LOG"
        else
            echo "No deployment logs found"
        fi
        ;;
    
    "maintenance")
        case "$2" in
            "on")
                enable_maintenance_mode
                ;;
            "off")
                disable_maintenance_mode
                ;;
            *)
                echo "Usage: $0 maintenance [on|off]"
                exit 1
                ;;
        esac
        ;;
    
    "help")
        echo "Pinterest Template Generator Deployment Script"
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  deploy              Deploy latest code (default)"
        echo "  status              Show deployment status"
        echo "  logs                Show deployment logs"
        echo "  maintenance on|off  Enable/disable maintenance mode"
        echo ""
        echo "Examples:"
        echo "  $0 deploy"
        echo "  $0 status"
        echo "  $0 maintenance on"
        ;;
    
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

log "Deployment script completed! 🚀"