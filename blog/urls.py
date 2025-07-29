from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'posts', views.BlogPostViewSet)
router.register(r'images', views.BlogImageViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'categories', views.CategoryViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # User profile endpoint
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Comment actions
    path('comments/counts/', views.comment_counts, name='comment-counts'),
    path('comments/<str:action>/<int:comment_id>/', views.comment_action, name='comment-action'),
    
    # Custom endpoint for retrieving posts by slug
    path('posts/by-slug/<slug:slug>/', views.get_post_by_slug, name='post-by-slug'),
    
    # Related posts endpoint
    path('posts/<slug:slug>/related/', views.get_related_posts, name='related-posts'),
]
