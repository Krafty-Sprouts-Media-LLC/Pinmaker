#!/bin/bash

# Disk Space Monitoring Script for Pinmaker
# Alerts when disk usage exceeds thresholds

set -e

# Configuration
WARN_THRESHOLD=75  # Warning at 75%
CRIT_THRESHOLD=85  # Critical at 85%
LOG_FILE="/opt/Pinmaker/logs/disk-monitor.log"
EMAIL_ALERTS=false  # Set to true to enable email alerts
ADMIN_EMAIL="admin@kraftysprouts.com"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] CRITICAL: $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Check disk usage
check_disk_usage() {
    local partition="$1"
    local usage=$(df "$partition" | awk 'NR==2 {print $5}' | sed 's/%//')
    local available=$(df -h "$partition" | awk 'NR==2 {print $4}')
    
    log "Checking disk usage for $partition: ${usage}% used, ${available} available"
    
    if [ "$usage" -ge "$CRIT_THRESHOLD" ]; then
        error "CRITICAL: Disk usage on $partition is ${usage}% (threshold: ${CRIT_THRESHOLD}%)"
        error "Available space: $available"
        
        # Show largest directories
        error "Largest directories:"
        du -h "$partition" 2>/dev/null | sort -rh | head -10 | while read size dir; do
            error "  $size - $dir"
        done
        
        # Cleanup suggestions
        error "Cleanup suggestions:"
        error "  1. Run log cleanup: sudo journalctl --vacuum-time=7d"
        error "  2. Clean package cache: sudo apt autoremove && sudo apt autoclean"
        error "  3. Check /opt/Pinmaker/logs/ for large log files"
        error "  4. Check /tmp for temporary files"
        
        if [ "$EMAIL_ALERTS" = true ]; then
            send_alert "CRITICAL" "$partition" "$usage" "$available"
        fi
        
        return 2
        
    elif [ "$usage" -ge "$WARN_THRESHOLD" ]; then
        warn "WARNING: Disk usage on $partition is ${usage}% (threshold: ${WARN_THRESHOLD}%)"
        warn "Available space: $available"
        
        if [ "$EMAIL_ALERTS" = true ]; then
            send_alert "WARNING" "$partition" "$usage" "$available"
        fi
        
        return 1
    else
        success "Disk usage on $partition is healthy: ${usage}% used, ${available} available"
        return 0
    fi
}

# Send email alert (requires mailutils)
send_alert() {
    local level="$1"
    local partition="$2"
    local usage="$3"
    local available="$4"
    
    if command -v mail >/dev/null 2>&1; then
        {
            echo "Subject: [$level] Disk Space Alert - Pinmaker Server"
            echo ""
            echo "Disk usage alert for Pinmaker server:"
            echo ""
            echo "Partition: $partition"
            echo "Usage: ${usage}%"
            echo "Available: $available"
            echo "Timestamp: $(date)"
            echo ""
            echo "Please check the server and free up disk space if necessary."
        } | mail "$ADMIN_EMAIL"
        
        log "Email alert sent to $ADMIN_EMAIL"
    else
        warn "Mail command not available - email alert not sent"
    fi
}

# Cleanup old files
cleanup_old_files() {
    log "Running cleanup of old files..."
    
    # Clean old logs (older than 30 days)
    find /opt/Pinmaker/logs/ -name "*.log" -mtime +30 -delete 2>/dev/null || true
    find /var/log/ -name "*.log.*.gz" -mtime +30 -delete 2>/dev/null || true
    
    # Clean old journal logs
    sudo journalctl --vacuum-time=14d >/dev/null 2>&1 || true
    
    # Clean package cache
    sudo apt autoremove -y >/dev/null 2>&1 || true
    sudo apt autoclean >/dev/null 2>&1 || true
    
    # Clean temporary files
    find /tmp -type f -mtime +7 -delete 2>/dev/null || true
    
    log "Cleanup completed"
}

# Main execution
main() {
    log "Starting disk space monitoring..."
    
    local exit_code=0
    
    # Check root partition
    check_disk_usage "/" || exit_code=$?
    
    # Check /opt if it's a separate partition
    if mountpoint -q /opt 2>/dev/null; then
        check_disk_usage "/opt" || exit_code=$?
    fi
    
    # Check /var if it's a separate partition
    if mountpoint -q /var 2>/dev/null; then
        check_disk_usage "/var" || exit_code=$?
    fi
    
    # If usage is high, run cleanup
    if [ $exit_code -ge 1 ]; then
        cleanup_old_files
        
        # Re-check after cleanup
        log "Re-checking disk usage after cleanup..."
        check_disk_usage "/" || true
    fi
    
    log "Disk monitoring completed with exit code: $exit_code"
    exit $exit_code
}

# Run main function
main "$@"