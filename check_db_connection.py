import os
import sys
import django
from django.db import connections
from django.db.utils import OperationalError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def check_connection():
    """
    Check if the database connection is working.
    """
    try:
        # Try to get a cursor from the database
        connection = connections['default']
        connection.cursor()
        
        # Get database info
        db_name = connection.settings_dict['NAME']
        db_engine = connection.settings_dict['ENGINE']
        db_host = connection.settings_dict.get('HOST', 'localhost')
        
        print(f"✅ Successfully connected to database!")
        print(f"   - Database: {db_name}")
        print(f"   - Engine: {db_engine}")
        print(f"   - Host: {db_host}")
        
        # Try to execute a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                print("✅ Database query executed successfully")
            else:
                print("❌ Database query returned unexpected result")
        
        return True
    except OperationalError as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\nPossible solutions:")
        print("1. Make sure PostgreSQL is installed and running")
        print("2. Check your DATABASE_URL in the .env file")
        print("3. Run 'python setup_postgres.py' to set up the database")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

if __name__ == "__main__":
    print("Checking database connection...")
    success = check_connection()
    sys.exit(0 if success else 1) 