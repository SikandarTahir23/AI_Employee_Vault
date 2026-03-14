"""Quick test to see if browser opens and stays open"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from integrations.linkedin_client import connect_linkedin, cleanup_persistent_linkedin

print("\n=== TESTING LINKEDIN CONNECTION ===")
print("Browser should open and STAY OPEN for login\n")

success, msg = connect_linkedin(headless=False, timeout=120)

print(f"\nResult: {msg}")

if success:
    print("\n✓ Login successful!")
    print("Keeping browser open for 30 seconds...")
    import time
    time.sleep(30)
    cleanup_persistent_linkedin()
    print("Done!")
else:
    print("\n✗ Failed")
    cleanup_persistent_linkedin()
