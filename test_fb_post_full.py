"""
Test Facebook Posting - Full Test
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

token = os.getenv('META_ACCESS_TOKEN')
page_id = os.getenv('FB_PAGE_ID')

print("\n" + "=" * 60)
print("FACEBOOK POSTING TEST")
print("=" * 60)

print(f"\nPage ID: {page_id}")
print(f"Token: {token[:40]}...")

# Test posting to page feed
print("\n" + "-" * 60)
print("Creating Post on Page Feed...")
print("-" * 60)

url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
params = {
    'access_token': token,
    'message': '🧪 Test post from AI Dashboard!\n\nThis is testing the Facebook automation integration.\n\n#AI #Automation #Test',
}

try:
    response = requests.post(url, params=params, timeout=15)
    data = response.json()
    
    print(f"\nResponse: {data}")
    
    if 'error' in data:
        print(f"\n✗ Post Failed!")
        print(f"Error: {data['error'].get('message', 'Unknown')}")
        print(f"Error Code: {data['error'].get('code', 'N/A')}")
        print(f"Error Subcode: {data['error'].get('error_subcode', 'N/A')}")
        
        # Check if it's a permission error
        if data['error'].get('code') == 200:
            print("\nThis is a permission error.")
            print("\nPossible causes:")
            print("1. Token doesn't have pages_manage_posts permission")
            print("2. You're not an admin of the page")
            print("3. App needs Advanced Access for pages_manage_posts")
            
            print("\n" + "-" * 60)
            print("SOLUTION: Get token with proper permissions")
            print("-" * 60)
            print("""
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app
3. Click "Get Token" → "Get Page Access Token"
4. IMPORTANT: When permissions popup appears, check:
   ☑️ pages_manage_posts
   ☑️ pages_read_engagement  
   ☑️ pages_show_list
5. Select your page
6. Copy the NEW token
7. Update .env file
8. Test again
""")
    else:
        post_id = data.get('id')
        print(f"\n✓ POST SUCCESSFUL!")
        print(f"Post ID: {post_id}")
        print(f"\nView your post at:")
        print(f"https://www.facebook.com/{post_id}")
        
except Exception as e:
    print(f"\n✗ Request failed: {e}")

print()
