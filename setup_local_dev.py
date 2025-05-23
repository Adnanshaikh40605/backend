#!/usr/bin/env python
"""
Setup script for local development environment.
This script creates a .env.local file and sets up the SQLite database.
"""
import os
import shutil
import subprocess
import sys

def main():
    """Set up local development environment."""
    print("Setting up local development environment...")
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("WARNING: Virtual environment not detected. It's recommended to run this script within a virtual environment.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup aborted.")
            return
    
    # Create .env.local file if it doesn't exist
    if not os.path.exists('.env.local'):
        if os.path.exists('env.local.example'):
            shutil.copy('env.local.example', '.env.local')
            print("Created .env.local from env.local.example")
        else:
            print("Creating .env.local file...")
            with open('.env.local', 'w') as f:
                f.write("""# Local development environment variables
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
CORS_ALLOW_ALL_ORIGINS=True
FRONTEND_URL=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
SECRET_KEY=django-insecure-p4&t4m)l6oje8l8z9l2@lqy&#bwujg!81fc_pa8)+ec28dgrl3

# Comment out DATABASE_URL to use SQLite locally
# DATABASE_URL=postgres://postgres:password@localhost:5432/blogcms
""")
            print("Created .env.local file")
    else:
        print(".env.local file already exists")
    
    # Run migrations to set up SQLite database
    print("\nSetting up SQLite database...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("Database migrations applied successfully")
    except subprocess.CalledProcessError:
        print("Error applying migrations. Please check the output above for details.")
        return
    
    # Create superuser if needed
    response = input("\nDo you want to create a superuser? (y/n): ")
    if response.lower() == 'y':
        try:
            subprocess.run([sys.executable, 'manage.py', 'createsuperuser'])
        except subprocess.CalledProcessError:
            print("Error creating superuser. Please try again manually with 'python manage.py createsuperuser'")
    
    print("\nLocal development environment setup complete!")
    print("You can now run the development server with:")
    print("python manage.py runserver")

if __name__ == "__main__":
    main() 