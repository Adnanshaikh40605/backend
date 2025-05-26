from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import logging
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.utils import timezone
import uuid

logger = logging.getLogger(__name__)

def get_image_upload_path(instance, filename):
    """Generate a unique path for each uploaded image"""
    _, ext = os.path.splitext(filename)
    unique_id = uuid.uuid4().hex[:8]
    return f'blog_images/{timezone.now().strftime("%Y/%m/%d")}/{unique_id}{ext}'

class Category(models.Model):
    """Category model for blog posts"""
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    featured_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get URL for category page"""
        return reverse('blog:category_detail', args=[self.slug])
    
    @property
    def post_count(self):
        """Return the number of published posts in this category"""
        return self.blogpost_set.filter(published=True).count()

class BlogPost(models.Model):
    """Blog post model with optimized database fields"""
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    content = CKEditor5Field('Content', config_name='extends')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    excerpt = models.TextField(blank=True, null=True, help_text="Short description for SEO and previews")
    featured = models.BooleanField(default=False, help_text="Mark as a featured post")
    featured_image = models.ImageField(upload_to=get_image_upload_path, null=True, blank=True)
    published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['published', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        # Optimize featured image if present
        if self.featured_image:
            try:
                # Open image using PIL
                img = Image.open(self.featured_image)
                
                # Prepare BytesIO object
                img_io = BytesIO()
                
                # Try to convert to WebP if RGB/RGBA
                if img.mode in ('RGB', 'RGBA'):
                    # Save as WebP format
                    img.save(img_io, format='WEBP', quality=85, optimize=True)
                    
                    # Get original filename and change extension
                    filename = os.path.splitext(os.path.basename(self.featured_image.name))[0]
                    new_filename = f"{filename}.webp"
                    
                    # Save the optimized image
                    self.featured_image.save(
                        new_filename,
                        ContentFile(img_io.getvalue()),
                        save=False  # Don't trigger recursive save
                    )
                    logger.info(f"Converted featured image to WebP: {new_filename}")
                else:
                    # Just compress in original format
                    img_format = img.format if img.format else 'JPEG'
                    img.save(img_io, format=img_format, quality=85, optimize=True)
                    self.featured_image.save(
                        self.featured_image.name,
                        ContentFile(img_io.getvalue()),
                        save=False
                    )
                    logger.info(f"Compressed featured image: {self.featured_image.name}")
            except Exception as e:
                logger.error(f"Error optimizing featured image: {str(e)}")
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get URL for the blog post"""
        return reverse('blog:post_detail', args=[self.slug])

class BlogImage(models.Model):
    """Blog image model"""
    post = models.ForeignKey(BlogPost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_upload_path)
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Blog Image'
        verbose_name_plural = 'Blog Images'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
        ]
    
    def __str__(self):
        return f"Image for {self.post.title}"

class Comment(models.Model):
    """Comment model with optimized database fields"""
    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE, db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100, blank=True, null=True, default="Anonymous")
    author_email = models.EmailField(blank=True, null=True)
    author_website = models.URLField(blank=True, null=True)
    content = models.TextField()
    approved = models.BooleanField(default=False, db_index=True)
    is_trash = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin reply fields
    admin_reply = models.TextField(blank=True, null=True)
    admin_reply_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'approved']),
            models.Index(fields=['post', 'is_trash']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"
        
    def save(self, *args, **kwargs):
        """Update admin_reply_at if admin_reply is set"""
        if self.admin_reply and not self.admin_reply_at:
            self.admin_reply_at = timezone.now()
        super().save(*args, **kwargs)

# Add the following function for related models to make migrations easier
def generate_migrations():
    """Helper function to create migrations for the models"""
    from django.core.management import call_command
    call_command('makemigrations', 'blog')
    call_command('migrate', 'blog') 