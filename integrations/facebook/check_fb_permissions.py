"""
Check Facebook Token Permissions
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

token = os.getenv('META_ACCESS_TOKEN')
page_id = os.getenv('FB_PAGE_ID')
app_id = os.getenv('META_APP_ID')

print("\n" + "=" * 60)
print("FACEBOOK TOKEN PERMISSIONS CHECK")
print("=" * 60)

print(f"\nToken: {token[:40]}...")
print(f"Page ID: {page_id}")
print(f"App ID: {app_id}")

# Check token permissions
print("\n" + "-" * 60)
print("Checking Token Permissions...")
print("-" * 60)

url = "https://graph.facebook.com/v21.0/me/permissions"
params = {'access_token': token}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'data' in data:
        print("\nYour permissions:")
        for perm in data['data']:
            status = "✓" if perm.get('status') == 'granted' else "✗"
            print(f"  {status} {perm.get('permission')}: {perm.get('status')}")
        
        # Check for required permissions
        perms = {p['permission']: p['status'] for p in data['data']}
        
        print("\n" + "-" * 60)
        print("Required for posting:")
        required = ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list']
        
        all_ok = True
        for req_perm in required:
            status = perms.get(req_perm, 'not_found')
            ok = status == 'granted'
            symbol = "✓" if ok else "✗"
            print(f"  {symbol} {req_perm}: {status}")
            if not ok:
                all_ok = False
        
        if all_ok:
            print("\n✓ All required permissions granted!")
        else:
            print("\n✗ Missing required permissions!")
            print("\nTo fix:")
            print("1. Go to Facebook App Dashboard")
            print("2. Go to App Review → Permissions")
            print("3. Add pages_manage_posts permission")
            print("4. OR use a token with all required permissions")
    else:
        print(f"Error: {data}")
except Exception as e:
    print(f"Error: {e}")

# Also check if user is admin of page
print("\n" + "-" * 60)
print("Checking Page Admin Status...")
print("-" * 60)

url = f"https://graph.facebook.com/v21.0/{page_id}"
params = {
    'access_token': token,
    'fields': 'id,name'
}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'error' in data:
        print(f"✗ Cannot access page: {data['error']['message']}")
    else:
        print(f"✓ Can access page: {data.get('name')}")
except Exception as e:
    print(f"Error: {e}")

print()
