from django.test import TestCase
from blog.models import Category, BlogPost, Comment, BlogImage
from blog.serializers import (
    CategorySerializer,
    BlogPostSerializer,
    BlogPostListSerializer,
    CommentSerializer,
    BlogImageSerializer
)


class CategorySerializerTest(TestCase):
    """Test the category serializer"""
    
    def setUp(self):
        self.category_data = {
            'name': 'Test Category',
            'slug': 'test-category',
            'description': 'Test description'
        }
        
        self.category = Category.objects.create(**self.category_data)
        self.serializer = CategorySerializer(instance=self.category)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(),
            ['id', 'name', 'slug', 'description', 'featured_image', 'post_count', 'created_at', 'updated_at']
        )
    
    def test_name_field_content(self):
        """Test that name field content is correct"""
        data = self.serializer.data
        self.assertEqual(data['name'], self.category_data['name'])
    
    def test_post_count(self):
        """Test that post_count is calculated correctly"""
        # Create a few posts
        BlogPost.objects.create(
            title="Post 1",
            slug="post-1",
            content="<p>Content</p>",
            category=self.category,
            published=True
        )
        
        BlogPost.objects.create(
            title="Post 2",
            slug="post-2",
            content="<p>Content</p>",
            category=self.category,
            published=True
        )
        
        # Unpublished post (shouldn't be counted)
        BlogPost.objects.create(
            title="Unpublished",
            slug="unpublished",
            content="<p>Content</p>",
            category=self.category,
            published=False
        )
        
        # Refresh serializer
        serializer = CategorySerializer(instance=self.category)
        self.assertEqual(serializer.data['post_count'], 2)  # Only published posts


class BlogPostSerializerTest(TestCase):
    """Test the blog post serializer"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.post_data = {
            'title': 'Test Post',
            'slug': 'test-post',
            'content': '<p>Test content</p>',
            'category': self.category,
            'excerpt': 'Test excerpt',
            'featured': True,
            'published': True
        }
        
        self.post = BlogPost.objects.create(**self.post_data)
        self.serializer = BlogPostSerializer(instance=self.post)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(),
            ['id', 'title', 'slug', 'content', 'excerpt', 'category', 'category_name', 
             'category_slug', 'featured', 'featured_image', 'images', 'comments', 
             'published', 'created_at', 'updated_at']
        )
    
    def test_category_related_fields(self):
        """Test that category related fields are populated correctly"""
        data = self.serializer.data
        self.assertEqual(data['category'], self.category.id)
        self.assertEqual(data['category_name'], self.category.name)
        self.assertEqual(data['category_slug'], self.category.slug)
    
    def test_create_with_additional_images(self):
        """Test that create method correctly handles additional images"""
        # Note: We're not actually testing with real image files, just the behavior
        # of the create method with the additional_images field
        
        data = {
            'title': 'Post with Images',
            'content': '<p>Content</p>',
            'published': True,
            'additional_images': []  # In a real scenario this would be image files
        }
        
        serializer = BlogPostSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # The create method should handle the additional_images field
        post = serializer.save()
        self.assertEqual(post.title, data['title'])


class BlogPostListSerializerTest(TestCase):
    """Test the blog post list serializer"""
    
    def setUp(self):
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            content='<p>Test content</p>',
            published=True
        )
        self.serializer = BlogPostListSerializer(instance=self.post)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(),
            ['id', 'title', 'slug', 'featured_image', 'published', 'created_at']
        )
    
    def test_does_not_contain_content(self):
        """Test that the serializer does not include the content field"""
        data = self.serializer.data
        self.assertNotIn('content', data)


class CommentSerializerTest(TestCase):
    """Test the comment serializer"""
    
    def setUp(self):
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            content='<p>Test content</p>',
            published=True
        )
        
        self.comment_data = {
            'post': self.post,
            'author_name': 'Test User',
            'author_email': 'test@example.com',
            'content': 'Test comment content',
            'approved': True
        }
        
        self.comment = Comment.objects.create(**self.comment_data)
        self.serializer = CommentSerializer(instance=self.comment)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'post', 'post_title', 'author_name', 'author_email', 'author_website',
            'content', 'approved', 'is_trash', 'created_at', 'updated_at', 'admin_reply'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_post_title_field(self):
        """Test that post_title is populated correctly"""
        data = self.serializer.data
        self.assertEqual(data['post_title'], self.post.title)
    
    def test_to_representation_adds_post_info(self):
        """Test that to_representation adds post information"""
        data = self.serializer.data
        self.assertIn('post', data)
        self.assertIsInstance(data['post'], dict)
        self.assertEqual(data['post']['id'], self.post.id)
        self.assertEqual(data['post']['title'], self.post.title)


class BlogImageSerializerTest(TestCase):
    """Test the blog image serializer"""
    
    def setUp(self):
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            content='<p>Test content</p>',
            published=True
        )
        
        self.image = BlogImage.objects.create(
            post=self.post,
            caption='Test caption'
        )
        self.serializer = BlogImageSerializer(instance=self.image)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields"""
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(),
            ['id', 'image', 'created_at']
        ) 