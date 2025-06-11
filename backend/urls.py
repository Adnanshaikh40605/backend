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
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import traceback
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from blog.views import CustomTokenObtainPairView, debug_token

# Function to handle Swagger errors
def swagger_error_handler(request, exception=None):
    error_message = str(exception) if exception else "An error occurred generating the API documentation"
    tb = traceback.format_exc()
    return JsonResponse({
        "error": "Error generating API documentation",
        "message": error_message,
        "traceback": tb
    }, status=500)

# Health check endpoint for Railway
def health_check(request):
    """Health check endpoint for Railway"""
    # If requested as JSON, return JSON response
    if request.headers.get('Accept', '').find('application/json') != -1:
        return JsonResponse({'status': 'ok', 'server_time': timezone.now().isoformat()})
    
    # Otherwise return HTML response
    try:
        return render(request, 'health.html', {'server_time': timezone.now()})
    except Exception as e:
        # Fallback to simple response if template rendering fails
        return HttpResponse(f"Status: OK<br>Server time: {timezone.now()}", content_type='text/html')

# Basic Swagger configuration
schema_view = get_schema_view(
   openapi.Info(
      title="Blog CMS API",
      default_version='v1',
      description="API documentation for the Blog CMS platform",
      contact=openapi.Contact(email="skadnan40605@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Wrap schema view with error handling
def schema_view_with_error_handling(request, format=None):
    try:
        # Use the swagger UI view directly
        view = schema_view.with_ui('swagger', cache_timeout=0)
        return view(request, format=format)
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"Error generating API schema: {str(e)}"
        print(error_message)
        print(tb)
        return JsonResponse({
            "error": "Error generating API documentation",
            "message": str(e),
            "traceback": tb
        }, status=500)

# Wrap only the swagger UI view with error handling since we're removing the others
# schema_view_swagger_ui = schema_view_with_error_handling(schema_view.with_ui('swagger'))

# Welcome page
def welcome(request):
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
                <a href="https://blog-cms-frontend-ten.vercel.app/" class="btn">Frontend Website</a>
            </div>
            
            <div class="footer">
                <p>Contact: <a href="mailto:skadnan40605@gmail.com">skadnan40605@gmail.com</a></p>
                <p>Frontend URL: <a href="https://dohblog.vercel.app/">https://dohblog.vercel.app/</a></p>
            </div>
        </body>
    </html>
    """)

urlpatterns = [
    path('', welcome, name='welcome'),
    path('admin/', admin.site.urls),
    
    # Health check endpoint at root level
    path('health/', health_check, name='health_check'),
    
    # Include blog URLs with API prefix
    path('api/', include('blog.urls')),
    
    # JWT Authentication endpoints
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/debug-token/', debug_token, name='debug_token'),
    
    # CKEditor URLs
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    
    # Swagger documentation URL (only keeping the Swagger UI)
    path('api/docs/', schema_view_with_error_handling, name='schema-swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Add this to serve CKEditor 5 media files in development
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
# For production media serving (not recommended for high-traffic sites, but works for demos)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
