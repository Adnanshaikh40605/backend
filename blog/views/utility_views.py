from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver
import logging
import traceback
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status

# Setup logger
logger = logging.getLogger(__name__)

@api_view(['GET'])
def list_urls(request):
    """Debug endpoint that lists all URLs registered in the system"""
    try:
        def list_urls_recursive(patterns, parent_path=""):
            urls = []
            for pattern in patterns:
                if isinstance(pattern, URLPattern):
                    # Get the URL pattern
                    pattern_str = parent_path + str(pattern.pattern)
                    
                    # Get the view name
                    if hasattr(pattern.callback, '__name__'):
                        view_name = pattern.callback.__name__
                    elif hasattr(pattern, 'name') and pattern.name:
                        view_name = f"name:'{pattern.name}'"
                    else:
                        view_name = "(unknown)"
                    
                    urls.append({
                        "pattern": pattern_str,
                        "view": view_name,
                    })
                elif isinstance(pattern, URLResolver):
                    # Recursively resolve URL resolvers
                    resolver_path = parent_path + str(pattern.pattern)
                    urls.extend(list_urls_recursive(pattern.url_patterns, resolver_path))
            return urls
        
        resolver = get_resolver()
        urls = list_urls_recursive(resolver.url_patterns)
        
        return JsonResponse({
            'status': 'success',
            'url_count': len(urls),
            'urls': urls
        })
    except Exception as e:
        logger.error(f"Error listing URLs: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

@api_view(['GET'])
def test_api(request):
    """Test endpoint for API routing"""
    return JsonResponse({
        'status': 'success',
        'message': 'API is working',
        'endpoint': 'test_api'
    })

@api_view(['GET'])
def debug_swagger(request):
    """Debug endpoint (kept for backward compatibility)"""
    return JsonResponse({
        'status': 'success',
        'message': 'API is working, Swagger has been removed',
    })

@api_view(['GET'])
def public_test(request):
    """Public test endpoint for frontend connectivity tests"""
    response_data = {
        'status': 'success',
        'message': 'Public API endpoint is working',
        'timestamp': 'current_time'
    }
    
    return HttpResponse(
        content=JsonResponse(response_data).content,
        content_type='application/json',
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def test_approved_comments(request):
    """Test endpoint for approved comments"""
    post_id = request.query_params.get('post')
    return JsonResponse({
        'status': 'success',
        'message': 'Test endpoint for approved comments',
        'post_id': post_id,
        'endpoint': 'test_approved_comments'
    }) 