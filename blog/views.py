# Import all views from the new modules
from .views_posts import BlogPostViewSet, get_post_by_slug
from .views_comments import CommentViewSet, comment_counts, comment_action
from .views_users import UserProfileView
from .views_images import BlogImageViewSet

# Export all views
__all__ = [
    'BlogPostViewSet',
    'get_post_by_slug',
    'CommentViewSet',
    'comment_counts',
    'comment_action',
    'UserProfileView',
    'BlogImageViewSet',
]
