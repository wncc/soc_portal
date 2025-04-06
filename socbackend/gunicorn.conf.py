import multiprocessing

# Worker processes - adjust based on your system's capabilities
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
threads = 2
timeout = 120

# Logging
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# Bind to all interfaces on port 8000
bind = '0.0.0.0:8000'

# Application path
wsgi_app = 'socbackend.wsgi:application' 