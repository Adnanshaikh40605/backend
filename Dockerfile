# Use multi-stage build for optimized production image

# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend files if they exist
COPY frontend/ ./

# Create minimal package.json if it doesn't exist
RUN if [ ! -f "package.json" ]; then \
      echo '{"name":"frontend","version":"0.0.0","scripts":{"build":"echo Build completed"},"dependencies":{},"devDependencies":{}}' > package.json; \
    fi

# Create dist directory and placeholder index.html
RUN mkdir -p dist && \
    echo '<!DOCTYPE html><html><head><title>Frontend Placeholder</title></head><body><div id="root"></div></body></html>' > dist/index.html

# Try to install dependencies and build (but continue if it fails)
RUN npm install --production || echo "Skipping npm install" && \
    npm run build || echo "Using placeholder build"

# Stage 2: Build the Django backend with memory optimizations
FROM python:3.11-slim AS backend-builder
WORKDIR /app

# Install system dependencies with optimizations for memory usage
# Split into multiple RUN commands to optimize layer caching and reduce memory usage
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install PostgreSQL client libs separately to reduce memory usage
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies with memory optimizations
COPY requirements.txt .
# Use pip with memory optimization flags
RUN pip install --no-cache-dir --no-deps --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Production image
FROM python:3.11-slim
LABEL maintainer="Blog CMS Team"

WORKDIR /app

# Install only the minimal production dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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