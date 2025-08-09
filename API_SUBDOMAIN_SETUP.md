# API Subdomain Setup Guide

This guide explains how to implement direct VPS API communication using a dedicated subdomain, eliminating Netlify proxy and 504 timeout errors.

## Overview

The solution creates a direct connection between your Netlify frontend and VPS backend using:
- **Frontend**: Served from `pinmaker.kraftysprouts.com` (via Netlify)
- **API**: Accessible at `api.pinmaker.kraftysprouts.com` (direct to VPS)

## Implementation Steps

### 1. DNS Configuration (REQUIRED)

You need to create a new DNS record in your domain provider's control panel:

```
Type: A Record
Name: api
Value: [Your VPS IP Address]
TTL: 300 (or default)
```

This creates `api.pinmaker.kraftysprouts.com` pointing directly to your VPS.

**Important**: Do NOT route this through Netlify or any CDN - it must point directly to your VPS IP.

### 2. SSL Certificate Setup (VPS)

On your VPS, you'll need to obtain an SSL certificate for the new subdomain:

```bash
# Install certbot if not already installed
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate for the API subdomain
sudo certbot --nginx -d api.pinmaker.kraftysprouts.com

# Verify certificate
sudo certbot certificates
```

### 3. Nginx Configuration (VPS)

**IMPORTANT**: The nginx.conf file has been updated with the API subdomain configuration. You need to deploy this to your VPS.

**Step 1: Deploy Updated Nginx Configuration**
```bash
# On your VPS, backup current config
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Copy the updated nginx.conf from your repository
# (This will be deployed automatically via GitHub Actions)
# Or manually copy the updated configuration
```

**Step 2: Test and Reload Nginx**
```bash
# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Check nginx status
sudo systemctl status nginx
```

**Step 3: Verify API Subdomain is Accessible**
```bash
# Test that the subdomain responds (before SSL)
curl -I http://api.pinmaker.kraftysprouts.com/api/v1/health

# Should return HTTP 200 response
```

## Changes Made to Codebase

### Frontend Configuration
- Updated `frontend/.env.production` to use `https://api.pinmaker.kraftysprouts.com`
- Removed port 8000 specification (handled by Nginx)
- API calls now go directly to the subdomain

### Backend Configuration
- Added `api.pinmaker.kraftysprouts.com` to TrustedHostMiddleware
- CORS already configured for both Netlify domains
- FastAPI will handle requests from the new subdomain

## Testing the Setup

### 1. DNS Propagation
```bash
# Check DNS resolution
nslookup api.pinmaker.kraftysprouts.com
dig api.pinmaker.kraftysprouts.com
```

### 2. SSL Certificate
```bash
# Test SSL
curl -I https://api.pinmaker.kraftysprouts.com/api/v1/health
```

### 3. API Connectivity
```bash
# Test health endpoint
curl https://api.pinmaker.kraftysprouts.com/api/v1/health

# Should return: {"status": "healthy", "timestamp": "..."}
```

### 4. CORS Configuration
```bash
# Test CORS from Netlify domain
curl -H "Origin: https://pinmaker.kraftysprouts.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://api.pinmaker.kraftysprouts.com/api/v1/analyze
```

## Deployment Steps

### 1. Deploy Backend Changes
```bash
# Commit and push changes
git add .
git commit -m "Add API subdomain support to TrustedHostMiddleware"
git push origin main

# Changes will be deployed via GitHub Actions
```

### 2. Deploy Frontend Changes
```bash
# Frontend changes are already committed
# Netlify will automatically rebuild with new API URL
```

### 3. Configure DNS
- Add the A record in your domain provider's control panel
- Wait for DNS propagation (usually 5-15 minutes)

### 4. Setup SSL on VPS
- Run the certbot commands above
- Configure Nginx for the new subdomain

## Expected Results

✅ **Frontend**: Loads from `https://pinmaker.kraftysprouts.com` (Netlify)
✅ **API**: Accessible at `https://api.pinmaker.kraftysprouts.com` (direct VPS)
✅ **No 504 errors**: Direct connection bypasses Netlify timeouts
✅ **CORS working**: Both domains allowed in backend
✅ **SSL secured**: HTTPS for all communications

## Troubleshooting

### DNS Issues
- Verify A record points to correct VPS IP
- Check DNS propagation with online tools
- Ensure no CDN/proxy is interfering

### SSL Issues
- Verify certbot obtained certificate successfully
- Check Nginx configuration syntax
- Ensure firewall allows HTTPS (port 443)

### CORS Issues
- Verify both domains in FastAPI CORS configuration
- Check browser developer tools for specific errors
- Test with curl to isolate frontend vs backend issues

### Connection Issues
- Verify FastAPI is running on port 8000
- Check Nginx proxy configuration
- Ensure VPS firewall allows necessary ports

## Monitoring

```bash
# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check FastAPI logs
tail -f /opt/Pinmaker/logs/app.log
tail -f /opt/Pinmaker/logs/gunicorn_access.log

# Check SSL certificate status
sudo certbot certificates
```

This setup provides a clean separation between frontend hosting (Netlify) and API hosting (VPS), eliminating timeout issues while maintaining security and performance.