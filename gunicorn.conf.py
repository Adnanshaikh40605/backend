"""Gunicorn configuration file for Django ASGI application."""
import os
import multiprocessing

# Bind to 0.0.0.0 to ensure the app is accessible from outside the container
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
loglevel = "debug"
accesslog = "-"  # stdout
errorlog = "-"   # stderr

# Timeout configuration
timeout = 120
graceful_timeout = 60

# Prevent the worker from writing directly to stdout/stderr
capture_output = True

# Print configuration on startup
print_config = True

# Log worker process events
# child_exit = True

# Ensure the application has time to load before accepting connections
preload_app = False 