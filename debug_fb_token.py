"""
Debug Facebook Token - Check what we have
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

token = os.getenv('META_ACCESS_TOKEN')
page_id = os.getenv('FB_PAGE_ID')

print("\n" + "=" * 60)
print("FACEBOOK TOKEN DEBUG")
print("=" * 60)

print(f"\nToken: {token[:50]}...")
print(f"Token Length: {len(token)}")
print(f"Page ID: {page_id}")

# Test 1: Can we access the page?
print("\n" + "-" * 60)
print("Test 1: Access Page Info")
print("-" * 60)

url = f"https://graph.facebook.com/v21.0/{page_id}"
params = {'access_token': token, 'fields': 'id,name,link'}

response = requests.get(url, params=params, timeout=10)
data = response.json()

if 'error' in data:
    print(f"✗ Cannot access page: {data['error']['message']}")
else:
    print(f"✓ Page Name: {data.get('name')}")
    print(f"✓ Page Link: {data.get('link')}")

# Test 2: Try to get page access token info
print("\n" + "-" * 60)
print("Test 2: Check Token Type")
print("-" * 60)

url = "https://graph.facebook.com/v21.0/oauth/access_token_info"
params = {'access_token': token}

response = requests.get(url, params=params, timeout=10)
data = response.json()

if 'error' not in data:
    print(f"Token Type: {data.get('type', 'Unknown')}")
    print(f"App ID: {data.get('app_id', 'Unknown')}")
    print(f"User ID: {data.get('user_id', 'Unknown')}")
    print(f"Expires: {data.get('expires_at', 'Unknown')}")
    print(f"Issued: {data.get('issued_at', 'Unknown')}")
    
    scopes = data.get('scopes', [])
    print(f"\nYour token has {len(scopes)} permission(s):")
    for scope in scopes:
        print(f"  - {scope}")
else:
    print(f"Cannot get token info: {data.get('error', {}).get('message', 'Unknown')}")

# Test 3: Try posting with pages_manage_metadata permission
print("\n" + "-" * 60)
print("Test 3: Try Alternative Post Method")
print("-" * 60)

# Try using the page's feed endpoint with different parameters
url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
params = {
    'access_token': token,
    'message': 'Test post',
}

response = requests.post(url, params=params, timeout=10)
data = response.json()

if 'error' in data:
    print(f"✗ Post failed: {data['error']['message'][:100]}...")
else:
    print(f"✓ POST SUCCESS! Post ID: {data.get('id')}")

print()
