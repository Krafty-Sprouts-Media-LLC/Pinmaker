#!/bin/bash

# Disk Monitor Script
# Monitors disk usage and cleans up temporary files

echo "💾 Disk Monitor - $(date)"

# Check disk usage
echo "📊 Current Disk Usage:"
df -h /

# Check if disk usage is above 80%
USAGE=$(df / | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 }' | sed 's/%//g')

if [ $USAGE -gt 80 ]; then
    echo "⚠️ Disk usage is above 80%! Cleaning up..."
    
    # Clean up logs older than 7 days
    find /opt/Pinmaker/logs -name "*.log" -mtime +7 -delete 2>/dev/null
    
    # Clean up temporary files
    find /opt/Pinmaker/temp -type f -mtime +1 -delete 2>/dev/null
    
    # Clean up old uploads (if any)
    find /opt/Pinmaker/uploads -type f -mtime +30 -delete 2>/dev/null
    
    # Clean system logs
    sudo journalctl --vacuum-time=7d
    
    echo "✅ Cleanup completed"
else
    echo "✅ Disk usage is normal ($USAGE%)"
fi

# Show largest directories
echo ""
echo "📁 Largest directories in /opt/Pinmaker:"
du -sh /opt/Pinmaker/* 2>/dev/null | sort -hr | head -5