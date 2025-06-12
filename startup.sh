#!/bin/bash

# Echo commands for debugging
set -x

echo "Starting deployment at $(date)"

# Debug PORT environment variable
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

# Create a directory for static files if it doesn't exist
mkdir -p staticfiles

# Create various health check endpoints
echo "Creating health check files..."
mkdir -p staticfiles/health
mkdir -p staticfiles/railway-health

# Simple health check files
cat > staticfiles/health/index.html << EOF
OK
EOF

cat > staticfiles/railway-health/index.html << EOF
OK
EOF

cat > staticfiles/health.html << EOF
OK
EOF

# Run migrations (continue on error)
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migrations failed, but continuing..."

# Collect static files (continue on error)
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static collection failed, but continuing..."

# Start the application with our combined WSGI app
echo "Starting application with combined health checks on port $PORT..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi_health:application 