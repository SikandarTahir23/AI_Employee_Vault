"""
Send a test message using existing WhatsApp session.
"""

import logging
from whatsapp_automation import WhatsAppAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Contact and message
CONTACT = "+923162063441"
MESSAGE = "Test message from AI dashboard"

def main():
    whatsapp = WhatsAppAutomation(headless=False)
    
    try:
        logger.info("=" * 50)
        logger.info("WhatsApp Test Message Sender")
        logger.info("=" * 50)
        logger.info(f"Target contact: {CONTACT}")
        logger.info(f"Message: {MESSAGE}")
        logger.info("=" * 50)
        
        # Connect using existing session (wait up to 120 seconds for QR scan)
        logger.info("Connecting to WhatsApp Web...")
        logger.info("If QR code appears, please scan it with your WhatsApp mobile app.")
        
        # Manual connection with extended timeout
        from playwright.sync_api import sync_playwright
        from whatsapp_automation import SESSION_DIR
        import time
        
        playwright = sync_playwright().start()
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        whatsapp.context = context
        whatsapp.page = context.pages[0]
        whatsapp.page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
        
        # Check if already logged in, otherwise wait for QR scan
        if not whatsapp._is_logged_in():
            logger.info("Waiting for QR code scan (up to 120 seconds)...")
            if not whatsapp._wait_for_login(timeout=120):
                logger.error("Login timeout. Please try again.")
                whatsapp.close()
                return
        
        logger.info("WhatsApp Web loaded successfully!")
        
        logger.info("Successfully connected to WhatsApp Web!")
        
        # Send the test message
        logger.info(f"Sending message to {CONTACT}...")
        success = whatsapp.send_whatsapp_message(CONTACT, MESSAGE)
        
        if success:
            logger.info("=" * 50)
            logger.info("✓ MESSAGE SENT SUCCESSFULLY!")
            logger.info(f"  Contact: {CONTACT}")
            logger.info(f"  Message: {MESSAGE}")
            logger.info("=" * 50)
        else:
            logger.error("✗ Failed to send message.")
        
        # Keep browser open briefly to verify
        logger.info("Keeping browser open for 10 seconds to verify...")
        whatsapp.keep_alive(duration=10)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
    finally:
        whatsapp.close()
        logger.info("Done.")

if __name__ == "__main__":
    main()
