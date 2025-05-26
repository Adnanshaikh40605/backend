from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import BlogPost, Comment, BlogImage
import tempfile
from PIL import Image
from io import BytesIO

class ModelTests(TestCase):
    """Test cases for blog models"""
    
    def setUp(self):
        """Set up test data"""
        self.blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            content='<p>This is test content.</p>',
            published=True
        )
        
        self.comment = Comment.objects.create(
            post=self.blog_post,
            author_name='Test User',
            author_email='test@example.com',
            content='This is a test comment',
            approved=True
        )
        
    def test_blog_post_creation(self):
        """Test blog post model"""
        self.assertEqual(self.blog_post.title, 'Test Blog Post')
        self.assertEqual(self.blog_post.content, '<p>This is test content.</p>')
        self.assertTrue(self.blog_post.published)
        
    def test_blog_post_str(self):
        """Test blog post string representation"""
        self.assertEqual(str(self.blog_post), 'Test Blog Post')
        
    def test_comment_creation(self):
        """Test comment model"""
        self.assertEqual(self.comment.author_name, 'Test User')
        self.assertEqual(self.comment.author_email, 'test@example.com')
        self.assertEqual(self.comment.content, 'This is a test comment')
        self.assertTrue(self.comment.approved)
        self.assertEqual(self.comment.post, self.blog_post)

    def test_comment_str(self):
        """Test comment string representation"""
        expected_str = f'Comment by Test User on {self.blog_post.title}'
        self.assertEqual(str(self.comment), expected_str)

class APITests(TestCase):
    """Test cases for blog API endpoints"""
    
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        
        # Create test blog post
        self.blog_post = BlogPost.objects.create(
            title='API Test Blog Post',
            content='<p>This is API test content.</p>',
            published=True
        )
        
        # Create test comment
        self.comment = Comment.objects.create(
            post=self.blog_post,
            author_name='API Test User',
            author_email='apitest@example.com',
            content='This is an API test comment',
            approved=True
        )
        
        # Create temporary image for testing uploads
        self.image = self.create_test_image()
        
    def create_test_image(self):
        """Create a test image for testing file uploads"""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        return image_file
    
    def test_get_all_posts(self):
        """Test retrieving all posts"""
        url = reverse('blogpost-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'API Test Blog Post')
    
    def test_get_post_detail(self):
        """Test retrieving a specific post"""
        url = reverse('blogpost-detail', args=[self.blog_post.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Blog Post')
        self.assertEqual(response.data['content'], '<p>This is API test content.</p>')
    
    def test_get_comments(self):
        """Test retrieving comments"""
        url = reverse('comment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author_name'], 'API Test User')
    
    def test_create_comment(self):
        """Test creating a new comment"""
        url = reverse('comment-list')
        data = {
            'post': self.blog_post.id,
            'author_name': 'New API Test User',
            'author_email': 'newapitest@example.com',
            'content': 'This is a new API test comment'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.get(id=response.data['id']).content, 'This is a new API test comment')
    
    def test_approved_comments_for_post(self):
        """Test getting approved comments for a specific post"""
        url = reverse('comments-approved-for-post')
        response = self.client.get(url, {'post': self.blog_post.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author_name'], 'API Test User')
        
class UtilityTests(TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def test_test_api_endpoint(self):
        """Test the test_api endpoint"""
        url = reverse('api-test')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'success')
    
    def test_public_test_endpoint(self):
        """Test the public_test endpoint"""
        url = reverse('public-test-endpoint')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('message' in response.json())
