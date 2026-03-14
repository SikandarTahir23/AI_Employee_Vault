"""
Test Facebook post to user's page
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from facebook_browser import FacebookBrowser

async def main():
    print("=" * 60)
    print("FACEBOOK POST TEST")
    print("=" * 60)
    
    # User's page URL
    page_url = "https://www.facebook.com/profile.php?id=61582749851167"
    message = "Test post from AI dashboard automation"
    
    print(f"\nPage: {page_url}")
    print(f"Message: {message}")
    
    fb = FacebookBrowser()
    
    print("\n1. Connecting to Facebook...")
    connected, msg = await fb.connect(wait_for_login=True)
    
    print(f"   Result: {connected} - {msg}")
    
    if not connected:
        print("\n   ✗ NOT CONNECTED")
        print("   Browser should be open - please log in if needed")
        await fb.close()
        return
    
    print("\n2. Posting to page...")
    success, result = await fb.post_to_page(page_url, message)
    
    if success:
        print(f"\n   ✓ SUCCESS: {result}")
    else:
        print(f"\n   ✗ FAILED: {result}")
    
    await fb.close()
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())
