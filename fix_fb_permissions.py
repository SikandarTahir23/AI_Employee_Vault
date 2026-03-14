import webbrowser

app_id = "817958633939618"

print("\n" + "=" * 60)
print("EXACT STEPS TO GET pages_manage_posts PERMISSION")
print("=" * 60)

print("\nOpening Facebook App Dashboard...")
webbrowser.open(f"https://developers.facebook.com/apps/{app_id}/permissions/")

print("\n" + "-" * 60)
print("STEP 1: Add pages_manage_posts to Your App")
print("-" * 60)

print("""
1. In your App Dashboard, click "Add Permission" or "Edit"

2. Search for: pages_manage_posts

3. Click on it → Click "Add" or "Save"

4. Now go to: App Review → Permissions

5. You should see pages_manage_posts in the list

6. Toggle it ON (for development/testing)
""")

input("\nPress Enter after adding the permission...")

print("\n" + "-" * 60)
print("STEP 2: Get Token with pages_manage_posts")
print("-" * 60)

print("""
1. Go to: https://developers.facebook.com/tools/explorer/

2. Select your app at the top

3. Click "Get Token" → "Get User Access Token"

4. In the permissions list, FIND and CHECK:
   ☑️ pages_manage_posts     ← This is the KEY one!
   ☑️ pages_read_engagement
   ☑️ pages_show_list

5. Click "Generate Token" or "Continue"

6. Facebook will show a warning. Click "Continue as [Your Name]"

7. You now have a User Token with pages_manage_posts

8. NOW click "Get Token" AGAIN → "Get Page Access Token"

9. Select "Sunny K Vlogs" page

10. The Access Token field will update with a PAGE token
    (This token now has pages_manage_posts inherited)

11. Click COPY 📋

12. Update .env: META_ACCESS_TOKEN=new_token

13. Say "test now"
""")

print("\n" + "-" * 60)
print("IMPORTANT: You MUST add pages_manage_posts to your app")
print("first in App Dashboard before you can get the token!")
print("-" * 60)
