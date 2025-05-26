from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from blog.models import Category, BlogPost, Comment, BlogImage
from blog.serializers import (
    CategorySerializer,
    BlogPostSerializer,
    BlogPostListSerializer,
    CommentSerializer
)


class CategoryViewsTest(TestCase):
    """Test the category API views"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test categories
        self.category1 = Category.objects.create(
            name="Technology",
            slug="technology",
            description="Tech articles"
        )
        
        self.category2 = Category.objects.create(
            name="Health",
            slug="health",
            description="Health articles"
        )
        
        # Create test posts in the categories
        self.post1 = BlogPost.objects.create(
            title="Tech Post",
            slug="tech-post",
            content="<p>Technology content</p>",
            category=self.category1,
            published=True
        )
        
        self.post2 = BlogPost.objects.create(
            title="Health Post",
            slug="health-post",
            content="<p>Health content</p>",
            category=self.category2,
            published=True
        )
    
    def test_get_all_categories(self):
        """Test retrieving all categories"""
        url = reverse('blog:categories-all')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_get_category_by_slug(self):
        """Test retrieving a specific category by slug"""
        url = reverse('blog:category-by-slug', args=[self.category1.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category1.name)
        
    def test_get_category_posts(self):
        """Test retrieving posts for a specific category"""
        url = f'/api/categories/{self.category1.id}/posts/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.post1.title)


class BlogPostViewsTest(TestCase):
    """Test the blog post API views"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test category
        self.category = Category.objects.create(
            name="Technology",
            slug="technology"
        )
        
        # Create test posts
        self.post1 = BlogPost.objects.create(
            title="First Post",
            slug="first-post",
            content="<p>First post content</p>",
            category=self.category,
            excerpt="First post excerpt",
            featured=True,
            published=True
        )
        
        self.post2 = BlogPost.objects.create(
            title="Second Post",
            slug="second-post",
            content="<p>Second post content</p>",
            category=self.category,
            excerpt="Second post excerpt",
            featured=False,
            published=True
        )
        
        self.unpublished_post = BlogPost.objects.create(
            title="Unpublished Post",
            slug="unpublished-post",
            content="<p>Unpublished content</p>",
            category=self.category,
            published=False
        )
    
    def test_get_all_posts(self):
        """Test retrieving all published posts"""
        url = '/api/posts/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include all posts (both published and unpublished in default view)
        self.assertEqual(len(response.data), 3)
        
    def test_get_published_posts(self):
        """Test retrieving only published posts"""
        url = '/api/posts/?published=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only published posts
        
    def test_get_post_detail(self):
        """Test retrieving a specific post"""
        url = f'/api/posts/{self.post1.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post1.title)
        self.assertEqual(response.data['content'], self.post1.content)
        
    def test_get_post_by_slug(self):
        """Test retrieving a post by slug"""
        url = reverse('blog:get_post_by_slug', args=[self.post1.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post1.title)
        
    def test_get_featured_posts(self):
        """Test retrieving featured posts"""
        url = reverse('blog:featured_posts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one featured post
        self.assertEqual(response.data[0]['title'], self.post1.title)
        
    def test_get_latest_posts(self):
        """Test retrieving latest posts"""
        url = reverse('blog:get_latest_posts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two published posts
        # Posts should be ordered by created_at in descending order
        self.assertEqual(response.data[0]['title'], self.post2.title)
        
    def test_search_posts(self):
        """Test searching posts"""
        url = reverse('blog:search_posts') + '?q=First'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result_count'], 1)
        self.assertEqual(response.data['results'][0]['title'], self.post1.title)


class CommentViewsTest(TestCase):
    """Test the comment API views"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test post
        self.post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            content="<p>Test content</p>",
            published=True
        )
        
        # Create test comments
        self.approved_comment = Comment.objects.create(
            post=self.post,
            author_name="Approved User",
            author_email="approved@example.com",
            content="This is an approved comment",
            approved=True
        )
        
        self.pending_comment = Comment.objects.create(
            post=self.post,
            author_name="Pending User",
            author_email="pending@example.com",
            content="This is a pending comment",
            approved=False
        )
        
        self.trashed_comment = Comment.objects.create(
            post=self.post,
            author_name="Trashed User",
            author_email="trashed@example.com",
            content="This is a trashed comment",
            approved=False,
            is_trash=True
        )
    
    def test_get_approved_comments_for_post(self):
        """Test retrieving approved comments for a post"""
        url = reverse('blog:comments-approved-for-post') + f'?post={self.post.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one approved comment
        
    def test_get_comment_counts(self):
        """Test retrieving comment counts"""
        url = reverse('blog:comment_counts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 3)
        self.assertEqual(response.data['approved'], 1)
        self.assertEqual(response.data['pending'], 1)
        self.assertEqual(response.data['trashed'], 1)
        
    def test_create_comment(self):
        """Test creating a new comment"""
        url = '/api/comments/'
        data = {
            'post': self.post.id,
            'author_name': 'New User',
            'author_email': 'new@example.com',
            'content': 'This is a new comment'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 4)  # One new comment added
        
        # New comment should be pending by default
        new_comment = Comment.objects.get(author_name='New User')
        self.assertFalse(new_comment.approved)


class UtilityViewsTest(TestCase):
    """Test the utility API views"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_test_api(self):
        """Test the test API endpoint"""
        url = reverse('blog:api-test')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'API is working')
        
    def test_public_test(self):
        """Test the public test endpoint"""
        url = reverse('blog:public-test-endpoint')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Public API endpoint is working') 