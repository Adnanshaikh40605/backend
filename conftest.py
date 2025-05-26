"""
Global pytest fixtures and configuration
"""
import os
import pytest
from django.conf import settings

def pytest_configure():
    """
    Configure pytest settings.
    """
    # Make sure DEBUG is set to True during tests
    settings.DEBUG = True
    
    # Use in-memory SQLite for faster test runs if not using a custom database URL
    if not os.environ.get('DATABASE_URL'):
        print("Using in-memory SQLite for tests")
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    else:
        print(f"Using database from DATABASE_URL: {os.environ.get('DATABASE_URL')}")
        
    # Make sure we're using the test settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') 