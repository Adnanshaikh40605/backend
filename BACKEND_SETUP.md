# Backend Setup Guide

This guide provides instructions for configuring your Django backend to resolve the 404 errors and CORS issues with your Blog-Website frontend.

## 1. Fix 404 Errors for Blog Posts by Slug

The frontend is trying to access blog posts by slug using the endpoint `/api/posts/by-slug/{slug}/`, but this endpoint might not be properly implemented in your Django backend.

### Check Your Django URLs

Make sure your `blog/urls.py` file includes the slug-based URL pattern:

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... other URL patterns
    path('posts/by-slug/<str:slug>/', views.post_detail_by_slug, name='post-detail-by-slug'),
]
```

### Implement the View

In your `blog/views.py` file, implement the view function or class:

```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Post
from .serializers import PostSerializer

@api_view(['GET'])
def post_detail_by_slug(request, slug):
    try:
        post = Post.objects.get(slug=slug, published=True)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    except Post.DoesNotExist:
        return Response(
            {"error": f"Post with slug '{slug}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
```

Or if you're using class-based views:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import PostSerializer

class PostDetailBySlugView(APIView):
    def get(self, request, slug):
        try:
            post = Post.objects.get(slug=slug, published=True)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(
                {"error": f"Post with slug '{slug}' not found"},
                status=status.HTTP_404_NOT_FOUND
            )
```

## 2. Configure CORS for Vercel Deployment

To allow your Vercel-deployed frontend to communicate with your backend, you need to configure CORS properly.

### Install django-cors-headers

If not already installed:

```bash
pip install django-cors-headers
```

### Update settings.py

Add the following to your `backend/settings.py` file:

```python
# Add corsheaders to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

# Add corsheaders middleware (should be at the top)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # This should be at the top
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]

# CORS Configuration
CORS_ALLOW_CREDENTIALS = True

# Allowed origins - add your Vercel deployment URL
CORS_ALLOWED_ORIGINS = [
    'https://blog-website-sigma-one.vercel.app',  # Vercel deployment
    'http://localhost:3000',  # Default development server
    'http://localhost:3001',  # Alternative development port
    'http://localhost:8000',  # Django development server
]

# CSRF Trusted Origins (for Django admin and form submissions)
CSRF_TRUSTED_ORIGINS = [
    'https://blog-website-sigma-one.vercel.app',
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:8000',
]
```

## 3. Update Your Environment Variables

If you're using environment variables, update your `.env` file:

```
CORS_ALLOWED_ORIGINS=https://blog-website-sigma-one.vercel.app,http://localhost:3000,http://localhost:3001,http://localhost:8000
```

And in your `settings.py`:

```python
import os

# Get CORS allowed origins from environment variable
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]

# Add Vercel deployment URL if not already in the list
vercel_url = 'https://blog-website-sigma-one.vercel.app'
if vercel_url not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(vercel_url)
```

## 4. Deploy Your Updated Backend

After making these changes, deploy your updated backend:

1. Commit your changes
2. Push to your repository
3. Deploy to Railway or your hosting platform

## 5. Testing

To verify everything is working correctly:

1. Visit your Vercel deployment: `https://blog-website-sigma-one.vercel.app`
2. Open the browser's developer tools (F12)
3. Navigate to a blog post
4. Check the Network tab to ensure requests to your backend are successful
5. Verify that no CORS errors appear in the Console tab

## Troubleshooting

If you continue to see 404 errors:

1. **Check your slug format**: Ensure the slugs in your database match the format expected in the URL
2. **Verify the endpoint**: Make a direct API request to `/api/posts/by-slug/your-slug/` to test
3. **Check for typos**: Ensure the URL patterns match exactly between frontend and backend
4. **Review serializers**: Make sure your serializer includes all fields needed by the frontend

If you see CORS errors:

1. **Verify CORS settings**: Double-check your CORS configuration in `settings.py`
2. **Check the request origin**: The request's origin must exactly match one of the allowed origins
3. **Restart your server**: Changes to CORS settings may require a server restart
4. **Check for middleware order**: The CORS middleware must be at the top of your middleware list 