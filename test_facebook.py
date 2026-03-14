"""Quick test for Facebook integration"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from integrations import post_to_facebook, validate_facebook_token, get_facebook_status

print("=" * 60)
print("Testing Facebook Integration")
print("=" * 60)

# Test 1: Get status
print("\n1. Facebook Status:")
status = get_facebook_status()
for key, value in status.items():
    print(f"   {key}: {value}")

# Test 2: Validate token
print("\n2. Validating Token:")
success, msg = validate_facebook_token()
if success:
    print(f"   ✓ {msg}")
else:
    print(f"   ✗ {msg}")

# Test 3: Test post
print("\n3. Test Post:")
test_message = f"Test post from AI Dashboard - {Path(__file__).parent.name}"
success, msg = post_to_facebook(
    message=test_message,
    link=None
)

if success:
    print(f"   ✓ Post successful: {msg}")
else:
    print(f"   ✗ Post failed: {msg}")

print("\n" + "=" * 60)
