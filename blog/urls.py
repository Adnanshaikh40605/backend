from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.http import JsonResponse

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'posts', views.BlogPostViewSet)
router.register(r'images', views.BlogImageViewSet)
router.register(r'comments', views.CommentViewSet)

def health_check(request):
    """Health check endpoint for Railway"""
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # User profile endpoint
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Comment actions
    path('comments/counts/', views.comment_counts, name='comment-counts'),
    path('comments/<str:action>/<int:comment_id>/', views.comment_action, name='comment-action'),
    
    # Health check endpoint
    path('health/', health_check, name='health_check'),
]
