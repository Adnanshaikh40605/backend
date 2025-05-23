#!/usr/bin/env python
"""
Test script to verify database connections both through internal and external URLs.
This can help diagnose connection issues with Railway PostgreSQL.
"""
import sys
import os
import socket
import psycopg2
import time

# External and internal connection strings (copy directly from your settings.py)
EXTERNAL_DB_URL = 'postgresql://postgres:DGQzwoKpJuWRfgLKzDGeuUDcfRnRkAzW@switchyard.proxy.rlwy.net:47148/railway'
INTERNAL_DB_URL = 'postgresql://postgres:DGQzwoKpJuWRfgLKzDGeuUDcfRnRkAzW@postgres.railway.internal:5432/railway'

def mask_password(url):
    """Mask the password in the connection string for safer logging."""
    import re
    return re.sub(r'(://[^:]+:)([^@]+)(@)', r'\1*****\3', url)

def is_on_railway():
    """Check if we're running on Railway's internal network."""
    try:
        # Try to resolve the Railway internal hostname
        socket.gethostbyname('postgres.railway.internal')
        return True
    except socket.gaierror:
        return False

def parse_db_url(url):
    """Parse a database URL into connection parameters."""
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', url)
    if match:
        user, password, host, port, dbname = match.groups()
        return {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
    return None

def test_connection(url, label):
    """Test a database connection and return success status."""
    print(f"\nTesting {label} connection: {mask_password(url)}")
    start_time = time.time()
    
    try:
        # Parse the connection parameters
        params = parse_db_url(url)
        if not params:
            print(f"  Error: Invalid connection string format")
            return False
        
        # Connect to the database
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        
        # Execute a test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Report success
        elapsed = time.time() - start_time
        print(f"  Success: Connected in {elapsed:.2f} seconds")
        print(f"  PostgreSQL version: {version}")
        return True
    
    except psycopg2.OperationalError as e:
        elapsed = time.time() - start_time
        print(f"  Error: Connection failed after {elapsed:.2f} seconds")
        print(f"  Error message: {str(e)}")
        return False
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  Error: Unexpected error after {elapsed:.2f} seconds")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")
        return False

def main():
    """Main function to test database connections."""
    on_railway = is_on_railway()
    print(f"Running on Railway: {'Yes' if on_railway else 'No'}")
    
    # Always test the external connection
    external_success = test_connection(EXTERNAL_DB_URL, "External")
    
    # Only test internal if we're on Railway
    internal_success = False
    if on_railway:
        internal_success = test_connection(INTERNAL_DB_URL, "Internal")
    else:
        print("\nSkipping internal connection test (not running on Railway)")
    
    # Summary
    print("\nConnection Test Summary:")
    print(f"  External connection: {'SUCCESS' if external_success else 'FAILED'}")
    if on_railway:
        print(f"  Internal connection: {'SUCCESS' if internal_success else 'FAILED'}")
    
    # Return success only if all tested connections worked
    return 0 if external_success and (not on_railway or internal_success) else 1

if __name__ == "__main__":
    sys.exit(main()) 