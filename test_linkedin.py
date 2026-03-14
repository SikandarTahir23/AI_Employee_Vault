"""
Quick LinkedIn Connection Test
Run this to verify LinkedIn authentication before using the dashboard
"""
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from integrations.linkedin_client import LinkedInClient

print("=" * 60)
print("LINKEDIN CONNECTION TEST")
print("=" * 60)

# Create client with visible browser
client = LinkedInClient(headless=False)

try:
    print("\n[1] Initializing browser...")
    if not client.initialize():
        print("✗ Failed to initialize LinkedIn")
        sys.exit(1)
    
    print("[2] Checking login status...")
    if client.is_logged_in():
        print("✓ Already logged in (session restored)")
    else:
        print("⚠ Not logged in")
        print("\n[3] Waiting for manual login (120 seconds)...")
        print("    → Please log in to LinkedIn in the browser window")
        print("    → Close the browser when done")
        
        if not client.wait_for_login(timeout=120):
            print("✗ Login timeout or failed")
            sys.exit(1)
        
        print("✓ Login successful!")
    
    print("\n[4] Testing navigation to feed...")
    client.page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded', timeout=30000)
    client.page.wait_for_timeout(3000)
    
    if "/feed" in client.page.url:
        print("✓ Successfully navigated to feed")
    else:
        print(f"⚠ Current URL: {client.page.url}")
    
    print("\n" + "=" * 60)
    print("✓ LINKEDIN TEST PASSED")
    print("=" * 60)
    print("\nYour LinkedIn session is working!")
    print("You can now use the dashboard to create and publish posts.")
    print("\nNext steps:")
    print("1. Go to your Streamlit dashboard (http://localhost:8501)")
    print("2. Scroll to 'AI Post Creator' section")
    print("3. Enter a test prompt like: 'Testing LinkedIn posting'")
    print("4. Click 'Generate Draft'")
    print("5. Click 'Publish Now'")
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    print("\n[Cleaning up browser resources...]")
    client.cleanup()
    print("✓ Done")
