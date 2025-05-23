#!/usr/bin/env python
"""
Deployment helper script for Blog CMS
This script helps prepare your project for deployment to Railway and Vercel
"""

import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

def generate_secret_key():
    """Generate a secure Django secret key"""
    return secrets.token_urlsafe(50)

def create_env_file():
    """Create a .env file for Railway deployment"""
    if os.path.exists('.env'):
        print("A .env file already exists. Backing it up to .env.bak")
        shutil.copy('.env', '.env.bak')
    
    secret_key = generate_secret_key()
    
    with open('.env', 'w') as f:
        f.write(f"# Django settings\n")
        f.write(f"DEBUG=False\n")
        f.write(f"SECRET_KEY={secret_key}\n")
        f.write(f"ALLOWED_HOSTS=.railway.app\n\n")
        f.write(f"# CORS settings\n")
        f.write(f"CORS_ALLOW_ALL_ORIGINS=False\n")
        f.write(f"# Update these with your actual frontend URL\n")
        f.write(f"CORS_ALLOWED_ORIGINS=https://your-frontend-app.vercel.app\n")
        f.write(f"FRONTEND_URL=https://your-frontend-app.vercel.app\n")
        f.write(f"CSRF_TRUSTED_ORIGINS=https://your-frontend-app.vercel.app\n")
    
    print("Created .env file with a secure SECRET_KEY")

def update_vercel_json():
    """Update the vercel.json file with prompts for backend URL"""
    backend_url = input("Enter your Railway backend URL (e.g., https://your-app.railway.app): ")
    if not backend_url:
        print("No URL provided. Using placeholder.")
        backend_url = "https://your-railway-app-url.railway.app"
    
    # Create frontend/.env file
    frontend_env_path = os.path.join('frontend', '.env')
    with open(frontend_env_path, 'w') as f:
        f.write(f"# Frontend environment variables for production\n\n")
        f.write(f"VITE_API_BASE_URL={backend_url}\n")
        f.write(f"VITE_MEDIA_URL={backend_url}/media/\n")
        f.write(f"VITE_USE_MOCK_API=false\n")
        f.write(f"VITE_DEBUG=false\n")
    
    print(f"Created frontend/.env with backend URL: {backend_url}")
    
    # Update vercel.json
    vercel_path = os.path.join('frontend', 'vercel.json')
    if os.path.exists(vercel_path):
        with open(vercel_path, 'r') as f:
            content = f.read()
        
        # Replace placeholder URL with actual backend URL
        content = content.replace('https://your-railway-app-url.railway.app', backend_url)
        
        with open(vercel_path, 'w') as f:
            f.write(content)
        
        print(f"Updated {vercel_path} with backend URL: {backend_url}")
    else:
        print(f"Warning: {vercel_path} not found")

def collect_static():
    """Run collectstatic command"""
    try:
        print("Running collectstatic...")
        subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)
        print("Static files collected successfully")
    except subprocess.CalledProcessError:
        print("Error collecting static files")

def main():
    """Main function"""
    print("Blog CMS Deployment Helper")
    print("=========================")
    
    # Create .env file
    create_env = input("Create .env file for Railway deployment? (y/n): ")
    if create_env.lower() == 'y':
        create_env_file()
    
    # Update vercel.json
    update_vercel = input("Update frontend configuration with backend URL? (y/n): ")
    if update_vercel.lower() == 'y':
        update_vercel_json()
    
    # Collect static files
    collect_static_files = input("Run collectstatic command? (y/n): ")
    if collect_static_files.lower() == 'y':
        collect_static()
    
    print("\nDeployment preparation complete!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Deploy backend on Railway following DEPLOYMENT_GUIDE.md")
    print("3. Deploy frontend on Vercel following DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main() 