# Blog CMS

A full-featured Content Management System built with Django REST Framework backend and React frontend.

## Live Demo

- **Frontend**: [https://dohblog.vercel.app](https://dohblog.vercel.app)
- **Backend API**: [https://backend-production-49ec.up.railway.app](https://backend-production-49ec.up.railway.app)

## Features

- **User Authentication**: JWT-based authentication system
- **Content Management**: Create, edit, and delete blog posts
- **Image Uploads**: Support for image uploads using Django CKEditor 5
- **Comments System**: User comments with moderation features
- **Responsive Design**: Mobile-friendly interface
- **CORS Support**: Properly configured for cross-origin requests
- **API Documentation**: Swagger UI for API exploration
- **Health Check System**: Robust health monitoring with fallback mechanisms

## Tech Stack

### Backend
- Django 4.2
- Django REST Framework
- PostgreSQL (in production)
- SQLite (for development)
- JWT Authentication
- Django CKEditor 5
- Whitenoise for static file serving
- CORS headers middleware
- Deployed on Railway

### Frontend
- React
- Tailwind CSS
- Axios for API requests
- React Router for navigation
- Context API for state management
- Deployed on Vercel

## Local Development Setup

### Prerequisites
- Python 3.9+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Clone the repository
```bash
git clone <repository-url>
cd blog-cms
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings (for local development with SQLite)
# DATABASE_URL=sqlite:///db.sqlite3

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000
CORS_ALLOW_ALL_ORIGINS=False
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
DJANGO_LOG_LEVEL=DEBUG
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create a superuser
```bash
python manage.py createsuperuser
```

7. Run the development server
```bash
python manage.py runserver
```

The backend will be available at http://localhost:8000.

### Frontend Setup

The frontend code is not included in this repository. It's available as a separate project deployed at [https://dohblog.vercel.app](https://dohblog.vercel.app).

## API Documentation

API documentation is available at `/api/docs/` when the server is running. This provides a Swagger UI interface to explore and test all available endpoints.

## Deployment

### Backend Deployment on Railway

1. Create a Railway account and project
2. Connect your GitHub repository
3. Set up the required environment variables in Railway:
   - SECRET_KEY
   - DEBUG=False
   - ALLOWED_HOSTS=*.up.railway.app,your-railway-app-url,localhost,127.0.0.1
   - CORS_ALLOWED_ORIGINS=your-frontend-url,http://localhost:3000
   - CSRF_TRUSTED_ORIGINS=your-railway-app-url,your-frontend-url,http://localhost:3000

4. Railway will automatically deploy your application using the `railway.toml` configuration file.

### Health Check System

The application includes a robust health check system at `/health/` that:

1. Verifies database connectivity
2. Checks server status
3. Monitors port availability
4. Provides detailed diagnostics
5. Includes a fallback mechanism using Flask if the Django app fails

To test the health check locally:
```bash
curl http://localhost:8000/health/
```

The health check system is designed to work seamlessly with Railway's deployment monitoring.

### Frontend Deployment on Vercel

See the frontend repository for deployment instructions.

## CORS Configuration

This application includes custom CORS middleware to handle cross-origin requests properly, especially for authentication endpoints. The main configuration includes:

- Specific allowed origins instead of wildcard (*) to support credentials
- Proper handling of preflight requests
- Custom middleware to add CORS headers to all responses

## License

MIT

## Author

S K Adnan