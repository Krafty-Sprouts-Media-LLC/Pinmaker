import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 120
keepalive = 2

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
