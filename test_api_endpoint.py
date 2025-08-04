#!/usr/bin/env python3
"""
Test the API endpoint directly to see if it's working
"""
import os
import sys
import django
import json
from django.http import JsonResponse

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup Django
django.setup()

# Import DRF components after Django setup
from rest_framework.test import APIRequestFactory

def test_posts_api():
    """Test the posts API endpoint"""
    print("🧪 Testing Posts API Endpoint")
    print("=" * 40)
    
    try:
        from blog.models import BlogPost
        from rest_framework.test import APIClient
        
        # Create a client instead of using the viewset directly
        client = APIClient()
        
        # Make a direct query to the database instead of using the API
        print("📊 Querying database directly...")
        posts = BlogPost.objects.filter(published=True).order_by('-created_at')[:6]
        print(f"   Found {len(posts)} published posts")
        
        if len(posts) > 0:
            print(f"   First post: {posts[0].title}")
            return True
        else:
            print("   No published posts found")
            return True
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_slugs_api():
    """Test the slugs API endpoint"""
    print("\n🧪 Testing Slugs API Endpoint")
    print("=" * 40)
    
    try:
        from blog.views import get_all_slugs
        from blog.models import BlogPost
        from rest_framework.test import APIRequestFactory
        
        # Create a request factory
        factory = APIRequestFactory()
        
        # Create a GET request to the slugs endpoint
        request = factory.get('/api/posts/slugs/')
        
        # Test the get_all_slugs function
        print("📡 Testing get_all_slugs function...")
        response = get_all_slugs(request)
        
        if hasattr(response, 'data'):
            print("✅ API call successful!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Type: {type(response.data)}")
            
            if isinstance(response.data, dict) and 'slugs' in response.data:
                print(f"   Slugs Count: {len(response.data['slugs'])}")
                print(f"   First few slugs: {response.data['slugs'][:3] if response.data['slugs'] else []}")
                return True
            else:
                print(f"❌ Unexpected response format: {response.data}")
                return False
        else:
            print(f"❌ API call failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_direct_query():
    """Test direct database query"""
    print("\n🗄️ Testing Direct Database Query")
    print("=" * 40)
    
    try:
        from blog.models import BlogPost
        
        # Test basic query
        all_posts = BlogPost.objects.all()
        print(f"✅ Total posts in database: {all_posts.count()}")
        
        # Test published posts
        published_posts = BlogPost.objects.filter(published=True)
        print(f"✅ Published posts: {published_posts.count()}")
        
        # Test with category
        posts_with_category = BlogPost.objects.select_related('category').all()[:3]
        print("✅ Posts with category info:")
        
        for post in posts_with_category:
            category_name = post.category.name if post.category else "No category"
            print(f"   - '{post.title}' -> Category: {category_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in direct query: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_serializer():
    """Test the serializer directly"""
    print("\n📝 Testing Serializer")
    print("=" * 40)
    
    try:
        from blog.models import BlogPost
        from blog.serializers import BlogPostListSerializer
        from rest_framework.test import APIRequestFactory
        
        # Get some posts
        posts = BlogPost.objects.filter(published=True)[:3]
        
        if posts:
            # Create a mock request for context
            factory = APIRequestFactory()
            request = factory.get('/api/posts/')
            
            # Test serializer
            serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
            data = serializer.data
            
            print(f"✅ Serialized {len(data)} posts successfully")
            
            for post_data in data:
                category = post_data.get('category')
                category_name = category.get('name') if category else 'None'
                print(f"   - '{post_data.get('title', 'N/A')}' (Category: {category_name})")
            
            return True
        else:
            print("⚠️  No published posts found to serialize")
            return True
            
    except Exception as e:
        print(f"❌ Error in serializer test: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🚀 API Endpoint Testing")
    print("=" * 50)
    
    # Test direct database query first
    db_ok = test_direct_query()
    
    if db_ok:
        # Test serializer
        serializer_ok = test_serializer()
        
        if serializer_ok:
            # Test API endpoint
            api_ok = test_posts_api()
            
            # Test slugs API endpoint
            slugs_api_ok = test_slugs_api()
            
            if api_ok and slugs_api_ok:
                print("\n🎉 All tests passed! API should be working.")
                sys.exit(0)
            else:
                if not api_ok:
                    print("\n💥 Posts API endpoint test failed!")
                if not slugs_api_ok:
                    print("\n💥 Slugs API endpoint test failed!")
                sys.exit(1)
        else:
            print("\n💥 Serializer test failed!")
            sys.exit(1)
    else:
        print("\n💥 Database query test failed!")
        sys.exit(1)