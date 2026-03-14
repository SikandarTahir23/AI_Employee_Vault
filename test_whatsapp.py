"""
Quick WhatsApp Connection Test
Run this to verify WhatsApp authentication before using the dashboard
"""
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

try:
    from integrations import connect_whatsapp, send_whatsapp_message, get_whatsapp_status
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure whatsapp_client is properly configured")
    sys.exit(1)

print("=" * 60)
print("WHATSAPP CONNECTION TEST")
print("=" * 60)

# Check current status
print("\n[1] Checking current WhatsApp status...")
status = get_whatsapp_status()
print(f"    Session exists: {status.get('session_exists', False)}")
print(f"    Logged in: {status.get('logged_in', False)}")
print(f"    Initialized: {status.get('initialized', False)}")

if status.get('logged_in'):
    print("\n✓ WhatsApp is already connected!")
else:
    print("\n⚠ WhatsApp not connected")
    print("\n[2] Connecting to WhatsApp...")
    print("    → A browser window will open")
    print("    → Scan the QR code with your WhatsApp mobile app")
    print("    → Go to: Linked Devices > Link a Device")
    print("    → Wait for confirmation")
    
    success, message = connect_whatsapp(headless=False, timeout=120)
    
    if not success:
        print(f"\n✗ Connection failed: {message}")
        sys.exit(1)
    
    print(f"\n✓ {message}")

# Test sending a message
print("\n" + "=" * 60)
print("TEST MESSAGE")
print("=" * 60)

# Use a default test number or ask user
print("\nTo test sending a message, you can:")
print("1. Enter a phone number now (with country code, e.g., +1234567890)")
print("2. Press Enter to skip the message test")

phone_number = input("\nEnter phone number (or press Enter to skip): ").strip()

if phone_number:
    test_message = "🤖 This is an automated test message from my AI Employee Vault dashboard!"
    
    print(f"\n[3] Sending test message to: {phone_number}")
    print(f"    Message: {test_message}")
    
    try:
        success, result = send_whatsapp_message(phone_number, test_message)
        
        if success:
            print("\n✓ Message sent successfully!")
            print(f"  Result: {result}")
        else:
            print(f"\n✗ Failed to send message: {result}")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    print("\n⊘ Skipped message test")

print("\n" + "=" * 60)
print("✓ WHATSAPP TEST COMPLETED")
print("=" * 60)
