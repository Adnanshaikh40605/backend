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
import logging
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

# Set up logging
logger = logging.getLogger(__name__)

# Root view for the main entry point
def root_view(request):
    """API root that returns system status and links"""
    data = {
        "status": "online",
        "message": "Blog CMS API is running",
        "version": "1.0.0",
        "documentation": "/api/docs/",
        "admin": "/admin/",
        "timestamp": timezone.now().isoformat()
    }
    return JsonResponse(data)

# Ultra simple health check function
def health_check(request):
    """Ultra simple health check that returns a 200 OK"""
    logger.info(f"Health check called at {timezone.now().isoformat()}")
    try:
        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return HttpResponse("OK", content_type="text/plain")

# Specific health check for Railway
def railway_health_check(request):
    """Dedicated health check for Railway"""
    logger.info(f"Railway health check called at {timezone.now().isoformat()}")
    return JsonResponse({"status": "ok"})

# Debug endpoint
def debug_endpoint(request):
    """Debug endpoint that returns all request info"""
    data = {
        "path": request.path,
        "method": request.method,
        "is_secure": request.is_secure(),
        "is_ajax": request.headers.get('x-requested-with') == 'XMLHttpRequest',
        "headers": dict(request.headers),
        "cookies": dict(request.COOKIES),
        "get_params": dict(request.GET),
        "time": timezone.now().isoformat(),
        "remote_addr": request.META.get('REMOTE_ADDR'),
        "server_name": request.META.get('SERVER_NAME'),
        "server_port": request.META.get('SERVER_PORT'),
    }
    return JsonResponse(data)

# Function to handle Swagger errors
def swagger_error_handler(request, exception=None):
    error_message = str(exception) if exception else "An error occurred generating the API documentation"
    tb = traceback.format_exc()
    return JsonResponse({
        "error": "Error generating API documentation",
        "message": error_message,
        "traceback": tb
    }, status=500)

# Welcome page
def welcome(request):
    return render(request, 'welcome.html')

# Basic Railway health check at root level
def simple_health_check(request):
    """Simplest possible health check for Railway"""
    return HttpResponse("OK", content_type="text/plain")

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

urlpatterns = [
    # Root paths - using JSON response for API clients
    path('', root_view, name='root'),
    
    # HTML welcome page at /welcome/ for browser viewing
    path('welcome/', welcome, name='welcome'),
    
    # Favicon - serve directly from static files
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
    
    # Health check endpoints - multiple options to ensure one works
    path('health', railway_health_check, name='railway_health_check'),
    path('health/', railway_health_check, name='railway_health_check_slash'),
    path('health/check', health_check, name='health_check_no_slash'),
    path('health/check/', health_check, name='health_check_with_slash'),
    path('api/health', health_check, name='api_health_check'),
    path('debug', debug_endpoint, name='debug_endpoint'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Include blog URLs with API prefix
    path('api/', include('blog.urls')),
    
    # Include health check URLs
    path('health/', include('health.urls')),
    
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
