# Blog CMS

A modern, full-featured blog content management system with a Django backend and React frontend. This system provides a robust platform for creating, managing, and displaying blog content with advanced features.

## 📋 Features

- **Rich Content Management**: Create and edit blog posts with a powerful CKEditor 5 rich text editor
- **Media Handling**: Upload and manage images for blog posts with integrated image optimization
- **Comment System**: Fully-featured commenting system with moderation and threaded replies
- **SEO Optimized**: Built-in SEO features including meta tags, structured data, and SEO-friendly URLs
- **Responsive Design**: Mobile-first approach for perfect viewing on all devices
- **Table of Contents**: Automatic generation of table of contents from headings with navigation
- **Typography**: Premium reading experience with Lexend font integration
- **API-Driven Architecture**: RESTful API backend with comprehensive Swagger documentation

## 🛠️ Tech Stack

### Backend
- **Django**: Web framework for building robust web applications
- **Django REST Framework**: Powerful and flexible toolkit for building Web APIs
- **PostgreSQL**: Advanced relational database for production
- **CKEditor 5**: Advanced rich text editor with image upload capabilities
- **Django Jazzmin**: Modern, responsive admin interface theme
- **Whitenoise**: Simplified static file serving for Python web apps
- **Gunicorn**: Python WSGI HTTP Server for production
- **dj-database-url**: Database configuration with URL schemes

### Frontend
- **React**: UI library for building dynamic user interfaces
- **Vite**: Next-generation frontend build tool with HMR support
- **React Router**: Standard routing library for React applications
- **Styled Components**: CSS-in-JS styling solution with theming support
- **Axios**: Promise-based HTTP client for API requests
- **React Context API**: State management for sharing data across components
- **Custom Hooks**: Encapsulated logic for reusable functionality
- **Lexend Font**: Variable font family optimized for reading proficiency
- **React Error Boundaries**: Graceful error handling in components

## 📁 Project Structure

```
blog cms/
├── backend/                   # Django backend
│   ├── blog/                  # Blog application
│   │   ├── admin.py           # Admin interface configuration
│   │   ├── models.py          # Data models
│   │   ├── serializers.py     # API serializers
│   │   ├── urls.py            # URL routing
│   │   └── views.py           # API endpoints and logic
│   ├── templates/             # Django HTML templates
│   └── manage.py              # Django management script
├── frontend/                  # React frontend
│   ├── public/                # Static files
│   │   ├── css/               # Global CSS files
│   │   │   ├── toc.css        # Table of contents styling
│   │   │   └── lexend-font.css # Lexend font configuration
│   ├── src/
│   │   ├── api/               # API service layer
│   │   │   └── apiService.js  # Axios configuration and API methods
│   │   ├── assets/            # Static assets (images, icons)
│   │   ├── components/        # Reusable React components
│   │   │   ├── BlogHeader.jsx # Site header with navigation
│   │   │   ├── BlogFooter.jsx # Site footer
│   │   │   ├── Comment.jsx    # Comment display component
│   │   │   ├── CommentForm.jsx # Comment submission form
│   │   │   └── RichTextEditor.jsx # WYSIWYG editor component
│   │   ├── context/           # React context providers
│   │   │   └── BlogContext.js # Global blog state management
│   │   ├── hooks/             # Custom React hooks
│   │   │   └── usePostComments.js # Hook for post comments
│   │   ├── pages/             # Page components
│   │   │   ├── BlogPostPage.jsx # Single post display page
│   │   │   └── BlogListPage.jsx # Post listing page
│   │   └── utils/             # Utility functions
│   │       ├── sanitize.js    # Content sanitization
│   │       └── tocGenerator.js # Table of contents generation
├── media/                     # User uploaded content
│   └── featured_images/       # Blog post featured images
└── staticfiles/               # Collected static files
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL (optional, SQLite for development)

### Backend Setup

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (copy from env.example):
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
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

## 📄 API Documentation

The API is documented using Swagger UI, which provides interactive documentation to explore and test the API endpoints.

- **Swagger UI**: `/api/docs/` - Interactive API exploration interface

## 🔍 Rich Text Editor Integration

This project uses CKEditor 5 for rich text editing capabilities with custom integration for both backend and frontend.

## 🧩 Frontend Architecture

The application uses React Context API for state management with custom hooks for encapsulated logic and styled components for a responsive design approach.

## 📱 Responsive Design

The application is fully responsive with optimized layouts for mobile, tablet, and desktop devices.

## 🧪 Testing

- Backend: Django test framework with pytest
- Frontend: Jest and React Testing Library

## Project Status

In development phase.
Deployment will be added later.