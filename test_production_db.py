#!/usr/bin/env python3
"""
Test script to check if the production database connection is working
"""
import os
import sys
import django
from django.db import connections, connection
from django.db.utils import OperationalError
import traceback

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup Django
django.setup()

def test_database_connection():
    """Test the database connection and run basic queries"""
    print("🔍 Testing database connection...")
    
    try:
        # Test basic connection
        db_conn = connections['default']
        cursor = db_conn.cursor()
        
        print("✅ Database connection successful!")
        
        # Print connection details
        db_settings = connection.settings_dict
        print(f"📊 Database Info:")
        print(f"   - Engine: {db_settings['ENGINE']}")
        print(f"   - Name: {db_settings['NAME']}")
        print(f"   - Host: {db_settings.get('HOST', 'localhost')}")
        print(f"   - Port: {db_settings.get('PORT', 'default')}")
        print(f"   - User: {db_settings.get('USER', 'default')}")
        
        # Test a simple query
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        if result and result[0] == 1:
            print("✅ Basic query test passed")
        
        # Test if blog tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'blog_%'
            ORDER BY table_name;
        """)
        
        blog_tables = cursor.fetchall()
        if blog_tables:
            print(f"✅ Found {len(blog_tables)} blog tables:")
            for table in blog_tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️  No blog tables found - migrations may be needed")
        
        # Test if we can query blog posts
        try:
            cursor.execute("SELECT COUNT(*) FROM blog_blogpost;")
            post_count = cursor.fetchone()[0]
            print(f"✅ Found {post_count} blog posts in database")
            
            # Get a sample post if any exist
            if post_count > 0:
                cursor.execute("SELECT id, title, slug, published FROM blog_blogpost LIMIT 3;")
                posts = cursor.fetchall()
                print("📝 Sample posts:")
                for post in posts:
                    print(f"   - ID: {post[0]}, Title: '{post[1]}', Slug: '{post[2]}', Published: {post[3]}")
                    
        except Exception as e:
            print(f"⚠️  Could not query blog posts: {e}")
            print("   This might indicate missing migrations")
        
        return True
        
    except OperationalError as e:
        print(f"❌ Database connection failed!")
        print(f"   Error: {e}")
        print("\n🔧 Possible solutions:")
        print("   1. Check if DATABASE_URL is correct in Railway environment")
        print("   2. Ensure PostgreSQL service is running on Railway")
        print("   3. Check network connectivity")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_django_setup():
    """Test if Django is properly configured"""
    print("🔍 Testing Django configuration...")
    
    try:
        from django.conf import settings
        print(f"✅ Django settings loaded")
        print(f"   - DEBUG: {settings.DEBUG}")
        print(f"   - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   - DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
        
        # Test if apps are loaded
        from django.apps import apps
        blog_app = apps.get_app_config('blog')
        print(f"✅ Blog app loaded: {blog_app.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Production Database Connection Test")
    print("=" * 50)
    
    # Test Django setup
    django_ok = test_django_setup()
    print()
    
    if django_ok:
        # Test database connection
        db_ok = test_database_connection()
        
        if db_ok:
            print("\n🎉 All tests passed! Database is ready.")
            sys.exit(0)
        else:
            print("\n💥 Database connection failed!")
            sys.exit(1)
    else:
        print("\n💥 Django configuration failed!")
        sys.exit(1)