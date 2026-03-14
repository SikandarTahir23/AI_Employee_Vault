"""
Test Facebook Token - Fresh Load
"""
import requests
import os

# Fresh load of .env
from dotenv import load_dotenv
load_dotenv(override=True, dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

token = os.getenv('META_ACCESS_TOKEN')
page_id = os.getenv('FB_PAGE_ID')
app_id = os.getenv('META_APP_ID')

print("\n" + "=" * 60)
print("FACEBOOK TOKEN TEST - FRESH LOAD")
print("=" * 60)

print(f"\nToken: {token[:40]}...")
print(f"Page ID: {page_id}")
print(f"App ID: {app_id}")

# Test: Try to get page info
print("\n" + "-" * 60)
print("Testing: Get Page Info")
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
    else:
        print(f"✓ Page Name: {data.get('name', 'Unknown')}")
        print(f"✓ Page ID: {data.get('id', 'N/A')}")
        print("✓ TOKEN IS VALID!")
        
        # Now test posting
        print("\n" + "-" * 60)
        print("Testing: Create Post")
        print("-" * 60)
        
        post_url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
        post_params = {
            'access_token': token,
            'message': 'Test post from AI Dashboard! 🚀'
        }
        
        post_response = requests.post(post_url, params=post_params, timeout=10)
        post_data = post_response.json()
        
        if 'error' in post_data:
            print(f"✗ Post Error: {post_data['error']['message']}")
        else:
            print(f"✓ Post Created! ID: {post_data.get('id')}")
            print("\n🎉 FACEBOOK POSTING IS WORKING!")
except Exception as e:
    print(f"✗ Request failed: {e}")

print()
