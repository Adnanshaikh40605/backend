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

## API Documentation

The API is documented using Swagger UI, which provides interactive documentation to explore and test the API endpoints.

- **Swagger UI**: `/api/docs/` - Interactive API exploration interface

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL (optional, SQLite for development)

### Backend Setup

1. Set up a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables (copy from env.example):
   ```
   cp env.example .env
   # Edit .env with your configuration
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

## API Endpoints

- **Posts**: `/api/posts/`
- **Comments**: `/api/comments/`
- **Images**: `/api/images/`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 