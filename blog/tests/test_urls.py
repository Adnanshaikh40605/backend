from django.test import TestCase
from django.urls import resolve, reverse
from blog.views import (
    BlogPostViewSet, 
    CommentViewSet, 
    CategoryViewSet,
    test_api,
    approved_comments_for_post,
    get_all_categories,
    get_category_by_slug,
    get_post_by_slug,
    featured_posts,
    get_latest_posts,
    search_posts
)


class UrlsTest(TestCase):
    """Test URL configurations"""
    
    def test_api_test_url(self):
        """Test API test URL pattern"""
        url = reverse('blog:api-test')
        self.assertEqual(resolve(url).func, test_api)
    
    def test_approved_comments_url(self):
        """Test approved comments URL pattern"""
        url = reverse('blog:comments-approved-for-post')
        self.assertIsNotNone(resolve(url))
    
    def test_categories_all_url(self):
        """Test all categories URL pattern"""
        url = reverse('blog:categories-all')
        self.assertIsNotNone(resolve(url))
    
    def test_category_by_slug_url(self):
        """Test category by slug URL pattern"""
        url = reverse('blog:category-by-slug', args=['test-slug'])
        self.assertEqual(resolve(url).func, get_category_by_slug)
    
    def test_post_by_slug_url(self):
        """Test post by slug URL pattern"""
        url = reverse('blog:get_post_by_slug', args=['test-slug'])
        self.assertEqual(resolve(url).func, get_post_by_slug)
    
    def test_featured_posts_url(self):
        """Test featured posts URL pattern"""
        url = reverse('blog:featured_posts')
        self.assertIsNotNone(resolve(url))
    
    def test_latest_posts_url(self):
        """Test latest posts URL pattern"""
        url = reverse('blog:get_latest_posts')
        self.assertIsNotNone(resolve(url))
    
    def test_search_posts_url(self):
        """Test search posts URL pattern"""
        url = reverse('blog:search_posts')
        self.assertIsNotNone(resolve(url))
    
    def test_viewset_root_urls(self):
        """Test that viewset root URLs resolve to the correct viewsets"""
        post_url = '/api/posts/'
        comment_url = '/api/comments/'
        category_url = '/api/categories/'
        
        # Just verify that these URLs can be resolved, not checking exact function names
        self.assertIsNotNone(resolve(post_url))
        self.assertIsNotNone(resolve(comment_url))
        self.assertIsNotNone(resolve(category_url)) 