from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_dashboard

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
    
    # Endpoint for retrieving all post slugs
    path('all-slugs/', views.get_all_slugs, name='all-slugs'),
    
    
    # Related posts endpoint
    path('posts/<slug:slug>/related/', views.get_related_posts, name='related-posts'),
    
    # Image upload endpoints
    path('upload/quill/', views.QuillImageUploadView.as_view(), name='quill-image-upload'),
    path('upload/ckeditor/', views.CKEditorImageUploadView.as_view(), name='ckeditor-image-upload'),
    
    # Dashboard endpoints
    path('dashboard/stats/', views_dashboard.dashboard_stats, name='dashboard-stats'),
]
