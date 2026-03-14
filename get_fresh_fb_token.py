import webbrowser

print("\n" + "=" * 60)
print("GET FRESH FACEBOOK TOKEN - SHOWS ALL YOUR PAGES")
print("=" * 60)

print("\nOpening Facebook Graph API Explorer...")
webbrowser.open("https://developers.facebook.com/tools/explorer/")

print("\n" + "-" * 60)
print("FOLLOW THESE EXACT STEPS:")
print("-" * 60)

print("""
STEP 1: Get User Access Token
-----------------------------
1. Click "Get Token" button (top right)
2. Select "Get User Access Token"
3. Check these permissions:
   ☑️ pages_show_list
   ☑️ pages_read_engagement
   ☑️ pages_manage_posts (if you see it)
4. Click "Continue" or "Generate Token"
5. Facebook will ask you to authorize - click "Continue as [Your Name]"
6. You now have a User Access Token (long string starting with EAA...)


STEP 2: List Your Pages
-----------------------
1. In the Graph API Explorer, you'll see a text field at the top
2. Delete whatever is there and type: /me/accounts
3. Click "Submit" button
4. You should see a list of ALL your pages like:
   {
     "data": [
       {
         "name": "Your Page Name",
         "id": "123456789",
         "access_token": "EAAL..."
       }
     ]
   }


STEP 3: Copy Page Token
-----------------------
1. Find your NEW page in the list
2. Copy the "access_token" value (the long string)
3. Also copy the page "id"


STEP 4: Update .env
-------------------
Open your .env file and update:
  META_ACCESS_TOKEN=paste_the_access_token_here
  FB_PAGE_ID=paste_the_page_id_here


STEP 5: Test
------------
Come back and say: "test facebook"
""")

print("\n" + "-" * 60)
print("TIP: If /me/accounts doesn't work, try:")
print("  1. Copy your User Access Token")
print("  2. Go to: https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_TOKEN")
print("  3. You'll see your pages in the browser")
print("-" * 60)
