"""
List all Facebook pages you manage - Direct version
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

token = os.getenv('META_ACCESS_TOKEN')

print("\n" + "=" * 60)
print("YOUR FACEBOOK PAGES")
print("=" * 60)

url = "https://graph.facebook.com/v21.0/me/accounts"
params = {'access_token': token}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'error' in data:
        print(f"\n✗ Error: {data['error']['message']}")
        print("\nYour token might be expired. Get a new one:")
        print("1. Go to: https://developers.facebook.com/tools/explorer/")
        print("2. Get a fresh User Access Token")
        print("3. Then Get Page Access Token")
    elif 'data' in data and len(data['data']) > 0:
        print(f"\n✓ Found {len(data['data'])} page(s):\n")
        for i, page in enumerate(data['data'], 1):
            name = page.get('name', 'Unknown')
            page_id = page.get('id')
            access_token = page.get('access_token', '')
            
            print(f"{i}. {name}")
            print(f"   ID: {page_id}")
            if access_token:
                print(f"   Token: {access_token[:60]}...")
                print(f"   Full Token (copy this):")
                print(f"   {access_token}")
            print()
        
        print("=" * 60)
        print("INSTRUCTIONS:")
        print("=" * 60)
        print("\n1. Copy the FULL token for your NEW page")
        print("2. Open your .env file")
        print("3. Update these lines:")
        print(f"   META_ACCESS_TOKEN={data['data'][0].get('access_token', '')}")
        print(f"   FB_PAGE_ID={data['data'][0].get('id', '')}")
        print("4. Save the file")
        print("5. Say 'test facebook' and I'll test posting")
    else:
        print("\n✗ No pages found.")
        print("\nPossible reasons:")
        print("1. Your token is expired - get a new one")
        print("2. New page hasn't activated yet - wait 10 minutes")
        print("3. You're not admin of any page")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print()
