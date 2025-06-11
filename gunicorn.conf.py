"""Gunicorn configuration file for Django ASGI application."""
import os
import multiprocessing
import sys

# Log the PORT environment variable
port = os.environ.get('PORT', '8000')
print(f"Gunicorn config: PORT environment variable is set to '{port}'")

# Bind to 0.0.0.0 to ensure the app is accessible from outside the container
bind = f"0.0.0.0:{port}"
print(f"Gunicorn will bind to: {bind}")

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

# Log function to print important information during startup
def on_starting(server):
    print(f"Gunicorn starting with PORT={port}", file=sys.stderr)
    print(f"Binding to: {bind}", file=sys.stderr) 