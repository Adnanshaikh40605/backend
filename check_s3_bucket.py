#!/usr/bin/env python3
"""
Check S3 Bucket Status
"""

import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

def check_bucket():
    print("🔍 Checking S3 Bucket Status")
    print("=" * 40)
    
    # Get credentials
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_S3_REGION_NAME')
    
    print(f"Bucket Name: {bucket_name}")
    print(f"Region: {region}")
    print(f"Access Key: {access_key[:10]}..." if access_key else "Access Key: Not set")
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        print(f"\n✅ S3 Client created successfully")
        
        # Check if bucket exists
        try:
            response = s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' exists and is accessible")
            
            # Get bucket location
            location = s3_client.get_bucket_location(Bucket=bucket_name)
            bucket_region = location.get('LocationConstraint')
            if bucket_region is None:
                bucket_region = 'us-east-1'  # Default region
            
            print(f"📍 Bucket region: {bucket_region}")
            
            if bucket_region != region:
                print(f"⚠️  Region mismatch! Bucket is in {bucket_region}, but you configured {region}")
                return False
            
            # Test permissions
            try:
                # List objects (read permission)
                s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                print("✅ Read permission: OK")
                
                # Test upload (write permission)
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key='test-permission.txt',
                    Body=b'Permission test'
                )
                print("✅ Write permission: OK")
                
                # Test public access
                test_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/test-permission.txt"
                print(f"✅ Test file uploaded: {test_url}")
                
                # Clean up
                s3_client.delete_object(Bucket=bucket_name, Key='test-permission.txt')
                print("✅ Delete permission: OK")
                
                return True
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'AccessDenied':
                    print("❌ Access denied - check IAM permissions")
                else:
                    print(f"❌ Permission error: {e}")
                return False
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{bucket_name}' does not exist")
                print(f"   Create it at: https://s3.console.aws.amazon.com/s3/bucket/create")
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{bucket_name}'")
                print(f"   Check your AWS credentials and IAM permissions")
            else:
                print(f"❌ Bucket error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def list_available_buckets():
    """List all available buckets for this account"""
    print(f"\n📋 Available S3 Buckets")
    print("=" * 30)
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME')
        )
        
        response = s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        
        if not buckets:
            print("No buckets found in this account")
            return
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            created = bucket['CreationDate'].strftime('%Y-%m-%d')
            
            # Get bucket region
            try:
                location = s3_client.get_bucket_location(Bucket=bucket_name)
                region = location.get('LocationConstraint') or 'us-east-1'
            except:
                region = 'unknown'
            
            print(f"  • {bucket_name} (region: {region}, created: {created})")
            
    except Exception as e:
        print(f"❌ Could not list buckets: {e}")

if __name__ == "__main__":
    success = check_bucket()
    
    if not success:
        list_available_buckets()
        
        print(f"\n💡 Next Steps:")
        print("1. Create the bucket if it doesn't exist")
        print("2. Check the bucket region matches your configuration")
        print("3. Verify IAM permissions (S3FullAccess)")
        print("4. Ensure bucket allows public read access")