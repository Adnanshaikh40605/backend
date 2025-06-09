#!/usr/bin/env python
"""
Startup script for Django application on Railway.
"""
import os
import sys
import subprocess
import traceback

def main():
    """Main entry point for the application."""
    try:
        # Print debug information
        print("=" * 50)
        print("DJANGO APPLICATION STARTUP")
        print("=" * 50)
        print(f"Python version: {sys.version}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir('.')}")
        
        # Get PORT from environment
        port = os.environ.get('PORT', '8000')
        print(f"Using PORT: {port}")
        
        # Ensure gunicorn is installed
        try:
            import gunicorn
            print(f"Gunicorn version: {gunicorn.__version__}")
        except ImportError:
            print("Installing gunicorn...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "gunicorn"])
            import gunicorn
            print(f"Gunicorn installed: {gunicorn.__version__}")
        
        # Check Django installation
        try:
            import django
            print(f"Django version: {django.get_version()}")
        except ImportError:
            print("Django not found!")
            return 1
        
        # Check if wsgi.py exists
        if not os.path.exists('backend/wsgi.py'):
            print("Error: backend/wsgi.py not found!")
            print(f"Files in backend directory: {os.listdir('backend')}")
            return 1
        
        # Start gunicorn
        print("Starting gunicorn server...")
        cmd = [
            "gunicorn",
            "backend.wsgi:application",
            f"--bind=0.0.0.0:{port}",
            "--log-level=debug",
            "--workers=2",
            "--timeout=120"
        ]
        print(f"Command: {' '.join(cmd)}")
        
        # Execute gunicorn
        os.execvp("gunicorn", cmd)
        
    except Exception as e:
        print(f"Error in run.py: {e}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 