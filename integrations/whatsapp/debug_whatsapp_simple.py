"""
Simple test - just connect and show what we see
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = Path(__file__).parent / "whatsapp_session"

async def test():
    print("Starting test...")
    
    playwright = await async_playwright().start()
    
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=False,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
        viewport={"width": 1280, "height": 720},
    )
    
    page = context.pages[0] if context.pages else await context.new_page()
    
    print("Going to WhatsApp Web...")
    await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
    time.sleep(10)  # Give time to see what's happening
    
    # Check what we have
    print("\nChecking page...")
    
    # Try to find chat list
    try:
        await page.wait_for_selector('div[data-testid="chat-list"]', timeout=5000)
        print("✓ Found chat list - LOGGED IN!")
    except:
        print("✗ Chat list not found")
    
    # Try to find QR
    try:
        await page.wait_for_selector('div[data-ref]', timeout=3000)
        print("✗ Found QR code - NOT logged in")
    except:
        print("✓ No QR code found")
    
    # Screenshot
    await page.screenshot(path="debug_status.png")
    print("\nScreenshot saved to debug_status.png")
    
    print("\nKeep browser open for 30 seconds - check if you see chat list or QR code")
    time.sleep(30)
    
    await context.close()
    await playwright.stop()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(test())
