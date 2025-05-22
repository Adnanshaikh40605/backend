# Use official Python image
FROM python:3.10-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make build.sh executable
RUN chmod +x build.sh

# Run the build script to collect static files
RUN ./build.sh

# Start Gunicorn server
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --log-file - --log-level info --timeout 120 --workers 2 