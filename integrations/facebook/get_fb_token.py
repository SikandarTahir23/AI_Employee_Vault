import webbrowser

# Open Graph API Explorer with your app pre-selected
app_id = "817958633939618"
url = f"https://developers.facebook.com/tools/explorer/?app_id={app_id}"

print("\n" + "=" * 60)
print("GET FACEBOOK PAGE ACCESS TOKEN WITH CORRECT PERMISSIONS")
print("=" * 60)

print("\nOpening Facebook Graph API Explorer...")
webbrowser.open(url)

print("\n" + "-" * 60)
print("FOLLOW THESE STEPS EXACTLY:")
print("-" * 60)

print("""
1. In the opened page, click "Get Token" button (top right)

2. Select "Get Page Access Token"

3. A popup will show permissions. Make sure these are CHECKED:
   ☑️ pages_manage_posts     (REQUIRED for posting)
   ☑️ pages_read_engagement
   ☑️ pages_show_list

4. Click "Continue" or "Generate Token"

5. Select your page: "Sunny K Vlogs"

6. The Access Token field will update with a NEW token
   (it will be different from the current one)

7. Click the COPY icon 📋 next to the token

8. Open your .env file and replace:
   META_ACCESS_TOKEN=new_token_here

9. Save the .env file

10. Come back and say "test again"
""")

print("\n" + "-" * 60)
print("Current token starts with: EAALn7dXRIqIBQ8PK0N3p03059VrKVmpXgP5ZAhH...")
print("New token should start with: EAA... (different)")
print("-" * 60)
