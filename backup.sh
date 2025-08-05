#!/bin/bash

# Pinterest Template Generator - Backup and Recovery Script
# This script handles automated backups and recovery procedures

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Configuration
APP_USER="pinmaker"
APP_DIR="/home/$APP_USER"
APP_NAME="pinmaker"
DOMAIN="pinmaker.kraftysprouts.com"
BACKUP_DIR="/home/$APP_USER/backups"
REMOTE_BACKUP_DIR=""  # Set to remote backup location if needed
S3_BUCKET=""  # Set to S3 bucket name if using AWS S3
MAX_LOCAL_BACKUPS=7
MAX_REMOTE_BACKUPS=30
EMAIL="admin@kraftysprouts.com"

# Create backup directories
mkdir -p $BACKUP_DIR/{daily,weekly,monthly}
mkdir -p $BACKUP_DIR/logs

# Backup functions
backup_application() {
    local backup_type="$1"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="pinmaker_${backup_type}_${timestamp}"
    local backup_path="$BACKUP_DIR/$backup_type/$backup_name"
    
    log "Starting $backup_type backup: $backup_name"
    
    # Create backup directory
    mkdir -p "$backup_path"
    
    # Backup application code
    log "Backing up application code..."
    tar -czf "$backup_path/app_code.tar.gz" \
        --exclude="$APP_DIR/backups" \
        --exclude="$APP_DIR/logs" \
        --exclude="$APP_DIR/uploads" \
        --exclude="$APP_DIR/previews" \
        --exclude="$APP_DIR/venv" \
        --exclude="$APP_DIR/.git" \
        --exclude="$APP_DIR/node_modules" \
        --exclude="$APP_DIR/frontend/dist" \
        --exclude="$APP_DIR/frontend/node_modules" \
        -C "$APP_DIR" .
    
    # Backup user data
    log "Backing up user data..."
    if [ -d "$APP_DIR/uploads" ] && [ "$(ls -A $APP_DIR/uploads)" ]; then
        tar -czf "$backup_path/uploads.tar.gz" -C "$APP_DIR" uploads/
    fi
    
    if [ -d "$APP_DIR/templates" ] && [ "$(ls -A $APP_DIR/templates)" ]; then
        tar -czf "$backup_path/templates.tar.gz" -C "$APP_DIR" templates/
    fi
    
    if [ -d "$APP_DIR/fonts" ] && [ "$(ls -A $APP_DIR/fonts)" ]; then
        tar -czf "$backup_path/fonts.tar.gz" -C "$APP_DIR" fonts/
    fi
    
    # Backup configuration files
    log "Backing up configuration files..."
    mkdir -p "$backup_path/config"
    
    # Application configs
    [ -f "$APP_DIR/.env" ] && cp "$APP_DIR/.env" "$backup_path/config/"
    [ -f "$APP_DIR/gunicorn.conf.py" ] && cp "$APP_DIR/gunicorn.conf.py" "$backup_path/config/"
    
    # System configs
    [ -f "/etc/systemd/system/pinmaker.service" ] && cp "/etc/systemd/system/pinmaker.service" "$backup_path/config/"
    [ -f "/etc/nginx/sites-available/pinmaker" ] && cp "/etc/nginx/sites-available/pinmaker" "$backup_path/config/"
    [ -f "/etc/fail2ban/jail.d/pinmaker.conf" ] && cp "/etc/fail2ban/jail.d/pinmaker.conf" "$backup_path/config/"
    
    # SSL certificates
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        mkdir -p "$backup_path/ssl"
        cp -r "/etc/letsencrypt/live/$DOMAIN" "$backup_path/ssl/"
        cp -r "/etc/letsencrypt/archive/$DOMAIN" "$backup_path/ssl/" 2>/dev/null || true
    fi
    
    # Backup logs (last 7 days)
    log "Backing up recent logs..."
    if [ -d "$APP_DIR/logs" ]; then
        find "$APP_DIR/logs" -name "*.log" -mtime -7 -exec tar -czf "$backup_path/recent_logs.tar.gz" {} +
    fi
    
    # Create backup manifest
    log "Creating backup manifest..."
    cat > "$backup_path/manifest.txt" << MANIFEST_EOF
Pinterest Template Generator Backup
Backup Type: $backup_type
Timestamp: $(date -Iseconds)
Hostname: $(hostname)
Domain: $DOMAIN
Backup Size: $(du -sh "$backup_path" | cut -f1)

Contents:
$(ls -la "$backup_path")

System Info:
$(uname -a)
$(lsb_release -a 2>/dev/null || cat /etc/os-release)

Application Status:
$(systemctl status pinmaker --no-pager -l || echo "Service not found")
$(systemctl status nginx --no-pager -l || echo "Service not found")

Disk Usage:
$(df -h)

Memory Usage:
$(free -h)
MANIFEST_EOF
    
    # Calculate backup size
    local backup_size=$(du -sh "$backup_path" | cut -f1)
    
    log "$backup_type backup completed: $backup_name ($backup_size)"
    
    # Log backup completion
    echo "[$(date -Iseconds)] $backup_type backup completed: $backup_name ($backup_size)" >> "$BACKUP_DIR/logs/backup.log"
    
    echo "$backup_path"
}

cleanup_old_backups() {
    local backup_type="$1"
    local max_backups="$2"
    
    log "Cleaning up old $backup_type backups (keeping $max_backups)..."
    
    # Remove old backups
    ls -t "$BACKUP_DIR/$backup_type/" | tail -n +$((max_backups + 1)) | while read backup; do
        if [ -d "$BACKUP_DIR/$backup_type/$backup" ]; then
            log "Removing old backup: $backup"
            rm -rf "$BACKUP_DIR/$backup_type/$backup"
        fi
    done
}

upload_to_remote() {
    local backup_path="$1"
    local backup_name=$(basename "$backup_path")
    
    if [ -n "$S3_BUCKET" ]; then
        log "Uploading backup to S3: $S3_BUCKET"
        
        # Create compressed archive for upload
        local archive_path="/tmp/${backup_name}.tar.gz"
        tar -czf "$archive_path" -C "$(dirname $backup_path)" "$(basename $backup_path)"
        
        # Upload to S3 (requires AWS CLI configured)
        if command -v aws >/dev/null 2>&1; then
            aws s3 cp "$archive_path" "s3://$S3_BUCKET/pinmaker-backups/"
            rm -f "$archive_path"
            log "Backup uploaded to S3 successfully"
        else
            warn "AWS CLI not found, skipping S3 upload"
        fi
    elif [ -n "$REMOTE_BACKUP_DIR" ]; then
        log "Uploading backup to remote location: $REMOTE_BACKUP_DIR"
        
        # Use rsync for remote backup
        if command -v rsync >/dev/null 2>&1; then
            rsync -avz "$backup_path/" "$REMOTE_BACKUP_DIR/$backup_name/"
            log "Backup uploaded to remote location successfully"
        else
            warn "rsync not found, skipping remote upload"
        fi
    fi
}

verify_backup() {
    local backup_path="$1"
    
    log "Verifying backup integrity: $(basename $backup_path)"
    
    # Check if backup directory exists and is not empty
    if [ ! -d "$backup_path" ] || [ ! "$(ls -A $backup_path)" ]; then
        error "Backup directory is empty or does not exist"
        return 1
    fi
    
    # Verify tar files
    for tar_file in "$backup_path"/*.tar.gz; do
        if [ -f "$tar_file" ]; then
            if ! tar -tzf "$tar_file" >/dev/null 2>&1; then
                error "Corrupted tar file: $tar_file"
                return 1
            fi
        fi
    done
    
    # Check manifest
    if [ ! -f "$backup_path/manifest.txt" ]; then
        warn "Backup manifest missing"
    fi
    
    log "Backup verification completed successfully"
    return 0
}

restore_backup() {
    local backup_path="$1"
    local restore_type="$2"  # full, code, data, config
    
    if [ ! -d "$backup_path" ]; then
        error "Backup path does not exist: $backup_path"
        return 1
    fi
    
    log "Starting restore from backup: $(basename $backup_path)"
    log "Restore type: $restore_type"
    
    # Stop services
    log "Stopping services..."
    sudo systemctl stop pinmaker || true
    sudo systemctl stop nginx || true
    
    case "$restore_type" in
        "full")
            log "Performing full restore..."
            restore_code "$backup_path"
            restore_data "$backup_path"
            restore_config "$backup_path"
            ;;
        "code")
            log "Restoring application code..."
            restore_code "$backup_path"
            ;;
        "data")
            log "Restoring user data..."
            restore_data "$backup_path"
            ;;
        "config")
            log "Restoring configuration..."
            restore_config "$backup_path"
            ;;
        *)
            error "Invalid restore type: $restore_type"
            return 1
            ;;
    esac
    
    # Restart services
    log "Restarting services..."
    sudo systemctl start nginx
    sudo systemctl start pinmaker
    
    log "Restore completed successfully"
}

restore_code() {
    local backup_path="$1"
    
    if [ -f "$backup_path/app_code.tar.gz" ]; then
        log "Restoring application code..."
        
        # Backup current code
        if [ -d "$APP_DIR" ]; then
            mv "$APP_DIR" "${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        fi
        
        # Create app directory
        mkdir -p "$APP_DIR"
        
        # Extract code
        tar -xzf "$backup_path/app_code.tar.gz" -C "$APP_DIR"
        
        # Set permissions
        chown -R $APP_USER:$APP_USER "$APP_DIR"
        
        log "Application code restored"
    else
        warn "No application code backup found"
    fi
}

restore_data() {
    local backup_path="$1"
    
    # Restore uploads
    if [ -f "$backup_path/uploads.tar.gz" ]; then
        log "Restoring uploads..."
        [ -d "$APP_DIR/uploads" ] && rm -rf "$APP_DIR/uploads"
        tar -xzf "$backup_path/uploads.tar.gz" -C "$APP_DIR"
    fi
    
    # Restore templates
    if [ -f "$backup_path/templates.tar.gz" ]; then
        log "Restoring templates..."
        [ -d "$APP_DIR/templates" ] && rm -rf "$APP_DIR/templates"
        tar -xzf "$backup_path/templates.tar.gz" -C "$APP_DIR"
    fi
    
    # Restore fonts
    if [ -f "$backup_path/fonts.tar.gz" ]; then
        log "Restoring fonts..."
        [ -d "$APP_DIR/fonts" ] && rm -rf "$APP_DIR/fonts"
        tar -xzf "$backup_path/fonts.tar.gz" -C "$APP_DIR"
    fi
    
    # Set permissions
    chown -R $APP_USER:$APP_USER "$APP_DIR"
    
    log "User data restored"
}

restore_config() {
    local backup_path="$1"
    
    if [ -d "$backup_path/config" ]; then
        log "Restoring configuration files..."
        
        # Application configs
        [ -f "$backup_path/config/.env" ] && cp "$backup_path/config/.env" "$APP_DIR/"
        [ -f "$backup_path/config/gunicorn.conf.py" ] && cp "$backup_path/config/gunicorn.conf.py" "$APP_DIR/"
        
        # System configs
        [ -f "$backup_path/config/pinmaker.service" ] && sudo cp "$backup_path/config/pinmaker.service" "/etc/systemd/system/"
        [ -f "$backup_path/config/pinmaker" ] && sudo cp "$backup_path/config/pinmaker" "/etc/nginx/sites-available/"
        [ -f "$backup_path/config/pinmaker.conf" ] && sudo cp "$backup_path/config/pinmaker.conf" "/etc/fail2ban/jail.d/"
        
        # Reload systemd
        sudo systemctl daemon-reload
        
        log "Configuration restored"
    else
        warn "No configuration backup found"
    fi
    
    # Restore SSL certificates
    if [ -d "$backup_path/ssl" ]; then
        log "Restoring SSL certificates..."
        sudo cp -r "$backup_path/ssl/$DOMAIN" "/etc/letsencrypt/live/" 2>/dev/null || true
        sudo cp -r "$backup_path/ssl/$DOMAIN" "/etc/letsencrypt/archive/" 2>/dev/null || true
        log "SSL certificates restored"
    fi
}

list_backups() {
    echo "Available Backups:"
    echo "=================="
    
    for backup_type in daily weekly monthly; do
        echo ""
        echo "$backup_type backups:"
        if [ -d "$BACKUP_DIR/$backup_type" ] && [ "$(ls -A $BACKUP_DIR/$backup_type)" ]; then
            ls -la "$BACKUP_DIR/$backup_type" | grep "^d" | awk '{print $9, $6, $7, $8}' | while read backup date time size; do
                if [ -f "$BACKUP_DIR/$backup_type/$backup/manifest.txt" ]; then
                    backup_size=$(grep "Backup Size:" "$BACKUP_DIR/$backup_type/$backup/manifest.txt" | cut -d: -f2 | xargs)
                    echo "  $backup ($backup_size) - $date $time"
                else
                    echo "  $backup - $date $time"
                fi
            done
        else
            echo "  No $backup_type backups found"
        fi
    done
}

generate_backup_report() {
    local report_file="$BACKUP_DIR/logs/backup_report_$(date +%Y%m%d).log"
    
    {
        echo "=== Pinterest Template Generator Backup Report ==="
        echo "Date: $(date)"
        echo "Domain: $DOMAIN"
        echo ""
        
        echo "=== Backup Storage Usage ==="
        du -sh "$BACKUP_DIR"/* 2>/dev/null | sort -hr
        echo ""
        
        echo "=== Backup Counts ==="
        for backup_type in daily weekly monthly; do
            count=$(ls "$BACKUP_DIR/$backup_type" 2>/dev/null | wc -l)
            echo "$backup_type: $count backups"
        done
        echo ""
        
        echo "=== Recent Backup Activity ==="
        tail -10 "$BACKUP_DIR/logs/backup.log" 2>/dev/null || echo "No recent backup activity"
        echo ""
        
        echo "=== Disk Space ==="
        df -h "$BACKUP_DIR"
        echo ""
        
        echo "=== Backup Verification ==="
        # Verify latest backup
        latest_backup=$(ls -t "$BACKUP_DIR/daily/" 2>/dev/null | head -1)
        if [ -n "$latest_backup" ]; then
            if verify_backup "$BACKUP_DIR/daily/$latest_backup"; then
                echo "Latest backup verification: PASSED"
            else
                echo "Latest backup verification: FAILED"
            fi
        else
            echo "No backups found for verification"
        fi
    } > "$report_file"
    
    log "Backup report generated: $report_file"
}

# Main script logic
case "${1:-daily}" in
    "daily")
        log "Starting daily backup..."
        backup_path=$(backup_application "daily")
        verify_backup "$backup_path"
        upload_to_remote "$backup_path"
        cleanup_old_backups "daily" $MAX_LOCAL_BACKUPS
        ;;
    
    "weekly")
        log "Starting weekly backup..."
        backup_path=$(backup_application "weekly")
        verify_backup "$backup_path"
        upload_to_remote "$backup_path"
        cleanup_old_backups "weekly" 4
        ;;
    
    "monthly")
        log "Starting monthly backup..."
        backup_path=$(backup_application "monthly")
        verify_backup "$backup_path"
        upload_to_remote "$backup_path"
        cleanup_old_backups "monthly" 12
        ;;
    
    "restore")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 restore <backup_path> <restore_type>"
            echo "Restore types: full, code, data, config"
            exit 1
        fi
        restore_backup "$2" "$3"
        ;;
    
    "list")
        list_backups
        ;;
    
    "report")
        generate_backup_report
        ;;
    
    "verify")
        if [ -z "$2" ]; then
            echo "Usage: $0 verify <backup_path>"
            exit 1
        fi
        verify_backup "$2"
        ;;
    
    "help")
        echo "Pinterest Template Generator Backup Script"
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  daily          Create daily backup (default)"
        echo "  weekly         Create weekly backup"
        echo "  monthly        Create monthly backup"
        echo "  restore <path> <type>  Restore from backup"
        echo "  list           List available backups"
        echo "  report         Generate backup report"
        echo "  verify <path>  Verify backup integrity"
        echo "  help           Show this help message"
        echo ""
        echo "Restore types:"
        echo "  full           Restore everything"
        echo "  code           Restore application code only"
        echo "  data           Restore user data only"
        echo "  config         Restore configuration only"
        echo ""
        echo "Examples:"
        echo "  $0 daily"
        echo "  $0 restore /opt/Pinmaker/backups/daily/pinmaker_daily_20240101_120000 full"
        echo "  $0 list"
        echo "  $0 verify /opt/Pinmaker/backups/daily/pinmaker_daily_20240101_120000"
        ;;
    
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

log "Backup script completed successfully! 💾"