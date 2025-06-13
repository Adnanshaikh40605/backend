import os
import dj_database_url

def get_database_config():
    """
    Configure database using dj_database_url.
    Uses DATABASE_URL environment variable to connect to PostgreSQL.
    Falls back to SQLite if DATABASE_URL is not set.
    """
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Use dj_database_url to parse the DATABASE_URL environment variable
        return dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            ssl_require=not os.environ.get('DEBUG', 'False').lower() == 'true'  # SSL in production only
        )
    
    # Default to SQLite if no DATABASE_URL is provided (for development only)
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3'),
    } 