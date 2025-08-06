#!/bin/bash

# Fix SSL Setup Script
# This script fixes the SSL certificate issue by setting up nginx without SSL first

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
    exit 1
}

# Configuration
DOMAIN="pinmaker.kraftysprouts.com"
APP_DIR="/opt/Pinmaker"
EMAIL="admin@kraftysprouts.com"  # Update with your email

log "🔧 Fixing SSL setup for Pinmaker..."

# Check if running as pinmaker user
if [ "$(whoami)" != "pinmaker" ]; then
    error "This script must be run as the pinmaker user"
fi

# Navigate to application directory
cd $APP_DIR

# Step 1: Remove any existing nginx configuration
log "📝 Removing existing nginx configuration..."
sudo rm -f /etc/nginx/sites-enabled/pinmaker.kraftysprouts.com
sudo rm -f /etc/nginx/sites-available/pinmaker.kraftysprouts.com

# Step 2: Install temporary nginx configuration (HTTP only)
log "🌐 Installing temporary nginx configuration (HTTP only)..."
sudo cp nginx_temp.conf /etc/nginx/sites-available/pinmaker.kraftysprouts.com
sudo ln -sf /etc/nginx/sites-available/pinmaker.kraftysprouts.com /etc/nginx/sites-enabled/

# Step 3: Test nginx configuration
log "🧪 Testing nginx configuration..."
if sudo nginx -t; then
    log "✅ Nginx configuration is valid"
else
    error "❌ Nginx configuration test failed"
fi

# Step 4: Restart nginx
log "🔄 Restarting nginx..."
sudo systemctl restart nginx

# Step 5: Check if nginx is running
if sudo systemctl is-active --quiet nginx; then
    log "✅ Nginx is running"
else
    error "❌ Nginx failed to start"
fi

# Step 6: Start the application service
log "🚀 Starting Pinmaker service..."
sudo systemctl daemon-reload
sudo systemctl enable pinmaker
sudo systemctl restart pinmaker

# Wait for service to start
sleep 5

# Step 7: Check if application is running
if sudo systemctl is-active --quiet pinmaker; then
    log "✅ Pinmaker service is running"
else
    warn "⚠️ Pinmaker service may not be running properly"
    sudo systemctl status pinmaker --no-pager -l
fi

# Step 8: Test HTTP access
log "🌐 Testing HTTP access..."
if curl -f -s http://localhost/ >/dev/null 2>&1; then
    log "✅ HTTP access is working"
else
    warn "⚠️ HTTP access test failed"
fi

# Step 9: Obtain SSL certificates
log "🔒 Obtaining SSL certificates for both $DOMAIN and www.$DOMAIN..."
if sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect; then
    log "✅ SSL certificates obtained successfully"
    
    # Step 10: Replace with full SSL configuration
    log "🔧 Installing full SSL nginx configuration..."
    sudo cp nginx.conf /etc/nginx/sites-available/pinmaker.kraftysprouts.com
    
    # Test the new configuration
    if sudo nginx -t; then
        sudo systemctl reload nginx
        log "✅ SSL configuration installed successfully"
    else
        warn "⚠️ SSL configuration test failed, keeping temporary config"
    fi
else
    warn "⚠️ SSL certificate generation failed. The site will run on HTTP only."
    log "📝 You can manually run: sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi

# Step 11: Final verification
log "🔍 Final verification..."
echo "Service status:"
sudo systemctl status pinmaker --no-pager -l
echo ""
echo "Nginx status:"
sudo systemctl status nginx --no-pager -l
echo ""
echo "Testing endpoints:"
curl -I http://localhost/health 2>/dev/null || echo "Health check failed"

log "🎉 SSL setup fix completed!"
log "📝 Next steps:"
log "   1. Check your domain DNS settings point to this server"
log "   2. Test access: http://$DOMAIN and http://www.$DOMAIN"
log "   3. If SSL was successful, test: https://$DOMAIN and https://www.$DOMAIN"
log "   4. Both www and non-www versions should redirect to https://$DOMAIN"
log "   5. Monitor logs: sudo journalctl -u pinmaker -f"