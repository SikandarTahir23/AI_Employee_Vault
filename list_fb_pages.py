import webbrowser

app_id = "817958633939618"

print("\n" + "=" * 60)
print("GET TOKEN FOR NEW PAGE - TROUBLESHOOTING")
print("=" * 60)

print("\nOpening Graph API Explorer...")
webbrowser.open(f"https://developers.facebook.com/tools/explorer/?app_id={app_id}")

print("\n" + "-" * 60)
print("TRY THESE STEPS IN ORDER:")
print("-" * 60)

print("""
METHOD 1: Refresh the Page List
-------------------------------
1. In Graph API Explorer, click "Get Token"
2. Select "Get Page Access Token"
3. If your new page doesn't appear, click "Refresh" or close and reopen
4. Wait 30 seconds and try again


METHOD 2: Get User Token First, Then Page Token
-----------------------------------------------
1. Click "Get Token" → "Get User Access Token"
2. Check these permissions:
   ☑️ pages_show_list
   ☑️ pages_read_engagement
   ☑️ pages_manage_posts (if available)
3. Click "Generate Token" → "Continue"
4. After you get User Token, run the script below to list your pages


METHOD 3: Use API to List Your Pages
------------------------------------
1. In Graph API Explorer, change the endpoint to:
   /me/accounts

2. Click "Submit" or "Go"

3. You should see a list of ALL pages you manage

4. Find your new page and copy its ID

5. Then get token for that specific page
""")

print("\n" + "-" * 60)
print("QUICK TEST: List Your Pages via API")
print("-" * 60)

input("\nPress Enter to run page lister...")

# List pages using current token
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

token = os.getenv('META_ACCESS_TOKEN')

print("\nFetching your pages...")

url = "https://graph.facebook.com/v21.0/me/accounts"
params = {'access_token': token}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'error' in data:
        print(f"\n✗ Error: {data['error']['message']}")
    elif 'data' in data and len(data['data']) > 0:
        print(f"\n✓ Found {len(data['data'])} page(s) you manage:")
        print()
        for i, page in enumerate(data['data'], 1):
            print(f"  {i}. {page.get('name', 'Unknown')}")
            print(f"     ID: {page.get('id')}")
            print(f"     Token: {page.get('access_token', '')[:50]}...")
            print()
        
        print("-" * 60)
        print("COPY THE TOKEN FOR YOUR NEW PAGE")
        print("-" * 60)
        print("\nThen update .env:")
        print("  META_ACCESS_TOKEN=copy_full_token_here")
        print("  FB_PAGE_ID=copy_page_id_here")
    else:
        print("\n✗ No pages found. Make sure you're admin of a page.")
        print("\nTry this:")
        print("1. Log out of Facebook and log back in")
        print("2. Wait 5-10 minutes for new page to activate")
        print("3. Try again")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print()
