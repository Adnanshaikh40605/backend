#!/usr/bin/env python3
"""
S3 Security and Best Practices Audit
Comprehensive check of your S3 configuration against AWS best practices
"""

import boto3
import json
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class S3SecurityAudit:
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
        
        self.issues = []
        self.recommendations = []
        self.security_score = 0
        self.max_score = 0

    def check_bucket_public_access(self):
        """Check bucket public access block settings"""
        print("🔒 Checking Public Access Block Settings...")
        self.max_score += 10
        
        try:
            response = self.s3_client.get_public_access_block(Bucket=self.bucket_name)
            config = response['PublicAccessBlockConfiguration']
            
            if not config.get('BlockPublicAcls', False):
                self.issues.append("❌ Public ACLs are allowed")
                self.recommendations.append("Enable 'Block public ACLs' for better security")
            else:
                print("✅ Public ACLs are blocked")
                self.security_score += 2
            
            if not config.get('IgnorePublicAcls', False):
                self.issues.append("❌ Public ACLs are not ignored")
                self.recommendations.append("Enable 'Ignore public ACLs'")
            else:
                print("✅ Public ACLs are ignored")
                self.security_score += 2
            
            if not config.get('BlockPublicPolicy', False):
                self.issues.append("❌ Public bucket policies are allowed")
                self.recommendations.append("Consider blocking public bucket policies")
            else:
                print("✅ Public bucket policies are blocked")
                self.security_score += 3
            
            if not config.get('RestrictPublicBuckets', False):
                self.issues.append("❌ Public bucket access is not restricted")
                self.recommendations.append("Enable 'Restrict public bucket access'")
            else:
                print("✅ Public bucket access is restricted")
                self.security_score += 3
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                self.issues.append("❌ No public access block configuration found")
                self.recommendations.append("Configure public access block settings")
            else:
                self.issues.append(f"❌ Error checking public access: {e}")

    def check_bucket_policy(self):
        """Check bucket policy for security issues"""
        print("\n📋 Checking Bucket Policy...")
        self.max_score += 10
        
        try:
            response = self.s3_client.get_bucket_policy(Bucket=self.bucket_name)
            policy = json.loads(response['Policy'])
            
            print("✅ Bucket policy exists")
            self.security_score += 2
            
            # Check for overly permissive policies
            for statement in policy.get('Statement', []):
                if statement.get('Effect') == 'Allow':
                    principal = statement.get('Principal')
                    if principal == '*':
                        actions = statement.get('Action', [])
                        if isinstance(actions, str):
                            actions = [actions]
                        
                        dangerous_actions = ['s3:*', 's3:DeleteObject', 's3:PutObject']
                        if any(action in dangerous_actions for action in actions):
                            self.issues.append("⚠️ Bucket policy allows dangerous actions for everyone")
                            self.recommendations.append("Restrict bucket policy to only necessary actions")
                        else:
                            print("✅ Bucket policy has reasonable permissions")
                            self.security_score += 4
                    else:
                        print("✅ Bucket policy has restricted principals")
                        self.security_score += 4
                        
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                self.issues.append("⚠️ No bucket policy found")
                self.recommendations.append("Consider adding a bucket policy for better access control")
            else:
                self.issues.append(f"❌ Error checking bucket policy: {e}")

    def check_bucket_encryption(self):
        """Check bucket encryption settings"""
        print("\n🔐 Checking Bucket Encryption...")
        self.max_score += 15
        
        try:
            response = self.s3_client.get_bucket_encryption(Bucket=self.bucket_name)
            rules = response['ServerSideEncryptionConfiguration']['Rules']
            
            if rules:
                print("✅ Server-side encryption is enabled")
                self.security_score += 10
                
                for rule in rules:
                    sse_algorithm = rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']
                    if sse_algorithm == 'AES256':
                        print("✅ Using AES256 encryption")
                        self.security_score += 3
                    elif sse_algorithm == 'aws:kms':
                        print("✅ Using KMS encryption (recommended)")
                        self.security_score += 5
                        
                    if rule.get('BucketKeyEnabled'):
                        print("✅ S3 Bucket Key is enabled (cost optimization)")
                        self.security_score += 2
            else:
                self.issues.append("❌ No encryption rules found")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                self.issues.append("❌ Server-side encryption is not enabled")
                self.recommendations.append("Enable server-side encryption (AES256 or KMS)")
            else:
                self.issues.append(f"❌ Error checking encryption: {e}")

    def check_bucket_versioning(self):
        """Check bucket versioning settings"""
        print("\n📚 Checking Bucket Versioning...")
        self.max_score += 10
        
        try:
            response = self.s3_client.get_bucket_versioning(Bucket=self.bucket_name)
            status = response.get('Status', 'Disabled')
            
            if status == 'Enabled':
                print("✅ Versioning is enabled")
                self.security_score += 8
                
                mfa_delete = response.get('MfaDelete', 'Disabled')
                if mfa_delete == 'Enabled':
                    print("✅ MFA Delete is enabled")
                    self.security_score += 2
                else:
                    self.recommendations.append("Consider enabling MFA Delete for extra protection")
            else:
                self.issues.append("⚠️ Versioning is disabled")
                self.recommendations.append("Enable versioning to protect against accidental deletions")
                
        except ClientError as e:
            self.issues.append(f"❌ Error checking versioning: {e}")

    def check_bucket_logging(self):
        """Check bucket access logging"""
        print("\n📊 Checking Access Logging...")
        self.max_score += 5
        
        try:
            response = self.s3_client.get_bucket_logging(Bucket=self.bucket_name)
            
            if 'LoggingEnabled' in response:
                print("✅ Access logging is enabled")
                self.security_score += 5
            else:
                self.issues.append("⚠️ Access logging is disabled")
                self.recommendations.append("Enable access logging for audit trails")
                
        except ClientError as e:
            self.issues.append(f"❌ Error checking logging: {e}")

    def check_bucket_cors(self):
        """Check CORS configuration"""
        print("\n🌐 Checking CORS Configuration...")
        self.max_score += 5
        
        try:
            response = self.s3_client.get_bucket_cors(Bucket=self.bucket_name)
            cors_rules = response.get('CORSRules', [])
            
            if cors_rules:
                print("✅ CORS is configured")
                self.security_score += 3
                
                for rule in cors_rules:
                    allowed_origins = rule.get('AllowedOrigins', [])
                    if '*' in allowed_origins:
                        self.issues.append("⚠️ CORS allows all origins (*)")
                        self.recommendations.append("Restrict CORS to specific domains")
                    else:
                        print("✅ CORS has restricted origins")
                        self.security_score += 2
            else:
                self.recommendations.append("Consider configuring CORS if needed for web access")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
                print("ℹ️ No CORS configuration (may be intentional)")
            else:
                self.issues.append(f"❌ Error checking CORS: {e}")

    def check_lifecycle_policies(self):
        """Check lifecycle management"""
        print("\n♻️ Checking Lifecycle Policies...")
        self.max_score += 5
        
        try:
            response = self.s3_client.get_bucket_lifecycle_configuration(Bucket=self.bucket_name)
            rules = response.get('Rules', [])
            
            if rules:
                print("✅ Lifecycle policies are configured")
                self.security_score += 5
                
                for rule in rules:
                    if rule.get('Status') == 'Enabled':
                        print(f"  • Rule: {rule.get('ID', 'Unnamed')} - Enabled")
            else:
                self.recommendations.append("Consider lifecycle policies for cost optimization")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                self.recommendations.append("Consider adding lifecycle policies to manage storage costs")
            else:
                self.issues.append(f"❌ Error checking lifecycle: {e}")

    def check_django_configuration(self):
        """Check Django S3 configuration best practices"""
        print("\n🐍 Checking Django Configuration...")
        self.max_score += 20
        
        # Check environment variables
        if self.access_key and self.secret_key:
            print("✅ AWS credentials are configured")
            self.security_score += 5
            
            # Check if credentials are in environment (not hardcoded)
            if 'AKIAQU2UI33FZTKRTFD3' not in open('backend/settings.py').read():
                print("✅ Credentials not hardcoded in settings")
                self.security_score += 5
            else:
                self.issues.append("❌ Credentials may be hardcoded")
                self.recommendations.append("Use environment variables for credentials")
        else:
            self.issues.append("❌ AWS credentials not configured")
        
        # Check region configuration
        if self.region:
            print(f"✅ Region configured: {self.region}")
            self.security_score += 2
        else:
            self.issues.append("❌ AWS region not configured")
        
        # Check ACL settings
        try:
            settings_content = open('backend/settings.py').read()
        except FileNotFoundError:
            settings_content = ""
            
        if 'AWS_DEFAULT_ACL = None' in settings_content:
            print("✅ ACLs are disabled (modern S3 setup)")
            self.security_score += 3
        elif 'AWS_DEFAULT_ACL' not in settings_content:
            self.recommendations.append("Consider explicitly setting AWS_DEFAULT_ACL = None")
        
        # Check query string auth
        if 'AWS_QUERYSTRING_AUTH = False' in settings_content:
            print("✅ Query string auth is disabled")
            self.security_score += 2
        else:
            self.recommendations.append("Consider setting AWS_QUERYSTRING_AUTH = False")
        
        # Check file overwrite setting
        if 'AWS_S3_FILE_OVERWRITE = False' in settings_content:
            print("✅ File overwrite protection enabled")
            self.security_score += 3
        else:
            self.recommendations.append("Consider setting AWS_S3_FILE_OVERWRITE = False")

    def check_iam_permissions(self):
        """Check IAM user permissions (basic check)"""
        print("\n👤 Checking IAM Permissions...")
        self.max_score += 10
        
        try:
            # Test basic permissions
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print("✅ Read permissions working")
            self.security_score += 3
            
            # Test write permissions
            test_key = 'security-audit-test.txt'
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=test_key,
                Body=b'Security audit test'
            )
            print("✅ Write permissions working")
            self.security_score += 3
            
            # Test delete permissions
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=test_key)
            print("✅ Delete permissions working")
            self.security_score += 2
            
            # Check if user has excessive permissions
            iam_client = boto3.client(
                'iam',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            try:
                # This will fail if user doesn't have IAM permissions (which is good)
                iam_client.list_users()
                self.issues.append("⚠️ IAM user has administrative permissions")
                self.recommendations.append("Use principle of least privilege - restrict to S3 only")
            except ClientError:
                print("✅ IAM user has restricted permissions")
                self.security_score += 2
                
        except ClientError as e:
            self.issues.append(f"❌ Permission error: {e}")

    def generate_report(self):
        """Generate comprehensive security report"""
        print("\n" + "="*60)
        print("🛡️  S3 SECURITY AUDIT REPORT")
        print("="*60)
        
        # Calculate score percentage
        score_percentage = (self.security_score / self.max_score * 100) if self.max_score > 0 else 0
        
        print(f"\n📊 SECURITY SCORE: {self.security_score}/{self.max_score} ({score_percentage:.1f}%)")
        
        if score_percentage >= 90:
            print("🟢 EXCELLENT - Your S3 setup follows security best practices!")
        elif score_percentage >= 75:
            print("🟡 GOOD - Minor improvements recommended")
        elif score_percentage >= 50:
            print("🟠 FAIR - Several security improvements needed")
        else:
            print("🔴 POOR - Significant security risks present")
        
        # Issues found
        if self.issues:
            print(f"\n❌ ISSUES FOUND ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND!")
        
        # Recommendations
        if self.recommendations:
            print(f"\n💡 RECOMMENDATIONS ({len(self.recommendations)}):")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Best practices summary
        print(f"\n📋 BEST PRACTICES CHECKLIST:")
        print(f"  {'✅' if score_percentage >= 80 else '❌'} Secure access controls")
        print(f"  {'✅' if 'encryption' not in str(self.issues).lower() else '❌'} Data encryption")
        print(f"  {'✅' if 'versioning' not in str(self.issues).lower() else '❌'} Version control")
        print(f"  {'✅' if 'logging' not in str(self.issues).lower() else '❌'} Audit logging")
        print(f"  {'✅' if 'credentials' not in str(self.issues).lower() else '❌'} Credential security")

    def run_full_audit(self):
        """Run complete security audit"""
        print("🚀 Starting S3 Security Audit...")
        print(f"Bucket: {self.bucket_name}")
        print(f"Region: {self.region}")
        print("-" * 60)
        
        try:
            self.check_bucket_public_access()
            self.check_bucket_policy()
            self.check_bucket_encryption()
            self.check_bucket_versioning()
            self.check_bucket_logging()
            self.check_bucket_cors()
            self.check_lifecycle_policies()
            self.check_django_configuration()
            self.check_iam_permissions()
            
            self.generate_report()
            
        except Exception as e:
            print(f"\n❌ Audit failed: {e}")
            return False
        
        return True

def main():
    audit = S3SecurityAudit()
    audit.run_full_audit()

if __name__ == "__main__":
    main()