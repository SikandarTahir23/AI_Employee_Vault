"""
Facebook Token Refresh - Simple Method

This script helps you get a new Facebook token manually.
"""

import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

print("\n" + "=" * 60)
print("FACEBOOK TOKEN REFRESH - MANUAL METHOD")
print("=" * 60)

app_id = os.getenv("META_APP_ID", "4449990781989754")

print("\nSTEP 1: Open Facebook Graph API Explorer")
print("-" * 60)
input("Press Enter to open the page...")

url = "https://developers.facebook.com/tools/explorer/"
webbrowser.open(url)

print("\nSTEP 2: Get Page Access Token")
print("-" * 60)
print("""
1. In Graph API Explorer, click "Get Token" button
2. Select "Get Page Access Token"
3. Select your Facebook page from the list
4. A token will appear in the "Access Token" field
5. Click the copy icon to copy the token
""")

input("\nPress Enter when you have copied the token...")

print("\nSTEP 3: Update .env File")
print("-" * 60)

new_token = input("Paste your new token here: ").strip()

if new_token:
    # Update .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Update or add META_ACCESS_TOKEN
    token_found = False
    for i, line in enumerate(lines):
        if line.startswith("META_ACCESS_TOKEN="):
            lines[i] = f"META_ACCESS_TOKEN={new_token}\n"
            token_found = True
            break
    
    if not token_found:
        lines.append(f"\nMETA_ACCESS_TOKEN={new_token}\n")
    
    # Write back
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print("\n✓ .env file updated!")
    
    # Test the token
    print("\n" + "=" * 60)
    print("TESTING NEW TOKEN")
    print("=" * 60)
    
    try:
        from integrations.facebook_client import FacebookClient
        # Reload env
        load_dotenv(override=True)
        
        client = FacebookClient()
        success, info = client.validate_token()
        
        if success:
            print(f"\n✓ Token is valid!")
            print(f"✓ Page info: {info}")
            print("\n" + "=" * 60)
            print("SUCCESS! You can now post to Facebook.")
            print("=" * 60)
            print("\nTest with: python test_facebook_post.py")
        else:
            print(f"\n⚠ Token validation: {info}")
            print("The token might still work for posting. Try it!")
    except Exception as e:
        print(f"\n⚠ Could not validate: {e}")
        print("Try posting anyway with: python test_facebook_post.py")
else:
    print("\n✗ No token entered. .env file not updated.")

print()
