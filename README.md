# Blog CMS Backend

A Django-based backend API for a Blog Content Management System.

## Features

- RESTful API for blog posts and comments
- Admin panel for content management
- Rich text editing with CKEditor 5
- API documentation with Swagger UI
- CORS support for frontend integration

## Deployment

This project is configured to deploy on Railway.app.

### Railway Deployment

1. Push your code to GitHub
2. Create a new project on Railway and connect it to your GitHub repository
3. Railway will automatically detect the Python project and deploy it
4. Set the required environment variables in the Railway dashboard (see below)

### Environment Variables

The following environment variables should be set in your Railway project:

```json
{
  "DEBUG": "False",
  "SECRET_KEY": "your-secret-key-should-be-changed-in-production",
  "ALLOWED_HOSTS": "backend-production-92ae.up.railway.app,localhost,127.0.0.1",
  "BACKEND_URL": "https://backend-production-92ae.up.railway.app",
  "CORS_ALLOW_ALL_ORIGINS": "True",
  "CORS_ALLOWED_ORIGINS": "http://localhost:3000,http://localhost:5173,https://backend-production-92ae.up.railway.app",
  "CSRF_TRUSTED_ORIGINS": "http://localhost:3000,http://localhost:5173,https://backend-production-92ae.up.railway.app",
  "PORT": "8000",
  "PYTHONUNBUFFERED": "1",
  "DJANGO_LOG_LEVEL": "INFO"
}
```

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Run the development server: `python manage.py runserver`

## API Documentation

API documentation is available at `/api/docs/` when the server is running.

## Health Check

A health check endpoint is available at `/health/` to verify the server is running correctly.

## Backend URL

The backend is deployed at: https://backend-production-92ae.up.railway.app/