#!/bin/bash

# Pinterest Template Generator - Comprehensive Monitoring Setup
# This script sets up monitoring, logging, and alerting for the application

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
EMAIL="admin@kraftysprouts.com"  # Update with your email
SLACK_WEBHOOK=""  # Add your Slack webhook URL if needed

log "Setting up comprehensive monitoring for Pinterest Template Generator"

# Create monitoring directories
sudo mkdir -p /var/log/pinmaker
sudo mkdir -p /etc/pinmaker/monitoring
sudo mkdir -p $APP_DIR/monitoring
sudo chown -R $APP_USER:$APP_USER $APP_DIR/monitoring

# Install monitoring tools
log "Installing monitoring tools..."
sudo apt update
sudo apt install -y \
    htop \
    iotop \
    nethogs \
    ncdu \
    tree \
    jq \
    curl \
    mailutils \
    postfix \
    logwatch \
    fail2ban \
    unattended-upgrades

# Configure log rotation for application logs
log "Configuring log rotation..."
sudo tee /etc/logrotate.d/pinmaker > /dev/null << 'EOF'
/home/pinmaker/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 pinmaker pinmaker
    sharedscripts
    postrotate
        systemctl reload pinmaker || true
    endscript
}

/var/log/nginx/pinmaker_*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload nginx || true
    endscript
}
EOF

# Create comprehensive monitoring script
log "Creating monitoring script..."
sudo tee $APP_DIR/monitoring/system_monitor.sh > /dev/null << 'EOF'
#!/bin/bash

# Pinterest Template Generator - System Monitor
# This script monitors system health and sends alerts

# Configuration
APP_NAME="pinmaker"
DOMAIN="pinmaker.kraftysprouts.com"
LOG_FILE="/home/pinmaker/logs/monitor.log"
ALERT_LOG="/home/pinmaker/logs/alerts.log"
EMAIL="admin@kraftysprouts.com"
SLACK_WEBHOOK=""  # Add your Slack webhook URL

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=85
LOAD_THRESHOLD=4.0
REQUEST_THRESHOLD=1000  # requests per minute

# Functions
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

alert_message() {
    local message="$1"
    local severity="$2"
    
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$severity] $message" >> $ALERT_LOG
    log_message "ALERT [$severity]: $message"
    
    # Send email alert
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "[$severity] Pinterest Template Generator Alert" $EMAIL
    fi
    
    # Send Slack alert (if webhook configured)
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$severity] Pinterest Template Generator Alert: $message\"}" \
            $SLACK_WEBHOOK >/dev/null 2>&1
    fi
}

check_service() {
    local service="$1"
    if ! systemctl is-active --quiet $service; then
        alert_message "Service $service is not running. Attempting restart..." "CRITICAL"
        sudo systemctl restart $service
        sleep 10
        if systemctl is-active --quiet $service; then
            alert_message "Service $service restarted successfully" "INFO"
        else
            alert_message "Failed to restart service $service" "CRITICAL"
        fi
    fi
}

check_url() {
    local url="$1"
    local timeout="$2"
    
    if ! curl -f -s --max-time $timeout "$url" >/dev/null; then
        alert_message "URL $url is not responding" "CRITICAL"
        return 1
    fi
    return 0
}

get_cpu_usage() {
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}'
}

get_memory_usage() {
    free | awk 'NR==2{printf "%.0f", $3*100/$2}'
}

get_disk_usage() {
    df /home/pinmaker | awk 'NR==2 {print $5}' | sed 's/%//'
}

get_load_average() {
    uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//'
}

get_request_count() {
    # Count requests in the last minute from access log
    local log_file="/var/log/nginx/pinmaker_access.log"
    if [ -f "$log_file" ]; then
        local current_time=$(date +%s)
        local one_minute_ago=$((current_time - 60))
        
        awk -v start_time=$one_minute_ago '
        {
            # Parse nginx log timestamp
            gsub(/\[|\]/, "", $4)
            cmd = "date -d \"" $4 " " $5 "\" +%s"
            cmd | getline timestamp
            close(cmd)
            
            if (timestamp >= start_time) {
                count++
            }
        }
        END {
            print count+0
        }' "$log_file"
    else
        echo "0"
    fi
}

check_ssl_expiry() {
    local domain="$1"
    local days_until_expiry
    
    days_until_expiry=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | \
        openssl x509 -noout -dates | grep notAfter | cut -d= -f2 | \
        xargs -I {} date -d "{}" +%s | \
        awk -v now=$(date +%s) '{print int(($1 - now) / 86400)}')
    
    if [ "$days_until_expiry" -lt 30 ]; then
        alert_message "SSL certificate for $domain expires in $days_until_expiry days" "WARNING"
    elif [ "$days_until_expiry" -lt 7 ]; then
        alert_message "SSL certificate for $domain expires in $days_until_expiry days" "CRITICAL"
    fi
}

check_log_errors() {
    local error_count
    local app_log="/home/pinmaker/logs/error.log"
    local nginx_log="/var/log/nginx/pinmaker_error.log"
    
    # Check application errors in the last 5 minutes
    if [ -f "$app_log" ]; then
        error_count=$(tail -n 1000 "$app_log" | grep "$(date +'%Y-%m-%d %H:%M' -d '5 minutes ago')" | wc -l)
        if [ "$error_count" -gt 10 ]; then
            alert_message "High error rate in application log: $error_count errors in last 5 minutes" "WARNING"
        fi
    fi
    
    # Check nginx errors
    if [ -f "$nginx_log" ]; then
        error_count=$(tail -n 1000 "$nginx_log" | grep "$(date +'%Y/%m/%d %H:%M' -d '5 minutes ago')" | wc -l)
        if [ "$error_count" -gt 5 ]; then
            alert_message "High error rate in nginx log: $error_count errors in last 5 minutes" "WARNING"
        fi
    fi
}

check_disk_space() {
    local usage
    local path
    
    # Check main disk
    usage=$(get_disk_usage)
    if [ "$usage" -gt "$DISK_THRESHOLD" ]; then
        alert_message "Disk usage is ${usage}% (threshold: ${DISK_THRESHOLD}%)" "WARNING"
    fi
    
    # Check specific directories
    for path in "/home/pinmaker/uploads" "/home/pinmaker/previews" "/home/pinmaker/logs"; do
        if [ -d "$path" ]; then
            local size=$(du -sh "$path" | cut -f1)
            local size_mb=$(du -sm "$path" | cut -f1)
            
            # Alert if directory is larger than 5GB
            if [ "$size_mb" -gt 5120 ]; then
                alert_message "Directory $path is large: $size" "INFO"
            fi
        fi
    done
}

check_process_count() {
    local python_processes
    local nginx_processes
    
    python_processes=$(pgrep -f "python.*main:app" | wc -l)
    nginx_processes=$(pgrep nginx | wc -l)
    
    if [ "$python_processes" -eq 0 ]; then
        alert_message "No Python application processes found" "CRITICAL"
    elif [ "$python_processes" -gt 10 ]; then
        alert_message "High number of Python processes: $python_processes" "WARNING"
    fi
    
    if [ "$nginx_processes" -eq 0 ]; then
        alert_message "No Nginx processes found" "CRITICAL"
    fi
}

generate_report() {
    local report_file="/home/pinmaker/logs/daily_report_$(date +%Y%m%d).log"
    
    {
        echo "=== Pinterest Template Generator Daily Report ==="
        echo "Date: $(date)"
        echo "Domain: $DOMAIN"
        echo ""
        echo "=== System Resources ==="
        echo "CPU Usage: $(get_cpu_usage)%"
        echo "Memory Usage: $(get_memory_usage)%"
        echo "Disk Usage: $(get_disk_usage)%"
        echo "Load Average: $(get_load_average)"
        echo ""
        echo "=== Service Status ==="
        echo "Pinmaker Service: $(systemctl is-active pinmaker)"
        echo "Nginx Service: $(systemctl is-active nginx)"
        echo "Fail2ban Service: $(systemctl is-active fail2ban)"
        echo ""
        echo "=== Process Information ==="
        echo "Python Processes: $(pgrep -f 'python.*main:app' | wc -l)"
        echo "Nginx Processes: $(pgrep nginx | wc -l)"
        echo ""
        echo "=== Network Statistics ==="
        echo "Requests (last hour): $(get_request_count)"
        echo "Active Connections: $(ss -tun | grep :443 | wc -l)"
        echo ""
        echo "=== Disk Usage by Directory ==="
        du -sh /home/pinmaker/* 2>/dev/null | sort -hr
        echo ""
        echo "=== Recent Errors (last 24h) ==="
        if [ -f "/home/pinmaker/logs/error.log" ]; then
            grep "$(date +'%Y-%m-%d' -d 'yesterday')\|$(date +'%Y-%m-%d')" /home/pinmaker/logs/error.log | tail -10
        fi
        echo ""
        echo "=== SSL Certificate Status ==="
        echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | \
            openssl x509 -noout -dates
    } > "$report_file"
    
    log_message "Daily report generated: $report_file"
}

# Main monitoring checks
log_message "Starting system monitoring check"

# Check services
check_service "pinmaker"
check_service "nginx"
check_service "fail2ban"

# Check URLs
check_url "https://$DOMAIN/health" 10
check_url "https://$DOMAIN" 15

# Check system resources
CPU_USAGE=$(get_cpu_usage)
MEMORY_USAGE=$(get_memory_usage)
DISK_USAGE=$(get_disk_usage)
LOAD_AVG=$(get_load_average)
REQUEST_COUNT=$(get_request_count)

# CPU check
if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    alert_message "High CPU usage: ${CPU_USAGE}% (threshold: ${CPU_THRESHOLD}%)" "WARNING"
fi

# Memory check
if [ "$MEMORY_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
    alert_message "High memory usage: ${MEMORY_USAGE}% (threshold: ${MEMORY_THRESHOLD}%)" "WARNING"
fi

# Disk check
check_disk_space

# Load average check
if (( $(echo "$LOAD_AVG > $LOAD_THRESHOLD" | bc -l) )); then
    alert_message "High load average: $LOAD_AVG (threshold: $LOAD_THRESHOLD)" "WARNING"
fi

# Request rate check
if [ "$REQUEST_COUNT" -gt "$REQUEST_THRESHOLD" ]; then
    alert_message "High request rate: $REQUEST_COUNT requests/minute (threshold: $REQUEST_THRESHOLD)" "INFO"
fi

# Check SSL certificate expiry
check_ssl_expiry "$DOMAIN"

# Check for errors in logs
check_log_errors

# Check process counts
check_process_count

# Clean up old files
find /home/pinmaker/uploads -type f -mtime +1 -delete 2>/dev/null || true
find /home/pinmaker/previews -type f -mtime +7 -delete 2>/dev/null || true
find /home/pinmaker/logs -name "*.log" -mtime +30 -delete 2>/dev/null || true

# Generate daily report (only at midnight)
if [ "$(date +%H%M)" = "0000" ]; then
    generate_report
fi

log_message "System monitoring check completed"
EOF

# Make monitoring script executable
chmod +x $APP_DIR/monitoring/system_monitor.sh
sudo chown $APP_USER:$APP_USER $APP_DIR/monitoring/system_monitor.sh

# Create performance monitoring script
log "Creating performance monitoring script..."
sudo tee $APP_DIR/monitoring/performance_monitor.sh > /dev/null << 'EOF'
#!/bin/bash

# Pinterest Template Generator - Performance Monitor
# This script monitors application performance metrics

LOG_FILE="/home/pinmaker/logs/performance.log"
METRICS_FILE="/home/pinmaker/logs/metrics.json"

log_metric() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# Collect system metrics
collect_metrics() {
    local timestamp=$(date +%s)
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    local memory_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
    local disk_usage=$(df /home/pinmaker | awk 'NR==2 {print $5}' | sed 's/%//')
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    
    # Application-specific metrics
    local python_memory=$(ps -o pid,vsz,rss,comm -C python3 | awk 'NR>1 {sum+=$3} END {print sum+0}')
    local nginx_connections=$(ss -tun | grep :443 | wc -l)
    
    # Create JSON metrics
    cat > $METRICS_FILE << METRICS_EOF
{
    "timestamp": $timestamp,
    "datetime": "$(date -Iseconds)",
    "system": {
        "cpu_usage": $cpu_usage,
        "memory_usage": $memory_usage,
        "disk_usage": $disk_usage,
        "load_average": $load_avg
    },
    "application": {
        "python_memory_mb": $python_memory,
        "nginx_connections": $nginx_connections,
        "service_status": "$(systemctl is-active pinmaker)"
    },
    "files": {
        "uploads_count": $(find /home/pinmaker/uploads -type f | wc -l),
        "templates_count": $(find /home/pinmaker/templates -type f | wc -l),
        "previews_count": $(find /home/pinmaker/previews -type f | wc -l),
        "fonts_count": $(find /home/pinmaker/fonts -type f | wc -l)
    }
}
METRICS_EOF
    
    log_metric "Metrics collected - CPU: ${cpu_usage}%, Memory: ${memory_usage}%, Disk: ${disk_usage}%"
}

# Response time check
check_response_time() {
    local url="https://pinmaker.kraftysprouts.com/health"
    local response_time
    
    response_time=$(curl -o /dev/null -s -w "%{time_total}" "$url")
    
    if (( $(echo "$response_time > 5.0" | bc -l) )); then
        log_metric "WARNING: Slow response time: ${response_time}s"
    else
        log_metric "Response time: ${response_time}s"
    fi
}

# Main execution
collect_metrics
check_response_time
EOF

chmod +x $APP_DIR/monitoring/performance_monitor.sh
sudo chown $APP_USER:$APP_USER $APP_DIR/monitoring/performance_monitor.sh

# Create log analysis script
log "Creating log analysis script..."
sudo tee $APP_DIR/monitoring/log_analyzer.sh > /dev/null << 'EOF'
#!/bin/bash

# Pinterest Template Generator - Log Analyzer
# This script analyzes logs and generates insights

APP_LOG="/home/pinmaker/logs/app.log"
ACCESS_LOG="/var/log/nginx/pinmaker_access.log"
ERROR_LOG="/var/log/nginx/pinmaker_error.log"
ANALYSIS_LOG="/home/pinmaker/logs/log_analysis.log"

analyze_access_log() {
    if [ ! -f "$ACCESS_LOG" ]; then
        return
    fi
    
    echo "=== Access Log Analysis (Last 24 Hours) ===" >> $ANALYSIS_LOG
    echo "Date: $(date)" >> $ANALYSIS_LOG
    echo "" >> $ANALYSIS_LOG
    
    # Total requests
    local total_requests=$(grep "$(date +'%d/%b/%Y')" "$ACCESS_LOG" | wc -l)
    echo "Total Requests: $total_requests" >> $ANALYSIS_LOG
    
    # Top IPs
    echo "Top 10 IP Addresses:" >> $ANALYSIS_LOG
    grep "$(date +'%d/%b/%Y')" "$ACCESS_LOG" | awk '{print $1}' | sort | uniq -c | sort -nr | head -10 >> $ANALYSIS_LOG
    echo "" >> $ANALYSIS_LOG
    
    # Top endpoints
    echo "Top 10 Endpoints:" >> $ANALYSIS_LOG
    grep "$(date +'%d/%b/%Y')" "$ACCESS_LOG" | awk '{print $7}' | sort | uniq -c | sort -nr | head -10 >> $ANALYSIS_LOG
    echo "" >> $ANALYSIS_LOG
    
    # Status codes
    echo "Status Code Distribution:" >> $ANALYSIS_LOG
    grep "$(date +'%d/%b/%Y')" "$ACCESS_LOG" | awk '{print $9}' | sort | uniq -c | sort -nr >> $ANALYSIS_LOG
    echo "" >> $ANALYSIS_LOG
    
    # User agents
    echo "Top 5 User Agents:" >> $ANALYSIS_LOG
    grep "$(date +'%d/%b/%Y')" "$ACCESS_LOG" | awk -F'"' '{print $6}' | sort | uniq -c | sort -nr | head -5 >> $ANALYSIS_LOG
    echo "" >> $ANALYSIS_LOG
}

analyze_error_log() {
    if [ ! -f "$ERROR_LOG" ]; then
        return
    fi
    
    echo "=== Error Log Analysis (Last 24 Hours) ===" >> $ANALYSIS_LOG
    
    # Error count
    local error_count=$(grep "$(date +'%Y/%m/%d')" "$ERROR_LOG" | wc -l)
    echo "Total Errors: $error_count" >> $ANALYSIS_LOG
    
    if [ "$error_count" -gt 0 ]; then
        echo "Recent Errors:" >> $ANALYSIS_LOG
        grep "$(date +'%Y/%m/%d')" "$ERROR_LOG" | tail -10 >> $ANALYSIS_LOG
    fi
    echo "" >> $ANALYSIS_LOG
}

analyze_app_log() {
    if [ ! -f "$APP_LOG" ]; then
        return
    fi
    
    echo "=== Application Log Analysis (Last 24 Hours) ===" >> $ANALYSIS_LOG
    
    # Error patterns
    local app_errors=$(grep "$(date +'%Y-%m-%d')" "$APP_LOG" | grep -i "error\|exception\|failed" | wc -l)
    echo "Application Errors: $app_errors" >> $ANALYSIS_LOG
    
    if [ "$app_errors" -gt 0 ]; then
        echo "Recent Application Errors:" >> $ANALYSIS_LOG
        grep "$(date +'%Y-%m-%d')" "$APP_LOG" | grep -i "error\|exception\|failed" | tail -5 >> $ANALYSIS_LOG
    fi
    echo "" >> $ANALYSIS_LOG
}

# Clear previous analysis
> $ANALYSIS_LOG

# Run analysis
analyze_access_log
analyze_error_log
analyze_app_log

echo "Log analysis completed: $ANALYSIS_LOG"
EOF

chmod +x $APP_DIR/monitoring/log_analyzer.sh
sudo chown $APP_USER:$APP_USER $APP_DIR/monitoring/log_analyzer.sh

# Configure cron jobs for monitoring
log "Setting up monitoring cron jobs..."

# Add monitoring cron jobs for the app user
(crontab -u $APP_USER -l 2>/dev/null; cat << 'CRON_EOF'
# Pinterest Template Generator Monitoring
# System monitoring every 5 minutes
*/5 * * * * /home/pinmaker/monitoring/system_monitor.sh

# Performance monitoring every minute
* * * * * /home/pinmaker/monitoring/performance_monitor.sh

# Log analysis daily at 1 AM
0 1 * * * /home/pinmaker/monitoring/log_analyzer.sh

# Backup daily at 2 AM
0 2 * * * /home/pinmaker/backup.sh

# Clean up old monitoring logs weekly
0 3 * * 0 find /home/pinmaker/logs -name "daily_report_*.log" -mtime +30 -delete
CRON_EOF
) | crontab -u $APP_USER -

# Configure fail2ban for additional security
log "Configuring fail2ban..."
sudo tee /etc/fail2ban/jail.d/pinmaker.conf > /dev/null << 'EOF'
[pinmaker-auth]
enabled = true
port = http,https
filter = pinmaker-auth
logpath = /var/log/nginx/pinmaker_access.log
maxretry = 5
bantime = 3600
findtime = 600

[pinmaker-dos]
enabled = true
port = http,https
filter = pinmaker-dos
logpath = /var/log/nginx/pinmaker_access.log
maxretry = 100
bantime = 600
findtime = 60
EOF

# Create fail2ban filters
sudo tee /etc/fail2ban/filter.d/pinmaker-auth.conf > /dev/null << 'EOF'
[Definition]
failregex = ^<HOST> .* "(GET|POST) /api/.* HTTP/.*" 401 .*$
            ^<HOST> .* "(GET|POST) /api/.* HTTP/.*" 403 .*$
ignoreregex =
EOF

sudo tee /etc/fail2ban/filter.d/pinmaker-dos.conf > /dev/null << 'EOF'
[Definition]
failregex = ^<HOST> .* "(GET|POST) .* HTTP/.*" 200 .*$
ignoreregex =
EOF

# Configure unattended upgrades for security updates
log "Configuring automatic security updates..."
sudo tee /etc/apt/apt.conf.d/50unattended-upgrades > /dev/null << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::Package-Blacklist {
    // Add packages to blacklist if needed
};

Unattended-Upgrade::DevRelease "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
EOF

sudo tee /etc/apt/apt.conf.d/20auto-upgrades > /dev/null << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
EOF

# Create monitoring dashboard script
log "Creating monitoring dashboard..."
sudo tee $APP_DIR/monitoring/dashboard.sh > /dev/null << 'EOF'
#!/bin/bash

# Pinterest Template Generator - Monitoring Dashboard
# This script displays a real-time monitoring dashboard

clear

while true; do
    clear
    echo "==========================================="
    echo "Pinterest Template Generator - Dashboard"
    echo "==========================================="
    echo "Last Updated: $(date)"
    echo ""
    
    # System Information
    echo "=== SYSTEM STATUS ==="
    echo "Uptime: $(uptime -p)"
    echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
    echo "CPU Usage: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')%"
    echo "Memory Usage: $(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
    echo "Disk Usage: $(df /home/pinmaker | awk 'NR==2 {print $5}')"
    echo ""
    
    # Service Status
    echo "=== SERVICE STATUS ==="
    printf "Pinmaker: "
    if systemctl is-active --quiet pinmaker; then
        echo "✓ Running"
    else
        echo "✗ Stopped"
    fi
    
    printf "Nginx: "
    if systemctl is-active --quiet nginx; then
        echo "✓ Running"
    else
        echo "✗ Stopped"
    fi
    
    printf "Fail2ban: "
    if systemctl is-active --quiet fail2ban; then
        echo "✓ Running"
    else
        echo "✗ Stopped"
    fi
    echo ""
    
    # Application Metrics
    echo "=== APPLICATION METRICS ==="
    echo "Python Processes: $(pgrep -f 'python.*main:app' | wc -l)"
    echo "Active Connections: $(ss -tun | grep :443 | wc -l)"
    echo "Uploads: $(find /home/pinmaker/uploads -type f | wc -l) files"
    echo "Templates: $(find /home/pinmaker/templates -type f | wc -l) files"
    echo "Previews: $(find /home/pinmaker/previews -type f | wc -l) files"
    echo "Custom Fonts: $(find /home/pinmaker/fonts -type f | wc -l) files"
    echo ""
    
    # Recent Activity
    echo "=== RECENT ACTIVITY ==="
    if [ -f "/var/log/nginx/pinmaker_access.log" ]; then
        echo "Last 5 requests:"
        tail -5 /var/log/nginx/pinmaker_access.log | awk '{print $1, $4, $7, $9}'
    fi
    echo ""
    
    # Alerts
    echo "=== RECENT ALERTS ==="
    if [ -f "/home/pinmaker/logs/alerts.log" ]; then
        tail -3 /home/pinmaker/logs/alerts.log
    else
        echo "No recent alerts"
    fi
    echo ""
    
    echo "Press Ctrl+C to exit"
    sleep 10
done
EOF

chmod +x $APP_DIR/monitoring/dashboard.sh
sudo chown $APP_USER:$APP_USER $APP_DIR/monitoring/dashboard.sh

# Restart services
log "Restarting monitoring services..."
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Test monitoring setup
log "Testing monitoring setup..."
sudo -u $APP_USER $APP_DIR/monitoring/system_monitor.sh
sudo -u $APP_USER $APP_DIR/monitoring/performance_monitor.sh

log "Monitoring setup completed successfully!"
echo ""
echo "==========================================="
echo "Monitoring Setup Complete"
echo "==========================================="
echo "Monitoring Scripts:"
echo "  System Monitor: $APP_DIR/monitoring/system_monitor.sh"
echo "  Performance Monitor: $APP_DIR/monitoring/performance_monitor.sh"
echo "  Log Analyzer: $APP_DIR/monitoring/log_analyzer.sh"
echo "  Dashboard: $APP_DIR/monitoring/dashboard.sh"
echo ""
echo "Log Files:"
echo "  System Monitor: $APP_DIR/logs/monitor.log"
echo "  Performance: $APP_DIR/logs/performance.log"
echo "  Alerts: $APP_DIR/logs/alerts.log"
echo "  Analysis: $APP_DIR/logs/log_analysis.log"
echo ""
echo "Cron Jobs:"
echo "  System monitoring: Every 5 minutes"
echo "  Performance monitoring: Every minute"
echo "  Log analysis: Daily at 1 AM"
echo "  Backup: Daily at 2 AM"
echo ""
echo "Commands:"
echo "  View dashboard: $APP_DIR/monitoring/dashboard.sh"
echo "  Check alerts: tail -f $APP_DIR/logs/alerts.log"
echo "  View metrics: cat $APP_DIR/logs/metrics.json"
echo "  Manual monitoring: $APP_DIR/monitoring/system_monitor.sh"
echo ""
log "Monitoring is now active! 📊"