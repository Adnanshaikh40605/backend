#!/usr/bin/env python3
"""
Cloudinary Setup for Django
Easy cloud storage with automatic image optimization
"""

# 1. Install required packages
REQUIRED_PACKAGES = [
    "cloudinary==1.36.0",
    "django-cloudinary-storage==0.3.0",
]

# 2. Django settings for Cloudinary
CLOUDINARY_SETTINGS = """
# Cloudinary Settings for Production
if not DEBUG:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    # Cloudinary Configuration
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    
    # Use Cloudinary for media files
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # Cloudinary will handle the media URL automatically
else:
    # Local development settings
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
"""

# 3. Environment variables needed
ENV_VARS = {
    'CLOUDINARY_CLOUD_NAME': 'Your Cloudinary cloud name',
    'CLOUDINARY_API_KEY': 'Your Cloudinary API key',
    'CLOUDINARY_API_SECRET': 'Your Cloudinary API secret'
}

# 4. Benefits
BENEFITS = [
    "✅ Automatic image optimization",
    "✅ CDN delivery worldwide", 
    "✅ Automatic WebP conversion",
    "✅ Image transformations on-the-fly",
    "✅ Free tier available (25GB storage, 25GB bandwidth)",
    "✅ Easy setup and management"
]

def print_setup_instructions():
    print("Cloudinary Setup Instructions")
    print("=" * 50)
    
    print("\nBenefits:")
    for benefit in BENEFITS:
        print(f"  {benefit}")
    
    print("\n1. Sign up at https://cloudinary.com")
    print("2. Get your credentials from the dashboard")
    
    print("\n3. Install packages:")
    for package in REQUIRED_PACKAGES:
        print(f"   pip install {package}")
    
    print(f"\n4. Add to settings.py:")
    print(CLOUDINARY_SETTINGS)
    
    print(f"\n5. Set environment variables in Railway:")
    for key, description in ENV_VARS.items():
        print(f"   {key} = {description}")
    
    print(f"\n6. Deploy and test image uploads")
    print(f"\n7. Images will be automatically optimized and served via CDN!")

if __name__ == "__main__":
    print_setup_instructions()