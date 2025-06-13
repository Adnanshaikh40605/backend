#!/usr/bin/env python
"""
Script to help migrate from SQLite to PostgreSQL.
This script will:
1. Check if DATABASE_URL is set
2. Run migrations
3. Create a superuser if needed
"""

import os
import sys
import subprocess
import django
from django.core.management import call_command

def setup_django():
    """Set up Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

def check_database_url():
    """Check if DATABASE_URL is set."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL is not set!")
        print("Please set the DATABASE_URL environment variable.")
        return False
    
    if database_url.startswith('sqlite'):
        print("⚠️ DATABASE_URL is set to SQLite. This script is for migrating to PostgreSQL.")
        return False
    
    print(f"✅ DATABASE_URL is set to: {database_url}")
    return True

def run_migrations():
    """Run migrations."""
    print("\n🔄 Running migrations...")
    try:
        call_command('migrate')
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def create_superuser():
    """Create a superuser if needed."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if User.objects.filter(is_superuser=True).exists():
        print("\n✅ Superuser already exists.")
        return True
    
    print("\n🔑 Creating superuser...")
    try:
        call_command('createsuperuser', interactive=True)
        print("✅ Superuser created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False

def delete_sqlite_db():
    """Delete SQLite database if it exists."""
    sqlite_db = 'db.sqlite3'
    if os.path.exists(sqlite_db):
        print(f"\n🗑️ Deleting {sqlite_db}...")
        try:
            os.remove(sqlite_db)
            print(f"✅ {sqlite_db} deleted successfully!")
            return True
        except Exception as e:
            print(f"❌ Error deleting {sqlite_db}: {e}")
            return False
    else:
        print(f"\n✅ {sqlite_db} does not exist.")
        return True

def main():
    """Main function."""
    print("=== PostgreSQL Migration Helper ===\n")
    
    # Check if DATABASE_URL is set
    if not check_database_url():
        return
    
    # Set up Django
    setup_django()
    
    # Run migrations
    if not run_migrations():
        return
    
    # Delete SQLite database if it exists
    delete_sqlite_db()
    
    # Create superuser if needed
    create_superuser()
    
    print("\n✅ Migration to PostgreSQL completed successfully!")

if __name__ == "__main__":
    main() 