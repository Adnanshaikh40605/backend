from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from . import views
from .serializers import BlogPostSerializer, BlogPostListSerializer, CommentSerializer

app_name = 'blog'

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
    
    # Debug endpoints
    path('debug-swagger/', views.debug_swagger, name='debug-swagger'),
    path('list-urls/', views.list_urls, name='list-urls'),
    
    # Special comment endpoints (keep consistent naming with frontend)
    path('v1/comments/pending-count/', views.CommentViewSet.as_view({'get': 'pending_count'}), name='comment-pending-count'),
    path('v1/comments/all/', views.CommentViewSet.as_view({'get': 'all'}), name='comments-all'),
    path('v1/comments/debug/', views.CommentViewSet.as_view({'get': 'debug'}), name='comments-debug'),
    path('v1/comments/check-approved/', views.CommentViewSet.as_view({'get': 'check_approved'}), name='comments-check-approved'),
    
    # Comment endpoints
    path('v1/comments/approved-for-post/', views.approved_comments_for_post, name='comments-approved-for-post'),
    re_path(r'^v1/comments/approved-for-post/$', views.approved_comments_for_post, name='comments-approved-for-post-regex'),
    
    # Also provide underscore versions for better API compatibility
    path('v1/comments/pending_count/', views.CommentViewSet.as_view({'get': 'pending_count'}), name='comment-pending-count-alt'),
    
    # Category endpoints
    path('v1/categories/all/', views.get_all_categories, name='categories-all'),
    path('v1/categories/by-slug/<slug:slug>/', views.get_category_by_slug, name='category-by-slug'),
    
    # Post endpoints
    path('v1/posts/by-slug/<slug:slug>/', views.get_post_by_slug, name='get_post_by_slug'),
    path('v1/posts/featured/', views.featured_posts, name='featured_posts'),
    path('v1/posts/latest/', views.get_latest_posts, name='get_latest_posts'),
    path('v1/posts/search/', views.search_posts, name='search_posts'),
    
    # Legacy routes for backward compatibility
    path('comments/pending-count/', views.CommentViewSet.as_view({'get': 'pending_count'})),
    path('comments/all/', views.CommentViewSet.as_view({'get': 'all'})),
    path('comments/check-approved/', views.CommentViewSet.as_view({'get': 'check_approved'})),
    path('comments/approved-for-post/', views.approved_comments_for_post),
    
    # Public test endpoint
    path('public-test/', views.public_test, name='public-test-endpoint'),
] 