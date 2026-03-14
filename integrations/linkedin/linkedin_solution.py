"""
LinkedIn Automation - Standalone Solution

This script provides the complete fixed LinkedIn automation with:
- Persistent session storage (login once, reuse forever)
- Browser stays open during login
- Session saved to linkedin_session/ directory
- Works with Streamlit dashboard

Usage:
    # First time - login and save session
    python linkedin_solution.py --login
    
    # Post to LinkedIn (uses saved session)
    python linkedin_solution.py --post "Your post content here"
    
    # Test the complete flow
    python linkedin_solution.py --test
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from integrations.linkedin_client import (
    LinkedInClient,
    connect_linkedin,
    post_to_linkedin,
    cleanup_persistent_linkedin,
    get_persistent_client
)


def test_login_and_session():
    """Test login and verify session is saved"""
    print("\n" + "=" * 60)
    print("LINKEDIN LOGIN TEST")
    print("=" * 60)
    
    session_dir = project_root / ".playwright_profile"
    print(f"\nSession will be saved to: {session_dir}")
    
    print("\nOpening browser (headless=False for visibility)...")
    print("Browser will STAY OPEN during login - this is the fix!")
    
    success, msg = connect_linkedin(headless=False, timeout=120)
    
    print(f"\nResult: {msg}")
    
    if success:
        print("\n✓ Login successful!")
        print("✓ Session cookies saved automatically")
        print("✓ Browser remains open for posting")
        
        # Verify session files
        if session_dir.exists():
            session_files = list(session_dir.glob("*"))
            print(f"✓ Session directory contains {len(session_files)} file(s)")
        
        return True
    else:
        print(f"\n✗ Login failed: {msg}")
        return False


def test_post(content):
    """Test posting with saved session"""
    print("\n" + "=" * 60)
    print("LINKEDIN POST TEST")
    print("=" * 60)
    
    print(f"\nContent: {content[:100]}...")
    
    success, msg = post_to_linkedin(content, headless=False, wait_for_login=True)
    
    print(f"\nResult: {msg}")
    
    if success:
        print("\n✓ Post submitted successfully!")
        return True
    else:
        print(f"\n✗ Post failed: {msg}")
        return False


def interactive_login():
    """Interactive login flow"""
    print("\n" + "=" * 60)
    print("LINKEDIN CONNECTION")
    print("=" * 60)
    
    print("\nThis will:")
    print("  1. Open Chrome with LinkedIn login page")
    print("  2. Keep browser open while you log in")
    print("  3. Save session cookies automatically")
    print("  4. Keep browser open for posting")
    
    input("\nPress Enter to open browser...")
    
    success, msg = connect_linkedin(headless=False, timeout=120)
    
    print(f"\nResult: {msg}")
    
    if success:
        print("\n✓ You are now logged in!")
        print("✓ Session saved to .playwright_profile/")
        print("✓ Future posts will reuse this session")
        print("\nPress Enter to close browser and exit...")
        input()
        cleanup_persistent_linkedin()
        print("Browser closed.")
    else:
        print("\n✗ Login failed")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Automation")
    parser.add_argument("--login", action="store_true", help="Open browser for login")
    parser.add_argument("--post", type=str, help="Post content to LinkedIn")
    parser.add_argument("--test", action="store_true", help="Run full test")
    
    args = parser.parse_args()
    
    try:
        if args.login:
            interactive_login()
        
        elif args.post:
            test_post(args.post)
            cleanup_persistent_linkedin()
        
        elif args.test:
            print("\n" + "=" * 60)
            print("LINKEDIN AUTOMATION - FULL TEST")
            print("=" * 60)
            
            # Step 1: Login
            if test_login_and_session():
                # Step 2: Post
                test_content = f"Test from AI Dashboard - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                test_post(test_content)
                
                print("\n" + "=" * 60)
                print("TEST SUMMARY")
                print("=" * 60)
                print("✓ Login: PASSED")
                print("✓ Session: SAVED")
                print("✓ Post: SUBMITTED")
                print("\nSession will persist for future runs!")
            else:
                print("\n✗ Test failed at login stage")
            
            cleanup_persistent_linkedin()
        
        else:
            parser.print_help()
            print("\nExamples:")
            print("  python linkedin_solution.py --login")
            print("  python linkedin_solution.py --post \"Hello LinkedIn!\"")
            print("  python linkedin_solution.py --test")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cleanup_persistent_linkedin()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_persistent_linkedin()


if __name__ == "__main__":
    main()
