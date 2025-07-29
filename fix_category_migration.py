#!/usr/bin/env python3
"""
Fix the missing category_id column in blog_blogpost table
"""
import os
import sys
import django
from django.db import connection, transaction
from django.core.management import execute_from_command_line

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup Django
django.setup()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        """, [table_name, column_name])
        return cursor.fetchone() is not None

def check_table_exists(table_name):
    """Check if a table exists"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = %s
        """, [table_name])
        return cursor.fetchone() is not None

def get_table_columns(table_name):
    """Get all columns in a table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, [table_name])
        return cursor.fetchall()

def fix_migration_issue():
    """Fix the category migration issue"""
    print("🔍 Checking database schema...")
    
    # Check if blog_category table exists
    if not check_table_exists('blog_category'):
        print("❌ blog_category table does not exist!")
        print("🔧 Creating blog_category table...")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE blog_category (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    slug VARCHAR(120) UNIQUE NOT NULL DEFAULT '',
                    description TEXT,
                    color VARCHAR(7) NOT NULL DEFAULT '#007bff',
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """)
        print("✅ blog_category table created!")
    else:
        print("✅ blog_category table exists")
    
    # Check if blog_blogpost has category_id column
    if not check_column_exists('blog_blogpost', 'category_id'):
        print("❌ blog_blogpost.category_id column does not exist!")
        print("🔧 Adding category_id column...")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE blog_blogpost 
                ADD COLUMN category_id BIGINT NULL 
                REFERENCES blog_category(id) ON DELETE SET NULL;
            """)
            
            # Create index for better performance
            cursor.execute("""
                CREATE INDEX blog_blogpost_category_id_idx 
                ON blog_blogpost(category_id);
            """)
        print("✅ category_id column added!")
    else:
        print("✅ blog_blogpost.category_id column exists")
    
    # Show current blog_blogpost schema
    print("\n📊 Current blog_blogpost columns:")
    columns = get_table_columns('blog_blogpost')
    for col_name, data_type, is_nullable in columns:
        nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
        print(f"   - {col_name}: {data_type} ({nullable})")
    
    print("\n🎉 Database schema fix complete!")

def test_category_functionality():
    """Test if category functionality works"""
    print("\n🧪 Testing category functionality...")
    
    try:
        from blog.models import Category, BlogPost
        
        # Test creating a category
        category, created = Category.objects.get_or_create(
            name="Test Category",
            defaults={
                'description': 'A test category',
                'color': '#ff0000'
            }
        )
        
        if created:
            print("✅ Created test category")
        else:
            print("✅ Test category already exists")
        
        # Test querying posts with categories
        posts_with_categories = BlogPost.objects.select_related('category').all()[:3]
        print(f"✅ Found {posts_with_categories.count()} posts (showing first 3):")
        
        for post in posts_with_categories:
            category_name = post.category.name if post.category else "No category"
            print(f"   - '{post.title}' -> Category: {category_name}")
        
        print("✅ Category functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Category functionality test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🚀 Category Migration Fix")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            fix_migration_issue()
        
        # Test the functionality
        test_category_functionality()
        
        print("\n🎉 All fixes applied successfully!")
        print("🚀 You can now restart your Django server!")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)