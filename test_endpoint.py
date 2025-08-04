import requests
import json

url = 'http://localhost:8000/api/all-slugs/'
response = requests.get(url)

print(f'URL: {url}')
print(f'Status Code: {response.status_code}')
print(f'Response Headers: {json.dumps(dict(response.headers), indent=2)}')
print(f'Response Body: {response.text}')

# Also try the API root
root_url = 'http://localhost:8000/api/'
root_response = requests.get(root_url)
print(f'\nRoot URL: {root_url}')
print(f'Root Status Code: {root_response.status_code}')
print(f'Root Response Body: {root_response.text}')