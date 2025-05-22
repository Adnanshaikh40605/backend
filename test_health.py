#!/usr/bin/env python
"""
Test script to verify health check endpoints are working properly.
Run this script after starting the Django server to test health checks.
"""
import requests
import sys
import time

# Base URL - change this to match your server
BASE_URL = "http://localhost:8000"

# Endpoints to test
ENDPOINTS = [
    "/ping/",
    "/health/",
    "/railway-health/",
    "/debug-request/",
    "/?health=check"  # Test the welcome page with health check parameter
]

def test_endpoint(url):
    """Test a single endpoint and return the result"""
    try:
        print(f"Testing {url}...")
        headers = {
            "User-Agent": "Railway Health Check Test Script"
        }
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")  # Print first 200 chars
        print("-" * 80)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        print("-" * 80)
        return False

def main():
    """Main function to test all endpoints"""
    print("Testing health check endpoints...")
    success = True
    
    for endpoint in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        if not test_endpoint(url):
            success = False
    
    if success:
        print("All health check endpoints passed!")
        return 0
    else:
        print("Some health check endpoints failed!")
        return 1

if __name__ == "__main__":
    # Add a small delay to make sure server has started
    time.sleep(1)
    sys.exit(main()) 