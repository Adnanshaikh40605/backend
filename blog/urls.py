from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from . import views

# Create two routers for different API versions
router_v1 = DefaultRouter()
router_v1.register(r'posts', views.BlogPostViewSet)
router_v1.register(r'images', views.BlogImageViewSet)
router_v1.register(r'comments', views.CommentViewSet)
router_v1.register(r'categories', views.CategoryViewSet)

# These explicit paths override the default router paths for special actions
urlpatterns = [
    # API v1 - Include router-generated URLs
    path('v1/', include(router_v1.urls)),
    
    # Legacy URL path for backward compatibility - redirects to v1
    path('', include(router_v1.urls)),
    
    # Test endpoints for API routing
    path('test/', views.test_api, name='api-test'),
    path('test-approved-comments/', views.test_approved_comments, name='test-approved-comments'),
    
    # Debug endpoint for Swagger issues
    path('debug-swagger/', views.debug_swagger, name='debug-swagger'),
    
    # Special comment endpoints (keep consistent naming with frontend)
    path('v1/comments/pending-count/', views.CommentViewSet.as_view({'get': 'pending_count'}), name='comment-pending-count'),
    path('v1/comments/all/', views.CommentViewSet.as_view({'get': 'all'}), name='comments-all'),
    path('v1/comments/debug/', views.CommentViewSet.as_view({'get': 'debug'}), name='comments-debug'),
    path('v1/comments/check-approved/', views.CommentViewSet.as_view({'get': 'check_approved'}), name='comments-check-approved'),
    
    # Fix the approved-for-post endpoint - ensure it's registered correctly
    path('v1/comments/approved-for-post/', views.approved_comments_for_post, name='comments-approved-for-post'),
    # Add a direct endpoint for testing
    re_path(r'^v1/comments/approved-for-post/$', views.approved_comments_for_post, name='comments-approved-for-post-regex'),
    
    # Also provide underscore versions for better API compatibility
    path('v1/comments/pending_count/', views.CommentViewSet.as_view({'get': 'pending_count'}), name='comment-pending-count-alt'),
    
    # Category endpoints
    path('v1/categories/all/', views.get_all_categories, name='categories-all'),
    path('v1/categories/by-slug/<slug:slug>/', views.get_category_by_slug, name='category-by-slug'),
    
    # Legacy routes for backward compatibility
    path('comments/pending-count/', views.CommentViewSet.as_view({'get': 'pending_count'})),
    path('comments/all/', views.CommentViewSet.as_view({'get': 'all'})),
    path('comments/check-approved/', views.CommentViewSet.as_view({'get': 'check_approved'})),
    path('comments/approved-for-post/', views.approved_comments_for_post),
    
    # Public test endpoint
    path('public-test/', views.public_test, name='public-test-endpoint'),
] 