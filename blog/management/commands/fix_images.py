"""
Management command to fix and optimize existing blog images
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import BlogPost, BlogImage
from blog.utils.image_utils import ImageProcessor, ensure_media_directories, cleanup_unused_images
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix and optimize existing blog images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--optimize',
            action='store_true',
            help='Optimize all existing images',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up unused image files',
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check image status without making changes',
        )
        parser.add_argument(
            '--create-placeholders',
            action='store_true',
            help='Create placeholder images for missing files',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting image fix process...'))
        
        # Ensure media directories exist
        ensure_media_directories()
        self.stdout.write(self.style.SUCCESS('✓ Media directories ensured'))
        
        if options['check']:
            self.check_images()
        
        if options['optimize']:
            self.optimize_images()
        
        if options['cleanup']:
            self.cleanup_images()
        
        if options['create_placeholders']:
            self.create_placeholders()
        
        self.stdout.write(self.style.SUCCESS('Image fix process completed!'))

    def check_images(self):
        """Check the status of all images"""
        self.stdout.write(self.style.WARNING('Checking image status...'))
        
        # Check featured images
        posts_with_images = BlogPost.objects.filter(featured_image__isnull=False)
        missing_featured = 0
        valid_featured = 0
        
        for post in posts_with_images:
            if post.featured_image:
                file_path = os.path.join(settings.MEDIA_ROOT, post.featured_image.name)
                if os.path.exists(file_path):
                    valid_featured += 1
                else:
                    missing_featured += 1
                    self.stdout.write(
                        self.style.ERROR(f'Missing featured image: {post.title} - {post.featured_image.name}')
                    )
        
        # Check blog images
        blog_images = BlogImage.objects.all()
        missing_blog = 0
        valid_blog = 0
        
        for blog_image in blog_images:
            if blog_image.image:
                file_path = os.path.join(settings.MEDIA_ROOT, blog_image.image.name)
                if os.path.exists(file_path):
                    valid_blog += 1
                else:
                    missing_blog += 1
                    self.stdout.write(
                        self.style.ERROR(f'Missing blog image: {blog_image.post.title} - {blog_image.image.name}')
                    )
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'Featured images: {valid_featured} valid, {missing_featured} missing'))
        self.stdout.write(self.style.SUCCESS(f'Blog images: {valid_blog} valid, {missing_blog} missing'))

    def optimize_images(self):
        """Optimize all existing images"""
        self.stdout.write(self.style.WARNING('Optimizing images...'))
        
        # Optimize featured images
        posts_with_images = BlogPost.objects.filter(featured_image__isnull=False)
        optimized_count = 0
        
        for post in posts_with_images:
            if post.featured_image:
                file_path = os.path.join(settings.MEDIA_ROOT, post.featured_image.name)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            optimized = ImageProcessor.optimize_image(f)
                            if optimized:
                                # Save optimized image
                                post.featured_image.save(
                                    optimized.name,
                                    optimized,
                                    save=True
                                )
                                optimized_count += 1
                                self.stdout.write(f'✓ Optimized: {post.title}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error optimizing {post.title}: {str(e)}')
                        )
        
        # Optimize blog images
        blog_images = BlogImage.objects.all()
        
        for blog_image in blog_images:
            if blog_image.image:
                file_path = os.path.join(settings.MEDIA_ROOT, blog_image.image.name)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            optimized = ImageProcessor.optimize_image(f)
                            if optimized:
                                # Save optimized image
                                blog_image.image.save(
                                    optimized.name,
                                    optimized,
                                    save=True
                                )
                                optimized_count += 1
                                self.stdout.write(f'✓ Optimized blog image for: {blog_image.post.title}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error optimizing blog image: {str(e)}')
                        )
        
        self.stdout.write(self.style.SUCCESS(f'Optimized {optimized_count} images'))

    def cleanup_images(self):
        """Clean up unused image files"""
        self.stdout.write(self.style.WARNING('Cleaning up unused images...'))
        
        unused_files = cleanup_unused_images()
        
        if unused_files:
            self.stdout.write(f'Found {len(unused_files)} unused files:')
            for file in unused_files:
                self.stdout.write(f'  - {file}')
            
            # Ask for confirmation
            confirm = input('Delete these files? (y/N): ')
            if confirm.lower() == 'y':
                deleted_count = 0
                for file in unused_files:
                    file_path = os.path.join(settings.MEDIA_ROOT, file)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        self.stdout.write(f'✓ Deleted: {file}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error deleting {file}: {str(e)}')
                        )
                
                self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} unused files'))
            else:
                self.stdout.write('Cleanup cancelled')
        else:
            self.stdout.write(self.style.SUCCESS('No unused files found'))

    def create_placeholders(self):
        """Create placeholder images for missing files"""
        self.stdout.write(self.style.WARNING('Creating placeholder images...'))
        
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple placeholder image
        def create_placeholder(width=800, height=400, text="Image Not Available"):
            img = Image.new('RGB', (width, height), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            # Try to use a font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Draw text
            draw.text((x, y), text, fill='#6c757d', font=font)
            
            # Draw border
            draw.rectangle([0, 0, width-1, height-1], outline='#dee2e6', width=2)
            
            return img
        
        # Create placeholder directory
        placeholder_dir = os.path.join(settings.MEDIA_ROOT, 'placeholders')
        os.makedirs(placeholder_dir, exist_ok=True)
        
        # Create different sized placeholders
        sizes = [
            (800, 400, 'blog-placeholder.jpg'),
            (300, 200, 'thumbnail-placeholder.jpg'),
            (150, 150, 'avatar-placeholder.jpg'),
        ]
        
        created_count = 0
        for width, height, filename in sizes:
            file_path = os.path.join(placeholder_dir, filename)
            if not os.path.exists(file_path):
                img = create_placeholder(width, height)
                img.save(file_path, 'JPEG', quality=85)
                created_count += 1
                self.stdout.write(f'✓ Created: {filename}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} placeholder images'))