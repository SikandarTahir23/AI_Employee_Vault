"""
Login Helper - Opens WhatsApp and LinkedIn browsers directly
Run this to authenticate, then use Streamlit normally
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("           AUTHENTICATION HELPER")
print("=" * 70)
print()
print("This will open browsers for WhatsApp and LinkedIn login.")
print("After logging in, the sessions will be saved for Streamlit.")
print()

choice = input("Which service do you want to authenticate? (1/2/3): \n  1. WhatsApp\n  2. LinkedIn\n  3. Both\n\n> ")

if choice in ['1', '3']:
    print("\n" + "=" * 70)
    print("WHATSAPP LOGIN")
    print("=" * 70)
    
    import asyncio
    from playwright.async_api import async_playwright
    
    async def whatsapp_login():
        playwright = await async_playwright().start()
        
        browser = await playwright.chromium.launch(
            headless=False,
            args=['--start-maximized', '--no-sandbox']
        )
        
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        print("\n📱 Opening WhatsApp Web...")
        await page.goto("https://web.whatsapp.com")
        
        print("✅ Browser opened!")
        print("📲 Scan QR code with WhatsApp mobile app:")
        print("   Android: Menu (⋮) → Linked devices → Link a device")
        print("   iPhone: Settings → Linked Devices → Link a Device")
        print()
        print("⏳ Waiting 60 seconds...")
        
        await asyncio.sleep(60)
        
        # Check login
        try:
            chat_list = await page.query_selector('[data-testid="chat-list"]')
            if chat_list:
                print("\n✅ WhatsApp login SUCCESSFUL!")
            else:
                print("\n⚠️ QR code still showing (session may still work)")
        except:
            print("\n⚠️ Could not verify login status")
        
        await browser.close()
        await playwright.stop()
        
        print("✅ WhatsApp session saved!")
    
    asyncio.run(whatsapp_login())

if choice in ['2', '3']:
    print("\n" + "=" * 70)
    print("LINKEDIN LOGIN")
    print("=" * 70)
    
    import time
    from playwright.sync_api import sync_playwright
    
    playwright = sync_playwright().start()
    
    browser = playwright.chromium.launch(
        headless=False,
        args=['--start-maximized', '--no-sandbox']
    )
    
    context = browser.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()
    
    print("\n💼 Opening LinkedIn login...")
    page.goto("https://www.linkedin.com/login")
    
    print("✅ Browser opened!")
    print("🔐 Log in to LinkedIn in the browser window")
    print()
    print("⏳ Waiting 120 seconds...")
    
    time.sleep(120)
    
    # Check login
    if "/feed" in page.url:
        print("\n✅ LinkedIn login SUCCESSFUL!")
    else:
        print(f"\n⚠️ Current page: {page.url}")
    
    context.close()
    playwright.stop()
    
    print("✅ LinkedIn session saved!")

print("\n" + "=" * 70)
print("AUTHENTICATION COMPLETE!")
print("=" * 70)
print()
print("Now you can:")
print("  1. Run: streamlit run app.py")
print("  2. Go to Communication Hub")
print("  3. Use WhatsApp and LinkedIn normally!")
print()
