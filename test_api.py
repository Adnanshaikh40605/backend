import requests
import json

def test_api_endpoints():
    """Test the API endpoints for blog posts"""
    base_url = "http://localhost:8000/api"
    
    # Test the regular endpoint (should work)
    print("Testing regular endpoint...")
    try:
        response = requests.get(f"{base_url}/posts/")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                print(f"Found {len(data['results'])} posts")
            else:
                print(f"Found {len(data)} posts")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test the new by-slug endpoint
    print("\nTesting by-slug endpoint...")
    try:
        # Use a sample slug - replace with an actual slug from your database
        slug = "top-10-healthy-road-trip-snacks-for-outstation-driving"
        response = requests.get(f"{base_url}/posts/by-slug/{slug}/")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Post title: {data.get('title')}")
            print(f"Post ID: {data.get('id')}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api_endpoints() 