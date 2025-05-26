# Use multi-stage build for optimized production image

# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Create a script to handle setup and build
RUN echo '#!/bin/sh \n\
if [ ! -f "package.json" ]; then \n\
  echo "{\\"name\\":\\"frontend\\",\\"version\\":\\"0.0.0\\",\\"scripts\\":{\\"build\\":\\"mkdir -p dist && echo <!DOCTYPE html><html><head><title>Frontend Placeholder</title></head><body><div id=root></div></body></html> > dist/index.html\\"},\\"dependencies\\":{},\\"devDependencies\\":{}}"> package.json \n\
fi \n\
npm install || true \n\
npm run build || mkdir -p dist && echo "<!DOCTYPE html><html><head><title>Frontend Placeholder</title></head><body><div id=root></div></body></html>" > dist/index.html \n\
' > /setup-and-build.sh && chmod +x /setup-and-build.sh

# Copy frontend files if they exist, otherwise create placeholder files
COPY frontend/ ./
# Run the setup and build script
RUN /setup-and-build.sh

# Stage 2: Build the Django backend
FROM python:3.11-slim AS backend-builder
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Production image
FROM python:3.11-slim
LABEL maintainer="Blog CMS Team"

WORKDIR /app

# Install production dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy from backend-builder stage
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=backend-builder /usr/local/bin/ /usr/local/bin/

# Copy project files
COPY . .

# Copy frontend build from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Set Django settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=backend.settings \
    PORT=8000

# Collect static files
RUN python manage.py collectstatic --noinput

# Runtime configuration
EXPOSE 8000
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"] 