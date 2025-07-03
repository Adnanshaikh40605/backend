import os
import dj_database_url

def get_database_config():
    """
    Configure database using dj_database_url.
    Uses DATABASE_URL environment variable to connect to PostgreSQL.
    """
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:tjivRKybjCRWGgWiVAxNpASgEmhzASyi@localhost:5432/railway')
    
    # Use dj_database_url to parse the DATABASE_URL environment variable
    return dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        ssl_require=not os.environ.get('DEBUG', 'False').lower() == 'true'  # SSL in production only
    ) 