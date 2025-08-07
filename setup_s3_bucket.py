#!/usr/bin/env python3
"""
AWS S3 Bucket Setup Guide for Django Blog Images
"""

def print_s3_setup_guide():
    print("🚀 AWS S3 Setup Guide for Your Blog Images")
    print("=" * 60)
    
    print("\n📋 STEP 1: S3 Bucket Configuration")
    print("-" * 40)
    print("1. Go to AWS S3 Console: https://s3.console.aws.amazon.com/")
    print("2. Create a new bucket (or use existing one)")
    print("3. Choose a region (e.g., us-east-1)")
    print("4. Configure bucket settings:")
    print("   ✅ Uncheck 'Block all public access'")
    print("   ✅ Enable 'ACLs enabled'")
    print("   ✅ Enable 'Bucket owner preferred'")
    
    print("\n🔐 STEP 2: Bucket Policy (Public Read Access)")
    print("-" * 50)
    bucket_policy = '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}'''
    print("Add this bucket policy (replace YOUR-BUCKET-NAME):")
    print(bucket_policy)
    
    print("\n🔑 STEP 3: IAM User & Access Keys")
    print("-" * 40)
    print("1. Go to IAM Console: https://console.aws.amazon.com/iam/")
    print("2. Create new user (or use existing)")
    print("3. Attach policy: AmazonS3FullAccess")
    print("4. Create Access Keys (Application running outside AWS)")
    print("5. Save Access Key ID and Secret Access Key")
    
    print("\n⚙️ STEP 4: Railway Environment Variables")
    print("-" * 45)
    print("Set these in Railway Dashboard → Your Service → Variables:")
    print("AWS_ACCESS_KEY_ID=your-access-key-id")
    print("AWS_SECRET_ACCESS_KEY=your-secret-access-key")
    print("AWS_STORAGE_BUCKET_NAME=your-bucket-name")
    print("AWS_S3_REGION_NAME=us-east-1")
    print("DEBUG=False")
    
    print("\n🧪 STEP 5: Test Your Setup")
    print("-" * 30)
    print("1. Deploy your updated code to Railway")
    print("2. Upload an image through Django admin")
    print("3. Check if image URL points to S3:")
    print("   ✅ Should be: https://your-bucket.s3.amazonaws.com/featured_images/...")
    print("   ❌ Not: https://backend-production-92ae.up.railway.app/media/...")
    
    print("\n📁 STEP 6: Folder Structure in S3")
    print("-" * 35)
    print("Your S3 bucket will have this structure:")
    print("your-bucket-name/")
    print("├── featured_images/     # Blog featured images")
    print("├── blog_images/         # Additional blog images")
    print("└── uploads/")
    print("    └── ckeditor/        # CKEditor uploads")
    
    print("\n✅ STEP 7: Verify Everything Works")
    print("-" * 40)
    print("1. Upload test image via admin")
    print("2. Check image loads on frontend")
    print("3. Restart Railway service")
    print("4. Verify image still loads (persistence test)")
    
    print("\n🚨 IMPORTANT NOTES:")
    print("-" * 20)
    print("• Images will only use S3 in production (DEBUG=False)")
    print("• Local development still uses /media/ folder")
    print("• Existing images in Railway container will be lost")
    print("• Re-upload any critical images after S3 setup")
    
    print("\n💰 COST ESTIMATION:")
    print("-" * 20)
    print("• S3 Storage: ~$0.023/GB/month")
    print("• Data Transfer: First 1GB free/month")
    print("• Requests: Very minimal cost")
    print("• Typical blog: $1-5/month")

def print_troubleshooting():
    print("\n🔧 TROUBLESHOOTING")
    print("=" * 20)
    
    print("\n❌ Images not uploading to S3:")
    print("• Check AWS credentials in Railway")
    print("• Verify bucket policy allows uploads")
    print("• Check Django logs for AWS errors")
    
    print("\n❌ Images not loading:")
    print("• Verify bucket policy allows public read")
    print("• Check CORS configuration if needed")
    print("• Ensure DEBUG=False in production")
    
    print("\n❌ Permission denied errors:")
    print("• Check IAM user has S3FullAccess")
    print("• Verify access keys are correct")
    print("• Check bucket region matches settings")

if __name__ == "__main__":
    print_s3_setup_guide()
    print_troubleshooting()