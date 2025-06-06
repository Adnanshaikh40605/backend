from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Simple test view
@api_view(['GET'])
def test_view(request):
    return JsonResponse({'status': 'ok', 'message': 'Test endpoint is working'})

router = DefaultRouter()
router.register(r'posts', views.BlogPostViewSet, basename='posts')
router.register(r'images', views.BlogImageViewSet)
router.register(r'comments', views.CommentViewSet)

# These explicit paths override the default router paths for special actions
urlpatterns = [
    # Include router-generated URLs
    path('', include(router.urls)),
    
    # User authentication endpoints
    # path('register/', views.RegisterView.as_view(), name='register'),  # Registration disabled
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Debug endpoint for Swagger issues
    path('debug-swagger/', views.debug_swagger, name='debug-swagger'),
    path('debug-swagger-schema/', views.debug_swagger_schema, name='debug-swagger-schema'),
    
    # Special comment endpoints (keep consistent naming with frontend)
    path('comments/pending-count/', views.CommentViewSet.as_view({'get': 'pending_count'}), name='comment-pending-count'),
    path('comments/all/', views.CommentViewSet.as_view({'get': 'all'}), name='comments-all'),
    path('comments/debug/', views.CommentViewSet.as_view({'get': 'debug'}), name='comments-debug'),
    path('comments/check-approved/', views.CommentViewSet.as_view({'get': 'check_approved'}), name='comments-check-approved'),
    path('comments/approved-for-post/', views.CommentViewSet.as_view({'get': 'approved_for_post'}), name='comments-approved-for-post'),
    path('comments/counts/', views.CommentViewSet.as_view({'get': 'counts'}), name='comment-counts'),
    
    # Also provide underscore versions for better API compatibility
    path('comments/pending_count/', views.CommentViewSet.as_view({'get': 'pending_count'}), name='comment-pending-count-alt'),
    
    # Bulk operations
    path('comments/bulk_approve/', views.CommentViewSet.as_view({'post': 'bulk_approve'}), name='comments-bulk-approve'),
    path('comments/bulk_reject/', views.CommentViewSet.as_view({'post': 'bulk_reject'}), name='comments-bulk-reject'),
    
    # Comment action endpoints
    path('comments/<int:comment_id>/trash/', views.comment_action, {'action': 'trash'}, name='comment-trash'),
    path('comments/<int:comment_id>/restore/', views.comment_action, {'action': 'restore'}, name='comment-restore'),
    path('comments/<int:comment_id>/delete/', views.comment_action, {'action': 'delete'}, name='comment-delete'),
    
    # Legacy comment action endpoints
    path('comments/trash/', views.comment_action, {'action': 'trash'}, name='comment-trash-legacy'),
    path('comments/restore/', views.comment_action, {'action': 'restore'}, name='comment-restore-legacy'),
    path('comments/delete/', views.comment_action, {'action': 'delete'}, name='comment-delete-legacy'),
    
    # Test endpoint
    path('test/', test_view, name='test-view'),
] 