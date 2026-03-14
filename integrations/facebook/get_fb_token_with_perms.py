import webbrowser

app_id = "817958633939618"

# Open Graph API Explorer with direct permission request
url = f"https://developers.facebook.com/tools/explorer/?app_id={app_id}&permissions=pages_manage_posts,pages_read_engagement,pages_show_list"

print("\n" + "=" * 60)
print("GET PAGE ACCESS TOKEN WITH pages_manage_posts")
print("=" * 60)

print("\nOpening Facebook Graph API Explorer with permissions...")
webbrowser.open(url)

print("\n" + "-" * 60)
print("FOLLOW THESE STEPS:")
print("-" * 60)

print("""
1. In the opened page, you should see permissions pre-selected:
   ✓ pages_manage_posts
   ✓ pages_read_engagement
   ✓ pages_show_list

2. If not pre-selected, click "Get Token" → "Get User Access Token"
   Then manually check these permissions:
   ☑️ pages_manage_posts     ← MOST IMPORTANT!
   ☑️ pages_read_engagement
   ☑️ pages_show_list

3. Click "Generate Access Token" or "Continue"

4. Facebook will ask you to authorize. Click "Continue" or "Allow"
   (This works because you're the app admin)

5. AFTER getting the User Token, click "Get Token" again
   → Select "Get Page Access Token"

6. Select your page: "Sunny K Vlogs"

7. The Access Token field will show a NEW Page Access Token
   (It will be different and longer)

8. Click the COPY icon 📋

9. Open your .env file and replace:
   META_ACCESS_TOKEN=new_token_here

10. Save the file

11. Come back and say "test now"
""")

print("\n" + "-" * 60)
print("NOTE: Since you're the app admin, you can grant yourself")
print("these permissions for testing without App Review!")
print("-" * 60)
