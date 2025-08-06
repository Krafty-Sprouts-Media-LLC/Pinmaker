#!/bin/bash

# Check Backend Status Script
# This script checks the status of the Pinmaker backend service

echo "📊 Checking Pinmaker Backend Status..."

# Check if service is running
echo "🔍 Service Status:"
sudo systemctl status pinmaker --no-pager -l

echo ""
echo "🌐 Network Status:"
echo "Port 8000 listening:"
sudo netstat -tlnp | grep :8000 || echo "❌ Port 8000 not listening"

echo ""
echo "🏥 Health Check:"
curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Health check passed" || echo "❌ Health check failed"

echo ""
echo "📝 Recent Logs:"
sudo journalctl -u pinmaker --no-pager -n 10

echo ""
echo "💾 Memory Usage:"
ps aux | grep gunicorn | grep -v grep

echo ""
echo "📁 File Permissions:"
ls -la /opt/Pinmaker/ | head -10