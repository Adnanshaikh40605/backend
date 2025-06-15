#!/bin/bash

# Exit on error
set -e

# Define functions for different deployment tasks
function install_dependencies() {
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
}

function run_migrations() {
    echo "Running migrations..."
    python manage.py migrate
}

function collect_static() {
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
}

function start_server() {
    echo "Starting the application..."
    gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}
}

# Main deployment process
echo "Starting deployment process..."

# Process command line arguments
case "$1" in
    build)
        install_dependencies
        run_migrations
        collect_static
        ;;
    start)
        start_server
        ;;
    full)
        install_dependencies
        run_migrations
        collect_static
        start_server
        ;;
    *)
        echo "Usage: $0 {build|start|full}"
        echo "  build: Install dependencies, run migrations, and collect static files"
        echo "  start: Start the application server"
        echo "  full: Complete deployment process (build + start)"
        exit 1
        ;;
esac

echo "Deployment task completed!" 