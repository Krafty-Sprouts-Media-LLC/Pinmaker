# Direct API Connection Setup Guide

This guide explains how to configure your Pinmaker application for direct API connection between Netlify frontend and VPS backend, bypassing Nginx proxy.

## Overview

The direct API connection approach allows your Netlify-hosted frontend to communicate directly with your VPS-hosted FastAPI backend on port 8000, eliminating the need for Nginx as a reverse proxy.

## Changes Made

### 1. Frontend Configuration (`frontend/src/config/api.ts`)
- Updated to use direct VPS API URL in production: `https://pinmaker.kraftysprouts.com`
- Maintains localhost for development
- Uses environment variables for flexibility

### 2. Backend CORS Configuration (`main.py`)
- Added multiple Netlify domain patterns to CORS origins
- Updated TrustedHostMiddleware to include Netlify domains
- Ensures secure cross-origin requests

### 3. Gunicorn Configuration (`gunicorn.conf.py`)
- Changed bind address from `127.0.0.1:8000` to `0.0.0.0:8000`
- Allows external connections to the API server

### 4. Environment Configuration (`.env.production`)
- Already configured with correct API URL
- Ready for Netlify deployment

## Deployment Steps

### Step 1: Deploy Backend Changes
1. Commit and push the changes to your repository
2. The GitHub Actions workflow will deploy the updated configuration
3. Gunicorn will restart with the new bind configuration

### Step 2: Update VPS Firewall (if needed)
```bash
# Allow incoming connections on port 8000
sudo ufw allow 8000/tcp

# Check firewall status
sudo ufw status
```

### Step 3: Deploy Frontend to Netlify
1. Push frontend changes to trigger Netlify build
2. Netlify will use `.env.production` for build-time environment variables
3. Frontend will connect directly to `https://pinmaker.kraftysprouts.com:8000/api/v1`

## Testing the Setup

### 1. Test API Accessibility
```bash
# Test health endpoint directly
curl https://pinmaker.kraftysprouts.com:8000/api/v1/health

# Should return: {"status": "healthy", "timestamp": "..."}
```

### 2. Test CORS Configuration
```bash
# Test CORS headers
curl -H "Origin: https://your-netlify-domain.netlify.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://pinmaker.kraftysprouts.com:8000/api/v1/analyze
```

### 3. Monitor Logs
```bash
# Check gunicorn logs
tail -f /opt/Pinmaker/logs/gunicorn_access.log
tail -f /opt/Pinmaker/logs/gunicorn_error.log

# Check application logs
tail -f /opt/Pinmaker/logs/app.log
```

## Advantages of Direct Connection

1. **Simplified Architecture**: Removes Nginx complexity
2. **Reduced Latency**: Direct connection eliminates proxy overhead
3. **Easier Debugging**: Fewer components in the request path
4. **Better Error Handling**: Direct FastAPI error responses
5. **Simplified SSL**: Let's Encrypt handles SSL for the domain

## Security Considerations

1. **CORS Protection**: Configured to only allow your Netlify domains
2. **TrustedHost Middleware**: Validates incoming host headers
3. **Firewall Rules**: Only necessary ports are exposed
4. **HTTPS Only**: All communication encrypted via SSL

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check that your Netlify domain is in the CORS_ORIGINS list
   - Verify the domain spelling and protocol (https://)

2. **Connection Refused**
   - Ensure gunicorn is binding to 0.0.0.0:8000
   - Check firewall allows port 8000
   - Verify the service is running

3. **SSL Certificate Issues**
   - Ensure your domain SSL certificate covers port 8000
   - Check certificate validity

### Monitoring Commands

```bash
# Check if gunicorn is running
ps aux | grep gunicorn

# Check port binding
netstat -tlnp | grep :8000

# Test local API
curl http://localhost:8000/api/v1/health

# Test external API
curl https://pinmaker.kraftysprouts.com:8000/api/v1/health
```

## Rollback Plan

If issues occur, you can quickly rollback:

1. **Frontend**: Update `api.ts` to use relative URLs again
2. **Backend**: Change gunicorn bind back to `127.0.0.1:8000`
3. **Nginx**: Re-enable the proxy configuration

This approach provides a clean, direct connection while maintaining security and performance.