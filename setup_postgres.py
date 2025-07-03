import os
import subprocess
import sys

def setup_postgres():
    """
    Script to set up PostgreSQL database for development.
    """
    print("Setting up PostgreSQL database...")
    
    # Check if PostgreSQL is installed and accessible
    try:
        # Try to find psql in common installation paths on Windows
        if os.name == 'nt':
            possible_paths = [
                r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
                r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
                r"C:\Program Files\PostgreSQL\13\bin\psql.exe",
                r"C:\Program Files\PostgreSQL\12\bin\psql.exe",
                r"C:\Program Files\PostgreSQL\11\bin\psql.exe",
            ]
            
            psql_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    psql_path = path
                    break
            
            if psql_path:
                print(f"Found PostgreSQL at: {psql_path}")
                # Add PostgreSQL bin directory to PATH for this session
                os.environ['PATH'] += os.pathsep + os.path.dirname(psql_path)
            else:
                print("PostgreSQL not found in common installation paths.")
                print("Please install PostgreSQL from https://www.postgresql.org/download/windows/")
                print("After installation, make sure to add the PostgreSQL bin directory to your PATH.")
                sys.exit(1)
        else:
            # For Unix-like systems, try the command directly
            subprocess.run(["psql", "--version"], check=True, capture_output=True)
        
        print("PostgreSQL is installed and accessible.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("PostgreSQL is not installed or not in PATH.")
        print("Please install PostgreSQL:")
        print("- Windows: https://www.postgresql.org/download/windows/")
        print("- macOS: https://www.postgresql.org/download/macosx/")
        print("- Linux: Use your package manager (apt, yum, etc.)")
        print("\nAfter installation, make sure to add the PostgreSQL bin directory to your PATH.")
        sys.exit(1)
    
    # Database connection details
    db_name = "railway"
    db_user = "postgres"
    db_password = "tjivRKybjCRWGgWiVAxNpASgEmhzASyi"
    db_host = "localhost"
    db_port = "5432"
    
    print(f"Attempting to create database '{db_name}' if it doesn't exist...")
    print("You may be prompted for the PostgreSQL password.")
    
    try:
        # For Windows, use a different approach
        if os.name == 'nt':
            # Check if database exists
            check_cmd = f'psql -h {db_host} -p {db_port} -U {db_user} -c "SELECT 1 FROM pg_database WHERE datname = \'{db_name}\'"'
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            
            if "connection to server" in result.stderr.lower() or "could not connect" in result.stderr.lower():
                print("Error connecting to PostgreSQL server. Please check:")
                print("1. PostgreSQL service is running")
                print("2. Connection details are correct")
                print("3. PostgreSQL is configured to accept connections")
                sys.exit(1)
            
            # Create database if it doesn't exist
            if "1 row" not in result.stdout:
                create_cmd = f'psql -h {db_host} -p {db_port} -U {db_user} -c "CREATE DATABASE {db_name}"'
                create_result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
                
                if create_result.returncode == 0:
                    print(f"Database '{db_name}' created successfully.")
                else:
                    print(f"Error creating database: {create_result.stderr}")
                    sys.exit(1)
            else:
                print(f"Database '{db_name}' already exists.")
        else:
            # For Unix-like systems
            create_db_cmd = f'psql -h {db_host} -p {db_port} -U {db_user} -c "SELECT 1 FROM pg_database WHERE datname = \'{db_name}\'" | grep -q 1 || psql -h {db_host} -p {db_port} -U {db_user} -c "CREATE DATABASE {db_name}"'
            subprocess.run(create_db_cmd, shell=True, check=True)
            print(f"Database '{db_name}' setup completed.")
    except subprocess.SubprocessError as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)
    
    # Update .env file to use local PostgreSQL
    try:
        with open('.env', 'r') as f:
            env_content = f.readlines()
        
        updated = False
        for i, line in enumerate(env_content):
            if line.startswith('DATABASE_URL=') and 'switchyard.proxy.rlwy.net' in line:
                env_content[i] = f"# {line}"
                updated = True
            elif line.startswith('# DATABASE_URL=') and 'localhost' in line:
                env_content[i] = line[2:]  # Remove the comment
                updated = True
        
        if not updated:
            # If we didn't find the lines to update, add the local connection
            env_content.append(f"DATABASE_URL=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}\n")
        
        with open('.env', 'w') as f:
            f.writelines(env_content)
        
        print("Updated .env file to use local PostgreSQL database.")
    except Exception as e:
        print(f"Error updating .env file: {e}")
    
    print("\nPostgreSQL setup completed.")
    print("\nNext steps:")
    print("1. Run migrations: python manage.py migrate")
    print("2. Create a superuser: python manage.py createsuperuser")
    print("3. Run the server: python manage.py runserver")

if __name__ == "__main__":
    setup_postgres() 