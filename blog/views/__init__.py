from .post_views import (
    BlogPostViewSet, 
    post_detail, 
    category_posts, 
    search_posts, 
    get_latest_posts, 
    get_post_by_slug,
    featured_posts
)

from .comment_views import (
    CommentViewSet, 
    approved_comments_for_post, 
    comment_counts
)

from .image_views import (
    BlogImageViewSet,
    upload_image
)

from .utility_views import (
    list_urls,
    test_api,
    debug_swagger,
    public_test,
    test_approved_comments
)

from .category_views import (
    CategoryViewSet,
    get_all_categories,
    get_category_by_slug
)

# Expose all classes and functions to maintain backward compatibility
__all__ = [
    # Post views
    'BlogPostViewSet', 'post_detail', 'category_posts', 'search_posts', 
    'get_latest_posts', 'get_post_by_slug', 'featured_posts',
    
    # Comment views
    'CommentViewSet', 'approved_comments_for_post', 'comment_counts',
    
    # Image views
    'BlogImageViewSet', 'upload_image',
    
    # Category views
    'CategoryViewSet', 'get_all_categories', 'get_category_by_slug',
    
    # Utility views
    'list_urls', 'test_api', 'debug_swagger', 'public_test', 'test_approved_comments'
] 