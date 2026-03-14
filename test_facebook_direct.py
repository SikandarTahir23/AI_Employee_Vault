"""
Direct Facebook Test - Tests Graph API
Run this OUTSIDE of Streamlit
"""

import sys
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

def test_facebook():
    import os
    import requests
    
    print("=" * 60)
    print("Facebook Graph API Test")
    print("=" * 60)
    
    # Get credentials
    access_token = os.getenv('META_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    
    print(f"\n📋 Credentials Check:")
    print(f"   META_ACCESS_TOKEN: {'✓ Found' if access_token else '✗ MISSING'}")
    print(f"   FB_PAGE_ID: {'✓ Found' if page_id else '✗ MISSING'}")
    
    if not access_token or not page_id:
        print("\n❌ ERROR: Credentials missing in .env file!")
        return
    
    # Test 1: Validate Token
    print(f"\n🔍 Test 1: Validating Token...")
    debug_url = f"https://graph.facebook.com/v21.0/debug_token"
    params = {
        'input_token': access_token,
        'access_token': f"{os.getenv('META_APP_ID')}|{os.getenv('META_APP_SECRET')}"
    }
    
    try:
        response = requests.get(debug_url, params=params, timeout=10)
        token_data = response.json()
        
        if 'data' in token_data:
            is_valid = token_data['data'].get('is_valid', False)
            if is_valid:
                print(f"   ✅ Token is VALID")
                print(f"   User ID: {token_data['data'].get('user_id', 'N/A')}")
            else:
                print(f"   ❌ Token is INVALID")
                print(f"   Error: {token_data['data'].get('error', {})}")
        else:
            print(f"   ⚠️ Unexpected response: {token_data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Get Page Info
    print(f"\n📄 Test 2: Getting Page Info...")
    page_url = f"https://graph.facebook.com/v21.0/{page_id}"
    params = {'access_token': access_token, 'fields': 'id,name'}
    
    try:
        response = requests.get(page_url, params=params, timeout=10)
        page_data = response.json()
        
        if 'name' in page_data:
            print(f"   ✅ Page: {page_data['name']}")
            print(f"   Page ID: {page_data['id']}")
        else:
            print(f"   ⚠️ Response: {page_data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test Post
    print(f"\n📝 Test 3: Creating Test Post...")
    post_url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
    params = {
        'access_token': access_token,
        'message': f'Test post from AI Dashboard - {time.strftime("%Y-%m-%d %H:%M:%S")}'
    }
    
    import time
    try:
        response = requests.post(post_url, params=params, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            print(f"   ✅ Post created successfully!")
            print(f"   Post ID: {result.get('id', 'N/A')}")
        else:
            print(f"   ❌ Post failed: {result}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_facebook()
