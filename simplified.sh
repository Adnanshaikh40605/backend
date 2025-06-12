#!/bin/bash
set -e

echo "=== Starting Django ==="
echo "Current directory: $(pwd)"
echo "Content of directory: $(ls -la)"

echo "PORT environment variable is: $PORT"

# Check if wsgi.py exists and show its content
echo "Checking wsgi.py file:"
if [ -f wsgi.py ]; then
    echo "wsgi.py exists"
    echo "First 10 lines of wsgi.py:"
    head -n 10 wsgi.py
else
    echo "ERROR: wsgi.py not found"
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create health check file as backup
mkdir -p staticfiles
echo '{"status": "ok"}' > staticfiles/health.json

# Configure environment variables
export DJANGO_SETTINGS_MODULE=backend.settings
export PYTHONPATH=/app
export ALLOWED_HOSTS="*"

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
PYTHONUNBUFFERED=1 gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level debug --timeout 120 --error-logfile - 