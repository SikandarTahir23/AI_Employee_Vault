"""
WhatsApp QR Code Scanner
Opens WhatsApp Web and waits for you to scan the QR code
"""
import sys
from pathlib import Path
import time

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

try:
    from integrations import connect_whatsapp, get_whatsapp_status
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

print("=" * 60)
print("WHATSAPP QR CODE SCANNER")
print("=" * 60)

print("\n📱 This will open a browser window for WhatsApp Web")
print("\nSteps to link your WhatsApp:")
print("1. A browser window will open showing WhatsApp Web")
print("2. On your phone, open WhatsApp")
print("3. Go to: Settings > Linked Devices (or ⋮ > Linked Devices)")
print("4. Tap 'Link a Device'")
print("5. Scan the QR code shown in the browser")
print("6. Wait for confirmation")
print("\n⚠️  Keep the browser window open until scanning is complete")
print("⚠️  Don't close the browser after scanning - just leave it open")

input("\nPress Enter to open WhatsApp Web...")

print("\n[Opening browser...]")
success, message = connect_whatsapp(headless=False, timeout=180)

if success:
    print(f"\n✓ {message}")
    print("\n✓ WhatsApp is now linked!")
    print("\nYour session is saved. You can now use the dashboard to send messages.")
else:
    print(f"\n✗ Connection failed: {message}")
    print("Try again or check if WhatsApp is accessible on your phone.")

print("\n" + "=" * 60)
