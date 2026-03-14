"""
Simple Facebook login test - keeps browser open for login
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

FACEBOOK_SESSION_DIR = Path(__file__).parent / "facebook_session"

async def test_login():
    print("=" * 60)
    print("FACEBOOK LOGIN TEST")
    print("=" * 60)
    print("\nBrowser will open. Please login to Facebook.")
    print("After login, the session will be saved.")
    print("\nWaiting 5 minutes for you to login...")
    print("=" * 60)
    
    playwright = await async_playwright().start()
    
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(FACEBOOK_SESSION_DIR),
        headless=False,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
        viewport={"width": 1280, "height": 720},
    )
    
    page = context.pages[0] if context.pages else await context.new_page()
    
    print("\nNavigating to Facebook...")
    await page.goto("https://www.facebook.com", wait_until="domcontentloaded")
    
    # Wait 5 minutes for login
    print("\n⏳ Waiting 5 minutes for login...")
    print("   → Enter your email and password")
    print("   → Click 'Log In'")
    print("   → Wait for your feed to load")
    
    for i in range(30):  # 5 minutes
        await asyncio.sleep(10)
        
        # Check if logged in
        try:
            elem = await page.query_selector('div[role="navigation"]')
            if elem:
                print("\n✓ Login detected!")
                await page.screenshot(path="fb_logged_in.png")
                print("  Screenshot saved: fb_logged_in.png")
                break
        except:
            pass
        
        if (i + 1) * 10 % 60 == 0:
            print(f"   Still waiting... ({(i+1)*10}s)")
    
    print("\n\nBrowser will stay open for 30 more seconds...")
    print("Make sure you see your Facebook feed (not login page)")
    time.sleep(30)
    
    await context.close()
    await playwright.stop()
    print("\nDone! Session should be saved.")
    print("Try posting from the dashboard now.")

if __name__ == "__main__":
    asyncio.run(test_login())
