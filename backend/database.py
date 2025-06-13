import os
import re
from urllib.parse import urlparse

def get_database_config():
    """
    Parse database URL from environment and return Django database configuration.
    Supports PostgreSQL, MySQL, and SQLite.
    """
    database_url = os.environ.get('DATABASE_URL')
    
    # Default to SQLite if no DATABASE_URL is provided
    if not database_url:
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3'),
        }
    
    # Parse the DATABASE_URL
    if database_url.startswith('sqlite:///'):
        # SQLite URL in the form sqlite:///path/to/db.sqlite3
        database_path = database_url.replace('sqlite:///', '')
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': database_path,
        }
    
    # For PostgreSQL, MySQL, etc.
    parsed_url = urlparse(database_url)
    
    # Extract components
    db_engine = parsed_url.scheme
    db_user = parsed_url.username or ''
    db_password = parsed_url.password or ''
    db_host = parsed_url.hostname or ''
    db_port = parsed_url.port or ''
    db_name = parsed_url.path[1:] if parsed_url.path else ''
    
    # Map the scheme to Django database engine
    engine_mapping = {
        'postgres': 'django.db.backends.postgresql',
        'postgresql': 'django.db.backends.postgresql',
        'mysql': 'django.db.backends.mysql',
        'oracle': 'django.db.backends.oracle',
    }
    
    engine = engine_mapping.get(db_engine, 'django.db.backends.sqlite3')
    
    # Build the database config
    config = {
        'ENGINE': engine,
        'NAME': db_name,
    }
    
    if db_user:
        config['USER'] = db_user
    if db_password:
        config['PASSWORD'] = db_password
    if db_host:
        config['HOST'] = db_host
    if db_port:
        config['PORT'] = str(db_port)
    
    return config 