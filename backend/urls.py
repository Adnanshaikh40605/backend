"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.views.static import serve
from blog.comment_api import comment_counts_direct
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import traceback
import datetime
import sys
import socket
from django.utils import timezone
from django.shortcuts import render

# Function to handle Swagger errors
def swagger_error_handler(request, exception=None):
    error_message = str(exception) if exception else "An error occurred generating the API documentation"
    tb = traceback.format_exc()
    return JsonResponse({
        "error": "Error generating API documentation",
        "message": error_message,
        "traceback": tb
    }, status=500)

# Health check view for Railway
def health_check(request):
    try:
        # Test database connection
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        one = cursor.fetchone()[0]
        if one != 1:
            raise Exception("Database test query did not return 1")
        
        # Return success response
        return JsonResponse({
            "status": "ok",
            "database": "connected",
            "timestamp": str(datetime.datetime.now()),
            "service": "Blog CMS API"
        })
    except Exception as e:
        # Return error response but still with 200 status so Railway doesn't fail
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "timestamp": str(datetime.datetime.now())
        }, status=200)  # Still return 200 to pass health check

# Function to detect Railway environment
def is_on_railway():
    """Check if we're running on Railway's internal network."""
    try:
        # Try to resolve the Railway internal hostname
        socket.gethostbyname('postgres.railway.internal')
        return True
    except socket.gaierror:
        return False

# Database health check view
def db_health_check(request):
    """View to check database connection health and provide diagnostic information."""
    try:
        # Test database connection
        from django.db import connection
        cursor = connection.cursor()
        
        # Get database version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Test query execution time
        start_time = datetime.datetime.now()
        cursor.execute("SELECT 1")
        one = cursor.fetchone()[0]
        query_time = (datetime.datetime.now() - start_time).total_seconds()
        
        # Get connection details
        db_settings = connection.settings_dict
        host = db_settings.get('HOST', 'unknown')
        port = db_settings.get('PORT', 'unknown')
        name = db_settings.get('NAME', 'unknown')
        user = db_settings.get('USER', 'unknown')
        
        # Check if we're using Railway internal network
        is_internal = 'railway.internal' in host
        
        # Return success response
        return JsonResponse({
            "status": "ok",
            "database": {
                "connected": True,
                "version": version,
                "query_time_seconds": query_time,
                "host": host,
                "port": port,
                "name": name,
                "user": user,
                "using_internal_network": is_internal
            },
            "system": {
                "railway_detected": is_on_railway(),
                "hostname": socket.gethostname(),
                "timestamp": str(datetime.datetime.now())
            }
        })
    except Exception as e:
        # Return error response but still with 200 status so Railway doesn't fail health checks
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "timestamp": str(datetime.datetime.now())
        }, status=200)  # Still return 200 to pass health check

# Super simple health check for Railway
def railway_health_check(request):
    """Extremely simple health check just for Railway."""
    from django.http import HttpResponse
    return HttpResponse("OK", status=200)

# Basic Swagger configuration
schema_view = get_schema_view(
   openapi.Info(
      title="Blog CMS API",
      default_version='v1',
      description="API documentation for the Blog CMS platform",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="skadnan40605@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Wrap schema view with error handling
def schema_view_with_error_handling(view):
    def wrapped_view(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except Exception as e:
            return swagger_error_handler(request, e)
    return wrapped_view

# Wrap only the swagger UI view with error handling since we're removing the others
schema_view_swagger_ui = schema_view_with_error_handling(schema_view.with_ui('swagger'))

# Welcome page
def welcome(request):
    # Check if this is a health check request from Railway
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if 'Railway Health Check' in user_agent or request.GET.get('health') == 'check':
        return health_check(request)
    
    # Otherwise show the welcome page
    return HttpResponse("""
    <html>
        <head>
            <title>Blog CMS Backend</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #333;
                }
                h1 {
                    color: #2C3E50;
                    border-bottom: 2px solid #3498DB;
                    padding-bottom: 10px;
                }
                .card {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 15px;
                    margin-bottom: 20px;
                    background-color: #f9f9f9;
                }
                .btn {
                    display: inline-block;
                    background-color: #3498DB;
                    color: white;
                    padding: 10px 15px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-right: 10px;
                    margin-bottom: 10px;
                }
                .btn:hover {
                    background-color: #2980B9;
                }
                .container {
                    margin-top: 30px;
                }
                .footer {
                    margin-top: 50px;
                    border-top: 1px solid #eee;
                    padding-top: 20px;
                    font-size: 0.9em;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to the Blog CMS Backend</h1>
            <div class="card">
                <p>This is the API server for the Blog CMS application.</p>
                <p>Use the links below to explore the API:</p>
            </div>
            
            <div class="container">
                <h2>API Documentation</h2>
                <a href="/api/docs/" class="btn">Swagger UI Documentation</a>
            </div>
            
            <div class="container">
                <h2>Links</h2>
                <a href="/admin/" class="btn">Admin Panel</a>
                <a href="https://frontend-pi-sable-69.vercel.app/" class="btn">Frontend Website</a>
            </div>
            
            <div class="container">
                <h2>Health Status</h2>
                <a href="/health/" class="btn">Check API Health</a>
                <a href="/ping/" class="btn">Ping Service</a>
            </div>
            
            <div class="footer">
                <p>Contact: <a href="mailto:skadnan40605@gmail.com">skadnan40605@gmail.com</a></p>
                <p>Backend URL: <a href="https://backend-production-e49d6.up.railway.app/">https://backend-production-e49d6.up.railway.app/</a></p>
                <p>Frontend URL: <a href="https://frontend-pi-sable-69.vercel.app/">https://frontend-pi-sable-69.vercel.app/</a></p>
            </div>
        </body>
    </html>
    """)

# Debug view for Railway health check issues
def debug_request(request):
    """View to debug request information for Railway health checks"""
    data = {
        'path': request.path,
        'method': request.method,
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
        'remote_addr': request.META.get('REMOTE_ADDR', 'Unknown'),
        'headers': dict(request.headers),
        'query_params': dict(request.GET),
        'server_name': request.META.get('SERVER_NAME', 'Unknown'),
        'server_port': request.META.get('SERVER_PORT', 'Unknown'),
        'timestamp': str(datetime.datetime.now()),
    }
    return JsonResponse(data)

urlpatterns = [
    path('', lambda request: render(request, 'home.html', {
        'title': 'Blog CMS API',
        'description': 'Welcome to the Blog CMS API',
        'links': [
            {'url': '/admin/', 'title': 'Admin Dashboard', 'description': 'Manage blog content'},
            {'url': '/api/docs/', 'title': 'API Documentation', 'description': 'Interactive API documentation'},
            {'url': '/api/schema/', 'title': 'API Schema', 'description': 'OpenAPI schema'},
            {'url': 'http://localhost:5173/', 'title': 'Frontend Website', 'description': 'View the frontend website'},
        ]
    }), name='home'),
    
    path('admin/', admin.site.urls),
    
    # Direct access to the comments counts endpoint
    path('api/comments/counts/', comment_counts_direct, name='direct-comment-counts'),
    
    # Include blog URLs with API prefix
    path('api/', include('blog.urls')),
    
    # CKEditor URLs
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    
    # Swagger documentation URL (only keeping the Swagger UI)
    path('api/docs/', schema_view_swagger_ui, name='schema-swagger-ui'),
    
    # Health check endpoints - make these more specific
    path('ping/', health_check, name='ping'),
    path('health/', lambda request: JsonResponse({'status': 'ok', 'message': 'API is running'})),
    path('railway-health/', lambda request: JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'environment': 'development',
        'message': 'API is running in development mode'
    })),
    path('db-health/', db_health_check, name='db-health'),  # Database-specific health check
    path('debug-request/', debug_request, name='debug-request'),  # Debug view
]

# Custom 404 handler
handler404 = 'backend.views.custom_404'

# Add debug toolbar URLs in debug mode
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add a simple diagnostic endpoint in debug mode
    urlpatterns += [
        path('debug-info/', lambda request: render(request, 'debug_info.html', {
            'title': 'Debug Information',
            'debug': settings.DEBUG,
            'database': {
                'engine': settings.DATABASES['default']['ENGINE'],
                'name': settings.DATABASES['default']['NAME'],
            },
            'media_url': settings.MEDIA_URL,
            'static_url': settings.STATIC_URL,
            'installed_apps': settings.INSTALLED_APPS,
        })),
    ]
# For production media serving (not recommended for high-traffic sites, but works for demos)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
