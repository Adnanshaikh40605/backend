"""Gunicorn configuration file for Django ASGI application."""
import os
import multiprocessing
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("gunicorn.conf")

# Log the PORT environment variable
port = os.environ.get('PORT', '8000')
logger.info(f"Gunicorn config: PORT environment variable is set to '{port}'")

# Bind to 0.0.0.0 to allow external access
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
logger.info(f"Gunicorn will bind to: {bind}")

# Use multiple workers based on CPU cores
workers = os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
logger.info(f"Gunicorn will use {workers} workers")

# Set worker timeout to 120 seconds
timeout = 120

# Enable keepalive for better performance
keepalive = 5

# Enable access logging
accesslog = "-"
errorlog = "-"

# Set log level
loglevel = "info"

# Use standard sync worker class for Django WSGI
worker_class = "sync"

# Preload the application for better performance
preload_app = True

# Prevent the worker from writing directly to stdout/stderr
capture_output = True

# Print configuration on startup
print_config = True

# Don't daemonize to ensure Railway can see logs
daemon = False

# Log function to print important information during startup
def on_starting(server):
    logger.info(f"Gunicorn starting with PORT={port}")
    logger.info(f"Binding to: {bind}")
    logger.info(f"Worker class: {worker_class}")
    logger.info(f"Worker count: {workers}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Print all environment variables for debugging (excluding sensitive ones)
    logger.info("Environment variables:")
    for key, value in os.environ.items():
        if 'SECRET' not in key.upper() and 'PASSWORD' not in key.upper() and 'KEY' not in key.upper():
            logger.info(f"  {key}: {value}")

def on_exit(server):
    logger.info("Gunicorn is shutting down")

def worker_abort(worker):
    logger.error(f"Worker {worker.pid} aborted!")

def worker_exit(server, worker):
    logger.warning(f"Worker {worker.pid} exited (signal: {worker.signal})")

def post_fork(server, worker):
    logger.info(f"Worker {worker.pid} forked") 