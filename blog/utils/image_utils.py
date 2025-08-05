"""
Image utility functions for the blog application
"""

import os
import logging
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files.storage import default_storage
import mimetypes

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Image processing utility class for handling blog images
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {
        'JPEG': 'image/jpeg',
        'JPG': 'image/jpeg', 
        'PNG': 'image/png',
        'WEBP': 'image/webp',
        'GIF': 'image/gif'
    }
    
    # Default settings
    DEFAULT_QUALITY = 85
    DEFAULT_MAX_WIDTH = 1200
    DEFAULT_MAX_HEIGHT = 800
    THUMBNAIL_SIZE = (300, 200)
    
    @classmethod
    def optimize_image(cls, image_file, max_width=None, max_height=None, quality=None, convert_to_webp=True):
        """
        Optimize an image file by resizing and compressing
        
        Args:
            image_file: Django UploadedFile or file-like object
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            quality: JPEG/WebP quality (1-100)
            convert_to_webp: Whether to convert to WebP format
            
        Returns:
            ContentFile: Optimized image file
        """
        try:
            # Set defaults
            max_width = max_width or cls.DEFAULT_MAX_WIDTH
            max_height = max_height or cls.DEFAULT_MAX_HEIGHT
            quality = quality or cls.DEFAULT_QUALITY
            
            # Open image
            img = Image.open(image_file)
            
            # Auto-rotate based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Convert to RGB if necessary (for WebP/JPEG)
            if img.mode in ('RGBA', 'LA', 'P') and convert_to_webp:
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Resize if necessary
            original_width, original_height = img.size
            if original_width > max_width or original_height > max_height:
                # Calculate new size maintaining aspect ratio
                ratio = min(max_width / original_width, max_height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {original_width}x{original_height} to {new_width}x{new_height}")
            
            # Save optimized image
            img_io = BytesIO()
            
            if convert_to_webp and img.mode in ('RGB', 'RGBA'):
                # Save as WebP
                img.save(img_io, format='WEBP', quality=quality, optimize=True)
                
                # Generate new filename with .webp extension
                original_name = getattr(image_file, 'name', 'image.jpg')
                name_without_ext = os.path.splitext(original_name)[0]
                new_filename = f"{name_without_ext}.webp"
                
                logger.info(f"Converted image to WebP: {new_filename}")
            else:
                # Keep original format
                img_format = img.format or 'JPEG'
                img.save(img_io, format=img_format, quality=quality, optimize=True)
                
                new_filename = getattr(image_file, 'name', 'image.jpg')
                logger.info(f"Optimized image in {img_format} format: {new_filename}")
            
            # Create ContentFile
            img_io.seek(0)
            return ContentFile(img_io.getvalue(), name=new_filename)
            
        except Exception as e:
            logger.error(f"Error optimizing image: {str(e)}")
            # Return original file if optimization fails
            return image_file
    
    @classmethod
    def create_thumbnail(cls, image_file, size=None):
        """
        Create a thumbnail from an image file
        
        Args:
            image_file: Django UploadedFile or file-like object
            size: Tuple of (width, height) for thumbnail
            
        Returns:
            ContentFile: Thumbnail image file
        """
        try:
            size = size or cls.THUMBNAIL_SIZE
            
            # Open image
            img = Image.open(image_file)
            
            # Auto-rotate based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Save thumbnail
            img_io = BytesIO()
            img.save(img_io, format='WEBP', quality=80, optimize=True)
            
            # Generate thumbnail filename
            original_name = getattr(image_file, 'name', 'image.jpg')
            name_without_ext = os.path.splitext(original_name)[0]
            thumbnail_filename = f"{name_without_ext}_thumb.webp"
            
            img_io.seek(0)
            return ContentFile(img_io.getvalue(), name=thumbnail_filename)
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            return None
    
    @classmethod
    def validate_image(cls, image_file, max_size_mb=5):
        """
        Validate an uploaded image file
        
        Args:
            image_file: Django UploadedFile
            max_size_mb: Maximum file size in MB
            
        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []
        
        try:
            # Check file size
            if image_file.size > max_size_mb * 1024 * 1024:
                errors.append(f"File size {image_file.size / 1024 / 1024:.1f}MB exceeds maximum {max_size_mb}MB")
            
            # Check file type
            content_type = image_file.content_type
            if content_type not in cls.SUPPORTED_FORMATS.values():
                errors.append(f"File type {content_type} is not supported. Supported types: {', '.join(cls.SUPPORTED_FORMATS.values())}")
            
            # Try to open image to validate it's a real image
            try:
                img = Image.open(image_file)
                img.verify()  # Verify it's a valid image
                
                # Reset file pointer after verify()
                image_file.seek(0)
                
                # Check image dimensions
                img = Image.open(image_file)
                width, height = img.size
                
                if width < 100 or height < 100:
                    errors.append(f"Image dimensions {width}x{height} are too small. Minimum 100x100 pixels required.")
                
                if width > 5000 or height > 5000:
                    errors.append(f"Image dimensions {width}x{height} are too large. Maximum 5000x5000 pixels allowed.")
                
            except Exception as e:
                errors.append(f"Invalid image file: {str(e)}")
            
        except Exception as e:
            errors.append(f"Error validating image: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @classmethod
    def get_image_info(cls, image_file):
        """
        Get information about an image file
        
        Args:
            image_file: Django UploadedFile or file path
            
        Returns:
            dict: Image information
        """
        try:
            img = Image.open(image_file)
            
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.size[0],
                'height': img.size[1],
                'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            }
            
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            return None

def ensure_media_directories():
    """
    Ensure all required media directories exist
    """
    directories = [
        'featured_images',
        'blog_images',
        'thumbnails',
        'uploads'
    ]
    
    for directory in directories:
        dir_path = os.path.join(settings.MEDIA_ROOT, directory)
        os.makedirs(dir_path, exist_ok=True)
        
        # Create .gitkeep file if directory is empty
        gitkeep_path = os.path.join(dir_path, '.gitkeep')
        if not os.listdir(dir_path) or not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write('')
    
    logger.info("Media directories ensured")

def cleanup_unused_images():
    """
    Clean up unused image files (run as management command)
    """
    from blog.models import BlogPost, BlogImage
    
    # Get all image files in media directory
    media_files = set()
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for file in files:
            if not file.startswith('.'):
                rel_path = os.path.relpath(os.path.join(root, file), settings.MEDIA_ROOT)
                media_files.add(rel_path)
    
    # Get all referenced images from database
    referenced_files = set()
    
    # Featured images
    for post in BlogPost.objects.filter(featured_image__isnull=False):
        if post.featured_image:
            referenced_files.add(post.featured_image.name)
    
    # Blog images
    for blog_image in BlogImage.objects.all():
        if blog_image.image:
            referenced_files.add(blog_image.image.name)
    
    # Find unused files
    unused_files = media_files - referenced_files
    
    logger.info(f"Found {len(unused_files)} unused image files")
    
    return unused_files

# Convenience functions
def optimize_blog_image(image_file):
    """Optimize a blog image with default settings"""
    return ImageProcessor.optimize_image(
        image_file,
        max_width=1200,
        max_height=800,
        quality=85,
        convert_to_webp=True
    )

def create_blog_thumbnail(image_file):
    """Create a thumbnail for a blog image"""
    return ImageProcessor.create_thumbnail(image_file, size=(300, 200))

def validate_blog_image(image_file):
    """Validate a blog image upload"""
    return ImageProcessor.validate_image(image_file, max_size_mb=5)