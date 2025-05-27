"""
Simple script to test API endpoints and report any issues
"""

import requests
import json
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

# Base URL for the API
BASE_URL = "http://localhost:8000"

# List of endpoints to test
ENDPOINTS = [
    # Posts endpoints
    "/api/posts/",
    "/api/posts/featured/",
    "/api/posts/latest/",
    
    # Comments endpoints
    "/api/comments/",
    "/api/comments/counts/",
    "/api/comments/pending-count/",
    
    # Categories endpoints
    "/api/categories/",
    "/api/categories/all/",
    
    # Test endpoints
    "/api/public-test/",
    "/api/test/"
]

def test_endpoint(url):
    """Test an API endpoint and return the result"""
    full_url = f"{BASE_URL}{url}"
    try:
        print(f"Testing {full_url}...")
        response = requests.get(full_url, timeout=5)
        
        # Check if successful
        if response.status_code >= 200 and response.status_code < 300:
            print(f"{Fore.GREEN}✓ {url} - Status: {response.status_code}{Style.RESET_ALL}")
            try:
                json_data = response.json()
                print(f"  Response excerpt: {str(json_data)[:100]}...")
            except:
                print(f"  Response length: {len(response.text)} characters")
            return True
        else:
            print(f"{Fore.RED}✗ {url} - Status: {response.status_code}{Style.RESET_ALL}")
            print(f"  Response: {response.text[:100]}...")
            return False
    except requests.RequestException as e:
        print(f"{Fore.RED}✗ {url} - Error: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """Main function to test all endpoints"""
    print(f"{Fore.CYAN}Testing API endpoints at {BASE_URL}{Style.RESET_ALL}")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    for endpoint in ENDPOINTS:
        if test_endpoint(endpoint):
            successful += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"Results: {Fore.GREEN}{successful} successful{Style.RESET_ALL}, {Fore.RED}{failed} failed{Style.RESET_ALL}")
    
    if failed == 0:
        print(f"{Fore.GREEN}All endpoints are working correctly!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Some endpoints need fixing. See errors above.{Style.RESET_ALL}")
    
if __name__ == "__main__":
    main() 