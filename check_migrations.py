#!/usr/bin/env python3
"""
Check if database migrations are needed and optionally apply them
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup Django
django.setup()

def check_migrations():
    """Check if there are unapplied migrations"""
    print("🔍 Checking for unapplied migrations...")
    
    try:
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print(f"⚠️  Found {len(plan)} unapplied migrations:")
            for migration, backwards in plan:
                print(f"   - {migration.app_label}.{migration.name}")
            return True
        else:
            print("✅ All migrations are up to date!")
            return False
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
        return None

def apply_migrations():
    """Apply pending migrations"""
    print("🔧 Applying migrations...")
    
    try:
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✅ Migrations applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        return False

def create_superuser():
    """Create a superuser if none exists"""
    print("👤 Checking for superuser...")
    
    try:
        from django.contrib.auth.models import User
        
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superuser already exists")
            return True
        else:
            print("⚠️  No superuser found")
            print("   You may want to create one with: python manage.py createsuperuser")
            return False
            
    except Exception as e:
        print(f"❌ Error checking superuser: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Database Migration Check")
    print("=" * 40)
    
    # Check for pending migrations
    has_pending = check_migrations()
    print()
    
    if has_pending:
        response = input("Apply migrations now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            success = apply_migrations()
            if not success:
                sys.exit(1)
        else:
            print("⚠️  Migrations not applied. Your database may be out of sync.")
    
    print()
    create_superuser()
    
    print("\n🎉 Migration check complete!")