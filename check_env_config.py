#!/usr/bin/env python
import os
import json
from pathlib import Path
from dotenv import load_dotenv

def check_backend_env():
    """Check backend environment configuration"""
    print("\n=== BACKEND ENVIRONMENT CONFIGURATION ===")
    
    # Load .env file
    load_dotenv()
    
    # Check database configuration
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url:
        # Mask password in the URL for security
        masked_url = database_url
        if '@' in database_url:
            parts = database_url.split('@')
            auth_part = parts[0].split(':')
            if len(auth_part) > 2:
                masked_url = f"{auth_part[0]}:****@{parts[1]}"
        print(f"Database URL: {masked_url}")
        print(f"Database Type: {'PostgreSQL' if 'postgresql' in database_url else 'SQLite'}")
    else:
        print("WARNING: DATABASE_URL not set, will use SQLite")
    
    # Check CORS settings
    cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
    cors_all_origins = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
    print(f"CORS Allow All Origins: {cors_all_origins}")
    if not cors_all_origins:
        print("CORS Allowed Origins:")
        for origin in cors_origins:
            if origin.strip():
                print(f"  - {origin.strip()}")
    
    # Check CSRF settings
    csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    print("CSRF Trusted Origins:")
    for origin in csrf_origins:
        if origin.strip():
            print(f"  - {origin.strip()}")
    
    # Check other important settings
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"Debug Mode: {debug}")
    
    allowed_hosts = os.environ.get('ALLOWED_HOSTS', '').split(',')
    print("Allowed Hosts:")
    for host in allowed_hosts:
        if host.strip():
            print(f"  - {host.strip()}")

def check_frontend_env():
    """Check frontend environment configuration"""
    print("\n=== FRONTEND ENVIRONMENT CONFIGURATION ===")
    
    # Check if frontend directory exists
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("ERROR: Frontend directory not found")
        return
    
    # Check .env file
    env_file = frontend_dir / '.env'
    if env_file.exists():
        print("Frontend .env file found")
        with open(env_file, 'r') as f:
            env_content = f.read()
            print("\nContent:")
            for line in env_content.splitlines():
                if line.strip() and not line.startswith('#'):
                    print(f"  {line}")
    else:
        print("WARNING: Frontend .env file not found")
    
    # Check vercel.json
    vercel_file = frontend_dir / 'vercel.json'
    if vercel_file.exists():
        print("\nVercel configuration found")
        try:
            with open(vercel_file, 'r') as f:
                vercel_config = json.load(f)
                if 'rewrites' in vercel_config:
                    print("API Rewrites:")
                    for rewrite in vercel_config['rewrites']:
                        if 'api' in rewrite.get('source', ''):
                            print(f"  {rewrite['source']} → {rewrite['destination']}")
        except json.JSONDecodeError:
            print("ERROR: Invalid vercel.json file")
    else:
        print("WARNING: vercel.json not found")
    
    # Check dohblog configuration
    dohblog_vercel = frontend_dir / 'vercel.dohblog.json'
    if dohblog_vercel.exists():
        print("\nDohblog Vercel configuration found")
        try:
            with open(dohblog_vercel, 'r') as f:
                dohblog_config = json.load(f)
                if 'rewrites' in dohblog_config:
                    print("API Rewrites:")
                    for rewrite in dohblog_config['rewrites']:
                        if 'api' in rewrite.get('source', ''):
                            print(f"  {rewrite['source']} → {rewrite['destination']}")
        except json.JSONDecodeError:
            print("ERROR: Invalid vercel.dohblog.json file")
    else:
        print("WARNING: vercel.dohblog.json not found")

def check_railway_variables():
    """Check Railway variables configuration"""
    print("\n=== RAILWAY VARIABLES CONFIGURATION ===")
    
    railway_file = Path('railway_variables.json')
    if railway_file.exists():
        try:
            with open(railway_file, 'r') as f:
                railway_config = json.load(f)
                
                # Check CORS settings
                cors_all_origins = railway_config.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
                print(f"CORS Allow All Origins: {cors_all_origins}")
                
                cors_origins = railway_config.get('CORS_ALLOWED_ORIGINS', '').split(',')
                print("CORS Allowed Origins:")
                for origin in cors_origins:
                    if origin.strip():
                        print(f"  - {origin.strip()}")
                
                # Check CSRF settings
                csrf_origins = railway_config.get('CSRF_TRUSTED_ORIGINS', '').split(',')
                print("CSRF Trusted Origins:")
                for origin in csrf_origins:
                    if origin.strip():
                        print(f"  - {origin.strip()}")
                
                # Check if dohblog.vercel.app is included
                dohblog_in_cors = any('dohblog.vercel.app' in origin for origin in cors_origins)
                dohblog_in_csrf = any('dohblog.vercel.app' in origin for origin in csrf_origins)
                
                if not dohblog_in_cors:
                    print("\nWARNING: dohblog.vercel.app not found in CORS_ALLOWED_ORIGINS")
                if not dohblog_in_csrf:
                    print("\nWARNING: dohblog.vercel.app not found in CSRF_TRUSTED_ORIGINS")
                
                if dohblog_in_cors and dohblog_in_csrf:
                    print("\nDohblog.vercel.app is properly configured in Railway variables")
        except json.JSONDecodeError:
            print("ERROR: Invalid railway_variables.json file")
    else:
        print("WARNING: railway_variables.json not found")

if __name__ == "__main__":
    print("Checking environment configurations...")
    check_backend_env()
    check_frontend_env()
    check_railway_variables()
    print("\nConfiguration check completed.") 