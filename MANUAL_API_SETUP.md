# Manual API Subdomain Setup Guide

## Issue
The deployment script failed to create the nginx configuration for `api.pinmaker.kraftysprouts.com`. This guide provides manual steps to set up the API subdomain.

## Prerequisites
- DNS A record for `api.pinmaker.kraftysprouts.com` pointing to your VPS IP
- SSH access to your VPS
- Root/sudo privileges

## Manual Setup Steps

### 1. Use Existing Nginx Configuration

**Good news!** The project already has the correct Nginx configuration in `nginx.conf`. The deployment script should copy this to `/etc/nginx/sites-available/api.pinmaker.kraftysprouts.com`.

If the deployment script didn't work, manually copy the existing configuration:

```bash
# SSH into your VPS
ssh pinmaker@your-vps-ip

# Copy the project's nginx.conf to the correct location
sudo cp /opt/Pinmaker/nginx.conf /etc/nginx/sites-available/api.pinmaker.kraftysprouts.com
```

The existing `nginx.conf` already contains:
- A dedicated server block for `api.pinmaker.kraftysprouts.com`
- Proper rate limiting and security headers
- Correct proxy configuration to the FastAPI backend
- Optimized settings for API responses

### 2. Enable the Site

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

### 3. Test HTTP Access

```bash
# Test that the API subdomain responds
curl -I http://api.pinmaker.kraftysprouts.com/api/v1/health

# Should return HTTP 200 response
```

### 4. Generate SSL Certificate

```bash
# Install certbot if not already installed
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Generate SSL certificate for API subdomain
sudo certbot --nginx -d api.pinmaker.kraftysprouts.com

# Follow the prompts to complete SSL setup
```

### 5. Verify HTTPS Access

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

### If Nginx Configuration Copy Fails
```bash
# Check if the source file exists
ls -la /opt/Pinmaker/nginx.conf

# Check nginx directory permissions
ls -la /etc/nginx/sites-available/

# Manual copy with verbose output
sudo cp -v /opt/Pinmaker/nginx.conf /etc/nginx/sites-available/api.pinmaker.kraftysprouts.com
```

### If Nginx Test Fails
```bash
# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Check for syntax errors in the copied config
sudo nginx -t

# Check if there are conflicting configurations
sudo nginx -T | grep -i "api.pinmaker"

# If you get "limit_req_zone 'api' is already bound" error:
# This means both old and new configs define the same zone name
# Disable the old pinmaker site first:
sudo rm /etc/nginx/sites-enabled/pinmaker
sudo nginx -t
# If test passes, reload nginx:
sudo systemctl reload nginx
```

### If SSL Certificate Generation Fails
```bash
# Check if HTTP access works first
curl -I http://api.pinmaker.kraftysprouts.com/api/v1/health

# Check certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Ensure the domain points to your server
nslookup api.pinmaker.kraftysprouts.com
```

### If Backend is Not Responding
```bash
# Check if FastAPI backend is running
sudo systemctl status pinmaker

# Check backend logs
sudo journalctl -u pinmaker -f

# Test backend directly
curl http://localhost:8000/api/v1/health
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