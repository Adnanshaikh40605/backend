#!/bin/bash
set -e

echo "=== Starting Django ==="
echo "Current directory: $(pwd)"
echo "Content of directory: $(ls -la)"

echo "PORT environment variable is: $PORT"

# Test health check URL directly
echo "Testing health check URL with curl:"
python -c "import django; django.setup(); from django.urls import reverse; from django.test import Client; c = Client(); response = c.get('/health'); print(f'Response status: {response.status_code}'); print(f'Response content: {response.content}')" || echo "Failed to test health check URL"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create health check file as backup
mkdir -p staticfiles
echo '{"status": "ok"}' > staticfiles/health.json

# Configure whitenoise to serve static files
export DJANGO_SETTINGS_MODULE=backend.settings
export PYTHONPATH=/app

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
PYTHONUNBUFFERED=1 gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level debug --timeout 120 