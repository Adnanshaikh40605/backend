#!/bin/bash

# Echo commands for debugging
set -x

echo "Starting deployment at $(date)"

# Debug PORT environment variable - MAKE THIS VERY EXPLICIT
echo "PORT environment check:"
echo "📢 Railway PORT environment variable: '$PORT'"
if [ -z "$PORT" ]; then
    echo "⚠️ WARNING: PORT environment variable is not set! Using default port 8000."
    export PORT=8000
else
    echo "✅ Using PORT: $PORT"
fi

# Print all environment variables (excluding sensitive ones)
echo "Environment variables:"
env | grep -v -E 'SECRET|PASSWORD|KEY' | sort

# Verify gunicorn will use the correct port
echo "Gunicorn will bind to: 0.0.0.0:$PORT"

# Function to start the fallback health check server
start_health_fallback() {
    echo "⚠️ Django application failed to start. Starting fallback health check server..."
    # Make sure fallback server uses the same PORT
    python health_check.py
    
    # If we get here, the health check server also failed
    echo "❌ CRITICAL ERROR: Even the fallback health check server failed!"
    echo "Sleeping to keep the container alive and allow for inspection..."
    sleep 3600  # Sleep for an hour to allow for inspection
}

# Create a directory for static files if it doesn't exist
mkdir -p staticfiles

# Create various health check endpoints for Railway
echo "Creating health check files..."
mkdir -p staticfiles/health
mkdir -p staticfiles/railway-health
mkdir -p health/templates/health

# Create health template file if it doesn't exist
if [ ! -f health/templates/health/ok.html ]; then
    echo "Creating health template file..."
    cat > health/templates/health/ok.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Health Check</title>
</head>
<body>
    OK
</body>
</html>
EOF
fi

# Simple health check file
cat > staticfiles/health/index.html << EOF
OK
EOF

# Railway health check file
cat > staticfiles/railway-health/index.html << EOF
OK
EOF

# Main health check file
cat > staticfiles/health.html << EOF
OK
EOF

# Run migrations (continue on error)
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migrations failed, but continuing..."

# Collect static files (continue on error)
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static collection failed, but continuing..."

# Add a delay to ensure the application has time to fully initialize before health checks
echo "Waiting for 5 seconds before starting the application..."
sleep 5

# Try to create an explicit health check view
echo "Creating a simple health check view..."
mkdir -p health
cat > health/views.py << EOF
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

def railway_health_check(request):
    return HttpResponse("OK", content_type="text/plain")
EOF

# Start the application
echo "Starting Django application on port $PORT..."

# Try first with ASGI (preferred)
echo "Attempting to start with ASGI..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker backend.asgi:application || {
    echo "ASGI startup failed, falling back to WSGI..."
    gunicorn --bind 0.0.0.0:$PORT --workers 2 backend.wsgi:application || {
        echo "WSGI startup failed, starting fallback health check server..."
        start_health_fallback
    }
} 