import multiprocessing

# Gunicorn configuration
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2
timeout = 120

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# SSL (if needed)
# keyfile = "/etc/certs/privkey.pem"
# certfile = "/etc/certs/fullchain.pem" 