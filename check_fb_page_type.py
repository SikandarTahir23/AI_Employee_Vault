"""
Check Facebook Page Type and Capabilities
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

token = os.getenv('META_ACCESS_TOKEN')
page_id = os.getenv('FB_PAGE_ID')

print("\n" + "=" * 60)
print("FACEBOOK PAGE CAPABILITIES CHECK")
print("=" * 60)

print(f"\nPage ID: {page_id}")

# Get page details
url = f"https://graph.facebook.com/v21.0/{page_id}"
params = {
    'access_token': token,
    'fields': 'id,name,link,category,page_types,can_post,about,description'
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

if 'error' in data:
    print(f"\n✗ Error: {data['error']['message']}")
else:
    print(f"\n✓ Page Name: {data.get('name')}")
    print(f"✓ Category: {data.get('category')}")
    print(f"✓ Link: {data.get('link')}")
    print(f"✓ Can Post: {data.get('can_post', 'Unknown')}")
    
    if 'page_types' in data:
        print(f"✓ Page Types: {data['page_types']}")
    
    if 'about' in data:
        print(f"✓ About: {data['about']}")

# Check if user is admin
print("\n" + "-" * 60)
print("Checking Your Role on This Page...")
print("-" * 60)

url = "https://graph.facebook.com/v21.0/me/roles"
params = {'access_token': token}

response = requests.get(url, params=params, timeout=10)
roles_data = response.json()

if 'data' in roles_data:
    print("\nYour roles:")
    for role in roles_data['data']:
        print(f"  - {role}")
else:
    print("\nCannot determine your role. You might not be admin.")

print("\n" + "=" * 60)
print("POSSIBLE ISSUES:")
print("=" * 60)

print("""
1. PAGE TYPE ISSUE:
   - Some page types (like "Public Figure") don't support posts
   - Solution: Create a "Business" or "Community" type page

2. NOT ADMIN:
   - You need to be an ADMIN (not just editor) of the page
   - Solution: Ask current admin to make you admin, or create your own page

3. PAGE RESTRICTIONS:
   - Page might have posting restrictions
   - Solution: Check Page Settings → General → Posting Ability

4. NEW PAGE:
   - Very new pages might need time to activate all features
   - Solution: Wait 24-48 hours, complete page setup
""")

print("\n" + "-" * 60)
print("RECOMMENDED SOLUTION:")
print("-" * 60)

print("""
Create a NEW Facebook Page that supports posts:

1. Go to: https://www.facebook.com/pages/create/

2. Select Page Type: "Business" or "Brand/Product"

3. Fill in:
   - Page Name: "Test Page" (or any name)
   - Category: "Community" or "Business Services"

4. Complete the setup

5. Make sure YOU are the ADMIN

6. Then get a Page Access Token for this new page

7. Update .env with new Page ID and Token

8. Test posting
""")

print()
