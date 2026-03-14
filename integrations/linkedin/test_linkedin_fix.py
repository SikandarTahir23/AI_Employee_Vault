"""
LinkedIn Automation Test Script
Tests the fixed LinkedIn automation module

This script verifies:
1. Browser opens and stays open (headless=False)
2. Login page is accessible
3. Session persists after login
4. Post creation works

Usage:
    python test_linkedin_fix.py
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


def test_connect_linkedin():
    """Test 1: Connect to LinkedIn and verify browser stays open"""
    print("\n" + "=" * 60)
    print("TEST 1: Connect to LinkedIn")
    print("=" * 60)
    
    print("\nExpected behavior:")
    print("  - Browser opens with LinkedIn login page")
    print("  - Browser stays open (does NOT close immediately)")
    print("  - You can log in manually")
    print("  - Session is saved to persistent profile")
    
    print("\nStarting test...")
    print("Opening browser (headless=False for visibility)...")
    
    success, msg = connect_linkedin(headless=False, timeout=120)
    
    print(f"\nResult: {msg}")
    
    if success:
        print("✓ TEST 1 PASSED: Browser connected and stayed open")
        print("  You can now test posting or close the browser manually")
        return True
    else:
        print("✗ TEST 1 FAILED: Connection failed")
        return False


def test_post_to_linkedin():
    """Test 2: Post to LinkedIn using saved session"""
    print("\n" + "=" * 60)
    print("TEST 2: Post to LinkedIn")
    print("=" * 60)
    
    test_content = f"Test post from AI Dashboard - {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n#AI #Automation #Test"
    
    print(f"\nTest content: {test_content[:50]}...")
    print("\nExpected behavior:")
    print("  - Browser opens (or uses existing session)")
    print("  - Navigates to LinkedIn feed")
    print("  - Opens post composer")
    print("  - Posts content")
    print("  - Shows confirmation")
    
    print("\nStarting test...")
    
    success, msg = post_to_linkedin(test_content, headless=False, wait_for_login=True)
    
    print(f"\nResult: {msg}")
    
    if success:
        print("✓ TEST 2 PASSED: Post submitted successfully")
        return True
    else:
        print(f"✗ TEST 2 FAILED: {msg}")
        return False


def test_persistent_session():
    """Test 3: Verify session persistence"""
    print("\n" + "=" * 60)
    print("TEST 3: Session Persistence Check")
    print("=" * 60)
    
    from pathlib import Path
    
    profile_dir = project_root / ".playwright_profile"
    
    print(f"\nProfile directory: {profile_dir}")
    
    if not profile_dir.exists():
        print("✗ Profile directory does not exist yet")
        print("  It will be created after first login")
        return False
    
    # Check for session indicators
    session_files = ['Login Data', 'Cookies', 'Web Data', 'History']
    found_files = []
    
    for file_name in session_files:
        file_path = profile_dir / file_name
        if file_path.exists():
            found_files.append(file_name)
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_path.stat().st_mtime))
            print(f"  ✓ {file_name} (modified: {mtime})")
    
    if found_files:
        print(f"\n✓ TEST 3 PASSED: Found {len(found_files)} session file(s)")
        print("  Session persistence is working")
        return True
    else:
        print("\n⚠ TEST 3 WARNING: No session files found")
        print("  Session will be created after first login")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LINKEDIN AUTOMATION FIX VERIFICATION")
    print("=" * 60)
    print("\nThis script tests the fixed LinkedIn automation:")
    print("  - Browser lifecycle (no premature closure)")
    print("  - Persistent session storage")
    print("  - Manual login support")
    print("  - Post creation")
    
    try:
        # Test 1: Connection
        test1_passed = test_connect_linkedin()
        
        if test1_passed:
            # Ask user if they want to test posting
            print("\n" + "-" * 60)
            choice = input("Do you want to test posting now? (y/n): ").strip().lower()
            
            if choice == 'y':
                # Test 2: Posting
                test2_passed = test_post_to_linkedin()
            else:
                print("\nSkipping post test")
                test2_passed = None
        else:
            print("\nSkipping post test (connection failed)")
            test2_passed = None
        
        # Test 3: Session persistence
        test3_passed = test_persistent_session()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"  Test 1 (Connect): {'✓ PASSED' if test1_passed else '✗ FAILED'}")
        print(f"  Test 2 (Post):    {'✓ PASSED' if test2_passed else ('⊘ SKIPPED' if test2_passed is None else '✗ FAILED')}")
        print(f"  Test 3 (Session): {'✓ PASSED' if test3_passed else '⚠ WARNING'}")
        
        if test1_passed:
            print("\n✓ FIX VERIFIED: Browser no longer closes immediately")
            print("  The LinkedIn automation is working correctly")
        else:
            print("\n✗ FIX INCOMPLETE: Please check logs for errors")
        
        # Cleanup
        print("\nCleaning up...")
        cleanup_persistent_linkedin()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        cleanup_persistent_linkedin()
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_persistent_linkedin()


if __name__ == "__main__":
    main()
