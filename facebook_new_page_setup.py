"""
Facebook Token Setup for New Pages

This script helps you get a Page Access Token when you have a new page.
"""

import webbrowser
import os
from dotenv import load_dotenv

print("\n" + "=" * 60)
print("FACEBOOK PAGE ACCESS TOKEN - NEW PAGE SETUP")
print("=" * 60)

print("""
PROBLEM: You created a new Facebook Page but can't get Page Access Token

SOLUTION: Follow these steps in order:
""")

print("\nSTEP 1: Create a Facebook App (if you haven't)")
print("-" * 60)
print("1. Go to: https://developers.facebook.com/apps/")
print("2. Click 'Create App'")
print("3. Select 'Other' → 'Next'")
print("4. Select 'Business' → 'Next'")
print("5. Fill in:")
print("   - App Name: AI Automation Dashboard (or any name)")
print("   - App Contact Email: your email")
print("6. Click 'Create App'")
print("7. Copy your App ID and App Secret from Dashboard")

input("\nPress Enter after creating the app...")

print("\nSTEP 2: Add Your Account as Developer")
print("-" * 60)
print("1. In your App Dashboard, go to 'Settings' → 'Basic'")
print("2. Scroll down to 'App Mode'")
print("3. Switch from 'Development' to 'Live' (IMPORTANT!)")
print("4. Go to 'Roles' → 'Administrators'")
print("5. Add your Facebook account as administrator")

input("\nPress Enter after adding yourself as admin...")

print("\nSTEP 3: Get User Access Token First")
print("-" * 60)
print("1. Go to: https://developers.facebook.com/tools/explorer/")
print("2. Select your app from the dropdown (top)")
print("3. Click 'Get Token' → 'Get User Access Token'")
print("4. Select these permissions:")
print("   ✓ pages_show_list")
print("   ✓ pages_read_engagement")
print("   ✓ pages_manage_posts")
print("   ✓ public_profile")
print("5. Click 'Generate Token'")
print("6. Log in and authorize if prompted")
print("7. Copy the User Access Token")

input("\nPress Enter after getting User Access Token...")

print("\nSTEP 4: Get Your Page ID")
print("-" * 60)
print("1. Go to: https://findmyfbid.in/")
print("2. Or look at your Page URL")
print("3. Copy your Page ID")

page_id = input("\nEnter your Page ID: ").strip()

print("\nSTEP 5: Get Page Access Token from User Token")
print("-" * 60)
print("Now we'll exchange your User Token for a Page Token")

user_token = input("Paste your User Access Token: ").strip()

if user_token and page_id:
    print("\nFetching your Page Access Token...")
    
    import urllib.request
    import json
    
    try:
        # Get pages
        url = f"https://graph.facebook.com/v21.0/me/accounts?access_token={user_token}"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            if "data" in data and len(data["data"]) > 0:
                # Find the specific page or use first available
                page_token = None
                for page in data["data"]:
                    if page["id"] == page_id:
                        page_token = page["access_token"]
                        page_name = page.get("name", "Unknown")
                        break
                
                if not page_token and data["data"]:
                    page_token = data["data"][0]["access_token"]
                    page_name = data["data"][0].get("name", "Unknown")
                    print(f"\n⚠ Using first available page: {page_name}")
                
                if page_token:
                    print(f"\n✓ SUCCESS! Page Access Token for: {page_name}")
                    print(f"\nToken: {page_token}")
                    
                    # Save to .env
                    save = input("\nSave to .env file? (y/n): ").strip().lower()
                    if save == 'y':
                        env_path = os.path.join(os.path.dirname(__file__), ".env")
                        
                        if os.path.exists(env_path):
                            with open(env_path, "r", encoding="utf-8") as f:
                                lines = f.readlines()
                        else:
                            lines = []
                        
                        # Update META_ACCESS_TOKEN
                        token_found = False
                        for i, line in enumerate(lines):
                            if line.startswith("META_ACCESS_TOKEN="):
                                lines[i] = f"META_ACCESS_TOKEN={page_token}\n"
                                token_found = True
                                break
                        
                        if not token_found:
                            lines.append(f"\nMETA_ACCESS_TOKEN={page_token}\n")
                        
                        # Update FB_PAGE_ID
                        page_id_found = False
                        for i, line in enumerate(lines):
                            if line.startswith("FB_PAGE_ID="):
                                lines[i] = f"FB_PAGE_ID={page_id}\n"
                                page_id_found = True
                                break
                        
                        if not page_id_found:
                            lines.append(f"FB_PAGE_ID={page_id}\n")
                        
                        with open(env_path, "w", encoding="utf-8") as f:
                            f.writelines(lines)
                        
                        print("✓ Saved to .env file!")
                        
                        # Test the token
                        print("\n" + "=" * 60)
                        print("TESTING TOKEN")
                        print("=" * 60)
                        
                        load_dotenv(override=True)
                        
                        from integrations.facebook_client import FacebookClient
                        
                        client = FacebookClient()
                        success, info = client.validate_token()
                        
                        if success:
                            print(f"\n✓ Token is valid!")
                            print(f"✓ Page: {info}")
                            print("\n🎉 READY TO POST!")
                            print("\nTest with: python test_facebook_post.py")
                        else:
                            print(f"\n⚠ Validation: {info}")
                            print("Try posting anyway")
                
                else:
                    print("\n✗ Could not find your page. Make sure you're admin of the page.")
            else:
                print("\n✗ No pages found. Make sure you selected the right permissions.")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your app is in 'Live' mode")
        print("2. Make sure you're admin of both the app and the page")
        print("3. Make sure you selected all required permissions")
else:
    print("\n✗ Token or Page ID not provided")

print("\n" + "=" * 60)
print("ALTERNATIVE: Use Graph API Explorer Directly")
print("=" * 60)
print("""
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app
3. Click "Get Token" → "Get Page Access Token"
4. If your page doesn't appear, you need to:
   - Make sure app is Live (not Development)
   - Make sure you're admin of the page
   - Make sure you have pages_* permissions
5. Select your page and copy the token
""")

print()
