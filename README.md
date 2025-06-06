# Blog CMS

A modern, full-featured blog content management system with a Django backend and React frontend. This system provides a robust platform for creating, managing, and displaying blog content with advanced features.

## 📋 Features

- **Rich Content Management**: Create and edit blog posts with a powerful CKEditor 5 rich text editor
- **Media Handling**: Upload and manage images for blog posts with integrated image optimization and WebP conversion
- **Comment System**: Fully-featured commenting system with moderation, approval workflow, and admin replies
- **Featured Posts**: Highlight important blog posts with a featured flag for special display on the homepage
- **Responsive Design**: Mobile-first approach with a modern UI for perfect viewing on all devices
- **SEO Optimized**: Built-in SEO features including meta tags and SEO-friendly URLs with automatic slug generation
- **User-Friendly Dashboard**: Clean and intuitive admin interface for content management
- **API-Driven Architecture**: RESTful API backend with comprehensive documentation
- **Performance Optimized**: Efficient API calls with caching and debouncing to reduce server load

## 🛠️ Tech Stack

### Backend
- **Django 4.2**: Web framework for building robust web applications
- **Django REST Framework**: Powerful and flexible toolkit for building Web APIs
- **PostgreSQL**: Advanced relational database for production (SQLite for development)
- **CKEditor 5**: Advanced rich text editor with image upload capabilities
- **Django Jazzmin**: Modern, responsive admin interface theme
- **Pillow**: Python Imaging Library for image processing and optimization
- **Whitenoise**: Simplified static file serving for Python web apps
- **Gunicorn**: Python WSGI HTTP Server for production
- **dj-database-url**: Database configuration with URL schemes

### Frontend
- **React 18**: UI library for building dynamic user interfaces
- **Vite**: Next-generation frontend build tool with HMR support
- **React Router 6**: Standard routing library for React applications
- **Styled Components**: CSS-in-JS styling solution with theming support
- **Custom API Layer**: Centralized API services with caching and error handling
- **Formik & Yup**: Form handling and validation
- **DOMPurify**: XSS sanitization for user-generated content
- **React Helmet Async**: Document head manager for SEO
- **date-fns**: Modern JavaScript date utility library

## 📁 Project Structure

```
blog cms/
├── backend/                   # Django backend configuration
│   ├── blog/                  # Main blog application
│   │   ├── admin.py           # Admin interface configuration
│   │   ├── models.py          # Data models (BlogPost, BlogImage, Comment)
│   │   ├── serializers.py     # API serializers
│   │   ├── urls.py            # URL routing
│   │   ├── views.py           # API endpoints and logic
│   │   └── swagger_schema.py  # API documentation configuration
│   ├── templates/             # Django HTML templates
│   ├── settings.py            # Django settings
│   └── urls.py                # Main URL configuration
├── blog/                      # Django blog app (models, views, etc.)
├── frontend/                  # React frontend
│   ├── public/                # Static files
│   ├── src/
│   │   ├── api/               # API service layer
│   │   │   ├── index.js       # Main API exports
│   │   │   ├── apiEndpoints.js # Centralized API endpoint URLs
│   │   │   ├── apiService.js  # API service functions
│   │   │   ├── apiUtils.js    # Shared API utility functions
│   │   │   └── apiMocks.js    # Mock data for development
│   │   ├── assets/            # Static assets (images, icons)
│   │   ├── components/        # Reusable React components
│   │   │   ├── BlogHeader.jsx # Site header with navigation
│   │   │   ├── BlogFooter.jsx # Site footer
│   │   │   ├── BlogPostCard.jsx # Card component for blog posts
│   │   │   ├── Button.jsx     # Reusable button component
│   │   │   ├── Comment.jsx    # Comment display component
│   │   │   ├── CommentForm.jsx # Comment submission form
│   │   │   ├── RichTextEditor.jsx # WYSIWYG editor component
│   │   │   └── SEO.jsx        # SEO metadata component
│   │   ├── context/           # React context providers
│   │   │   ├── BlogContext.jsx # Global blog state management
│   │   │   └── CommentContext.jsx # Comment state management
│   │   ├── pages/             # Page components
│   │   │   ├── BlogPostPage.jsx # Single post display page
│   │   │   ├── BlogListPage.jsx # Post listing page
│   │   │   ├── HomePage.jsx   # Dashboard home page
│   │   │   ├── CommentsPage.jsx # Comments management page
│   │   │   ├── PostDetailPage.jsx # Admin post detail page
│   │   │   └── PostFormPage.jsx # Post creation/editing page
│   │   └── utils/             # Utility functions
├── media/                     # User uploaded content
│   └── featured_images/       # Blog post featured images
├── static/                    # Static files
├── templates/                 # HTML templates
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── entrypoint.sh              # Deployment script
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18.x
- PostgreSQL (optional, SQLite for development)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/blog-cms.git
   cd blog-cms
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
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

## 📄 API Overview

The API follows a RESTful architecture with the following main endpoints:

### Blog Posts

- `GET /api/posts/` - List all blog posts with optional filtering
- `POST /api/posts/` - Create a new blog post
- `GET /api/posts/{slug}/` - Retrieve a specific blog post by slug
- `PUT/PATCH /api/posts/{id}/` - Update a blog post
- `DELETE /api/posts/{id}/` - Delete a blog post

### Comments

- `GET /api/comments/` - List all comments with optional filtering
- `POST /api/comments/` - Create a new comment
- `GET /api/comments/{id}/` - Retrieve a specific comment
- `POST /api/comments/{id}/approve/` - Approve a comment
- `POST /api/comments/{id}/reject/` - Reject a comment
- `GET /api/comments/counts/` - Get counts of comments by status (all, pending, approved, trash)
- `POST /api/comments/{id}/reply/` - Add admin reply to a comment
- `POST /api/comments/bulk_approve/` - Approve multiple comments at once
- `POST /api/comments/bulk_reject/` - Reject multiple comments at once

## 🔧 Key Features

### Image Optimization

The system automatically optimizes uploaded images:
- Converts images to WebP format when supported
- Compresses images to reduce file size
- Maintains image quality with configurable settings

### Comment Management

The blog includes a comprehensive comment system:
- Comment moderation workflow
- Admin approval process
- Spam protection
- Admin replies to comments
- Comment status tracking (approved, pending, trash)
- Bulk comment actions (approve, reject, trash, restore, delete)

### Featured Posts

The blog now supports featured posts:
- Mark important posts as featured
- Display featured posts prominently on the homepage
- Filter posts by featured status in the API

### Rich Text Editing

The CKEditor 5 integration provides:
- WYSIWYG editing experience
- Image uploads directly in the editor
- Formatting options for blog content
- Clean HTML output

### Performance Optimizations

Recent performance improvements include:
- Fixed duplicate API calls in the comment management interface
- Implemented debounced API calls to reduce server load
- Added caching for comment counts to improve UI responsiveness

## 🌐 Deployment

The project includes configuration files for various deployment options:
- Railway configuration for full-stack deployment
- Vercel configuration for frontend deployment
- Procfile for Heroku deployment
- Docker support via entrypoint.sh

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔄 Recent Updates

- Added featured flag to blog posts for highlighting important content
- Fixed duplicate API calls in the comment management interface
- Improved comment count caching and API efficiency
- Enhanced image optimization for better performance
- Updated deployment configurations for Railway