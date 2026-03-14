"""
Test WhatsApp message using the correct session directory.
"""

import asyncio
import logging
import time
from pathlib import Path
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test contact and message
CONTACT = "+923162063441"
MESSAGE = "Test message from AI dashboard"
PROJECT_ROOT = Path(__file__).parent

# Use the CORRECT session directory (without dot)
USER_DATA_DIR = PROJECT_ROOT / "whatsapp_session"

async def main():
    logger.info("=" * 60)
    logger.info("WHATSAPP MESSAGE TEST")
    logger.info("=" * 60)
    
    logger.info(f"Session directory: {USER_DATA_DIR}")
    logger.info(f"Contact: {CONTACT}")
    logger.info(f"Message: {MESSAGE}")
    logger.info("-" * 60)
    
    playwright = None
    context = None
    page = None
    
    try:
        # Launch browser with persistent context
        logger.info("Launching browser...")
        playwright = await async_playwright().start()
        
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
            viewport={"width": 1280, "height": 720},
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Navigate to WhatsApp Web
        logger.info("Navigating to WhatsApp Web...")
        await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        
        # Check if logged in by looking for chat list
        logger.info("Checking if logged in...")
        is_logged_in = False
        
        try:
            await page.wait_for_selector('div[data-testid="chat-list"]', timeout=5000)
            is_logged_in = True
            logger.info("✓ Already logged in!")
        except:
            pass
        
        if not is_logged_in:
            logger.info("⚠ Not logged in - waiting for QR scan...")
            logger.info("Please scan the QR code with your phone.")
            
            # Wait for login (up to 120 seconds)
            start_time = time.time()
            timeout = 120
            
            while time.time() - start_time < timeout:
                try:
                    await page.wait_for_selector('div[data-testid="chat-list"]', timeout=3000)
                    is_logged_in = True
                    logger.info("✓ Login successful!")
                    break
                except:
                    elapsed = int(time.time() - start_time)
                    if elapsed % 15 == 0:
                        logger.info(f"Still waiting... ({elapsed}s/{timeout}s)")
                    time.sleep(2)
            
            if not is_logged_in:
                logger.error("Login timeout!")
                return
        
        # Navigate to the contact
        logger.info(f"Opening chat with {CONTACT}...")
        clean_number = CONTACT.replace("+", "").replace("-", "").replace(" ", "")
        chat_url = f"https://web.whatsapp.com/send?phone={clean_number}"
        await page.goto(chat_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        
        # Check for errors
        try:
            error_elem = await page.query_selector('div[data-testid="contact-not-exist-title"]')
            if error_elem:
                logger.error("✗ Contact not found on WhatsApp")
                return
        except:
            pass
        
        # Find message input
        logger.info("Finding message input...")
        message_input = None
        input_selectors = [
            'div[contenteditable="true"][data-tab="10"]',
            'div[contenteditable="true"][data-tab="6"]',
            'div[contenteditable="true"]',
            'footer div[contenteditable="true"]',
        ]
        
        for selector in input_selectors:
            try:
                message_input = await page.wait_for_selector(selector, timeout=3000)
                if message_input:
                    logger.info(f"✓ Found input: {selector}")
                    break
            except:
                continue
        
        if not message_input:
            logger.error("✗ Could not find message input")
            return
        
        # Type and send message
        logger.info("Typing message...")
        await message_input.click()
        time.sleep(1)
        await message_input.fill(MESSAGE)
        time.sleep(1)
        
        # Try send button first, then Enter key
        send_button = None
        try:
            send_button = await page.wait_for_selector('button[aria-label="Send"]', timeout=3000)
        except:
            pass
        
        if send_button:
            logger.info("Clicking send button...")
            await send_button.click()
        else:
            logger.info("Pressing Enter to send...")
            await message_input.press("Enter")
        
        time.sleep(2)
        
        logger.info("=" * 60)
        logger.info("✓ MESSAGE SENT SUCCESSFULLY!")
        logger.info(f"  Contact: {CONTACT}")
        logger.info(f"  Message: {MESSAGE}")
        logger.info("=" * 60)
        
        # Keep browser open for verification
        logger.info("Browser will stay open for 15 seconds to verify...")
        time.sleep(15)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        if context:
            await context.close()
        if playwright:
            await playwright.stop()
        logger.info("Done.")

if __name__ == "__main__":
    asyncio.run(main())
