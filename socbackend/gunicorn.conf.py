import multiprocessing

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
threads = 2
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'

# Bind
bind = '0.0.0.0:8000' 