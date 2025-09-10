#!/usr/bin/env python
"""
Migration rollback utility for the blog application.
This script provides safe rollback strategies for database migrations.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


def get_migration_status():
    """Get current migration status for all apps."""
    from django.core.management import call_command
    from io import StringIO
    
    output = StringIO()
    call_command('showmigrations', stdout=output)
    return output.getvalue()


def rollback_to_migration(app_name, target_migration):
    """
    Rollback to a specific migration.
    
    Args:
        app_name (str): Name of the Django app
        target_migration (str): Target migration number (e.g., '0003')
    """
    try:
        print(f"Rolling back {app_name} to migration {target_migration}...")
        
        # Use Django's migrate command with fake flag for safety
        execute_from_command_line([
            'manage.py', 'migrate', app_name, target_migration, '--fake'
        ])
        
        print(f"Successfully rolled back {app_name} to {target_migration}")
        return True
        
    except Exception as e:
        print(f"Error rolling back {app_name}: {e}")
        return False


def rollback_comment_migrations():
    """Rollback comment-related migrations safely."""
    print("Rolling back comment nesting migrations...")
    
    # Rollback to before comment nesting was added
    success = rollback_to_migration('blog', '0002')
    
    if success:
        print("Comment nesting migrations rolled back successfully.")
        print("You can now reapply migrations with: python manage.py migrate")
    else:
        print("Failed to rollback comment migrations.")
        print("Manual intervention may be required.")


def create_migration_backup():
    """Create a backup of current migration state."""
    try:
        with connection.cursor() as cursor:
            # Get current migration state
            cursor.execute("""
                SELECT app, name FROM django_migrations 
                WHERE app = 'blog' 
                ORDER BY applied
            """)
            
            migrations = cursor.fetchall()
            
            # Create backup file
            with open('migration_backup.txt', 'w') as f:
                f.write("Migration Backup - " + str(datetime.now()) + "\n")
                f.write("=" * 50 + "\n")
                for app, name in migrations:
                    f.write(f"{app}: {name}\n")
            
            print("Migration backup created: migration_backup.txt")
            return True
            
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False


def reset_comment_nesting():
    """Reset comment nesting fields to default values."""
    try:
        with connection.cursor() as cursor:
            # Reset all comment nesting fields
            cursor.execute("""
                UPDATE blog_comment 
                SET level = 0, path = CAST(id AS TEXT), parent_id = NULL
            """)
            
            print("Comment nesting fields reset successfully.")
            return True
            
    except Exception as e:
        print(f"Error resetting comment nesting: {e}")
        return False


def main():
    """Main rollback function."""
    print("Blog Migration Rollback Utility")
    print("=" * 40)
    
    # Show current status
    print("\nCurrent migration status:")
    print(get_migration_status())
    
    # Create backup
    print("\nCreating migration backup...")
    create_migration_backup()
    
    # Ask user what they want to do
    print("\nRollback options:")
    print("1. Rollback comment nesting migrations")
    print("2. Reset comment nesting fields only")
    print("3. Show migration status only")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        rollback_comment_migrations()
    elif choice == '2':
        reset_comment_nesting()
    elif choice == '3':
        print(get_migration_status())
    elif choice == '4':
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...")


if __name__ == '__main__':
    from datetime import datetime
    main()
