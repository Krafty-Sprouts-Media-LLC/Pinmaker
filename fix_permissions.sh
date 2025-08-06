#!/bin/bash

# Fix Pinmaker Backend Permission Issues
# This script resolves the permission denied errors preventing the backend from starting

echo "🔧 Fixing Pinmaker Backend Permission Issues..."

# Stop the service first
echo "⏹️ Stopping pinmaker service..."
sudo systemctl stop pinmaker

# Create necessary directories with proper permissions
echo "📁 Creating and fixing directory permissions..."

# Fix EasyOCR model directory
sudo mkdir -p /home/pinmaker/.EasyOCR/model
sudo chown -R pinmaker:pinmaker /home/pinmaker/.EasyOCR
sudo chmod -R 755 /home/pinmaker/.EasyOCR

# Fix matplotlib config directory
sudo mkdir -p /home/pinmaker/.config/matplotlib
sudo chown -R pinmaker:pinmaker /home/pinmaker/.config
sudo chmod -R 755 /home/pinmaker/.config

# Fix Ultralytics config directory
sudo mkdir -p /home/pinmaker/.config/Ultralytics
sudo chown -R pinmaker:pinmaker /home/pinmaker/.config/Ultralytics
sudo chmod -R 755 /home/pinmaker/.config/Ultralytics

# Ensure the application directory has correct permissions
echo "📂 Fixing application directory permissions..."
sudo chown -R pinmaker:pinmaker /opt/Pinmaker
sudo chmod -R 755 /opt/Pinmaker

# Create a proper environment file for the service
echo "⚙️ Setting up environment variables..."
cat > /tmp/pinmaker.env << EOF
# Matplotlib configuration
MPLCONFIGDIR=/home/pinmaker/.config/matplotlib

# Ultralytics configuration
YOLO_CONFIG_DIR=/home/pinmaker/.config/Ultralytics

# EasyOCR configuration
EASYOCR_MODULE_PATH=/home/pinmaker/.EasyOCR

# Python path
PYTHONPATH=/opt/Pinmaker

# Working directory
WORKDIR=/opt/Pinmaker
EOF

sudo mv /tmp/pinmaker.env /opt/Pinmaker/.env
sudo chown pinmaker:pinmaker /opt/Pinmaker/.env
sudo chmod 644 /opt/Pinmaker/.env

# Update the systemd service file to include environment variables
echo "🔄 Updating systemd service configuration..."
sudo tee /etc/systemd/system/pinmaker.service > /dev/null << EOF
[Unit]
Description=Pinterest Template Generator - AI-powered template creation service
After=network.target

[Service]
Type=exec
User=pinmaker
Group=pinmaker
WorkingDirectory=/opt/Pinmaker
EnvironmentFile=/opt/Pinmaker/.env
ExecStart=/opt/Pinmaker/venv/bin/gunicorn -c gunicorn.conf.py main:app
Restart=always
RestartSec=10
WatchdogSec=30
NotifyAccess=all

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/Pinmaker /home/pinmaker/.config /home/pinmaker/.EasyOCR /tmp

# Resource limits
LimitNOFILE=65536
MemoryMax=2G

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and restart the service
echo "🔄 Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "🚀 Starting pinmaker service..."
sudo systemctl enable pinmaker
sudo systemctl start pinmaker

# Wait a moment for the service to start
sleep 5

# Check service status
echo "📊 Checking service status..."
sudo systemctl status pinmaker --no-pager

# Test the health endpoint
echo "🏥 Testing health endpoint..."
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ Backend is now running successfully!"
    echo "🌐 Website should be accessible at: https://pinmaker.kraftysprouts.com"
else
    echo "❌ Health check failed. Checking logs..."
    sudo journalctl -u pinmaker --lines=20 --no-pager
fi

echo "🎉 Permission fix script completed!"