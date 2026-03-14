"""
Quick Facebook post test - with hardcoded values
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from facebook_browser import FacebookBrowser

async def main():
    print("=" * 60)
    print("FACEBOOK POST TEST")
    print("=" * 60)
    
    # Test values - change these
    page_url = "https://www.facebook.com/"  # Your page URL here
    message = "Test post from automation"
    
    print(f"\nPage URL: {page_url}")
    print(f"Message: {message}")
    
    fb = FacebookBrowser()
    
    print("\n1. Connecting to Facebook...")
    connected, msg = await fb.connect(wait_for_login=True)
    
    if not connected:
        print(f"   ✗ Connection failed: {msg}")
        await fb.close()
        return
    
    print(f"   ✓ Connected: {msg}")
    
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
