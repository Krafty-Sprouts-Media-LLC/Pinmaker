# Gunicorn configuration for Pinmaker
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes - optimized for 4GB RAM
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 100
max_requests = 500
max_requests_jitter = 50
preload_app = True
worker_tmp_dir = "/dev/shm"

# Logging
accesslog = "/opt/Pinmaker/logs/gunicorn_access.log"
errorlog = "/opt/Pinmaker/logs/gunicorn_error.log"
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
