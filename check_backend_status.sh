#!/bin/bash

# Backend Status Check and Restart Script
# This script checks if the backend is running and restarts it if necessary

echo "🔍 Checking Pinmaker Backend Status..."

# Check if the service is running
echo "📊 Service Status:"
sudo systemctl status pinmaker --no-pager

echo ""
echo "🌐 Testing Health Endpoint:"
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ Backend is responding successfully!"
    echo "🎉 No action needed - service is healthy"
else
    echo "❌ Backend health check failed"
    echo "🔄 Attempting to restart the service..."
    
    # Stop the service
    sudo systemctl stop pinmaker
    sleep 3
    
    # Start the service
    sudo systemctl start pinmaker
    sleep 10
    
    # Check status again
    echo "📊 Service Status After Restart:"
    sudo systemctl status pinmaker --no-pager
    
    echo ""
    echo "🏥 Testing Health Endpoint Again:"
    if curl -f http://localhost:8000/health 2>/dev/null; then
        echo "✅ Backend is now responding successfully!"
        echo "🌐 Website should be accessible at: https://pinmaker.kraftysprouts.com"
    else
        echo "❌ Backend still not responding. Checking logs..."
        sudo journalctl -u pinmaker --lines=20 --no-pager
    fi
fi

echo ""
echo "📈 Memory Usage:"
free -h

echo ""
echo "🔧 Process Information:"
ps aux | grep -E '(gunicorn|pinmaker)' | grep -v grep

echo "🎯 Backend status check completed!"