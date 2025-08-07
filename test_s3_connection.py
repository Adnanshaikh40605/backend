#!/usr/bin/env python
"""
Test S3 connection and bucket access
"""
import os
import sys
import django
from pathlib import Path
from dotenv import load_dotenv

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings

def test_s3_connection():
    """Test S3 connection and bucket access"""
    print("Testing S3 connection...")
    
    # Check if AWS credentials are configured
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    print(f"AWS Access Key ID: {'*' * (len(aws_access_key) - 4) + aws_access_key[-4:] if aws_access_key else 'Not set'}")
    print(f"AWS Secret Key: {'*' * 10 if aws_secret_key else 'Not set'}")
    print(f"Bucket Name: {bucket_name}")
    print(f"Region: {region}")
    
    if not all([aws_access_key, aws_secret_key, bucket_name]):
        print("❌ AWS credentials not properly configured")
        return False
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        # Test connection by listing bucket contents
        print(f"Testing connection to bucket: {bucket_name}")
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        
        print("✅ Successfully connected to S3!")
        print(f"Bucket exists and is accessible")
        
        # Test upload permissions by creating a test file
        test_key = 'test-connection.txt'
        test_content = b'This is a test file to verify upload permissions'
        
        print(f"Testing upload permissions...")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print("✅ Upload test successful!")
        
        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Cleanup successful!")
        
        # Test Django storage
        print("Testing Django S3 storage...")
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        # Test file upload through Django
        test_file = ContentFile(b'Django storage test', name='django-test.txt')
        file_path = default_storage.save('test/django-test.txt', test_file)
        print(f"✅ Django storage test successful! File saved to: {file_path}")
        
        # Get the URL
        file_url = default_storage.url(file_path)
        print(f"File URL: {file_url}")
        
        # Clean up
        default_storage.delete(file_path)
        print("✅ Django storage cleanup successful!")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{bucket_name}' does not exist")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to bucket '{bucket_name}'. Check permissions.")
        else:
            print(f"❌ AWS Error: {error_code} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_s3_connection()
    sys.exit(0 if success else 1)