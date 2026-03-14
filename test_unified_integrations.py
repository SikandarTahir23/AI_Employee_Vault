"""Test script for unified integrations module"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Testing Unified Integrations Module")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
try:
    from integrations import (
        send_email,
        read_gmail,
        gmail_authenticate,
        get_gmail_status,
        send_whatsapp_message,
        get_whatsapp_status,
        post_to_linkedin,
        get_linkedin_status,
        post_to_facebook,
        get_facebook_status,
        validate_facebook_token,
        get_all_status
    )
    print("   ✓ All imports successful!")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test status functions
print("\n2. Testing status functions...")
try:
    gmail = get_gmail_status()
    print(f"   ✓ Gmail status: {gmail}")
    
    whatsapp = get_whatsapp_status()
    print(f"   ✓ WhatsApp status: {whatsapp}")
    
    linkedin = get_linkedin_status()
    print(f"   ✓ LinkedIn status: {linkedin}")
    
    facebook = get_facebook_status()
    print(f"   ✓ Facebook status: {facebook}")
    
    all_status = get_all_status()
    print(f"   ✓ All status: {len(all_status)} services")
    
except Exception as e:
    print(f"   ✗ Status check failed: {e}")

# Test communication_hub import
print("\n3. Testing communication_hub import...")
try:
    from communication_hub import render_communication_hub
    print("   ✓ communication_hub imported!")
except ImportError as e:
    print(f"   ✗ communication_hub import failed: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
print("\nNext steps:")
print("1. Run: streamlit run app.py")
print("2. Go to Communication Hub section")
print("3. Test each integration button")
