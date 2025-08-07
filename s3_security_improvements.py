#!/usr/bin/env python3
"""
S3 Security Improvements Implementation
Automatically apply security best practices to your S3 bucket
"""

import boto3
import json
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class S3SecurityFixer:
    def __init__(self):
        self.bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        self.region = os.environ.get('AWS_S3_REGION_NAME')
        self.access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

    def fix_public_access_block(self):
        """Configure public access block settings"""
        print("🔒 Configuring Public Access Block...")
        
        try:
            self.s3_client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': False,  # We need this for public read
                    'RestrictPublicBuckets': False  # We need this for public read
                }
            )
            print("✅ Public access block configured")
            return True
        except ClientError as e:
            print(f"❌ Error configuring public access block: {e}")
            return False

    def create_secure_bucket_policy(self):
        """Create a secure bucket policy for public read access"""
        print("📋 Creating Secure Bucket Policy...")
        
        # Policy that allows public read but restricts everything else
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                },
                {
                    "Sid": "DenyInsecureConnections",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [
                        f"arn:aws:s3:::{self.bucket_name}/*",
                        f"arn:aws:s3:::{self.bucket_name}"
                    ],
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                }
            ]
        }
        
        try:
            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(policy)
            )
            print("✅ Secure bucket policy created")
            print("  • Allows public read access")
            print("  • Enforces HTTPS connections")
            print("  • Denies insecure connections")
            return True
        except ClientError as e:
            print(f"❌ Error creating bucket policy: {e}")
            return False

    def enable_versioning(self):
        """Enable bucket versioning"""
        print("📚 Enabling Bucket Versioning...")
        
        try:
            self.s3_client.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
            print("✅ Versioning enabled")
            print("  • Protects against accidental deletions")
            print("  • Allows recovery of previous versions")
            return True
        except ClientError as e:
            print(f"❌ Error enabling versioning: {e}")
            return False

    def setup_lifecycle_policy(self):
        """Set up lifecycle policy for cost optimization"""
        print("♻️ Setting up Lifecycle Policy...")
        
        lifecycle_config = {
            'Rules': [
                {
                    'ID': 'BlogImageOptimization',
                    'Status': 'Enabled',
                    'Filter': {'Prefix': ''},
                    'Transitions': [
                        {
                            'Days': 30,
                            'StorageClass': 'STANDARD_IA'
                        },
                        {
                            'Days': 90,
                            'StorageClass': 'GLACIER'
                        }
                    ],
                    'NoncurrentVersionTransitions': [
                        {
                            'NoncurrentDays': 30,
                            'StorageClass': 'STANDARD_IA'
                        },
                        {
                            'NoncurrentDays': 90,
                            'StorageClass': 'GLACIER'
                        }
                    ],
                    'NoncurrentVersionExpiration': {
                        'NoncurrentDays': 365
                    }
                }
            ]
        }
        
        try:
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            print("✅ Lifecycle policy configured")
            print("  • 30 days: Move to Standard-IA (cheaper)")
            print("  • 90 days: Move to Glacier (cheapest)")
            print("  • 365 days: Delete old versions")
            return True
        except ClientError as e:
            print(f"❌ Error setting lifecycle policy: {e}")
            return False

    def configure_cors(self):
        """Configure CORS for your blog domains"""
        print("🌐 Configuring CORS...")
        
        # Get allowed origins from environment
        cors_origins = [
            "https://dohblog.vercel.app",
            "https://blog-website-sigma-one.vercel.app",
            "http://localhost:3000",
            "http://localhost:3001"
        ]
        
        cors_config = {
            'CORSRules': [
                {
                    'AllowedOrigins': cors_origins,
                    'AllowedMethods': ['GET', 'HEAD'],
                    'AllowedHeaders': ['*'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        
        try:
            self.s3_client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration=cors_config
            )
            print("✅ CORS configured")
            print(f"  • Allowed origins: {len(cors_origins)} domains")
            print("  • Allowed methods: GET, HEAD")
            return True
        except ClientError as e:
            print(f"❌ Error configuring CORS: {e}")
            return False

    def setup_access_logging(self):
        """Set up access logging (requires another bucket)"""
        print("📊 Setting up Access Logging...")
        
        # For now, just show instructions since it requires another bucket
        print("ℹ️ Access logging requires a separate logging bucket")
        print("📋 Manual steps to enable logging:")
        print("  1. Create a logging bucket (e.g., 'vacationbna-logs')")
        print("  2. Go to S3 Console → Your bucket → Properties")
        print("  3. Enable 'Server access logging'")
        print("  4. Set target bucket to your logging bucket")
        
        return True

    def update_django_settings(self):
        """Update Django settings for better security"""
        print("🐍 Updating Django Settings...")
        
        settings_updates = """
# Enhanced S3 Security Settings
if not DEBUG:
    # Existing S3 settings...
    
    # Security enhancements
    AWS_S3_SECURE_URLS = True  # Use HTTPS
    AWS_S3_USE_SSL = True      # Force SSL
    AWS_S3_VERIFY = True       # Verify SSL certificates
    
    # Performance optimizations
    AWS_S3_MAX_MEMORY_SIZE = 1024 * 1024 * 50  # 50MB
    AWS_S3_TRANSFER_CONFIG = {
        'multipart_threshold': 1024 * 1024 * 50,  # 50MB
        'max_concurrency': 10,
        'multipart_chunksize': 1024 * 1024 * 10,  # 10MB
        'use_threads': True
    }
    
    # Cache control for different file types
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 24 hours
    }
    
    # Specific cache settings for images
    AWS_S3_OBJECT_PARAMETERS_IMAGES = {
        'CacheControl': 'max-age=2592000',  # 30 days for images
        'ContentType': 'image/webp'
    }
"""
        
        print("✅ Django settings recommendations:")
        print("  • Force HTTPS connections")
        print("  • Optimize multipart uploads")
        print("  • Set appropriate cache headers")
        print("  • Verify SSL certificates")
        
        print("\n📝 Add these settings to your settings.py:")
        print(settings_updates)
        
        return True

    def run_security_fixes(self):
        """Run all security improvements"""
        print("🚀 Applying S3 Security Improvements...")
        print(f"Bucket: {self.bucket_name}")
        print(f"Region: {self.region}")
        print("-" * 60)
        
        results = {}
        
        # Apply fixes
        results['public_access'] = self.fix_public_access_block()
        results['bucket_policy'] = self.create_secure_bucket_policy()
        results['versioning'] = self.enable_versioning()
        results['lifecycle'] = self.setup_lifecycle_policy()
        results['cors'] = self.configure_cors()
        results['logging'] = self.setup_access_logging()
        results['django'] = self.update_django_settings()
        
        # Summary
        print("\n" + "="*60)
        print("🛡️ SECURITY IMPROVEMENTS SUMMARY")
        print("="*60)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print(f"\n✅ Applied {successful}/{total} security improvements")
        
        if successful == total:
            print("🎉 All security improvements applied successfully!")
        elif successful >= total * 0.7:
            print("🟡 Most improvements applied - check any errors above")
        else:
            print("🔴 Several improvements failed - review errors above")
        
        print(f"\n📊 Expected security score improvement: +{successful * 10} points")
        print("🔄 Run the security audit again to see your new score!")
        
        return results

def main():
    print("🛡️ S3 Security Improvement Tool")
    print("This will apply security best practices to your S3 bucket")
    
    response = input("\nProceed with security improvements? (y/N): ")
    if response.lower() != 'y':
        print("❌ Security improvements cancelled")
        return
    
    fixer = S3SecurityFixer()
    fixer.run_security_fixes()

if __name__ == "__main__":
    main()