"""
Debug Facebook connection
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

FACEBOOK_SESSION_DIR = Path(__file__).parent / "facebook_session"

async def debug():
    print("=" * 60)
    print("FACEBOOK CONNECTION DEBUG")
    print("=" * 60)
    
    playwright = await async_playwright().start()
    
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(FACEBOOK_SESSION_DIR),
        headless=False,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
        viewport={"width": 1280, "height": 720},
    )
    
    page = context.pages[0] if context.pages else await context.new_page()
    
    print("\n1. Navigating to Facebook...")
    await page.goto("https://www.facebook.com", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    
    # Screenshot
    await page.screenshot(path="debug_fb_status.png")
    print("   Screenshot saved: debug_fb_status.png")
    
    print("\n2. Checking page info...")
    print(f"   URL: {page.url}")
    print(f"   Title: {await page.title()}")
    
    print("\n3. Looking for elements...")
    
    # Check for logged-in indicators
    selectors = {
        'Main nav': 'div[role="navigation"]',
        'Watch link': 'a[href^="/watch/"]',
        'Marketplace': 'a[href^="/marketplace/"]',
        'Create post': '[aria-label*="What\'s on your mind"]',
        'Search box': 'input[placeholder*="Search"]',
        'Menu button': 'div[aria-label="Menu"]',
        'Profile link': 'a[href^="/profile.php"]',
        'Home link': 'a[href="/"]',
    }
    
    for name, sel in selectors.items():
        try:
            elem = await page.query_selector(sel)
            print(f"   {name}: {'✓ Found' if elem else '✗ Not found'}")
        except:
            print(f"   {name}: ✗ Error")
    
    # Check for login form
    login_form = await page.query_selector('form#login_form')
    print(f"\n   Login form: {'✓ Found (NOT LOGGED IN)' if login_form else '✗ Not found'}")
    
    # Check for login input
    email_input = await page.query_selector('input[type="email"]')
    print(f"   Email input: {'✓ Found (NOT LOGGED IN)' if email_input else '✗ Not found'}")
    
    print("\n4. Browser will stay open for 30 seconds...")
    print("   Check if you see Facebook feed (logged in) or login page")
    time.sleep(30)
    
    await context.close()
    await playwright.stop()
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(debug())
