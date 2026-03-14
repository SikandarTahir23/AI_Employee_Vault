"""
LinkedIn Connection Launcher
Runs independently from Streamlit to handle LinkedIn login

This script:
1. Opens browser with persistent profile (headless=False for visibility)
2. Navigates to LinkedIn login
3. Waits for user to log in (up to 2 minutes)
4. Saves session cookies to persistent profile
5. Keeps browser open during the entire login process
6. Browser closes only after login completes or user closes it

Usage:
    python linkedin_launcher.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from integrations.linkedin_client import connect_linkedin, cleanup_persistent_linkedin, get_persistent_client

if __name__ == "__main__":
    print("=" * 60)
    print("LinkedIn Connection")
    print("=" * 60)

    try:
        # Connect to LinkedIn (opens browser, waits for login)
        print("\n1. Opening browser...")
        print("   IMPORTANT: Browser will stay open - please log in to LinkedIn")
        print("   After login, the browser will remain open for posting")

        success, msg = connect_linkedin(headless=False, timeout=120)

        # Write result to file for Streamlit to read
        result_file = project_root / ".linkedin_connect_result.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(f"{success}|{msg}")

        print(f"\n2. Result: {msg}")

        if success:
            print("   ✓ Login successful!")
            print("   ✓ Session saved to persistent profile")
            print("   Browser will remain open for posting.")
            print("\n   You can now post to LinkedIn from the Streamlit dashboard.")
            print("   Close the browser window when you're done.")
            
            # Keep browser open - wait for user to close it or press Enter
            print("\n   Press Enter to close browser and exit...")
            input()
        else:
            print("   ✗ Login failed or timed out")
            print("   Browser will close in 5 seconds...")
            time.sleep(5)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
        result_file = project_root / ".linkedin_connect_result.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(f"False|{e}")

    finally:
        # Only cleanup if explicitly exiting
        cleanup_persistent_linkedin()
        print("\nBrowser closed.")
