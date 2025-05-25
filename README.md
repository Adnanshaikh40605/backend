# Blog CMS Backend

A Django-based backend for a modern blog content management system with comprehensive API support.

## Features

- **Rich Content Management**: Backend support for creating and editing blog posts with CKEditor 5
- **Media Handling**: Upload and manage images with integrated image optimization
- **Comment System**: Fully-featured commenting system with moderation
- **API-Driven Architecture**: RESTful API with comprehensive Swagger documentation
- **Admin Interface**: Customized Django admin for content management

## Tech Stack

- **Django**: Web framework for building robust web applications
- **Django REST Framework**: Powerful and flexible toolkit for building Web APIs
- **CKEditor 5**: Advanced rich text editor with image upload capabilities
- **Whitenoise**: Simplified static file serving for Python web apps

## Environment Variables

For local development, create a `.env` file in the project root with the following variables:

```
# Django settings
SECRET_KEY=your-very-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
CORS_ALLOW_ALL_ORIGINS=True

# Security settings
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
```

## Railway Deployment

To deploy this application to Railway:

1. Push your code to GitHub
2. Go to [Railway](https://railway.app) and create a new project
3. Select "Deploy from GitHub" and choose your repository
4. Add a PostgreSQL database from the Railway dashboard
5. Set the following environment variables in the Railway dashboard:
   - `SECRET_KEY`: A secure random string
   - `DEBUG`: Set to "False"
   - `ALLOWED_HOSTS`: Your Railway app domain (e.g., your-app-name.up.railway.app)
   - `CORS_ALLOWED_ORIGINS`: Your frontend domain(s)
   - `CORS_ALLOW_ALL_ORIGINS`: Set to "False" in production
   - `CSRF_TRUSTED_ORIGINS`: Your frontend domain(s)

6. Railway will automatically deploy your application and set up the database connection

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - Unix/MacOS: `source env/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file using the template above
6. Run migrations: `python manage.py migrate`
7. Create a superuser: `python manage.py createsuperuser`
8. Run the development server: `python manage.py runserver`

## API Documentation

The API is documented using Swagger UI, which provides interactive documentation to explore and test the API endpoints.

- **Swagger UI**: `/api/docs/` - Interactive API exploration interface

## API Endpoints

- **Posts**: `/api/posts/`
- **Comments**: `/api/comments/`
- **Images**: `/api/images/`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 