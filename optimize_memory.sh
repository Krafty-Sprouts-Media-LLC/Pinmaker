#!/bin/bash

# Memory Optimization Script
# Optimizes memory usage for Pinmaker on a 4GB server

echo "🧠 Optimizing Memory Usage..."

# Show current memory usage
echo "📊 Current Memory Usage:"
free -h

# Clear page cache, dentries and inodes
echo "🧹 Clearing system caches..."
sudo sync
sudo echo 3 > /proc/sys/vm/drop_caches

# Restart Pinmaker service to free memory
echo "🔄 Restarting Pinmaker service..."
sudo systemctl restart pinmaker

# Wait for service to start
sleep 5

# Check if service is running
if sudo systemctl is-active --quiet pinmaker; then
    echo "✅ Pinmaker service restarted successfully"
else
    echo "❌ Pinmaker service failed to restart"
    sudo systemctl status pinmaker --no-pager -l
fi

# Show memory usage after optimization
echo ""
echo "📊 Memory Usage After Optimization:"
free -h

# Show process memory usage
echo ""
echo "🔍 Top Memory Consumers:"
ps aux --sort=-%mem | head -10

# Check swap usage
echo ""
echo "💾 Swap Usage:"
swapon --show

echo ""
echo "✅ Memory optimization completed!"