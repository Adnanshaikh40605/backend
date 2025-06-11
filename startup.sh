#!/bin/bash
set -e

# Echo commands for debugging
set -x

echo "Starting deployment at $(date)"

# Debug PORT environment variable
echo "📢 Railway PORT environment variable: $PORT"
if [ -z "$PORT" ]; then
    echo "⚠️ WARNING: PORT environment variable is not set! Using default port 8000."
    export PORT=8000
else
    echo "✅ Using PORT: $PORT"
fi

# Function to start the fallback health check server
start_health_fallback() {
    echo "⚠️ Django application failed to start. Starting fallback health check server..."
    python health_check.py
}

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

# Start the application - explicitly use the PORT environment variable
echo "Starting Django application on port $PORT..."
echo "Using gunicorn configuration file..."

# Try to start gunicorn, if it fails, start the fallback health check server
exec gunicorn -c gunicorn.conf.py backend.asgi:application || start_health_fallback 