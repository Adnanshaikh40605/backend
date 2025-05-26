#!/bin/bash

set -e

# Parse database URL from environment
if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL environment variable is not set"
  exit 1
fi

# Extract host and port from DATABASE_URL
HOST=$(echo $DATABASE_URL | awk -F[@/:] '{print $4}')
PORT=$(echo $DATABASE_URL | awk -F[@/:] '{print $5}')

# If port is not specified, use default PostgreSQL port
if [ -z "$PORT" ]; then
  PORT=5432
fi

# Wait for database to be ready
echo "Waiting for PostgreSQL at $HOST:$PORT..."

until nc -z $HOST $PORT; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing command" 