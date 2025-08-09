# Manual API Subdomain Setup Guide

## Issue
The deployment script failed to create the nginx configuration for `api.pinmaker.kraftysprouts.com`. This guide provides manual steps to set up the API subdomain.

## Prerequisites
- DNS A record for `api.pinmaker.kraftysprouts.com` pointing to your VPS IP
- SSH access to your VPS
- Root/sudo privileges

## Manual Setup Steps

### 1. Create Nginx Site Configuration

```bash
# SSH into your VPS
ssh pinmaker@your-vps-ip

# Create the nginx site configuration
sudo nano /etc/nginx/sites-available/api.pinmaker.kraftysprouts.com
```

### 2. Add Nginx Configuration

Paste the following configuration:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=api_conn:10m;

# Upstream backend
upstream pinmaker_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# API Subdomain Server Block
server {
    listen 80;
    server_name api.pinmaker.kraftysprouts.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate limiting
    limit_req zone=api_limit burst=20 nodelay;
    limit_conn api_conn 10;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Proxy all requests to FastAPI backend
    location / {
        proxy_pass http://pinmaker_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
```

### 3. Enable the Site

```bash
# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/api.pinmaker.kraftysprouts.com /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Check nginx status
sudo systemctl status nginx
```

### 4. Test HTTP Access

```bash
# Test that the API subdomain responds
curl -I http://api.pinmaker.kraftysprouts.com/api/v1/health

# Should return HTTP 200 response
```

### 5. Generate SSL Certificate

```bash
# Install certbot if not already installed
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Generate SSL certificate for API subdomain
sudo certbot --nginx -d api.pinmaker.kraftysprouts.com

# Follow the prompts to complete SSL setup
```

### 6. Verify HTTPS Access

```bash
# Test HTTPS access
curl -I https://api.pinmaker.kraftysprouts.com/api/v1/health

# Should return HTTP 200 with SSL
```

### 7. Update Frontend (Already Done)

The frontend is already configured to use `https://api.pinmaker.kraftysprouts.com` via the `.env.production` file.

## Verification

### Check Services
```bash
# Verify all services are running
sudo systemctl status nginx pinmaker

# Check nginx error logs if issues
sudo tail -f /var/log/nginx/error.log

# Check access logs
sudo tail -f /var/log/nginx/access.log
```

### Test API Endpoints
```bash
# Health check
curl https://api.pinmaker.kraftysprouts.com/api/v1/health

# Should return: {"status": "healthy"}
```

## Troubleshooting

### If nginx test fails:
```bash
# Check syntax errors
sudo nginx -t

# Check nginx error log
sudo tail -20 /var/log/nginx/error.log
```

### If SSL generation fails:
```bash
# Ensure HTTP works first
curl -I http://api.pinmaker.kraftysprouts.com

# Check DNS resolution
nslookup api.pinmaker.kraftysprouts.com

# Retry certbot with verbose output
sudo certbot --nginx -d api.pinmaker.kraftysprouts.com --verbose
```

### If API not responding:
```bash
# Check FastAPI service
sudo systemctl status pinmaker

# Check if port 8000 is listening
sudo netstat -tlnp | grep :8000

# Restart FastAPI if needed
sudo systemctl restart pinmaker
```

## Expected Result

After completing these steps:
- ✅ `https://api.pinmaker.kraftysprouts.com` serves your FastAPI backend
- ✅ SSL certificate is properly configured
- ✅ Frontend can connect directly to VPS API
- ✅ No more Netlify proxy issues or 504 errors
- ✅ Faster API response times

## Notes

- This creates a dedicated API subdomain separate from the main website
- The main `pinmaker.kraftysprouts.com` can still serve static content if needed
- All API traffic goes directly to your VPS, bypassing Netlify
- Rate limiting and security headers are included for protection