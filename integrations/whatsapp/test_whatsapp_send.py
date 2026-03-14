"""
Test WhatsApp - Send a test message
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from whatsapp_client import send_whatsapp_message, cleanup_whatsapp

print("=" * 60)
print("WhatsApp Test - Send Message")
print("=" * 60)

# Get phone number
phone = input("\nEnter phone number (with country code, e.g., +92300...): ").strip()
if not phone:
    print("❌ No phone number entered")
    sys.exit(1)

# Get message
message = input("Enter test message: ").strip()
if not message:
    message = "This is a test message from AI Dashboard"

print(f"\nSending to: {phone}")
print(f"Message: {message}")
print("\nOpening browser...")

# Send message
success, result = send_whatsapp_message(phone, message, headless=False)

print("\n" + "=" * 60)
if success:
    print(f"✓ SUCCESS: {result}")
else:
    print(f"✗ FAILED: {result}")
print("=" * 60)

cleanup_whatsapp()
input("\nPress Enter to exit...")
