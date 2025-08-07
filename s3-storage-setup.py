#!/usr/bin/env python3
"""
AWS S3 Storage Setup for Django
This script helps set up S3 storage for production image uploads
"""

# 1. Install required packages
REQUIRED_PACKAGES = [
    "django-storages[boto3]==1.14.2",
    "boto3==1.34.0",
]

# 2. Add to requirements.txt
def update_requirements():
    with open('requirements.txt', 'a') as f:
        f.write('\n# S3 Storage\n')
        for package in REQUIRED_PACKAGES:
            f.write(f'{package}\n')

# 3. Django settings for S3
S3_SETTINGS = """
# AWS S3 Settings for Production
if not DEBUG:
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    # S3 Settings
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    
    # Use S3 for media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # Update media URL to use S3
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Local development settings
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
"""

# 4. Environment variables needed
ENV_VARS = {
    'AWS_ACCESS_KEY_ID': 'Your AWS access key',
    'AWS_SECRET_ACCESS_KEY': 'Your AWS secret key', 
    'AWS_STORAGE_BUCKET_NAME': 'your-bucket-name',
    'AWS_S3_REGION_NAME': 'us-east-1'
}

def print_setup_instructions():
    print("AWS S3 Setup Instructions")
    print("=" * 50)
    
    print("\n1. Install packages:")
    for package in REQUIRED_PACKAGES:
        print(f"   pip install {package}")
    
    print(f"\n2. Add to settings.py:")
    print(S3_SETTINGS)
    
    print(f"\n3. Set environment variables in Railway:")
    for key, description in ENV_VARS.items():
        print(f"   {key} = {description}")
    
    print(f"\n4. Create S3 bucket with public read access")
    print(f"5. Deploy and test image uploads")

if __name__ == "__main__":
    print_setup_instructions()