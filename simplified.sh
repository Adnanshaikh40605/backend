#!/bin/bash
set -e

echo "=== Starting Django ==="
echo "Current directory: $(pwd)"
echo "PORT environment variable is: $PORT"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

mkdir -p staticfiles
echo '{"status": "ok"}' > staticfiles/health.json

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
PYTHONUNBUFFERED=1 gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level debug 