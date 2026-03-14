"""
Test Facebook Token Validity
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('META_ACCESS_TOKEN')
page_id = os.getenv('FB_PAGE_ID')

print("\n" + "=" * 60)
print("FACEBOOK TOKEN VALIDITY TEST")
print("=" * 60)

print(f"\nToken: {token[:30]}...")
print(f"Page ID: {page_id}")

# Test 1: Try to get page info
print("\n" + "-" * 60)
print("Test 1: Getting Page Info")
print("-" * 60)

url = f"https://graph.facebook.com/v21.0/{page_id}"
params = {
    'access_token': token,
    'fields': 'name,id'
}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'error' in data:
        print(f"✗ Error: {data['error']['message']}")
        print(f"  Error Code: {data['error'].get('code', 'N/A')}")
        print(f"  Error Subcode: {data['error'].get('error_subcode', 'N/A')}")
    else:
        print(f"✓ Page Name: {data.get('name', 'Unknown')}")
        print(f"✓ Page ID: {data.get('id', 'N/A')}")
        print("✓ Token is VALID for this page!")
except Exception as e:
    print(f"✗ Request failed: {e}")

# Test 2: Try to get pages list
print("\n" + "-" * 60)
print("Test 2: Getting Pages List")
print("-" * 60)

url = "https://graph.facebook.com/v21.0/me/accounts"
params = {
    'access_token': token
}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'error' in data:
        print(f"✗ Error: {data['error']['message']}")
    else:
        print(f"✓ Found {len(data.get('data', []))} page(s):")
        for page in data.get('data', []):
            print(f"  - {page.get('name', 'Unknown')} (ID: {page.get('id')})")
except Exception as e:
    print(f"✗ Request failed: {e}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)

# Final verdict
url = f"https://graph.facebook.com/v21.0/{page_id}"
params = {'access_token': token, 'fields': 'name'}
response = requests.get(url, params=params, timeout=10)
data = response.json()

if 'error' in data:
    print("\n✗ TOKEN IS INVALID")
    print("\nReason:", data['error']['message'])
    print("\nTo fix:")
    print("1. Create a NEW Facebook App at:")
    print("   https://developers.facebook.com/apps/")
    print("2. Make sure app is 'Live' (not Development)")
    print("3. Get a fresh Page Access Token from:")
    print("   https://developers.facebook.com/tools/explorer/")
    print("4. Update .env with new token")
else:
    print("\n✓ TOKEN IS VALID")
    print(f"✓ Page: {data.get('name', 'Unknown')}")
    print("\nYou should be able to post!")

print()
