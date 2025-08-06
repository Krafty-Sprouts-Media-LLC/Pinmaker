#!/bin/bash

# Optimize Memory Usage for Pinmaker Backend
echo "🔧 Optimizing Pinmaker Memory Usage..."

# Stop the service
echo "⏹️ Stopping pinmaker service..."
sudo systemctl stop pinmaker

# Clear system caches
echo "🧹 Clearing system caches..."
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

# Update gunicorn configuration for lower memory usage
echo "⚙️ Updating gunicorn configuration..."
cat > /opt/Pinmaker/gunicorn.conf.py << 'EOF'
import multiprocessing

# Reduce workers to minimize memory usage
workers = 1  # Reduced from default
worker_class = "sync"
worker_connections = 100  # Reduced from default 1000
max_requests = 500  # Restart workers after 500 requests to prevent memory leaks
max_requests_jitter = 50
preload_app = True  # Share memory between workers
timeout = 120
keepalive = 5
bind = "0.0.0.0:8000"
user = "pinmaker"
group = "pinmaker"
chdir = "/opt/Pinmaker"
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files
EOF

# Update systemd service for better memory management
echo "🔧 Updating systemd service configuration..."
sudo tee /etc/systemd/system/pinmaker.service > /dev/null << 'EOF'
[Unit]
Description=Pinterest Template Generator - AI-powered template creation service
After=network.target
Wants=network.target

[Service]
Type=notify
User=pinmaker
Group=pinmaker
WorkingDirectory=/opt/Pinmaker
Environment=PATH=/opt/Pinmaker/venv/bin
EnvironmentFile=/opt/Pinmaker/.env
ExecStart=/opt/Pinmaker/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
WatchdogSec=120
KillMode=mixed
TimeoutStopSec=30

# Memory optimization
MemoryAccounting=true
MemoryMax=1.5G
MemorySwapMax=512M
OOMPolicy=continue

# Security settings (relaxed for file access)
NoNewPrivileges=true
PrivateTmp=false
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/opt/Pinmaker /home/pinmaker /tmp /var/tmp
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF

# Set Python memory optimization environment variables
echo "🐍 Setting Python memory optimization..."
cat >> /opt/Pinmaker/.env << 'EOF'

# Memory optimization
PYTHONOPTIMIZE=1
PYTHONDONTWRITEBYTECODE=1
MALLOC_TRIM_THRESHOLD_=100000
MALLOC_MMAP_THRESHOLD_=100000

# Reduce EasyOCR memory usage
EASYOCR_MODULE_PATH=/home/pinmaker/.EasyOCR
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
NUMEXPR_MAX_THREADS=1
EOF

# Reload systemd and start service
echo "🔄 Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl start pinmaker

# Wait for service to initialize
echo "⏳ Waiting for service to initialize..."
sleep 45

# Check status
echo "📊 Service Status:"
sudo systemctl status pinmaker --no-pager

echo "\n🧠 Memory Usage:"
free -h

echo "\n🔍 Testing health endpoint..."
for i in {1..5}; do
    echo "Attempt $i/5:"
    if curl -f http://localhost:8000/health 2>/dev/null; then
        echo "✅ Backend is responding!"
        break
    else
        echo "❌ Backend not responding, waiting 10 seconds..."
        sleep 10
    fi
done

echo "\n📈 Process Information:"
ps aux | grep gunicorn | grep -v grep

echo "\n✅ Memory optimization complete!"
