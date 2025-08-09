#!/bin/bash

# Caddy Deployment Script for Pinmaker API
# This script replaces Nginx with Caddy for automatic HTTPS

set -e

echo "🚀 Starting Caddy deployment for Pinmaker API..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons."
   print_status "Please run as a regular user with sudo privileges."
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    print_error "sudo is required but not installed."
    exit 1
fi

print_status "Checking system requirements..."

# Update system packages
print_status "Updating system packages..."
sudo apt update

# Install required packages
print_status "Installing required packages..."
sudo apt install -y curl wget debian-keyring debian-archive-keyring apt-transport-https

# Stop and disable Nginx if it's running
print_status "Checking for existing Nginx installation..."
if systemctl is-active --quiet nginx; then
    print_warning "Nginx is running. Stopping and disabling it..."
    sudo systemctl stop nginx
    sudo systemctl disable nginx
    print_success "Nginx stopped and disabled"
else
    print_status "Nginx is not running"
fi

# Install Caddy
print_status "Installing Caddy..."

# Add Caddy's official repository
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list

# Update package list and install Caddy
sudo apt update
sudo apt install -y caddy

print_success "Caddy installed successfully"

# Create necessary directories
print_status "Creating necessary directories..."
sudo mkdir -p /var/log/caddy
sudo mkdir -p /etc/caddy
sudo mkdir -p /var/lib/caddy

# Set proper permissions
sudo chown -R caddy:caddy /var/log/caddy
sudo chown -R caddy:caddy /var/lib/caddy
sudo chmod 755 /var/log/caddy
sudo chmod 755 /var/lib/caddy

# Copy Caddyfile to the system
print_status "Installing Caddyfile..."
if [ -f "./Caddyfile" ]; then
    sudo cp ./Caddyfile /etc/caddy/Caddyfile
    sudo chown caddy:caddy /etc/caddy/Caddyfile
    sudo chmod 644 /etc/caddy/Caddyfile
    print_success "Caddyfile installed"
else
    print_error "Caddyfile not found in current directory"
    exit 1
fi

# Validate Caddyfile
print_status "Validating Caddyfile configuration..."
if sudo caddy validate --config /etc/caddy/Caddyfile; then
    print_success "Caddyfile configuration is valid"
else
    print_error "Caddyfile configuration is invalid"
    exit 1
fi

# Create systemd service override for better logging
print_status "Configuring Caddy service..."
sudo mkdir -p /etc/systemd/system/caddy.service.d
sudo tee /etc/systemd/system/caddy.service.d/override.conf > /dev/null <<EOF
[Service]
# Override to ensure proper logging
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/Caddyfile
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/Caddyfile

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectHome=yes
ProtectSystem=strict
ReadWritePaths=/var/lib/caddy /var/log/caddy

# Resource limits
LimitNOFILE=1048576
LimitNPROC=1048576
EOF

# Reload systemd and enable Caddy
print_status "Enabling Caddy service..."
sudo systemctl daemon-reload
sudo systemctl enable caddy

# Check if FastAPI backend is running
print_status "Checking FastAPI backend status..."
if pgrep -f "uvicorn\|gunicorn" > /dev/null; then
    print_success "FastAPI backend is running"
else
    print_warning "FastAPI backend is not running. Starting it..."
    
    # Try to start the backend
    if [ -f "./main.py" ]; then
        print_status "Starting FastAPI with uvicorn..."
        nohup python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 > /var/log/fastapi.log 2>&1 &
        sleep 3
        
        if pgrep -f "uvicorn" > /dev/null; then
            print_success "FastAPI backend started"
        else
            print_error "Failed to start FastAPI backend"
            print_status "Check /var/log/fastapi.log for errors"
        fi
    else
        print_error "main.py not found. Please ensure FastAPI app is available"
    fi
fi

# Start Caddy
print_status "Starting Caddy..."
sudo systemctl start caddy

# Wait a moment for Caddy to start
sleep 3

# Check Caddy status
if sudo systemctl is-active --quiet caddy; then
    print_success "Caddy is running successfully"
else
    print_error "Caddy failed to start"
    print_status "Checking Caddy logs..."
    sudo journalctl -u caddy --no-pager --lines=20
    exit 1
fi

# Test configuration
print_status "Testing Caddy configuration..."
sudo caddy validate --config /etc/caddy/Caddyfile

# Check if ports are open
print_status "Checking port availability..."
if sudo netstat -tlnp | grep -q ":80 "; then
    print_success "Port 80 is open"
else
    print_warning "Port 80 is not open"
fi

if sudo netstat -tlnp | grep -q ":443 "; then
    print_success "Port 443 is open"
else
    print_warning "Port 443 is not open"
fi

# Setup log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/caddy > /dev/null <<EOF
/var/log/caddy/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 caddy caddy
    postrotate
        systemctl reload caddy
    endscript
}
EOF

print_success "Log rotation configured"

# Create a simple health check script
print_status "Creating health check script..."
sudo tee /usr/local/bin/caddy-health-check.sh > /dev/null <<'EOF'
#!/bin/bash

# Simple health check for Caddy and FastAPI
echo "=== Caddy Health Check ==="
echo "Date: $(date)"
echo

# Check Caddy status
echo "Caddy Status:"
systemctl is-active caddy
echo

# Check if Caddy is listening on ports
echo "Port Status:"
netstat -tlnp | grep -E ":(80|443) " || echo "Ports 80/443 not listening"
echo

# Check FastAPI backend
echo "FastAPI Backend:"
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "FastAPI backend is responding"
else
    echo "FastAPI backend is not responding"
fi
echo

# Check certificate status (if available)
echo "Certificate Status:"
if [ -d "/var/lib/caddy/.local/share/caddy/certificates" ]; then
    find /var/lib/caddy/.local/share/caddy/certificates -name "*.crt" -exec echo "Found certificate: {}" \;
else
    echo "No certificates found yet (normal for first run)"
fi
EOF

sudo chmod +x /usr/local/bin/caddy-health-check.sh

print_success "Health check script created at /usr/local/bin/caddy-health-check.sh"

# Final status check
print_status "Running final health check..."
sudo /usr/local/bin/caddy-health-check.sh

echo
print_success "🎉 Caddy deployment completed successfully!"
echo
echo "📋 Caddy Configuration Features:"
echo "  ✅ Automatic HTTPS for both domains"
echo "  ✅ Security headers (enhanced from Nginx config)"
echo "  ✅ Gzip compression for better performance"
echo "  ✅ Request size limits for uploads (50MB)"
echo "  ✅ Proper logging with rotation"
echo "  ✅ HTTP/2 and HTTP/3 support by default"
echo
print_status "Next steps:"
echo "1. Ensure your DNS records point to this server"
echo "2. Wait a few minutes for SSL certificates to be automatically provisioned"
echo "3. Test your API endpoints:"
echo "   - https://api.pinmaker.kraftysprouts.com/api/v1/health"
echo "   - https://pinmaker.kraftysprouts.com/api/v1/health"
echo "4. Monitor logs with: sudo journalctl -u caddy -f"
echo "5. Run health checks with: sudo /usr/local/bin/caddy-health-check.sh"
echo
print_warning "Note: SSL certificates may take a few minutes to provision on first run"
print_status "Caddy will automatically handle certificate renewal"

echo
print_success "Deployment complete! 🚀"