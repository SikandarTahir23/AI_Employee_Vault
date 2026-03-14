"""
Debug WhatsApp connection with detailed logging
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = Path(__file__).parent / "whatsapp_session"

async def debug_connect():
    print("=" * 60)
    print("WHATSAPP CONNECTION DEBUG")
    print("=" * 60)
    
    playwright = None
    context = None
    page = None
    
    try:
        print(f"\n1. Session directory: {USER_DATA_DIR}")
        print(f"   Exists: {USER_DATA_DIR.exists()}")
        
        print("\n2. Starting Playwright...")
        playwright = await async_playwright().start()
        print("   ✓ Playwright started")
        
        print("\n3. Launching browser with persistent context...")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
            viewport={"width": 1280, "height": 720},
        )
        print("   ✓ Browser launched")
        
        page = context.pages[0] if context.pages else await context.new_page()
        print(f"   ✓ Page obtained (total pages: {len(context.pages)})")
        
        print("\n4. Navigating to WhatsApp Web...")
        try:
            await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
            print("   ✓ Navigation completed")
        except Exception as e:
            print(f"   ✗ Navigation error: {e}")
            return
        
        print("\n5. Waiting for network idle...")
        try:
            await page.wait_for_load_state("networkidle", timeout=30000)
            print("   ✓ Network idle reached")
        except Exception as e:
            print(f"   ✗ Network wait error: {e}")
        
        print("\n6. Waiting for page stability...")
        time.sleep(5)
        
        # Take screenshot
        await page.screenshot(path="debug_nav.png")
        print("   ✓ Screenshot saved: debug_nav.png")
        
        print("\n7. Checking page content...")
        title = await page.title()
        print(f"   Page title: {title}")
        
        url = page.url
        print(f"   Current URL: {url}")
        
        print("\n8. Looking for elements...")
        
        # Check for chat list
        chat_list = await page.query_selector('div[data-testid="chat-list"]')
        print(f"   Chat list found: {chat_list is not None}")
        
        # Check for navigation
        nav = await page.query_selector('div[role="navigation"]')
        print(f"   Navigation found: {nav is not None}")
        
        # Check for search input
        search = await page.query_selector('input[title="Search or start new chat"]')
        print(f"   Search input found: {search is not None}")
        
        # Check for QR code
        qr = await page.query_selector('div[data-ref]')
        print(f"   QR code found: {qr is not None}")
        
        # Check for default user (welcome screen)
        default_user = await page.query_selector('div[data-testid="default-user"]')
        print(f"   Default user (welcome) found: {default_user is not None}")
        
        print("\n9. Checking if logged in...")
        is_logged_in = chat_list is not None or nav is not None or search is not None
        print(f"   Logged in: {is_logged_in}")
        
        if is_logged_in:
            print("\n" + "=" * 60)
            print("✓ SUCCESS: You are logged in!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠ NOT LOGGED IN: QR code may be shown")
            print("=" * 60)
        
        print("\n10. Browser will stay open for 30 seconds...")
        print("    Check the browser window to see what's displayed")
        time.sleep(30)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if context:
            await context.close()
        if playwright:
            await playwright.stop()
        print("\nDone!")

if __name__ == "__main__":
    asyncio.run(debug_connect())
