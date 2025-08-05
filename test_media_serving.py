#!/usr/bin/env python3
"""
Test script to verify media file serving is working correctly
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.test import Client
from blog.models import BlogPost
import requests

def test_media_settings():
    """Test Django media settings"""
    print("=== Django Media Settings ===")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"Media root exists: {os.path.exists(settings.MEDIA_ROOT)}")
    
    # List media files
    if os.path.exists(settings.MEDIA_ROOT):
        print("\nMedia files found:")
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), settings.MEDIA_ROOT)
                print(f"  {rel_path}")
    else:
        print("Media root directory does not exist!")

def test_media_urls():
    """Test media URL serving"""
    print("\n=== Testing Media URL Serving ===")
    
    # Test with Django test client
    client = Client()
    
    # Find a media file to test
    media_files = []
    if os.path.exists(settings.MEDIA_ROOT):
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                if not file.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, file), settings.MEDIA_ROOT)
                    media_files.append(rel_path)
    
    if media_files:
        test_file = media_files[0]
        test_url = f"{settings.MEDIA_URL}{test_file}"
        print(f"Testing URL: {test_url}")
        
        response = client.get(test_url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Media serving is working!")
        else:
            print("❌ Media serving failed!")
    else:
        print("No media files found to test")

def test_blog_images():
    """Test blog post images"""
    print("\n=== Testing Blog Post Images ===")
    
    posts_with_images = BlogPost.objects.filter(featured_image__isnull=False)[:5]
    
    if posts_with_images:
        for post in posts_with_images:
            print(f"\nPost: {post.title}")
            print(f"Featured image: {post.featured_image}")
            print(f"Image URL: {post.featured_image.url if post.featured_image else 'None'}")
            
            if post.featured_image:
                # Check if file exists
                file_path = post.featured_image.path
                exists = os.path.exists(file_path)
                print(f"File exists: {exists}")
                
                if exists:
                    file_size = os.path.getsize(file_path)
                    print(f"File size: {file_size} bytes")
    else:
        print("No blog posts with images found")

def test_external_access():
    """Test external access to media files"""
    print("\n=== Testing External Access ===")
    
    # Test localhost access
    base_urls = [
        'http://localhost:8000',
        'http://127.0.0.1:8000'
    ]
    
    # Find a media file to test
    media_files = []
    if os.path.exists(settings.MEDIA_ROOT):
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                if not file.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, file), settings.MEDIA_ROOT)
                    media_files.append(rel_path)
    
    if media_files:
        test_file = media_files[0]
        
        for base_url in base_urls:
            test_url = f"{base_url}{settings.MEDIA_URL}{test_file}"
            print(f"Testing external URL: {test_url}")
            
            try:
                response = requests.get(test_url, timeout=5)
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ External access working!")
                else:
                    print("❌ External access failed!")
            except requests.exceptions.ConnectionError:
                print("❌ Connection failed - server may not be running")
            except Exception as e:
                print(f"❌ Error: {e}")
    else:
        print("No media files found to test")

if __name__ == "__main__":
    print("Testing Media File Serving")
    print("=" * 50)
    
    test_media_settings()
    test_media_urls()
    test_blog_images()
    test_external_access()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    
    print("\n=== Recommendations ===")
    print("1. Ensure Django development server is running: python manage.py runserver")
    print("2. Check that MEDIA_URL and MEDIA_ROOT are correctly configured")
    print("3. Verify media files exist in the media directory")
    print("4. Test media URLs in browser: http://localhost:8000/media/[filename]")
    print("5. Check Django URL patterns include media serving for development")