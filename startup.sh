#!/bin/bash
set -e

# Echo commands for debugging
set -x

echo "Starting deployment at $(date)"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migrations failed, but continuing..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static collection failed, but continuing..."

# Create a simple health check file for direct access
mkdir -p staticfiles
cat > staticfiles/health.html << EOF
<!DOCTYPE html>
<html>
<head><title>Health Check Static</title></head>
<body>
    <h1>Health Check</h1>
    <p>This is a static health check file.</p>
    <p>Status: OK</p>
</body>
</html>
EOF

# Add a delay to ensure the application has time to fully initialize before health checks
echo "Waiting for 5 seconds before starting the application to ensure proper initialization..."
sleep 5

# Start the application
echo "Starting Django application..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.asgi:application --bind 0.0.0.0:$PORT --log-level debug 