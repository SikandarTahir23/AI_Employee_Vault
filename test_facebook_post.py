"""
Test Facebook Posting
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from integrations import post_to_facebook_page

# Test content
test_content = """
🧪 Testing Facebook Post from AI Dashboard!

This is a test post to verify the Facebook integration is working correctly.

#AI #Automation #Test
"""

print("\n" + "=" * 60)
print("FACEBOOK POSTING TEST")
print("=" * 60)

print(f"\nPosting content:\n{test_content}")

print("\nPosting to Facebook...")

success, msg = post_to_facebook_page(test_content)

print(f"\nResult: {msg}")

if success:
    print("\n✓ Facebook post successful!")
else:
    print(f"\n✗ Facebook post failed: {msg}")

print("\n" + "=" * 60)
