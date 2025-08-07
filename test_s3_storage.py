#!/usr/bin/env python3
"""
Test S3 Storage Configuration
Run this script to verify your S3 setup is working correctly
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_s3_configuration():
    """Test if S3 is properly configured"""
    print("🧪 Testing S3 Configuration")
    print("=" * 40)
    
    # Check if we're in production mode
    if settings.DEBUG:
        print("❌ DEBUG=True - S3 will not be used")
        print("   Set DEBUG=False to test S3 storage")
        return False
    
    # Check required environment variables
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_REGION_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All environment variables present")
    
    # Check storage backend
    storage_backend = settings.DEFAULT_FILE_STORAGE
    if 'S3Boto3Storage' not in storage_backend:
        print(f"❌ Storage backend not set to S3: {storage_backend}")
        return False
    
    print("✅ Storage backend configured for S3")
    
    # Check media URL
    media_url = settings.MEDIA_URL
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    # Handle different URL formats
    if region == 'us-east-1':
        expected_url = f"https://{bucket_name}.s3.amazonaws.com/"
    else:
        expected_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/"
    
    if media_url != expected_url:
        print(f"❌ Media URL mismatch:")
        print(f"   Expected: {expected_url}")
        print(f"   Actual: {media_url}")
        return False
    
    print("✅ Media URL correctly configured")
    
    return True

def test_s3_connection():
    """Test actual connection to S3"""
    print("\n🔗 Testing S3 Connection")
    print("=" * 30)
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME')
        )
        
        bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        
        # Test bucket access
        s3_client.head_bucket(Bucket=bucket_name)
        print("✅ Successfully connected to S3 bucket")
        
        # Test upload permissions
        test_key = 'test-upload.txt'
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=b'Test upload'
        )
        print("✅ Upload permissions working")
        
        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Delete permissions working")
        
        return True
        
    except ImportError:
        print("❌ boto3 not installed - run: pip install boto3")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print("❌ Access denied - check your AWS credentials")
        elif error_code == '404':
            print("❌ Bucket not found - check bucket name and region")
        else:
            print(f"❌ AWS Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_django_file_upload():
    """Test file upload through Django"""
    print("\n📁 Testing Django File Upload")
    print("=" * 35)
    
    try:
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.files.storage import default_storage
        
        # Create test file
        test_file = SimpleUploadedFile(
            "test-image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        # Upload through Django storage
        file_path = default_storage.save('test-uploads/test-image.jpg', test_file)
        print(f"✅ File uploaded to: {file_path}")
        
        # Get URL
        file_url = default_storage.url(file_path)
        print(f"✅ File URL: {file_url}")
        
        # Verify URL format
        bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
        
        # Check for correct S3 URL format
        if f"{bucket_name}.s3" in file_url and "amazonaws.com" in file_url:
            print("✅ URL points to S3")
        else:
            print("❌ URL does not point to S3")
            return False
        
        # Clean up
        default_storage.delete(file_path)
        print("✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Django upload error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 S3 Storage Test Suite")
    print("=" * 50)
    
    # Test 1: Configuration
    config_ok = test_s3_configuration()
    
    if not config_ok:
        print("\n❌ Configuration test failed")
        print("Fix configuration issues before proceeding")
        return
    
    # Test 2: S3 Connection
    connection_ok = test_s3_connection()
    
    if not connection_ok:
        print("\n❌ S3 connection test failed")
        print("Check your AWS credentials and bucket settings")
        return
    
    # Test 3: Django Upload
    upload_ok = test_django_file_upload()
    
    if not upload_ok:
        print("\n❌ Django upload test failed")
        return
    
    # All tests passed
    print("\n🎉 ALL TESTS PASSED!")
    print("=" * 25)
    print("Your S3 storage is properly configured!")
    print("You can now upload images and they will be stored in S3.")
    
    print("\n📋 Next Steps:")
    print("1. Deploy your code to Railway")
    print("2. Set DEBUG=False in Railway environment")
    print("3. Upload test images through Django admin")
    print("4. Verify images load correctly on your frontend")

if __name__ == "__main__":
    main()