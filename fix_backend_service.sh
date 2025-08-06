#!/bin/bash

# Fix Backend Service Script
# This script ensures the FastAPI backend service is properly configured and running

echo "🔧 Fixing Pinmaker Backend Service..."

# Navigate to application directory
cd /opt/Pinmaker

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3.12 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
fi

# Create systemd service file if it doesn't exist
if [ ! -f "/etc/systemd/system/pinmaker.service" ]; then
    echo "🔧 Creating systemd service file..."
    sudo tee /etc/systemd/system/pinmaker.service > /dev/null <<EOF
[Unit]
Description=Pinmaker FastAPI Application
After=network.target

[Service]
Type=exec
User=pinmaker
Group=pinmaker
WorkingDirectory=/opt/Pinmaker
Environment=PATH=/opt/Pinmaker/venv/bin
ExecStart=/opt/Pinmaker/venv/bin/gunicorn main:app -c gunicorn.conf.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
fi

# Reload systemd and enable service
echo "🔄 Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable pinmaker

# Stop service if running
sudo systemctl stop pinmaker

# Start the service
echo "🚀 Starting Pinmaker service..."
sudo systemctl start pinmaker

# Check service status
echo "📊 Service Status:"
sudo systemctl status pinmaker --no-pager -l

# Test the health endpoint
echo "🏥 Testing health endpoint..."
sleep 5
curl -f http://localhost:8000/health || echo "❌ Health check failed"

echo "✅ Backend service fix completed!"