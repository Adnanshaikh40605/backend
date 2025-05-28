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

4. Configure environment variables (copy from env.example):
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
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

### API Endpoints

Our API is organized around REST principles. It accepts form-encoded request bodies, returns JSON-encoded responses, and uses standard HTTP response codes and authentication.

#### Posts

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/posts/` | GET | List all published posts with pagination |
| `/api/posts/` | POST | Create a new post (admin) |
| `/api/posts/<id>/` | GET | Retrieve a specific post |
| `/api/posts/<id>/` | PUT | Update a post (admin) |
| `/api/posts/<id>/` | DELETE | Delete a post (admin) |
| `/api/posts/<slug>/` | GET | Retrieve a post by slug |
| `/api/posts/validate-slug/` | POST | Validate or generate a slug for a post |
| `/api/posts/check-links/` | POST | Check for broken links in post content |
| `/api/posts/preview/` | POST | Preview a post before publishing |
| `/api/posts/<id>/upload_images/` | POST | Upload additional images to a post |

#### Comments

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/comments/` | GET | List all approved comments |
| `/api/comments/` | POST | Create a new comment |
| `/api/comments/<id>/` | GET | Retrieve a specific comment |
| `/api/comments/<id>/` | PUT | Update a comment (admin) |
| `/api/comments/<id>/` | DELETE | Delete a comment (admin) |
| `/api/posts/<post_id>/comments/` | GET | Get comments for a post |
| `/api/comments/pending-count/` | GET | Get count of pending comments |
| `/api/comments/bulk-approve/` | POST | Approve multiple comments at once |
| `/api/comments/bulk-reject/` | POST | Reject multiple comments at once |
| `/api/comments/<id>/approve/` | POST | Approve a specific comment |
| `/api/comments/<id>/reject/` | POST | Reject a specific comment |

#### Media

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/media/upload/` | POST | Upload a media file |
| `/api/media/` | GET | List all media files (admin) |
| `/ckeditor5/image_upload/` | POST | Upload an image via CKEditor |

### API Documentation with Swagger

The API is documented using Swagger UI, which provides interactive documentation to explore and test the API endpoints.

- **Swagger UI**: `/api/docs/` - Interactive API exploration interface

### Setting Up Swagger Documentation

To enable Swagger documentation in your Django project:

1. Install required packages:
   ```bash
   pip install drf-yasg
   ```

2. Add to INSTALLED_APPS in settings.py:
   ```python
   INSTALLED_APPS = [
       # ...
       'drf_yasg',
   ]
   ```

3. Configure Swagger in urls.py:
   ```python
   from rest_framework import permissions
   from drf_yasg.views import get_schema_view
   from drf_yasg import openapi

   schema_view = get_schema_view(
       openapi.Info(
           title="Blog CMS API",
           default_version='v1',
           description="API documentation for Blog CMS",
           terms_of_service="https://www.google.com/policies/terms/",
           contact=openapi.Contact(email="contact@example.com"),
           license=openapi.License(name="BSD License"),
       ),
       public=True,
       permission_classes=(permissions.AllowAny,),
   )

   urlpatterns = [
       # ... your other URL patterns
       path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   ]
   ```

4. Add proper docstrings to your ViewSets and API views:
   ```python
   class PostViewSet(viewsets.ModelViewSet):
       """
       API endpoint that allows posts to be viewed or edited.
       """
       queryset = Post.objects.all()
       serializer_class = PostSerializer
   ```

## 🔍 Rich Text Editor Integration

This project uses CKEditor 5 for rich text editing capabilities:

### Backend Integration

- **Model Field**: The BlogPost model uses `RichTextUploadingField` from django-ckeditor5
- **Storage Configuration**: Media uploads are stored in the configured MEDIA_ROOT directory
- **Image Processing**: Uploaded images are automatically processed for optimal web display
- **Security**: Content is sanitized to prevent XSS attacks while preserving rich formatting

### Frontend Integration

- **Custom React Component**: A wrapper component for the CKEditor instance with additional features
- **Image Upload Handling**: Direct integration with Django backend for image uploads
- **Toolbar Configuration**: Customized toolbar with all necessary formatting options
- **Content Sanitization**: HTML content is sanitized using DOMPurify before display

### Media Upload Flow

1. User selects an image in the editor
2. Frontend component handles the file and shows a loading placeholder
3. File is uploaded to `/ckeditor5/image_upload/` endpoint
4. Backend processes the image (resizing, optimization)
5. Image URL is returned to the editor and replaces the placeholder
6. Image is stored in the media directory with appropriate permissions

### Features Supported

- **Text Formatting**: Bold, italic, underline, strikethrough
- **Headings**: H1-H6 heading levels
- **Lists**: Ordered and unordered lists
- **Media**: Image upload and embedding
- **Links**: URL linking with target control
- **Tables**: Table creation and formatting
- **Code Blocks**: Code syntax highlighting
- **Quotes**: Blockquote formatting

## 🧩 Frontend Architecture

### State Management

The application uses React Context API for state management:

- **BlogContext**: Manages global blog state including posts, categories, and pagination
  - Provides post data to components throughout the application
  - Handles post caching and prefetching for improved performance
  - Manages post filtering and search functionality

- **UserContext**: Manages user preferences and settings
  - Stores reading progress and history
  - Handles theme preferences (light/dark mode)
  - Manages user comment information

- **Custom Hooks**: Encapsulated data fetching and business logic
  - `usePostComments`: Manages comment loading, pagination, and submission
  - `useTOC`: Handles table of contents generation and navigation
  - `useMediaUpload`: Manages media file uploads with progress feedback

### Key Components

- **BlogPostPage**: Main component for displaying a single blog post
  - Handles post loading and error states
  - Manages table of contents generation
  - Coordinates comment display and submission

- **BlogHeader/BlogFooter**: Application-wide header and footer components
  - Responsive navigation system
  - Dynamic link generation
  - Styled with Lexend font for consistency

- **RichTextEditor**: Custom editor component for content creation
  - Integrates CKEditor 5 with React
  - Handles image uploads via custom API endpoints
  - Provides toolbar customization and content sanitization

- **CommentForm/Comment**: Comment creation and display components
  - Form validation and submission handling
  - Threaded comment display
  - Moderation interface for administrators

- **TableOfContents**: Auto-generated navigation from post headings
  - Analyzes post content to extract heading structure
  - Builds hierarchical navigation with proper nesting
  - Provides smooth scrolling to different sections
  - Highlights current section during scrolling

### Styling Approach

- **Styled Components**: Component-scoped CSS with theme support
  - Consistent styling with theme variables
  - Dynamic styling based on props
  - Responsive design with media queries

- **Responsive Design**: Mobile-first approach with adaptive layouts
  - Fluid grid system for different screen sizes
  - Conditional rendering for mobile/desktop experiences
  - Touch-friendly interactions for mobile users

- **Typography**: Custom Lexend font implementation for better readability
  - Variable font setup for optimal performance
  - Custom letter-spacing and line-height for readability
  - Different font weights for visual hierarchy

## 📱 Responsive Design

The application is fully responsive with breakpoints at:

- Mobile: < 768px
  - Single column layout
  - Simplified navigation
  - Optimized for touch interaction

- Tablet: 768px - 1024px
  - Two-column layout where appropriate
  - Sidebar navigation on larger tablets
  - Balanced content density

- Desktop: > 1024px
  - Multi-column layout
  - Full feature set visible
  - Optimized for mouse/keyboard interaction

## 🆕 Latest Features

### Table of Contents Generation

- Automatically extracts headings (H1-H6) from blog post content
- Creates a hierarchical navigation structure for easy section browsing
- Adds anchor links to each heading for direct URL navigation
- Provides smooth scrolling behavior with scroll margin for fixed headers
- Can be positioned either at the beginning or end of the blog post content

### Lexend Font Integration

- Implemented Lexend font family for improved reading experience
- Custom CSS variables for consistent font usage throughout the app
- Optimized letter-spacing and line-height for better readability
- Variable font loading for faster page loads and better performance
- Adjusted weight distribution for proper visual hierarchy

### Image Optimization

- Automatic resizing of uploaded images for optimal web display
- Progressive loading with placeholder images during loading
- Lazy loading implementation for improved page performance
- Alt text generation for better accessibility and SEO
- Responsive images with srcset for different device sizes

## 🔄 Deployment

### Prerequisites

- A PostgreSQL database
- A web server (Nginx or similar)
- A hosting service (e.g., Railway, Heroku, DigitalOcean)

### Deployment Steps

1. Set production environment variables
2. Collect static files: `python manage.py collectstatic`
3. Set up database with migrations
4. Configure web server to serve Django application
5. Build the frontend: `npm run build`
6. Serve the frontend build directory

## 🧪 Testing

- Backend: Django test framework with pytest
- Frontend: Jest and React Testing Library

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

# Blog CMS API Documentation

## API Documentation URL

The Blog CMS API is now documented using Swagger/OpenAPI. You can access the interactive documentation at:

- **Swagger UI**: [https://web-production-f03ff.up.railway.app/api/docs/](https://web-production-f03ff.up.railway.app/api/docs/)

## Features Implemented

1. **Interactive API Documentation**
   - All API endpoints are fully documented
   - Test API endpoints directly from the browser
   - Browse the API structure and understand the data models

2. **Organized API Sections**
   - Posts - Endpoints for managing blog posts
   - Comments - Endpoints for managing and moderating comments
   - Images - Endpoints for managing blog images

3. **Custom Styling**
   - Branded UI for the Swagger interface
   - Clear documentation of request/response formats
   - Contact information and links to frontend/backend

4. **Authentication Support**
   - Bearer token authentication documentation
   - Secure access to protected endpoints

## Links

- **Frontend**: [https://blog-cms-frontend-ten.vercel.app/](https://blog-cms-frontend-ten.vercel.app/)
- **Backend**: [https://web-production-f03ff.up.railway.app/](https://web-production-f03ff.up.railway.app/)
- **Contact**: skadnan40605@gmail.com

For more detailed information about the API, please see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md).