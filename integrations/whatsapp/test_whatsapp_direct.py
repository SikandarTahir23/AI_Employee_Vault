"""
Direct WhatsApp Test - Shows Browser Window
Run this OUTSIDE of Streamlit
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_whatsapp():
    from playwright.async_api import async_playwright
    
    print("=" * 60)
    print("WhatsApp QR Code Test")
    print("=" * 60)
    
    # Launch Playwright
    playwright = await async_playwright().start()
    
    # Launch browser VISIBLE (not headless)
    browser = await playwright.chromium.launch(
        headless=False,  # SHOW the browser!
        args=[
            '--disable-gpu',
            '--no-sandbox',
            '--start-maximized'
        ]
    )
    
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720}
    )
    
    page = await context.new_page()
    
    print("\n📱 Navigating to WhatsApp Web...")
    await page.goto("https://web.whatsapp.com", wait_until='domcontentloaded')
    
    print("✅ Browser window should be visible now!")
    print("📲 Scan the QR code with your WhatsApp mobile app:")
    print("   - Android: Menu (⋮) → Linked devices → Link a device")
    print("   - iPhone: Settings → Linked Devices → Link a Device")
    print("\n⏳ Waiting 60 seconds for QR scan...")
    
    # Wait 60 seconds
    await asyncio.sleep(60)
    
    # Check if logged in
    try:
        main_interface = await page.query_selector('[data-testid="chat-list"]')
        if main_interface:
            print("\n✅ Login successful!")
        else:
            print("\n⚠️ QR code still showing or not detected")
    except Exception as e:
        print(f"\n⚠️ Error checking status: {e}")
    
    print("\nClosing browser...")
    await browser.close()
    await playwright.stop()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_whatsapp())
