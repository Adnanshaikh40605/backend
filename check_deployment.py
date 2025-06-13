#!/usr/bin/env python
"""
Deployment readiness check script for Django application.
This script checks various aspects of the Django application to ensure it's ready for deployment.
"""

import os
import sys
import subprocess
import importlib.util
import json
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if a file exists."""
    exists = os.path.isfile(filepath)
    if exists:
        print(f"✅ {filepath} exists")
    else:
        if required:
            print(f"❌ {filepath} does not exist (REQUIRED)")
        else:
            print(f"⚠️ {filepath} does not exist (optional)")
    return exists

def check_directory_exists(dirpath, required=True):
    """Check if a directory exists."""
    exists = os.path.isdir(dirpath)
    if exists:
        print(f"✅ {dirpath} directory exists")
    else:
        if required:
            print(f"❌ {dirpath} directory does not exist (REQUIRED)")
        else:
            print(f"⚠️ {dirpath} directory does not exist (optional)")
    return exists

def check_env_vars():
    """Check if required environment variables are set."""
    required_vars = [
        'SECRET_KEY',
        'ALLOWED_HOSTS',
    ]
    
    optional_vars = [
        'DEBUG',
        'BACKEND_URL',
        'DATABASE_URL',
        'CORS_ALLOWED_ORIGINS',
        'CSRF_TRUSTED_ORIGINS',
    ]
    
    all_good = True
    
    print("\nChecking environment variables:")
    for var in required_vars:
        if os.environ.get(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set (REQUIRED)")
            all_good = False
    
    for var in optional_vars:
        if os.environ.get(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️ {var} is not set (optional)")
    
    return all_good

def check_deployment_files():
    """Check if deployment-related files exist."""
    print("\nChecking deployment files:")
    
    required_files = [
        'requirements.txt',
        'Procfile',
        'manage.py',
    ]
    
    optional_files = [
        'runtime.txt',
        'nixpacks.toml',
        'Dockerfile',
        '.dockerignore',
        'railway.toml',
    ]
    
    all_good = True
    
    for filepath in required_files:
        if not check_file_exists(filepath, required=True):
            all_good = False
    
    for filepath in optional_files:
        check_file_exists(filepath, required=False)
    
    return all_good

def check_django_settings():
    """Check Django settings for deployment readiness."""
    print("\nChecking Django settings:")
    
    try:
        # Try to import the settings module
        from backend import settings
        
        # Check DEBUG setting
        if settings.DEBUG:
            print("⚠️ DEBUG is set to True (should be False in production)")
        else:
            print("✅ DEBUG is set to False")
        
        # Check ALLOWED_HOSTS
        if settings.ALLOWED_HOSTS and '*' not in settings.ALLOWED_HOSTS:
            print(f"✅ ALLOWED_HOSTS is properly configured: {settings.ALLOWED_HOSTS}")
        else:
            print("⚠️ ALLOWED_HOSTS contains wildcard '*' (security risk in production)")
        
        # Check STATIC_ROOT
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            print(f"✅ STATIC_ROOT is set: {settings.STATIC_ROOT}")
        else:
            print("❌ STATIC_ROOT is not set (required for collectstatic)")
            return False
        
        # Check DATABASE settings
        if settings.DATABASES and 'default' in settings.DATABASES:
            db_engine = settings.DATABASES['default'].get('ENGINE', '')
            if 'sqlite3' in db_engine and not os.environ.get('DATABASE_URL'):
                print("⚠️ Using SQLite database (consider PostgreSQL for production)")
            else:
                print(f"✅ Database engine: {db_engine}")
        else:
            print("❌ Database settings are not properly configured")
            return False
        
        # Check STATICFILES_STORAGE
        if hasattr(settings, 'STATICFILES_STORAGE') and 'whitenoise' in settings.STATICFILES_STORAGE.lower():
            print(f"✅ Using WhiteNoise for static files: {settings.STATICFILES_STORAGE}")
        else:
            print("⚠️ Not using WhiteNoise for static files (recommended for production)")
        
        return True
    
    except ImportError as e:
        print(f"❌ Could not import Django settings: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking Django settings: {e}")
        return False

def check_database_connection():
    """Check database connection."""
    print("\nChecking database connection:")
    
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'check_db', '--retry'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("✅ Database connection successful")
            return True
        else:
            print(result.stderr)
            print("❌ Database connection failed")
            return False
    
    except Exception as e:
        print(f"❌ Error checking database connection: {e}")
        return False

def check_static_files():
    """Check if static files are collected."""
    print("\nChecking static files:")
    
    static_root = os.environ.get('STATIC_ROOT', 'staticfiles')
    
    if os.path.isdir(static_root):
        # Check if the directory has files
        files = os.listdir(static_root)
        if files:
            print(f"✅ Static files are collected ({len(files)} files/directories found)")
            return True
        else:
            print("⚠️ Static files directory exists but is empty")
    else:
        print("⚠️ Static files are not collected (run 'python manage.py collectstatic')")
    
    return False

def check_railway_variables():
    """Check if Railway variables are properly configured."""
    print("\nChecking Railway variables:")
    
    railway_vars_file = 'railway_variables.json'
    
    if os.path.isfile(railway_vars_file):
        try:
            with open(railway_vars_file, 'r') as f:
                variables = json.load(f)
            
            required_vars = [
                'SECRET_KEY',
                'ALLOWED_HOSTS',
                'DEBUG',
                'BACKEND_URL',
            ]
            
            all_good = True
            for var in required_vars:
                if var in variables:
                    print(f"✅ {var} is set in Railway variables")
                else:
                    print(f"❌ {var} is not set in Railway variables (REQUIRED)")
                    all_good = False
            
            return all_good
        
        except Exception as e:
            print(f"❌ Error reading Railway variables: {e}")
            return False
    else:
        print("⚠️ Railway variables file not found (optional but recommended)")
        return True

def main():
    """Main function to run all checks."""
    print("=== Django Deployment Readiness Check ===\n")
    
    # Run all checks
    deployment_files_ok = check_deployment_files()
    django_settings_ok = check_django_settings()
    env_vars_ok = check_env_vars()
    railway_vars_ok = check_railway_variables()
    db_connection_ok = check_database_connection()
    static_files_ok = check_static_files()
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Deployment files: {'✅' if deployment_files_ok else '❌'}")
    print(f"Django settings: {'✅' if django_settings_ok else '❌'}")
    print(f"Environment variables: {'✅' if env_vars_ok else '❌'}")
    print(f"Railway variables: {'✅' if railway_vars_ok else '❌'}")
    print(f"Database connection: {'✅' if db_connection_ok else '❌'}")
    print(f"Static files: {'✅' if static_files_ok else '⚠️'}")
    
    # Overall status
    critical_checks = [deployment_files_ok, django_settings_ok, env_vars_ok, db_connection_ok]
    if all(critical_checks):
        print("\n✅ Your Django application is ready for deployment!")
    else:
        print("\n❌ Your Django application is NOT ready for deployment. Please fix the issues above.")

if __name__ == "__main__":
    main() 