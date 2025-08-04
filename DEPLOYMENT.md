# Pinterest Template Generator - Deployment Guide

This guide provides comprehensive instructions for deploying the Pinterest Template Generator on a VPS (Virtual Private Server).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Server Requirements](#server-requirements)
- [Initial Server Setup](#initial-server-setup)
- [Automated Deployment](#automated-deployment)
- [Manual Deployment](#manual-deployment)
- [Configuration](#configuration)
- [SSL Certificate Setup](#ssl-certificate-setup)
- [Service Management](#service-management)
- [Monitoring Setup](#monitoring-setup)
- [Backup Configuration](#backup-configuration)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)
- [Scaling](#scaling)

## Prerequisites

### Domain and DNS

1. **Domain**: `pinmaker.kraftysprouts.com`
2. **DNS Records**: Point your domain to your VPS IP address
   ```
   A     pinmaker.kraftysprouts.com    YOUR_VPS_IP
   AAAA  pinmaker.kraftysprouts.com    YOUR_VPS_IPv6 (optional)
   ```

### VPS Requirements

- **Operating System**: Ubuntu 20.04 LTS or 22.04 LTS
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: Minimum 2 cores (4 cores recommended)
- **Storage**: Minimum 40GB SSD (100GB recommended)
- **Network**: 1Gbps connection

### Local Requirements

- Git installed
- SSH access to your VPS
- Basic knowledge of Linux command line

## Server Requirements

### Minimum Specifications

```
CPU: 2 cores @ 2.4GHz
RAM: 4GB
Storage: 40GB SSD
Bandwidth: 1TB/month
OS: Ubuntu 20.04/22.04 LTS
```

### Recommended Specifications

```
CPU: 4 cores @ 3.0GHz
RAM: 8GB
Storage: 100GB SSD
Bandwidth: 2TB/month
OS: Ubuntu 22.04 LTS
```

### Performance Considerations

- **AI Processing**: More CPU cores improve AI model performance
- **Memory**: Additional RAM helps with concurrent requests
- **Storage**: SSD storage improves file I/O performance
- **Network**: Higher bandwidth supports more concurrent users

## Initial Server Setup

### 1. Connect to Your VPS

```bash
ssh root@YOUR_VPS_IP
```

### 2. Update System

```bash
apt update && apt upgrade -y
apt install -y curl wget git unzip
```

### 3. Create User Account

```bash
# Create pinmaker user
useradd -m -s /bin/bash pinmaker
usermod -aG sudo pinmaker

# Set password
passwd pinmaker

# Switch to pinmaker user
su - pinmaker
```

### 4. Setup SSH Key (Optional but Recommended)

```bash
# On your local machine
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
ssh-copy-id pinmaker@YOUR_VPS_IP

# Test SSH key login
ssh pinmaker@YOUR_VPS_IP
```

### 5. Configure Firewall

```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw status
```

## Automated Deployment

### Quick Setup (Recommended)

The easiest way to deploy is using the automated setup script:

```bash
# Download and run setup script
wget https://raw.githubusercontent.com/yourusername/pinmaker/main/setup.sh
chmod +x setup.sh
sudo ./setup.sh
```

The setup script will:
- Install all dependencies
- Create necessary directories
- Clone the repository
- Set up Python virtual environment
- Install Python dependencies
- Build the frontend
- Configure services
- Set up SSL certificates
- Configure monitoring

### Setup Script Options

```bash
# Full installation (default)
sudo ./setup.sh

# Skip SSL setup (for testing)
sudo ./setup.sh --no-ssl

# Use custom domain
sudo ./setup.sh --domain your-domain.com

# Development mode
sudo ./setup.sh --dev
```

## Manual Deployment

If you prefer manual deployment or need to customize the setup:

### 1. Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install system packages
sudo apt install -y \
    nginx \
    supervisor \
    fail2ban \
    ufw \
    certbot \
    python3-certbot-nginx \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libmagickwand-dev

# Install AI/CV dependencies
sudo apt install -y \
    libopencv-dev \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1
```

### 2. Create Directory Structure

```bash
# Create application directories
sudo mkdir -p /home/pinmaker/{app,uploads,templates,previews,fonts,logs,backups}
sudo chown -R pinmaker:pinmaker /home/pinmaker

# Set permissions
chmod 755 /home/pinmaker
chmod 775 /home/pinmaker/{uploads,templates,previews,fonts}
chmod 755 /home/pinmaker/{app,logs,backups}
```

### 3. Clone Repository

```bash
cd /home/pinmaker
git clone https://github.com/yourusername/pinmaker.git app
cd app
```

### 4. Setup Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt
```

### 5. Build Frontend

```bash
# Install Node.js dependencies
npm install

# Build production frontend
npm run build
```

### 6. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Key environment variables to configure:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
DOMAIN=pinmaker.kraftysprouts.com
APP_URL=https://pinmaker.kraftysprouts.com
SECRET_KEY=your-secret-key-here

# Server
HOST=127.0.0.1
PORT=8000
WORKERS=4

# API Keys (optional)
UNSPLASH_ACCESS_KEY=your-unsplash-key
PEXELS_API_KEY=your-pexels-key
PIXABAY_API_KEY=your-pixabay-key
GOOGLE_FONTS_API_KEY=your-google-fonts-key
```

### 7. Setup Systemd Service

```bash
# Copy service file
sudo cp pinmaker.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable pinmaker
sudo systemctl start pinmaker

# Check status
sudo systemctl status pinmaker
```

### 8. Configure Nginx

```bash
# Copy Nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/pinmaker

# Enable site
sudo ln -s /etc/nginx/sites-available/pinmaker /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Configuration

### Environment Variables

Edit `/home/pinmaker/app/.env`:

```bash
# Application Settings
ENVIRONMENT=production
DEBUG=false
DOMAIN=pinmaker.kraftysprouts.com
APP_URL=https://pinmaker.kraftysprouts.com
SECRET_KEY=generate-a-secure-secret-key

# Server Configuration
HOST=127.0.0.1
PORT=8000
WORKERS=4
TIMEOUT=300
KEEP_ALIVE=2

# File Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp
CLEANUP_HOURS=24

# AI/ML Settings
MODEL_CACHE_DIR=/home/pinmaker/app/models
BATCH_SIZE=1
CONFIDENCE_THRESHOLD=0.5

# Stock Photo APIs (Optional)
UNSPLASH_ACCESS_KEY=your-unsplash-access-key
PEXELS_API_KEY=your-pexels-api-key
PIXABAY_API_KEY=your-pixabay-api-key

# Font Settings
GOOGLE_FONTS_API_KEY=your-google-fonts-api-key
MAX_FONT_SIZE=5242880  # 5MB

# Security
CORS_ORIGINS=https://pinmaker.kraftysprouts.com
RATE_LIMIT_PER_MINUTE=100
ADMIN_API_KEY=generate-admin-api-key

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/pinmaker/logs/app.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

### Nginx Configuration

Edit `/etc/nginx/sites-available/pinmaker`:

```nginx
server {
    listen 80;
    server_name pinmaker.kraftysprouts.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pinmaker.kraftysprouts.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/pinmaker.kraftysprouts.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pinmaker.kraftysprouts.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # File upload size
    client_max_body_size 10M;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Static files
    location /static/ {
        alias /home/pinmaker/app/dist/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Uploaded files
    location /uploads/ {
        alias /home/pinmaker/uploads/;
        expires 1h;
    }
    
    # Generated templates
    location /templates/ {
        alias /home/pinmaker/templates/;
        expires 1h;
    }
    
    # Preview images
    location /previews/ {
        alias /home/pinmaker/previews/;
        expires 1h;
    }
    
    # Custom fonts
    location /fonts/ {
        alias /home/pinmaker/fonts/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # API routes
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Frontend application
    location / {
        try_files $uri $uri/ /index.html;
        root /home/pinmaker/app/dist;
        index index.html;
    }
}
```

## SSL Certificate Setup

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d pinmaker.kraftysprouts.com

# Test automatic renewal
sudo certbot renew --dry-run

# Setup automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Manual SSL Certificate

If you have your own SSL certificate:

```bash
# Copy certificate files
sudo mkdir -p /etc/ssl/certs/pinmaker
sudo cp your-certificate.crt /etc/ssl/certs/pinmaker/
sudo cp your-private-key.key /etc/ssl/private/pinmaker/

# Set permissions
sudo chmod 644 /etc/ssl/certs/pinmaker/your-certificate.crt
sudo chmod 600 /etc/ssl/private/pinmaker/your-private-key.key

# Update Nginx configuration
sudo nano /etc/nginx/sites-available/pinmaker
```

## Service Management

### Systemd Service Commands

```bash
# Start service
sudo systemctl start pinmaker

# Stop service
sudo systemctl stop pinmaker

# Restart service
sudo systemctl restart pinmaker

# Reload service (graceful restart)
sudo systemctl reload pinmaker

# Check status
sudo systemctl status pinmaker

# View logs
sudo journalctl -u pinmaker -f

# Enable auto-start
sudo systemctl enable pinmaker

# Disable auto-start
sudo systemctl disable pinmaker
```

### Nginx Commands

```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx

# View error logs
sudo tail -f /var/log/nginx/error.log

# View access logs
sudo tail -f /var/log/nginx/access.log
```

## Monitoring Setup

### Install Monitoring Scripts

```bash
# Run monitoring setup
cd /home/pinmaker/app
sudo ./monitoring.sh
```

This sets up:
- System health monitoring
- Performance monitoring
- Log analysis
- Automated alerts
- Real-time dashboard

### Manual Monitoring Setup

```bash
# Create monitoring directory
sudo mkdir -p /home/pinmaker/monitoring

# Copy monitoring scripts
sudo cp monitoring/*.sh /home/pinmaker/monitoring/
sudo chmod +x /home/pinmaker/monitoring/*.sh

# Setup cron jobs
sudo crontab -e
```

Add these cron jobs:

```bash
# System monitoring (every 5 minutes)
*/5 * * * * /home/pinmaker/monitoring/system_monitor.sh

# Performance monitoring (every minute)
* * * * * /home/pinmaker/monitoring/performance_monitor.sh

# Log analysis (every hour)
0 * * * * /home/pinmaker/monitoring/log_analyzer.sh

# Cleanup old files (daily at 2 AM)
0 2 * * * /home/pinmaker/monitoring/cleanup.sh
```

### Monitoring Dashboard

```bash
# Start monitoring dashboard
/home/pinmaker/monitoring/dashboard.sh
```

Access the dashboard at: `http://your-server-ip:3000`

## Backup Configuration

### Automated Backups

```bash
# Setup backup system
cd /home/pinmaker/app
sudo ./backup.sh setup

# Configure backup schedule
sudo crontab -e
```

Add backup cron jobs:

```bash
# Daily backup at 3 AM
0 3 * * * /home/pinmaker/app/backup.sh daily

# Weekly backup on Sunday at 4 AM
0 4 * * 0 /home/pinmaker/app/backup.sh weekly

# Monthly backup on 1st at 5 AM
0 5 1 * * /home/pinmaker/app/backup.sh monthly
```

### Manual Backup

```bash
# Create immediate backup
/home/pinmaker/app/backup.sh backup

# List available backups
/home/pinmaker/app/backup.sh list

# Restore from backup
/home/pinmaker/app/backup.sh restore backup-2024-01-15.tar.gz
```

### Remote Backup (Optional)

Configure remote backup to AWS S3:

```bash
# Install AWS CLI
sudo apt install -y awscli

# Configure AWS credentials
aws configure

# Edit backup script configuration
nano /home/pinmaker/app/backup.sh
```

Update backup configuration:

```bash
# Remote backup settings
REMOTE_BACKUP_ENABLED=true
S3_BUCKET="your-backup-bucket"
S3_PREFIX="pinmaker-backups"
AWS_REGION="us-east-1"
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check service status
sudo systemctl status pinmaker

# View detailed logs
sudo journalctl -u pinmaker -n 50

# Check Python environment
sudo -u pinmaker /home/pinmaker/venv/bin/python -c "import main"

# Verify dependencies
sudo -u pinmaker /home/pinmaker/venv/bin/pip check
```

#### 2. Nginx Configuration Issues

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify file permissions
ls -la /home/pinmaker/app/dist/
```

#### 3. SSL Certificate Problems

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Test SSL configuration
ssl-cert-check -c /etc/letsencrypt/live/pinmaker.kraftysprouts.com/fullchain.pem
```

#### 4. File Upload Issues

```bash
# Check upload directory permissions
ls -la /home/pinmaker/uploads/

# Verify disk space
df -h

# Check file size limits
grep client_max_body_size /etc/nginx/sites-available/pinmaker
```

#### 5. AI Model Loading Issues

```bash
# Check model directory
ls -la /home/pinmaker/app/models/

# Test model loading
sudo -u pinmaker /home/pinmaker/venv/bin/python -c "import torch; print(torch.cuda.is_available())"

# Check memory usage
free -h
```

### Performance Issues

#### 1. High CPU Usage

```bash
# Check running processes
top -u pinmaker

# Monitor system resources
htop

# Check AI model performance
sudo -u pinmaker /home/pinmaker/monitoring/performance_monitor.sh
```

#### 2. Memory Issues

```bash
# Check memory usage
free -h

# Monitor memory by process
ps aux --sort=-%mem | head

# Check for memory leaks
sudo -u pinmaker /home/pinmaker/monitoring/memory_check.sh
```

#### 3. Disk Space Issues

```bash
# Check disk usage
df -h

# Find large files
sudo du -h /home/pinmaker/ | sort -rh | head -20

# Clean up old files
sudo -u pinmaker /home/pinmaker/monitoring/cleanup.sh
```

### Log Analysis

```bash
# Application logs
tail -f /home/pinmaker/logs/app.log

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -f

# Filter logs by error level
grep ERROR /home/pinmaker/logs/app.log
```

## Maintenance

### Regular Maintenance Tasks

#### Daily

```bash
# Check service status
sudo systemctl status pinmaker nginx

# Monitor disk space
df -h

# Check error logs
grep ERROR /home/pinmaker/logs/app.log | tail -10
```

#### Weekly

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean up old files
sudo -u pinmaker /home/pinmaker/monitoring/cleanup.sh

# Verify backups
/home/pinmaker/app/backup.sh verify

# Check SSL certificate expiry
sudo certbot certificates
```

#### Monthly

```bash
# Review performance metrics
/home/pinmaker/monitoring/performance_report.sh

# Update Python dependencies
sudo -u pinmaker /home/pinmaker/venv/bin/pip list --outdated

# Security audit
sudo apt audit

# Review log files
/home/pinmaker/monitoring/log_analyzer.sh --monthly
```

### Updates and Deployments

#### Code Updates

```bash
# Use deployment script
cd /home/pinmaker/app
./deploy.sh deploy

# Manual update process
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
npm install
npm run build
sudo systemctl restart pinmaker
```

#### Rollback

```bash
# Rollback to previous version
./deploy.sh rollback

# Manual rollback
git checkout previous-commit-hash
sudo systemctl restart pinmaker
```

### Security Updates

```bash
# Update system security patches
sudo apt update && sudo apt upgrade -y

# Update Python security packages
sudo -u pinmaker /home/pinmaker/venv/bin/pip install --upgrade pip setuptools

# Update Node.js security packages
npm audit fix

# Review Fail2ban logs
sudo fail2ban-client status
sudo tail -f /var/log/fail2ban.log
```

## Scaling

### Vertical Scaling

#### Increase Server Resources

1. **CPU Upgrade**
   - More cores improve AI processing
   - Better concurrent request handling

2. **Memory Upgrade**
   - Increase Gunicorn workers
   - Better AI model caching

3. **Storage Upgrade**
   - SSD for better I/O performance
   - More space for user uploads

#### Configuration Updates

Update `/home/pinmaker/app/.env`:

```bash
# Increase workers based on CPU cores
WORKERS=8  # 2 * CPU cores

# Adjust memory settings
MAX_UPLOAD_SIZE=20971520  # 20MB
BATCH_SIZE=2  # Process more images at once
```

### Horizontal Scaling

#### Load Balancer Setup

```nginx
# /etc/nginx/nginx.conf
upstream pinmaker_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location /api/ {
        proxy_pass http://pinmaker_backend;
        # ... other proxy settings
    }
}
```

#### Multiple Application Instances

```bash
# Create additional service files
sudo cp /etc/systemd/system/pinmaker.service /etc/systemd/system/pinmaker-2.service
sudo cp /etc/systemd/system/pinmaker.service /etc/systemd/system/pinmaker-3.service

# Update port numbers in service files
sudo nano /etc/systemd/system/pinmaker-2.service
# Change PORT=8001

sudo nano /etc/systemd/system/pinmaker-3.service
# Change PORT=8002

# Start additional instances
sudo systemctl enable pinmaker-2 pinmaker-3
sudo systemctl start pinmaker-2 pinmaker-3
```

#### Shared Storage

For multiple servers, use shared storage:

```bash
# NFS setup (on storage server)
sudo apt install -y nfs-kernel-server
sudo mkdir -p /shared/pinmaker/{uploads,templates,previews,fonts}
sudo chown -R pinmaker:pinmaker /shared/pinmaker

# Export NFS share
echo "/shared/pinmaker *(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports
sudo systemctl restart nfs-kernel-server

# Mount on application servers
sudo apt install -y nfs-common
sudo mount -t nfs storage-server:/shared/pinmaker /home/pinmaker/shared
```

### Cloud Migration

#### Docker Containerization

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build frontend
RUN npm install && npm run build

EXPOSE 8000

CMD ["gunicorn", "main:app", "-c", "gunicorn.conf.py"]
```

#### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pinmaker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pinmaker
  template:
    metadata:
      labels:
        app: pinmaker
    spec:
      containers:
      - name: pinmaker
        image: pinmaker:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

---

*This deployment guide covers all aspects of setting up and maintaining the Pinterest Template Generator in production. For additional support, refer to the troubleshooting section or create an issue in the project repository.*