#!/usr/bin/env python
"""
Create S3 bucket and configure it for the blog application
"""
import os
import sys
import django
from pathlib import Path
import json
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

def create_s3_bucket():
    """Create S3 bucket and configure it"""
    print("Creating S3 bucket...")
    
    # Get credentials from environment
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_S3_REGION_NAME', 'ap-south-1')
    
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
        
        # Check if bucket already exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists!")
            return True
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                print(f"Bucket '{bucket_name}' does not exist. Creating...")
            else:
                print(f"❌ Error checking bucket: {e}")
                return False
        
        # Create bucket
        if region == 'us-east-1':
            # us-east-1 doesn't need LocationConstraint
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✅ Bucket '{bucket_name}' created successfully!")
        
        # Configure bucket for public read access (for media files)
        print("Configuring bucket permissions...")
        
        # Disable block public access for this bucket
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        
        # Set bucket policy to allow public read access to media files
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        print("✅ Bucket policy configured for public read access!")
        
        # Configure CORS for web access
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': ['*'],
                    'ExposeHeaders': ['ETag'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        
        print("✅ CORS configuration applied!")
        
        # Test upload
        print("Testing upload...")
        test_key = 'test-setup.txt'
        test_content = b'S3 bucket setup successful!'
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        
        # Get the URL
        test_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{test_key}"
        print(f"✅ Test file uploaded successfully!")
        print(f"Test URL: {test_url}")
        
        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Test cleanup completed!")
        
        print(f"\n🎉 S3 bucket '{bucket_name}' is ready for use!")
        print(f"Media URL: https://{bucket_name}.s3.{region}.amazonaws.com/")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ AWS Error: {error_code} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == '__main__':
    success = create_s3_bucket()
    sys.exit(0 if success else 1)