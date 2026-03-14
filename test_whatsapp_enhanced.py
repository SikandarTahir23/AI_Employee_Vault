"""
Test WhatsApp message with enhanced debugging and wait conditions.
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
USER_DATA_DIR = PROJECT_ROOT / ".whatsapp_session"

async def main():
    logger.info("=" * 60)
    logger.info("WHATSAPP MESSAGE TEST - ENHANCED")
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
        logger.info("Launching browser with persistent context...")
        playwright = await async_playwright().start()
        
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
            viewport={"width": 1280, "height": 720},
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Navigate to WhatsApp Web
        logger.info("Navigating to WhatsApp Web...")
        await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)  # Wait for page to stabilize
        
        # Check if logged in
        logger.info("Checking login status...")
        try:
            await page.wait_for_selector('div[data-testid="chat-list"]', timeout=5000)
            logger.info("✓ Already logged in!")
        except:
            logger.info("Waiting for QR scan (if needed)...")
            try:
                await page.wait_for_selector('div[data-testid="chat-list"]', timeout=60000)
                logger.info("✓ Login successful!")
            except:
                logger.error("Login timeout")
                return
        
        # Navigate to the contact using wa.me link
        logger.info(f"Navigating to chat with {CONTACT}...")
        clean_number = CONTACT.replace("+", "").replace("-", "").replace(" ", "")
        chat_url = f"https://web.whatsapp.com/send?phone={clean_number}"
        await page.goto(chat_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)  # Wait for chat to load
        
        # Check for "contact not found" error
        try:
            error_elem = await page.wait_for_selector(
                'div[data-testid="contact-not-exist-title"]',
                timeout=3000
            )
            if error_elem:
                logger.error("Contact not found on WhatsApp")
                return
        except:
            pass  # No error, contact exists
        
        # Find message input with multiple attempts
        logger.info("Looking for message input field...")
        message_input = None
        
        input_selectors = [
            'div[contenteditable="true"][data-tab="10"]',
            'div[contenteditable="true"][data-tab="6"]',
            'div[contenteditable="true"]',
            '[data-testid="compose-input"]',
            'footer div[contenteditable="true"]',
            'div[role="textbox"]',
        ]
        
        for selector in input_selectors:
            try:
                message_input = await page.wait_for_selector(selector, timeout=3000)
                if message_input:
                    logger.info(f"Found message input with selector: {selector}")
                    break
            except:
                continue
        
        if not message_input:
            logger.error("Could not find message input field")
            # Take screenshot for debugging
            await page.screenshot(path="debug_no_input.png")
            logger.info("Screenshot saved to debug_no_input.png")
            return
        
        # Type the message
        logger.info("Typing message...")
        await message_input.click()
        time.sleep(1)
        await message_input.fill(MESSAGE)
        time.sleep(1)
        
        # Find and click send button
        logger.info("Looking for send button...")
        send_button = None
        
        send_selectors = [
            'button[data-testid="compose-btn-send"]',
            'button[aria-label="Send"]',
            'button[aria-label="Send message"]',
            'div[data-testid="send-button"]',
        ]
        
        for selector in send_selectors:
            try:
                send_button = await page.wait_for_selector(selector, timeout=3000)
                if send_button:
                    logger.info(f"Found send button with selector: {selector}")
                    break
            except:
                continue
        
        if not send_button:
            logger.error("Could not find send button, trying Enter key...")
            await message_input.press("Enter")
        else:
            await send_button.click()
        
        time.sleep(2)
        
        logger.info("=" * 60)
        logger.info("✓ MESSAGE SENT SUCCESSFULLY!")
        logger.info(f"  Contact: {CONTACT}")
        logger.info(f"  Message: {MESSAGE}")
        logger.info("=" * 60)
        
        # Keep browser open for verification
        logger.info("Keeping browser open for 10 seconds to verify...")
        time.sleep(10)
        
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
