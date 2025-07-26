import os
import dj_database_url
from pathlib import Path

def get_database_config():
    """
    Configure database using dj_database_url.
    Uses DATABASE_URL environment variable to connect to PostgreSQL.
    """
    # Always use PostgreSQL now that it's set up
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:adnan%4012@localhost:5432/blog_cms')
    
    # Use dj_database_url to parse the DATABASE_URL environment variable
    return dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        ssl_require=False  # No SSL for local development
    ) 