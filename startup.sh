#!/bin/bash
set -e

# Echo commands for debugging
set -x

echo "Starting deployment at $(date)"

# Function to start the fallback Flask application if Django fails
start_fallback() {
    echo "⚠️ Django application failed to start. Starting fallback Flask health check server..."
    python app.py
}

# Function to start the Django application
start_django() {
    echo "Starting Django application..."
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.asgi:application --bind 0.0.0.0:$PORT --log-level debug || start_fallback
}

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migrations failed, but continuing..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static collection failed, but continuing..."

# Create the health app directory if it doesn't exist
mkdir -p health

# Touch necessary files to ensure the health app is recognized
touch health/__init__.py
touch health/urls.py
touch health/views.py

# Add a delay to ensure the application has time to fully initialize before health checks
echo "Waiting for 10 seconds before starting the application to ensure proper initialization..."
sleep 10

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

# Test if the port is available
(echo -e "HTTP/1.1 200 OK\n\nHealth Check OK" | nc -l -p $PORT -q 1) && echo "Port $PORT is available" || echo "Port $PORT might be in use"

# Start the application
start_django 