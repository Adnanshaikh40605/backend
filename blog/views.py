# Import all views from the new modules
from .views_posts import BlogPostViewSet, get_post_by_slug, get_all_slugs, get_post_schema
from .views_comments import CommentViewSet, comment_counts, comment_action
from .views_users import UserProfileView
from .views_images import BlogImageViewSet
from .views_categories import CategoryViewSet, get_related_posts
from .views_upload import QuillImageUploadView, CKEditorImageUploadView

# Export all views
__all__ = [
    'BlogPostViewSet',
    'get_post_by_slug',
    'get_all_slugs',
    'get_post_schema',
    'CommentViewSet',
    'comment_counts',
    'comment_action',
    'UserProfileView',
    'BlogImageViewSet',
    'CategoryViewSet',
    'get_related_posts',
    'QuillImageUploadView',
    'CKEditorImageUploadView',
]
