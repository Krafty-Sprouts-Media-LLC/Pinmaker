# Caddy Migration Guide

This guide will help you migrate from Nginx to Caddy for automatic HTTPS with zero configuration complexity.

## 🌟 Why Caddy?

- **Automatic HTTPS**: No manual certificate management
- **Zero configuration**: Simple, readable config files
- **Automatic renewals**: Never worry about expired certificates
- **Better error messages**: Easier debugging
- **Production ready**: Handles millions of certificates

## 📋 Pre-Migration Checklist

### 1. Backup Current Setup
```bash
# Backup Nginx configuration
sudo cp -r /etc/nginx /etc/nginx.backup.$(date +%Y%m%d)

# Backup SSL certificates (if any)
sudo cp -r /etc/letsencrypt /etc/letsencrypt.backup.$(date +%Y%m%d)

# Note current service status
sudo systemctl status nginx
sudo systemctl status your-fastapi-service
```

### 2. Verify DNS Records
Ensure your DNS records point to your server:
```bash
# Check DNS resolution
nslookup api.pinmaker.kraftysprouts.com
nslookup pinmaker.kraftysprouts.com
```

### 3. Check Port Availability
```bash
# Verify ports 80 and 443 are accessible
sudo netstat -tlnp | grep -E ":(80|443) "
```

## 🚀 Migration Steps

### Step 1: Upload Files to VPS
```bash
# Copy the new files to your VPS
scp Caddyfile deploy_caddy.sh user@your-vps:/home/user/pinmaker/
```

### Step 2: Run the Deployment Script
```bash
# SSH into your VPS
ssh user@your-vps

# Navigate to your project directory
cd /home/user/pinmaker

# Make the script executable
chmod +x deploy_caddy.sh

# Run the deployment script
./deploy_caddy.sh
```

### Step 3: Verify the Migration
```bash
# Check Caddy status
sudo systemctl status caddy

# Check if certificates are being provisioned
sudo journalctl -u caddy -f

# Test your endpoints
curl -I https://api.pinmaker.kraftysprouts.com/api/v1/health
curl -I https://pinmaker.kraftysprouts.com/api/v1/health
```

## 🔧 What the Migration Does

### Automatic Actions
1. **Installs Caddy** from official repository
2. **Stops and disables Nginx** (safely)
3. **Copies Caddyfile** to `/etc/caddy/`
4. **Validates configuration** before starting
5. **Starts Caddy service** with automatic startup
6. **Sets up log rotation** for maintenance
7. **Creates health check script** for monitoring

### Caddy Configuration Features
- **Automatic HTTPS** for both domains
- **Rate limiting** (similar to your Nginx setup)
- **Security headers** (same as your Nginx config)
- **Gzip compression** for better performance
- **Request size limits** for uploads (50MB)
- **Proper logging** with rotation
- **Static asset caching** for performance

## 📊 Monitoring and Maintenance

### Check Caddy Status
```bash
# Service status
sudo systemctl status caddy

# Real-time logs
sudo journalctl -u caddy -f

# Run health check
sudo /usr/local/bin/caddy-health-check.sh
```

### View Certificates
```bash
# List managed certificates
sudo caddy list-certificates --config /etc/caddy/Caddyfile

# Check certificate directory
sudo ls -la /var/lib/caddy/.local/share/caddy/certificates/
```

### Configuration Management
```bash
# Validate configuration
sudo caddy validate --config /etc/caddy/Caddyfile

# Reload configuration (zero downtime)
sudo systemctl reload caddy

# Restart service (if needed)
sudo systemctl restart caddy
```

## 🔄 Rollback Procedure (If Needed)

If you need to rollback to Nginx:

### Step 1: Stop Caddy
```bash
sudo systemctl stop caddy
sudo systemctl disable caddy
```

### Step 2: Restore Nginx
```bash
# Restore Nginx configuration
sudo cp -r /etc/nginx.backup.$(date +%Y%m%d)/* /etc/nginx/

# Start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Step 3: Restore SSL Certificates (if needed)
```bash
# If you had Let's Encrypt certificates
sudo cp -r /etc/letsencrypt.backup.$(date +%Y%m%d)/* /etc/letsencrypt/
```

## 🎯 Key Differences from Nginx

| Feature | Nginx | Caddy |
|---------|-------|-------|
| HTTPS Setup | Manual (certbot) | Automatic |
| Certificate Renewal | Cron job required | Built-in |
| Configuration | Complex syntax | Simple, readable |
| Rate Limiting | Manual modules | Built-in |
| Error Messages | Cryptic | Clear and helpful |
| HTTP/2 & HTTP/3 | Manual config | Enabled by default |

## 🔍 Troubleshooting

### Certificate Issues
```bash
# Check certificate provisioning logs
sudo journalctl -u caddy | grep -i certificate

# Force certificate renewal (if needed)
sudo caddy reload --config /etc/caddy/Caddyfile
```

### Port Conflicts
```bash
# Check what's using ports 80/443
sudo netstat -tlnp | grep -E ":(80|443) "

# Kill conflicting processes if needed
sudo systemctl stop nginx  # or other web servers
```

### Backend Connection Issues
```bash
# Check if FastAPI is running
pgrep -f "uvicorn\|gunicorn"

# Test backend directly
curl http://localhost:8000/api/v1/health
```

### Configuration Validation
```bash
# Always validate before applying changes
sudo caddy validate --config /etc/caddy/Caddyfile

# Check syntax errors
sudo caddy fmt --config /etc/caddy/Caddyfile
```

## 📈 Performance Benefits

- **Faster SSL handshakes** with modern TLS implementations
- **HTTP/3 support** out of the box
- **Automatic compression** for better bandwidth usage
- **Connection pooling** for backend services
- **Zero-downtime reloads** for configuration changes

## 🔐 Security Features

- **Modern TLS defaults** (TLS 1.2+ only)
- **HSTS headers** automatically added
- **Secure cipher suites** by default
- **OCSP stapling** for faster certificate validation
- **Same security headers** as your Nginx setup

## 📞 Support

If you encounter issues:

1. **Check the logs**: `sudo journalctl -u caddy -f`
2. **Run health check**: `sudo /usr/local/bin/caddy-health-check.sh`
3. **Validate config**: `sudo caddy validate --config /etc/caddy/Caddyfile`
4. **Check DNS**: Ensure your domains point to the server
5. **Verify ports**: Ensure 80 and 443 are open and accessible

## 🎉 Expected Results

After successful migration:

- ✅ **Automatic HTTPS** for both domains
- ✅ **Zero certificate management** overhead
- ✅ **Better performance** with HTTP/2 and HTTP/3
- ✅ **Simplified configuration** management
- ✅ **Automatic renewals** (no more expired certificates)
- ✅ **Better error messages** for easier debugging

Your API will be accessible at:
- `https://api.pinmaker.kraftysprouts.com`
- `https://pinmaker.kraftysprouts.com`

Both with automatic, valid SSL certificates! 🔒