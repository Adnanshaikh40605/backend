"""
Global pytest fixtures and configuration
"""
import pytest
from django.conf import settings

def pytest_configure():
    """
    Configure pytest settings.
    """
    # Make sure DEBUG is set to True during tests
    settings.DEBUG = True
    
    # Use in-memory SQLite for faster test runs if not specified otherwise
    if 'sqlite' not in settings.DATABASES['default']['ENGINE']:
        print("Using in-memory SQLite for tests")
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        } 