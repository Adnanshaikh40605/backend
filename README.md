# Blog CMS Backend

A Django-based backend API for a Blog Content Management System.

## Features

- RESTful API for blog posts and comments
- Admin panel for content management
- Rich text editing with CKEditor 5
- API documentation with Swagger UI
- CORS support for frontend integration
- PostgreSQL database integration

## Deployment

This project is configured to deploy on Railway.app with PostgreSQL.

### Railway Deployment

1. Push your code to GitHub
2. Create a new project on Railway and connect it to your GitHub repository
3. Add a PostgreSQL database to your project
4. Railway will automatically detect the Python project and deploy it
5. Set the required environment variables in the Railway dashboard (see below)

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
  "DATABASE_URL": "postgresql://postgres:password@postgres.railway.internal:5432/railway",
  "PORT": "8000",
  "PYTHONUNBUFFERED": "1",
  "DJANGO_LOG_LEVEL": "INFO"
}
```

### PostgreSQL Setup

This project uses PostgreSQL as the database. The connection is configured using the `DATABASE_URL` environment variable.

For Railway deployment:
- Use the internal URL: `postgresql://postgres:password@postgres.railway.internal:5432/railway`

For local development with Railway PostgreSQL:
1. Get the external connection URL from Railway dashboard
2. Format: `postgresql://postgres:password@switchyard.proxy.rlwy.net:port/railway`
3. Set this as your `DATABASE_URL` environment variable in your `.env` file

To ensure the PostgreSQL database is used:
1. Create a `.env` file with your `DATABASE_URL`
2. Run migrations: `python run_with_env.py migrate`
3. Create a superuser: `python run_with_env.py createsuperuser`
4. Verify the connection: `python check_db.py`

If you need to switch between SQLite and PostgreSQL, simply update or remove the `DATABASE_URL` environment variable.

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env.development` file with the necessary environment variables (see below)
6. Run migrations: `python manage.py migrate`
7. Create a superuser: `python manage.py createsuperuser`
8. Run the development server: `python manage.py runserver`

### Local Environment Variables

Create a `.env.development` file with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
BACKEND_URL=http://localhost:8000
DATABASE_URL=postgresql://postgres:password@switchyard.proxy.rlwy.net:port/railway
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
DJANGO_LOG_LEVEL=DEBUG
```

## Migrating from SQLite to PostgreSQL

If you were previously using SQLite and want to migrate to PostgreSQL:

1. Delete the SQLite database file (`db.sqlite3`) if it exists
2. Set the `DATABASE_URL` environment variable to your PostgreSQL connection string
3. Run migrations: `python run_with_env.py migrate`
4. Create a new superuser: `python run_with_env.py createsuperuser`

## API Documentation

API documentation is available at `/api/docs/` when the server is running.

## Health Check

A health check endpoint is available at `/health/` to verify the server is running correctly.

## Backend URL

The backend is deployed at: https://backend-production-92ae.up.railway.app/