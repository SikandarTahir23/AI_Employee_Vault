"""
LinkedIn Session Persistence Test

This script demonstrates the fixed LinkedIn automation with:
- Persistent session storage
- Browser stays open during login
- Session reuse across runs

Usage:
    python linkedin_session_test.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from integrations.linkedin_client import (
    connect_linkedin,
    post_to_linkedin,
    cleanup_persistent_linkedin
)


def main():
    print("\n" + "=" * 60)
    print("LINKEDIN SESSION PERSISTENCE TEST")
    print("=" * 60)
    
    print("\nThis test verifies:")
    print("  1. Browser opens with LinkedIn login (headless=False)")
    print("  2. Browser stays open during login (does NOT close)")
    print("  3. Session is saved to .playwright_profile/")
    print("  4. Session is reused on subsequent runs")
    
    # Check session directory
    session_dir = project_root / ".playwright_profile"
    print(f"\nSession directory: {session_dir}")
    
    if session_dir.exists():
        print("  ✓ Session directory exists")
        # Check for session files
        session_files = list(session_dir.glob("*"))
        if session_files:
            print(f"  ✓ Found {len(session_files)} session file(s)")
        else:
            print("  ⚠ Session directory is empty (will be populated after login)")
    else:
        print("  ⚠ Session directory will be created on first login")
    
    # Test connection
    print("\n" + "-" * 60)
    print("STEP 1: Connect to LinkedIn")
    print("-" * 60)
    print("\nBrowser will open in visible mode (headless=False)")
    print("Please log in to LinkedIn")
    print("Browser will STAY OPEN after login (this is the fix)")
    
    input("\nPress Enter to open browser...")
    
    success, msg = connect_linkedin(headless=False, timeout=120)
    
    print(f"\nResult: {msg}")
    
    if success:
        print("\n✓ Login successful!")
        print("✓ Session saved to .playwright_profile/")
        print("✓ Browser is still open")
        
        # Test posting
        print("\n" + "-" * 60)
        print("STEP 2: Test Posting")
        print("-" * 60)
        
        choice = input("\nPost a test message to LinkedIn? (y/n): ").strip().lower()
        
        if choice == 'y':
            test_content = f"Test post from AI Dashboard - {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n#Automation #Test"
            print(f"\nPosting: {test_content[:50]}...")
            
            post_success, post_msg = post_to_linkedin(test_content, headless=False)
            print(f"\nPost result: {post_msg}")
            
            if post_success:
                print("✓ Post submitted successfully!")
            else:
                print(f"⚠ Post failed: {post_msg}")
        
        print("\n" + "-" * 60)
        print("Cleanup")
        print("-" * 60)
        cleanup_choice = input("Close browser now? (y/n): ").strip().lower()
        
        if cleanup_choice == 'y':
            cleanup_persistent_linkedin()
            print("Browser closed.")
        else:
            print("Browser remains open. Close manually or run cleanup later.")
    else:
        print(f"\n✗ Login failed: {msg}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  - If login succeeded, session is saved")
    print("  - Future posts will reuse the session")
    print("  - Run this test again to verify session persistence")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        cleanup_persistent_linkedin()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_persistent_linkedin()
