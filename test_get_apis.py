#!/usr/bin/env python3
"""
Test script for GET API endpoints
"""

import os
import sys
import django
import requests
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from blog.models import BlogPost, Comment, Category

def get_auth_token():
    """Get a valid JWT token for testing"""
    try:
        # Get first user or create one for testing
        user = User.objects.first()
        if not user:
            print("❌ No users found. Please create a user first.")
            return None
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"✅ Generated token for user: {user.username}")
        return access_token
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        return None

def test_get_api(endpoint, token, description):
    """Test a GET API endpoint"""
    print(f"\n🔍 Testing: {description}")
    print(f"📡 Endpoint: {endpoint}")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response:")
            print(json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data, indent=2)) > 500 else json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Failed! Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the Django server running?")
        print("💡 Start the server with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_comment_apis():
    """Test comment-related GET APIs"""
    print("🧪 Testing Comment GET APIs")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return False
    
    base_url = "http://localhost:8000"
    
    # Test comment endpoints
    endpoints = [
        (f"{base_url}/api/comments/", "Get all comments"),
        (f"{base_url}/api/comments/counts/", "Get comment counts"),
    ]
    
    success_count = 0
    for endpoint, description in endpoints:
        if test_get_api(endpoint, token, description):
            success_count += 1
    
    return success_count == len(endpoints)

def test_post_apis():
    """Test post-related GET APIs"""
    print("\n🧪 Testing Post GET APIs")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return False
    
    base_url = "http://localhost:8000"
    
    # Get a sample post slug for testing
    post = BlogPost.objects.filter(published=True).first()
    if not post:
        print("❌ No published posts found for testing")
        return False
    
    # Test post endpoints
    endpoints = [
        (f"{base_url}/api/posts/", "Get all posts"),
        (f"{base_url}/api/posts/by-slug/{post.slug}/", f"Get post by slug: {post.slug}"),
        (f"{base_url}/api/posts/{post.slug}/related/", f"Get related posts for: {post.slug}"),
        (f"{base_url}/api/all-slugs/", "Get all post slugs"),
    ]
    
    success_count = 0
    for endpoint, description in endpoints:
        if test_get_api(endpoint, token, description):
            success_count += 1
    
    return success_count == len(endpoints)

def test_dashboard_apis():
    """Test dashboard GET APIs"""
    print("\n🧪 Testing Dashboard GET APIs")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return False
    
    base_url = "http://localhost:8000"
    
    # Test dashboard endpoints
    endpoints = [
        (f"{base_url}/api/dashboard/stats/", "Get dashboard statistics"),
        (f"{base_url}/api/profile/", "Get user profile"),
    ]
    
    success_count = 0
    for endpoint, description in endpoints:
        if test_get_api(endpoint, token, description):
            success_count += 1
    
    return success_count == len(endpoints)

def test_category_apis():
    """Test category GET APIs"""
    print("\n🧪 Testing Category GET APIs")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return False
    
    base_url = "http://localhost:8000"
    
    # Test category endpoints
    endpoints = [
        (f"{base_url}/api/categories/", "Get all categories"),
    ]
    
    success_count = 0
    for endpoint, description in endpoints:
        if test_get_api(endpoint, token, description):
            success_count += 1
    
    return success_count == len(endpoints)

def test_public_endpoints():
    """Test public endpoints (no auth required)"""
    print("\n🧪 Testing Public Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test public endpoints
    endpoints = [
        (f"{base_url}/", "API root"),
        (f"{base_url}/health/", "Health check"),
    ]
    
    success_count = 0
    for endpoint, description in endpoints:
        try:
            response = requests.get(endpoint)
            print(f"\n🔍 Testing: {description}")
            print(f"📡 Endpoint: {endpoint}")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                success_count += 1
            else:
                print(f"❌ Failed! Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return success_count == len(endpoints)

if __name__ == "__main__":
    print("🧪 Testing All GET API Endpoints")
    print("=" * 60)
    
    # Test all API categories
    tests = [
        ("Public Endpoints", test_public_endpoints),
        ("Comment APIs", test_comment_apis),
        ("Post APIs", test_post_apis),
        ("Dashboard APIs", test_dashboard_apis),
        ("Category APIs", test_category_apis),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} test categories passed")
    
    if passed_tests == total_tests:
        print("🎉 All API tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
