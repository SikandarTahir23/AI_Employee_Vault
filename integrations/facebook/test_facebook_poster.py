"""
Test Facebook posting automation
"""

import asyncio
from facebook_browser import FacebookBrowser

async def test():
    print("=" * 60)
    print("FACEBOOK POSTER TEST")
    print("=" * 60)
    
    fb = FacebookBrowser()
    
    # Connect
    print("\n1. Connecting to Facebook...")
    connected, msg = await fb.connect(wait_for_login=True)
    
    if not connected:
        print(f"   ✗ Failed: {msg}")
        return
    
    print(f"   ✓ Connected: {msg}")
    
    # Get page URL and message
    print("\n2. Enter test details:")
    page_url = input("   Page URL: ").strip()
    message = input("   Message: ").strip()
    
    if not page_url or not message:
        print("   ✗ Invalid input")
        await fb.close()
        return
    
    # Post
    print("\n3. Posting...")
    success, result = await fb.post_to_page(page_url, message)
    
    if success:
        print(f"\n   ✓ SUCCESS: {result}")
    else:
        print(f"\n   ✗ FAILED: {result}")
    
    await fb.close()
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(test())
