
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from meta_automation import MetaAutomation
from whatsapp_integration import check_whatsapp_login, send_whatsapp_message, init_whatsapp_login

# Load environment variables
load_dotenv()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def test_facebook():
    print("\n" + "="*60)
    print("  FACEBOOK POSTING TEST - SIKANDAR TAHIR")
    print("="*60)
    
    try:
        meta = MetaAutomation()
        
        # Check if credentials are loaded
        if not meta.access_token or not meta.fb_page_id:
            print("❌ ERROR: META_ACCESS_TOKEN or FB_PAGE_ID not found in .env")
            return False

        print(f"✅ Credentials loaded for Page ID: {meta.fb_page_id}")
        
        test_message = f"Test Post from Sikandar Tahir's AI Dashboard - {os.urandom(4).hex()}"
        print(f"📝 Attempting to post: {test_message}")
        
        result = meta.post_to_facebook(message=test_message)
        
        if result.get("success"):
            print("\n✅ SUCCESS!")
            print(f"🔗 Post ID: {result.get('post_id')}")
            print(f"🔗 Post URL: {result.get('post_url')}")
            print("📂 Logged to Obsidian: Yes")
            return True
        else:
            print(f"\n❌ FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_whatsapp():
    print("\n" + "="*60)
    print("  WHATSAPP POSTING TEST - SIKANDAR TAHIR")
    print("="*60)
    
    # Check login status
    print("\n[1] Checking login status...")
    is_logged = check_whatsapp_login()

    if not is_logged:
        print("⚠️  NOT LOGGED IN")
        print("\nTo login:")
        print("1. Scan QR code with your phone in the browser that will open.")
        
        response = input("\nDo you want to open login browser now? (y/n): ").strip().lower()
        if response == 'y':
            print("\nOpening browser for QR scan...")
            result = init_whatsapp_login()
            print(result)
            
            # Re-check
            print("\nRe-checking login status...")
            is_logged = check_whatsapp_login()
            if is_logged:
                print("✅ Login successful!")
            else:
                print("⚠️  Still not logged in. Please try again.")
                return False
        else:
            print("WhatsApp test skipped (not logged in).")
            return False

    # Send a test message
    print("\n[2] Send a test message")
    print("\nEnter test contact (name or phone with country code):")
    print("Example: +923001234567 or 'Hamza Naeem'")
    contact = input("Contact: ").strip()
    
    if contact:
        message = "🤖 Sikandar Tahir Agency - WhatsApp Automation Test\n\nThis is a test message from your AI Employee Vault.\n\nIf you receive this, the WhatsApp automation is working correctly!"
        
        print(f"\nSending to: {contact}")
        print(f"Message:\n{message}\n")
        
        confirm = input("Send this message? (y/n): ").strip().lower()
        
        if confirm == 'y':
            def progress_cb(msg):
                print(f"  → {msg}")
            
            result = send_whatsapp_message(contact, message, progress_callback=progress_cb)
            
            if result["success"]:
                print("\n✅ TEST PASSED: Message sent successfully!")
                return True
            else:
                print("\n❌ TEST FAILED")
                print(f"Error: {result['error']}")
                return False
        else:
            print("Test cancelled by user")
            return False
    else:
        print("No contact entered, skipping send test")
        return False

def main():
    while True:
        # os.system('cls' if os.name == 'nt' else 'clear') # Disabling clear for tool output
        print("="*60)
        print("  SIKANDAR TAHIR - SOCIAL POSTING TEST COMMANDER")
        print("="*60)
        print("1. Test Facebook Posting")
        print("2. Test WhatsApp Posting")
        print("3. Test Both (FB then WhatsApp)")
        print("4. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            test_facebook()
            input("\nPress Enter to return to menu...")
        elif choice == '2':
            test_whatsapp()
            input("\nPress Enter to return to menu...")
        elif choice == '3':
            fb_ok = test_facebook()
            wa_ok = test_whatsapp()
            print("\n" + "="*60)
            print(f"SUMMARY: FB: {'✅' if fb_ok else '❌'} | WhatsApp: {'✅' if wa_ok else '❌'}")
            input("\nPress Enter to return to menu...")
        elif choice == '4':
            print("\nGoodbye, Sikandar!")
            break
        else:
            print("\nInvalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
