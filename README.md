# Blog CMS Platform

A full-stack Blog Content Management System with Django backend and React frontend.

## Project Overview

This project is a modern blog platform that consists of:
- **Backend**: Django-based RESTful API with PostgreSQL
- **Frontend**: React application with Vite build system
- **Deployment**: Railway.app (backend) and Vercel (frontend)

## Features

### Backend Features
- RESTful API for blog posts and comments
- JWT-based authentication system
- Admin panel for content management
- Rich text editing with CKEditor 5
- API documentation with Swagger UI
- CORS support for frontend integration
- PostgreSQL database integration (with SQLite fallback for development)
- Health check endpoints
- Comprehensive logging system
- Docker support for containerization

### Frontend Features
- Modern React application built with Vite
- Responsive and beautiful UI
- Rich text content rendering
- Image optimization and handling
- Authentication and authorization
- ESLint code quality enforcement
- Production-ready build configuration

## Tech Stack

### Backend Stack
- Python 3.11
- Django & Django REST Framework
- PostgreSQL
- JWT Authentication
- CKEditor 5
- Swagger/OpenAPI
- Docker
- Gunicorn (Production server)

### Frontend Stack
- React
- Vite
- ESLint
- Node.js
- Modern JavaScript (ES6+)
- CSS Modules/Styled Components

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 16 or higher
- PostgreSQL (optional for development)
- Git

### Backend Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env.development` file with the necessary environment variables (see Environment Variables section)
6. Run migrations:
   ```bash
   python run_with_env.py migrate
   ```
7. Create a superuser:
   ```bash
   python run_with_env.py createsuperuser
   ```
8. Run the development server:
   ```bash
   python run_server.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Environment Variables

### Backend Environment Variables

Create a `.env.development` file with the following variables:

```ini
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

### Frontend Environment Variables

Create a `.env` file in the frontend directory:

```ini
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

## Deployment

### Backend Deployment (Railway.app)

1. Push your code to GitHub
2. Create a new project on Railway and connect it to your GitHub repository
3. Add a PostgreSQL database to your project
4. Railway will automatically detect the Python project and deploy it
5. Set the required environment variables in the Railway dashboard

### Frontend Deployment (Vercel)

1. Push your code to GitHub
2. Create a new project on Vercel and connect it to your GitHub repository
3. Configure the build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Set the environment variables in the Vercel dashboard
5. Deploy

## API Documentation

- Swagger UI documentation is available at `/api/docs/` when the server is running
- Health check endpoint is available at `/health/`

### Main API Endpoints

- Blog Posts: `/api/posts/`
- Blog Post by Slug: `/api/posts/{slug}/`
- Comments: `/api/comments/`
- Images: `/api/images/`
- Authentication: `/api/auth/token/`

## Database Management

### PostgreSQL Setup

This project uses PostgreSQL as the primary database. The connection is configured using the `DATABASE_URL` environment variable.

For Railway deployment:
- Use the internal URL: `postgresql://postgres:password@postgres.railway.internal:5432/railway`

For local development with Railway PostgreSQL:
1. Get the external connection URL from Railway dashboard
2. Format: `postgresql://postgres:password@switchyard.proxy.rlwy.net:port/railway`
3. Set this as your `DATABASE_URL` environment variable

### SQLite Fallback

For development without PostgreSQL:
1. Remove or comment out the `DATABASE_URL` environment variable
2. The system will automatically use SQLite

### Database Migration

To migrate from SQLite to PostgreSQL:
1. Delete the SQLite database file (`db.sqlite3`) if it exists
2. Set the `DATABASE_URL` environment variable
3. Run migrations: `python run_with_env.py migrate`
4. Create a new superuser: `python run_with_env.py createsuperuser`

## Common Issues and Solutions

### CORS Issues

If experiencing CORS errors:
1. Check that your frontend domain is included in `CORS_ALLOWED_ORIGINS`
2. Ensure `CORS_ALLOW_CREDENTIALS` is set to `True` if using authentication
3. For development, you may set `CORS_ALLOW_ALL_ORIGINS=True`

### Media Files

Media files are stored in the `/media/` directory:
- Local: `http://localhost:8000/media/path/to/image.jpg`
- Production: `https://backend-production-92ae.up.railway.app/media/path/to/image.jpg`

Note: For production, consider using cloud storage (e.g., AWS S3) for media files.

### 404 Errors for Blog Posts

If receiving 404 errors for blog posts:
1. Verify the URL format: `/api/posts/{slug}/`
2. Confirm the slug exists in the database
3. Check CORS configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Deployment URLs

- Backend: https://backend-production-92ae.up.railway.app/
- Frontend: https://dohblog.vercel.app/

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.