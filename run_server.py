import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Run the Django development server with PostgreSQL database
    """
    # Check if DATABASE_URL is set
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Warning: DATABASE_URL is not set. Using SQLite database.")
        print("Set DATABASE_URL in your .env file to use PostgreSQL.")
    else:
        print(f"Using PostgreSQL database: {database_url.split('@')[1]}")
    
    # Run the Django development server
    command = ["python", "manage.py", "runserver"]
    
    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 