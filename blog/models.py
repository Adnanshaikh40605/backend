from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import logging
from django.utils.text import slugify
from django.utils.html import strip_tags
import re
import math
from .utils.image_utils import optimize_blog_image, ensure_media_directories

logger = logging.getLogger(__name__)

# Ensure media directories exist on import
ensure_media_directories()

class Category(models.Model):
    """
    Category model for organizing blog posts
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code for category display')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_post_count(self):
        """Get the number of published posts in this category"""
        return self.posts.filter(published=True).count()

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    content = CKEditor5Field('Content', config_name='extends')
    excerpt = models.TextField(
        max_length=300, 
        blank=True, 
        help_text='Brief description of the post (max 300 characters). If left blank, will be auto-generated from content.'
    )
    featured_image = models.ImageField(upload_to='featured_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', db_index=True)
    published = models.BooleanField(default=False, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    position = models.IntegerField(default=0, db_index=True)
    read_time = models.PositiveIntegerField(
        default=0, 
        help_text='Estimated reading time in minutes (auto-calculated based on content)'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    def calculate_read_time(self):
        """Calculate estimated reading time based on content"""
        if not self.content:
            return 1
        
        # Strip HTML tags and get plain text
        plain_text = strip_tags(self.content)
        
        # Count words (average reading speed is 200-250 words per minute)
        word_count = len(plain_text.split())
        
        # Calculate read time (using 200 words per minute as average)
        read_time = math.ceil(word_count / 200)
        
        # Minimum 1 minute read time
        return max(1, read_time)
    
    def generate_excerpt(self):
        """Generate excerpt from content if not provided"""
        if self.excerpt:
            return self.excerpt
        
        if not self.content:
            return ""
        
        # Strip HTML tags and get plain text
        plain_text = strip_tags(self.content)
        
        # Clean up extra whitespace
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        
        # Generate excerpt (first 250 characters, ending at word boundary)
        if len(plain_text) <= 250:
            return plain_text
        
        # Find the last complete word within 250 characters
        excerpt = plain_text[:250]
        last_space = excerpt.rfind(' ')
        
        if last_space > 200:  # Ensure we have a reasonable length
            excerpt = excerpt[:last_space]
        
        return excerpt + "..."

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            self.excerpt = self.generate_excerpt()
        
        # Auto-calculate read time
        self.read_time = self.calculate_read_time()
        # Optimize featured image if present and it's a new upload
        if self.featured_image and hasattr(self.featured_image, '_file'):
            try:
                optimized_image = optimize_blog_image(self.featured_image)
                if optimized_image:
                    self.featured_image.save(
                        optimized_image.name,
                        optimized_image,
                        save=False  # Don't trigger recursive save
                    )
                    logger.info(f"Optimized featured image: {optimized_image.name}")
            except Exception as e:
                logger.error(f"Error optimizing featured image: {str(e)}")
        
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class BlogImage(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.post.title}"

    def save(self, *args, **kwargs):
        """Optimize image on save"""
        if self.image and hasattr(self.image, '_file'):
            try:
                optimized_image = optimize_blog_image(self.image)
                if optimized_image:
                    self.image.save(
                        optimized_image.name,
                        optimized_image,
                        save=False  # Don't trigger recursive save
                    )
                    logger.info(f"Optimized blog image: {optimized_image.name}")
            except Exception as e:
                logger.error(f"Error optimizing blog image: {str(e)}")
        
        super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments', db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', db_index=True)
    author_name = models.CharField(max_length=100, blank=True, null=True)
    author_email = models.EmailField(blank=True, null=True)
    author_website = models.URLField(blank=True, null=True)
    content = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False, db_index=True)
    is_trash = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_reply = models.TextField(null=True, blank=True)
    # New fields for nested comments
    level = models.IntegerField(default=0, db_index=True)
    path = models.CharField(max_length=255, blank=True, db_index=True)

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None
        
    def get_replies(self):
        """Get all approved replies to this comment"""
        return self.replies.filter(approved=True, is_trash=False)
        
    def get_replies_count(self):
        """Get count of approved replies"""
        return self.replies.filter(approved=True, is_trash=False).count()
    
    def save(self, *args, **kwargs):
        # Calculate the level based on parent
        if self.parent:
            self.level = self.parent.level + 1
            
            # Generate path for efficient querying
            if self.parent.path:
                if self.id:
                    self.path = f"{self.parent.path}/{self.id}"
                # For new comments (no ID yet), we'll update path after save
            else:
                if self.id:
                    self.path = f"{self.parent.id}/{self.id}"
                # For new comments (no ID yet), we'll update path after save
        else:
            self.level = 0
            if self.id:
                self.path = str(self.id)
            # For new comments (no ID yet), we'll update path after save
        
        # Call the "real" save method
        super().save(*args, **kwargs)
        
        # Update path after save to include this comment's ID if needed
        if not self.path and self.id:
            if self.parent and self.parent.path:
                self.path = f"{self.parent.path}/{self.id}"
            elif self.parent:
                self.path = f"{self.parent.id}/{self.id}"
            else:
                self.path = str(self.id)
            # Update only the path field to avoid recursion
            Comment.objects.filter(id=self.id).update(path=self.path)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'approved']),
            models.Index(fields=['is_trash']),
            models.Index(fields=['parent']),
            models.Index(fields=['approved', 'parent']),
            models.Index(fields=['level']),
            models.Index(fields=['path']),
        ] 

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('comment', 'user_name')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user_name} liked comment {self.comment.id}"