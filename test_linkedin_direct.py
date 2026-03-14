"""
Direct LinkedIn Test - Shows Browser Window
Run this OUTSIDE of Streamlit
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_linkedin():
    from playwright.sync_api import sync_playwright
    
    print("=" * 60)
    print("LinkedIn Login Test")
    print("=" * 60)
    
    # Launch Playwright
    playwright = sync_playwright().start()
    
    # Launch browser VISIBLE
    browser = playwright.chromium.launch(
        headless=False,  # SHOW browser!
        args=[
            '--disable-gpu',
            '--no-sandbox',
            '--start-maximized'
        ]
    )
    
    context = browser.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()
    
    print("\n💼 Navigating to LinkedIn login...")
    page.goto("https://www.linkedin.com/login", wait_until='domcontentloaded')
    
    print("✅ Browser window is visible!")
    print("🔐 Log in to LinkedIn in the browser window")
    print("\n⏳ Waiting 120 seconds for login...")
    
    # Wait for login
    time.sleep(120)
    
    # Check if logged in
    if "/feed" in page.url or "linkedin.com/feed" in page.url:
        print("\n✅ Login successful!")
        print(f"   Current page: {page.url}")
    else:
        print(f"\n⚠️ Still on: {page.url}")
    
    print("\nClosing browser...")
    context.close()
    playwright.stop()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_linkedin()
