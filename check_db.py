import os
import django
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Now we can import Django models
from django.db import connection
from django.contrib.auth.models import User

def check_database_connection():
    """Check database connection and list tables"""
    try:
        # Get database engine being used
        db_engine = connection.settings_dict['ENGINE']
        print(f"Database engine: {db_engine}")
        
        # Get database name
        db_name = connection.settings_dict['NAME']
        print(f"Database name: {db_name}")
        
        # Get database host and port
        db_host = connection.settings_dict.get('HOST', 'localhost')
        db_port = connection.settings_dict.get('PORT', '')
        print(f"Database host: {db_host}")
        print(f"Database port: {db_port}")
        
        # List tables
        with connection.cursor() as cursor:
            if 'postgresql' in db_engine:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                print("\nDatabase tables:")
                for table in tables:
                    print(f"- {table[0]}")
        
        # Check for users
        users = User.objects.all()
        print(f"\nNumber of users: {users.count()}")
        for user in users:
            print(f"- {user.username} (superuser: {user.is_superuser})")
            
        print("\nDatabase connection successful!")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
        
if __name__ == "__main__":
    check_database_connection() 