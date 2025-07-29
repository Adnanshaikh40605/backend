from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import logging
from django.utils.text import slugify

logger = logging.getLogger(__name__)

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
    featured_image = models.ImageField(upload_to='featured_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', db_index=True)
    published = models.BooleanField(default=False, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    position = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
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
        if self.image:
            self.optimize_image()
        super().save(*args, **kwargs)
    
    def optimize_image(self, quality=85, convert_to_webp=True):
        """Compress image and optionally convert to WebP format"""
        try:
            # Open image using PIL
            img = Image.open(self.image)
            
            # If convert to WebP is requested and format is supported
            if convert_to_webp and img.mode in ('RGB', 'RGBA'):
                # Prepare BytesIO object to save the image
                img_io = BytesIO()
                
                # Save as WebP format with specified quality
                img.save(img_io, format='WEBP', quality=quality, optimize=True)
                
                # Get original filename and change extension
                filename = os.path.splitext(os.path.basename(self.image.name))[0]
                new_filename = f"{filename}.webp"
                
                # Save the optimized image back to the model field
                self.image.save(
                    new_filename,
                    ContentFile(img_io.getvalue()),
                    save=False  # Don't trigger recursive save
                )
                logger.info(f"Converted image to WebP: {new_filename}")
            else:
                # If WebP not requested or not supported, just compress in original format
                img_io = BytesIO()
                img_format = img.format if img.format else 'JPEG'
                
                # Save with quality settings
                img.save(img_io, format=img_format, quality=quality, optimize=True)
                
                # Save the optimized image back to the model field
                self.image.save(
                    self.image.name,
                    ContentFile(img_io.getvalue()),
                    save=False  # Don't trigger recursive save
                )
                logger.info(f"Compressed image: {self.image.name}")
                
        except Exception as e:
            logger.error(f"Error optimizing image: {str(e)}")

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