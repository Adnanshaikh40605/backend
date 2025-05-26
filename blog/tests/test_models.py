from django.test import TestCase
from django.utils.text import slugify
from blog.models import Category, BlogPost, Comment, BlogImage


class CategoryModelTest(TestCase):
    """Test the Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            description="A test category"
        )
    
    def test_category_creation(self):
        """Test that category can be created"""
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.slug, "test-category")
        self.assertEqual(self.category.description, "A test category")
        
    def test_str_representation(self):
        """Test string representation of category"""
        self.assertEqual(str(self.category), "Test Category")
        
    def test_auto_slug_generation(self):
        """Test that slug is auto-generated"""
        category = Category.objects.create(name="Auto Slug Test")
        self.assertEqual(category.slug, slugify("Auto Slug Test"))
        
    def test_unique_slug(self):
        """Test that slugs are made unique"""
        # Create a category with the same name
        category2 = Category.objects.create(name="Test Category")
        self.assertNotEqual(category2.slug, self.category.slug)
        self.assertTrue(category2.slug.startswith(self.category.slug))


class BlogPostModelTest(TestCase):
    """Test the BlogPost model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category"
        )
        
        self.post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            content="<p>Test content</p>",
            category=self.category,
            excerpt="Test excerpt",
            featured=True,
            published=True
        )
    
    def test_post_creation(self):
        """Test that post can be created"""
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.slug, "test-post")
        self.assertEqual(self.post.content, "<p>Test content</p>")
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.excerpt, "Test excerpt")
        self.assertTrue(self.post.featured)
        self.assertTrue(self.post.published)
        
    def test_str_representation(self):
        """Test string representation of post"""
        self.assertEqual(str(self.post), "Test Post")
        
    def test_auto_slug_generation(self):
        """Test that slug is auto-generated"""
        post = BlogPost.objects.create(
            title="Auto Slug Test",
            content="<p>Content</p>",
            published=True
        )
        self.assertEqual(post.slug, slugify("Auto Slug Test"))
        
    def test_unique_slug(self):
        """Test that slugs are made unique"""
        # Create a post with the same title
        post2 = BlogPost.objects.create(
            title="Test Post",
            content="<p>Another test post</p>",
            published=True
        )
        self.assertNotEqual(post2.slug, self.post.slug)
        self.assertTrue(post2.slug.startswith(self.post.slug))


class CommentModelTest(TestCase):
    """Test the Comment model"""
    
    def setUp(self):
        self.post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            content="<p>Test content</p>",
            published=True
        )
        
        self.comment = Comment.objects.create(
            post=self.post,
            author_name="Test User",
            author_email="test@example.com",
            content="This is a test comment",
            approved=True
        )
    
    def test_comment_creation(self):
        """Test that comment can be created"""
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author_name, "Test User")
        self.assertEqual(self.comment.author_email, "test@example.com")
        self.assertEqual(self.comment.content, "This is a test comment")
        self.assertTrue(self.comment.approved)
        self.assertFalse(self.comment.is_trash)
        
    def test_str_representation(self):
        """Test string representation of comment"""
        self.assertEqual(str(self.comment), f"Comment by Test User on Test Post")
        
    def test_admin_reply(self):
        """Test admin reply functionality"""
        self.comment.admin_reply = "Admin response"
        self.comment.save()
        
        # Fetch the comment again to ensure it was saved
        updated_comment = Comment.objects.get(pk=self.comment.pk)
        self.assertEqual(updated_comment.admin_reply, "Admin response")
        self.assertIsNotNone(updated_comment.admin_reply_at)
        
    def test_parent_child_relationship(self):
        """Test parent-child relationship between comments"""
        # Create a reply to the existing comment
        reply = Comment.objects.create(
            post=self.post,
            parent=self.comment,
            author_name="Reply User",
            content="This is a reply",
            approved=True
        )
        
        self.assertEqual(reply.parent, self.comment)
        # Test that we can get replies to a comment
        self.assertEqual(list(self.comment.replies.all()), [reply])


class BlogImageModelTest(TestCase):
    """Test the BlogImage model"""
    
    def setUp(self):
        self.post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            content="<p>Test content</p>",
            published=True
        )
        
        self.image = BlogImage.objects.create(
            post=self.post,
            caption="Test image caption"
        )
    
    def test_image_creation(self):
        """Test that image can be created"""
        self.assertEqual(self.image.post, self.post)
        self.assertEqual(self.image.caption, "Test image caption")
        
    def test_str_representation(self):
        """Test string representation of image"""
        self.assertEqual(str(self.image), f"Image for Test Post") 