from dotenv import load_dotenv
import os

load_dotenv()

print("Facebook Configuration Check")
print("=" * 40)
print(f"META_ACCESS_TOKEN: {'✓ Set' if os.getenv('META_ACCESS_TOKEN') else '✗ Not set'}")
print(f"FB_PAGE_ID: {'✓ Set' if os.getenv('FB_PAGE_ID') else '✗ Not set'}")
print(f"META_APP_ID: {'✓ Set' if os.getenv('META_APP_ID') else '✗ Not set'}")
print(f"META_APP_SECRET: {'✓ Set' if os.getenv('META_APP_SECRET') else '✗ Not set'}")

if os.getenv('META_ACCESS_TOKEN') and os.getenv('FB_PAGE_ID'):
    print("\n✓ Facebook is configured and ready to test!")
else:
    print("\n✗ Facebook credentials not configured")
    print("\nTo configure Facebook:")
    print("1. Get a Page Access Token from:")
    print("   https://developers.facebook.com/tools/explorer/")
    print("2. Find your Page ID from:")
    print("   https://findmyfbid.in/")
    print("3. Add to .env file:")
    print("   META_ACCESS_TOKEN=your_token_here")
    print("   FB_PAGE_ID=your_page_id_here")
