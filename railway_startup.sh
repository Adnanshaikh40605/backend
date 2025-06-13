#!/bin/bash
set -e

echo "=== Starting Railway Application ==="
echo "Current directory: $(pwd)"

# Set default port if not provided
export PORT=${PORT:-8000}
export HEALTH_PORT=8081

echo "PORT environment variable is: $PORT"
echo "HEALTH_PORT set to: $HEALTH_PORT"

# Start the standalone health server in the background
echo "Starting standalone health server..."
python standalone_health.py &

# Wait a moment to ensure health server starts
sleep 2

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create health check file as backup
mkdir -p staticfiles
echo '{"status": "ok"}' > staticfiles/health.json

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
PYTHONUNBUFFERED=1 gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level debug --timeout 120 