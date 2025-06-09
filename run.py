#!/usr/bin/env python
"""
Railway deployment entry point script.
This script serves as the main entry point for Railway deployments,
handling environment variables and starting the gunicorn server.
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("railway-runner")

def main():
    """Main entry point for Railway deployment"""
    logger.info("Starting Railway deployment script")
    
    # Get PORT from environment or default to 8000
    port = os.environ.get("PORT", "8000")
    logger.info(f"Using PORT: {port}")
    
    # Print environment information
    railway_env = os.environ.get("RAILWAY_ENVIRONMENT", "development")
    railway_project = os.environ.get("RAILWAY_PROJECT_NAME", "unknown")
    railway_service = os.environ.get("RAILWAY_SERVICE_NAME", "unknown")
    
    logger.info(f"Environment: {railway_env}")
    logger.info(f"Project: {railway_project}")
    logger.info(f"Service: {railway_service}")
    
    # Check if Django can be imported
    try:
        import django
        logger.info(f"Django version: {django.get_version()}")
    except ImportError:
        logger.error("Django is not installed. Please check your requirements.txt file.")
        sys.exit(1)
    
    # Check if database URL is set
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Mask the password for logging
        masked_url = database_url.replace("://", "://***:***@", 1) if "://" in database_url else database_url
        logger.info(f"Database URL is configured: {masked_url}")
    else:
        logger.warning("DATABASE_URL is not set. Will use SQLite by default.")
    
    # Check if static files directory exists
    static_dir = Path("staticfiles")
    if not static_dir.exists():
        logger.warning("Static files directory does not exist. Running collectstatic...")
        try:
            subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to collect static files: {e}")
            # Continue anyway, as static files might be served differently
    
    # Start gunicorn
    logger.info("Starting gunicorn server...")
    cmd = [
        "gunicorn",
        "backend.wsgi:application",
        f"--bind=0.0.0.0:{port}",
        "--log-file=-",  # Log to stdout
        "--workers=2",   # Number of worker processes
        "--timeout=120"  # Timeout in seconds
    ]
    
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        # Use os.execvp to replace the current process with gunicorn
        os.execvp(cmd[0], cmd)
    except Exception as e:
        logger.error(f"Failed to start gunicorn: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 