import webbrowser

page_id = "104578769189982"  # Your original page

print("\n" + "=" * 60)
print("GET PAGE ACCESS TOKEN - DIRECT METHOD")
print("=" * 60)

print("\nOpening Facebook Graph API Explorer...")
webbrowser.open("https://developers.facebook.com/tools/explorer/")

print("\n" + "-" * 60)
print("FOLLOW THESE EXACT STEPS:")
print("-" * 60)

print("""
STEP 1: Get Page Access Token Directly
--------------------------------------
1. In Graph API Explorer, click "Get Token" (top right)
2. Select "Get Page Access Token"
3. A popup will appear showing your pages
4. Look for ANY page in the list (even if not your new one)
5. Click on a page name
6. The Access Token field will update
7. Click COPY 📋 to copy the token


STEP 2: Test If Token Works
---------------------------
1. In the API field at top, type: /104578769189982
   (or your page ID)
2. Click "Submit"
3. If you see page info, the token works!
4. If error, try a different page


STEP 3: Try Posting
-------------------
1. With the same token, change API field to:
   /104578769189982/feed
2. Click "Submit" dropdown → select "POST"
3. In the request body, add:
   message: Test post from API
4. Click "Submit"
5. If it works, you'll see a post ID!


STEP 4: Update .env
-------------------
If posting worked:
  META_ACCESS_TOKEN=copy_the_token_here
  FB_PAGE_ID=your_page_id
""")

print("\n" + "-" * 60)
print("ALTERNATIVE: Use Your Page's Direct URL")
print("-" * 60)

print(f"""
1. Go to your Facebook page:
   https://www.facebook.com/{page_id}

2. Make sure you can post manually (create a post by hand)

3. If manual posting works, then the issue is just the token

4. Go back to Graph API Explorer and get a fresh Page Token
""")

print("\n" + "-" * 60)
print("OR: Try This Direct Link")
print("-" * 60)

# Open a link that might work better
direct_url = f"https://graph.facebook.com/{page_id}?fields=access_token&access_token=YOUR_TOKEN"
print(f"\nAfter getting a token, try this URL:")
print(direct_url)
print("\nReplace YOUR_TOKEN with your actual token")

print()
