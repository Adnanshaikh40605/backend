FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create the simplified.sh script
RUN echo '#!/bin/bash\n\
echo "Running simplified.sh script"\n\
echo "Current directory: $(pwd)"\n\
echo "Content of directory: $(ls -la)"\n\
\n\
echo "PORT environment variable is: $PORT"\n\
\n\
# Apply migrations\n\
echo "Applying migrations..."\n\
python manage.py migrate --noinput\n\
\n\
# Collect static files\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
# Start Django on the correct network interface\n\
echo "Starting Django on 0.0.0.0:$PORT..."\n\
python manage.py runserver 0.0.0.0:$PORT' > simplified.sh

# Make the script executable
RUN chmod +x simplified.sh

# Create static directory with health check file
RUN mkdir -p staticfiles
RUN echo "OK" > staticfiles/index.html

# Expose the port
EXPOSE 8080

# Start the Django server
CMD ["bash", "simplified.sh"] 