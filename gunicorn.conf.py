import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes (optimized for 4GB RAM)
workers = 2  # Fixed to 2 workers for memory efficiency
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 100  # Reduced for memory efficiency
max_requests = 500  # Restart workers after 500 requests to prevent memory leaks
max_requests_jitter = 50
preload_app = True
timeout = 120
keepalive = 2
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance

# Logging
accesslog = "/opt/Pinmaker/logs/access.log"
errorlog = "/opt/Pinmaker/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "pinmaker"

# Server mechanics
daemon = False
pidfile = "/opt/Pinmaker/logs/gunicorn.pid"
user = "pinmaker"
group = "pinmaker"
tmp_upload_dir = None

# SSL (handled by nginx)
keyfile = None
certfile = None
