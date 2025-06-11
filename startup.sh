#!/bin/bash
set -e

# Echo commands for debugging
set -x

echo "Starting deployment at $(date)"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application using the configuration from Procfile
echo "Starting the application..."
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.asgi:application --bind 0.0.0.0:$PORT --log-level debug 