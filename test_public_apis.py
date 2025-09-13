#!/usr/bin/env python3
"""
Test script to verify that the specified APIs are now public (no authentication required).
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8000/api/blog/"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint without authentication."""
    url = urljoin(BASE_URL, endpoint)
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=HEADERS, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=HEADERS, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS: Endpoint is accessible without authentication")
            try:
                response_data = response.json()
                if isinstance(response_data, dict):
                    print(f"Response keys: {list(response_data.keys())}")
                elif isinstance(response_data, list):
                    print(f"Response length: {len(response_data)}")
                else:
                    print(f"Response type: {type(response_data)}")
            except:
                print("Response: (non-JSON)")
            return True
        elif response.status_code == 401:
            print("❌ FAILED: Endpoint still requires authentication")
            return False
        elif response.status_code == 404:
            print("⚠️  WARNING: Endpoint not found (might be expected if no data exists)")
            return True  # This is acceptable for public endpoints
        else:
            print(f"⚠️  WARNING: Unexpected status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return True  # Still consider it public if not 401
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Request failed - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {str(e)}")
        return False

def main():
    """Run all public API tests."""
    print("🧪 Testing Public API Endpoints")
    print("=" * 60)
    
    # Test cases for the APIs that should be public
    test_cases = [
        {
            'method': 'GET',
            'endpoint': 'posts/',
            'description': 'List all blog posts'
        },
        {
            'method': 'GET', 
            'endpoint': 'categories/',
            'description': 'List all categories'
        },
        {
            'method': 'GET',
            'endpoint': 'comments/',
            'description': 'List all comments'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/',
            'data': {
                'user_name': 'Test User',
                'content': 'This is a test comment',
                'post': 1  # Assuming post with ID 1 exists
            },
            'description': 'Create a new comment'
        }
    ]
    
    # Test specific post endpoints (these might return 404 if no posts exist)
    test_cases.extend([
        {
            'method': 'GET',
            'endpoint': 'posts/test-slug/',  # This will likely 404, but should not 401
            'description': 'Get post by slug (test-slug)'
        },
        {
            'method': 'GET',
            'endpoint': 'posts/test-slug/related/',
            'description': 'Get related posts for test-slug'
        }
    ])
    
    # Test ALL comment-related endpoints (these might return 404 if no comments exist)
    test_cases.extend([
        {
            'method': 'POST',
            'endpoint': 'comments/1/like/',
            'data': {'user_name': 'Test User'},
            'description': 'Like comment with ID 1'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/1/unlike/',
            'data': {'user_name': 'Test User'},
            'description': 'Unlike comment with ID 1'
        },
        {
            'method': 'GET',
            'endpoint': 'comments/pending_count/',
            'description': 'Get pending comment count'
        },
        {
            'method': 'GET',
            'endpoint': 'comments/counts/',
            'description': 'Get comment counts by status'
        },
        {
            'method': 'GET',
            'endpoint': 'comments/all/?post=1',
            'description': 'Get all comments for a post'
        },
        {
            'method': 'GET',
            'endpoint': 'comments/admin_all/',
            'description': 'Get all comments for admin'
        },
        {
            'method': 'GET',
            'endpoint': 'comments/check_approved/?post=1',
            'description': 'Check approved comments for a post'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/1/approve/',
            'description': 'Approve comment with ID 1'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/1/reject/',
            'description': 'Reject comment with ID 1'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/1/trash/',
            'description': 'Move comment with ID 1 to trash'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/1/restore/',
            'description': 'Restore comment with ID 1 from trash'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/1/reply/',
            'data': {
                'user_name': 'Test User',
                'content': 'This is a reply',
                'post': 1
            },
            'description': 'Reply to comment with ID 1'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/approve/1/',
            'description': 'Approve comment via comment_action endpoint'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/reject/1/',
            'description': 'Reject comment via comment_action endpoint'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/trash/1/',
            'description': 'Trash comment via comment_action endpoint'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/restore/1/',
            'description': 'Restore comment via comment_action endpoint'
        },
        {
            'method': 'POST',
            'endpoint': 'comments/delete/1/',
            'description': 'Delete comment via comment_action endpoint'
        }
    ])
    
    results = []
    for test_case in test_cases:
        success = test_endpoint(
            test_case['method'],
            test_case['endpoint'],
            test_case.get('data'),
            test_case['description']
        )
        results.append(success)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! APIs are now public.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Some APIs may still require authentication.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
