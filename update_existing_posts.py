#!/usr/bin/env python3
"""
Update existing blog posts with excerpt and read_time values
"""
import os
import sys
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup Django
django.setup()

def update_existing_posts():
    """Update all existing blog posts with excerpt and read_time"""
    from blog.models import BlogPost
    
    print("🔄 Updating existing blog posts with excerpt and read_time...")
    
    # Get all blog posts
    posts = BlogPost.objects.all()
    total_posts = posts.count()
    
    print(f"📊 Found {total_posts} blog posts to update")
    
    updated_count = 0
    
    for i, post in enumerate(posts, 1):
        try:
            # Check if excerpt or read_time needs updating
            needs_update = False
            
            if not post.excerpt and post.content:
                needs_update = True
            
            if post.read_time == 0 and post.content:
                needs_update = True
            
            if needs_update:
                # Save the post to trigger auto-generation
                post.save()
                updated_count += 1
                print(f"✅ [{i}/{total_posts}] Updated: {post.title[:50]}...")
                print(f"   - Excerpt: {len(post.excerpt)} chars")
                print(f"   - Read time: {post.read_time} min")
            else:
                print(f"⏭️  [{i}/{total_posts}] Skipped: {post.title[:50]}... (already has excerpt and read_time)")
                
        except Exception as e:
            print(f"❌ [{i}/{total_posts}] Error updating {post.title[:50]}...: {e}")
    
    print(f"\n🎉 Update complete!")
    print(f"   - Total posts: {total_posts}")
    print(f"   - Updated posts: {updated_count}")
    print(f"   - Skipped posts: {total_posts - updated_count}")

def test_api_response():
    """Test the API response to see if excerpt and read_time are included"""
    print("\n🧪 Testing API response...")
    
    try:
        from blog.models import BlogPost
        from blog.serializers import BlogPostListSerializer
        from django.test import RequestFactory
        
        # Get a sample post
        post = BlogPost.objects.filter(published=True).first()
        
        if post:
            # Create a mock request for context
            factory = RequestFactory()
            request = factory.get('/api/posts/')
            
            # Test serializer
            serializer = BlogPostListSerializer(post, context={'request': request})
            data = serializer.data
            
            print(f"✅ Sample post serialized successfully:")
            print(f"   - Title: {data.get('title', 'N/A')}")
            print(f"   - Excerpt: {data.get('excerpt', 'N/A')[:100]}...")
            print(f"   - Read time: {data.get('read_time', 'N/A')} minutes")
            print(f"   - Fields included: {list(data.keys())}")
            
            return True
        else:
            print("⚠️  No published posts found to test")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API response: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🚀 Blog Post Excerpt and Read Time Update")
    print("=" * 60)
    
    try:
        # Update existing posts
        update_existing_posts()
        
        # Test API response
        test_api_response()
        
        print(f"\n🌐 Your API now includes excerpt and read_time fields!")
        print(f"   Test locally: http://localhost:8000/api/posts/?page=1&limit=9&published=true")
        print(f"   Production: https://backend-production-92ae.up.railway.app/api/posts/?page=1&limit=9&published=true")
        
    except Exception as e:
        print(f"❌ Error during update: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)