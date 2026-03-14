import webbrowser

print("\n" + "=" * 60)
print("CREATE A NEW FACEBOOK PAGE FOR TESTING")
print("=" * 60)

print("\nOpening Facebook Page Creation...")
webbrowser.open("https://www.facebook.com/pages/create/")

print("\n" + "-" * 60)
print("STEP-BY-STEP:")
print("-" * 60)

print("""
1. Fill in Page Details:
   - Page Name: "AI Test Page" (or any name)
   - Category: Select "Community" OR "Business/Brand/Organization"
   
2. Complete the setup (add profile pic if you want)

3. Once page is created, you'll be the ADMIN automatically

4. Now get a Page Access Token:
   - Go to: https://developers.facebook.com/tools/explorer/
   - Select your app
   - Click "Get Token" → "Get Page Access Token"
   - Select your NEW page ("AI Test Page")
   - Copy the token

5. Update .env file:
   - FB_PAGE_ID=new_page_id
   - META_ACCESS_TOKEN=new_token

6. Come back and say "test facebook"
""")

print("\n" + "-" * 60)
print("NOTE: New pages you create will have you as ADMIN")
print("and will support posting by default!")
print("-" * 60)
