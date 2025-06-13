import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Load environment variables from .env file and run the specified Django command
    """
    if len(sys.argv) < 2:
        print("Usage: python run_with_env.py [django_command]")
        sys.exit(1)
    
    # Get the Django command to run
    django_command = sys.argv[1:]
    command = ["python", "manage.py"] + django_command
    
    # Print environment variables for debugging
    print(f"Using DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    
    # Run the Django command
    result = subprocess.run(command)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main() 