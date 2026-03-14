"""
WhatsApp Web Client Module for AI Automation Dashboard
Uses Playwright for browser automation with persistent sessions

Features:
- Persistent session storage (survives browser restarts)
- QR code login detection
- Multiple selector strategies for resilience
- Phone number validation
- Error handling with detailed logging
"""

import os
import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dotenv import load_dotenv
from playwright.async_api import async_playwright, BrowserContext, Page

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
WHATSAPP_URL = "https://web.whatsapp.com"
PROJECT_ROOT = Path(__file__).parent.parent
USER_DATA_DIR = PROJECT_ROOT / ".whatsapp_session"
DEFAULT_TIMEOUT = 60000  # 60 seconds


class WhatsAppClient:
    """
    WhatsApp Web automation client using Playwright
    
    Features:
    - Persistent session (login once, reuse across restarts)
    - QR code detection and login wait
    - Multiple selector strategies for resilience
    - Phone number validation
    """

    # Multiple selector strategies for message input
    MESSAGE_INPUT_SELECTORS = [
        'div[contenteditable="true"][data-tab="10"]',
        'div[contenteditable="true"][data-tab="6"]',
        'div[contenteditable="true"]',
        '[data-testid="compose-input"]',
        'footer div[contenteditable="true"]',
        'div.selectable-text[contenteditable="true"]',
        'div[role="textbox"]',
        'div._3Uu1_',  # Old selector fallback
    ]

    # Multiple selector strategies for send button
    SEND_BUTTON_SELECTORS = [
        'button[data-testid="compose-btn-send"]',
        'button[aria-label="Send"]',
        'button[aria-label="Send message"]',
        'div[data-testid="send-button"]',
        'svg[data-icon="send"]',
        'button._2Uces',  # Old selector fallback
    ]

    # QR code detection selectors
    QR_SELECTORS = [
        'div[data-ref]',
        'canvas',
        'img[alt="QR Code"]',
        '[data-testid="qrcode"]',
        'div[data-testid="qrcode"]',
    ]

    # Main interface selectors (logged in)
    MAIN_INTERFACE_SELECTORS = [
        '[data-testid="default-user"]',
        '[data-testid="chat-list"]',
        'div[data-testid="chat-list"]',
        '.DTThI',  # Chat list container class
    ]

    def __init__(self, headless: bool = False):
        """
        Initialize WhatsApp client

        Args:
            headless: Run browser in headless mode (False recommended for QR login)
        """
        self.headless = headless
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None
        self._is_logged_in = False
        self._initialized = False

    async def initialize(self) -> bool:
        """
        Initialize browser and load WhatsApp Web

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return self._is_logged_in

        try:
            logger.info("Initializing WhatsApp Web automation...")

            # Create user data directory for persistent session
            USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Session directory: {USER_DATA_DIR}")

            # Launch Playwright
            self._playwright = await async_playwright().start()

            # Launch browser with persistent context
            self.context = await self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=self.headless,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-features=IsolateOrigins,site-per-process'
                ],
                viewport={'width': 1280, 'height': 720},
                timeout=DEFAULT_TIMEOUT
            )

            self.page = self.context.pages[0]

            # Navigate to WhatsApp Web
            logger.info(f"Navigating to {WHATSAPP_URL}")
            await self.page.goto(WHATSAPP_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

            # Wait for page to load
            await self.page.wait_for_load_state('networkidle', timeout=DEFAULT_TIMEOUT)
            logger.info("WhatsApp Web loaded")

            # Check login status
            self._is_logged_in = await self._check_login_status()

            if self._is_logged_in:
                logger.info("✓ Already logged in (session restored)")
            else:
                logger.info("⚠ QR code login required")

            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            await self.cleanup()
            return False

    async def _check_login_status(self) -> bool:
        """
        Check if WhatsApp Web is logged in

        Returns:
            True if logged in, False if QR code is shown
        """
        try:
            # Wait a bit for page to stabilize
            await asyncio.sleep(2)

            # Try to find main interface first (logged in)
            for selector in self.MAIN_INTERFACE_SELECTORS:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    logger.debug(f"Found main interface: {selector}")
                    return True
                except:
                    continue

            # Check for QR code (not logged in)
            for selector in self.QR_SELECTORS:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        logger.debug(f"QR code detected: {selector}")
                        return False
                except:
                    continue

            # Fallback: check page title
            title = await self.page.title()
            if "WhatsApp" in title:
                logger.info("Could not detect QR, assuming logged in")
                return True

            return False

        except Exception as e:
            logger.warning(f"Error checking login status: {e}")
            return False

    async def wait_for_login(self, timeout: int = 60) -> bool:
        """
        Wait for user to scan QR code and login

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if login successful, False if timeout
        """
        logger.info("Waiting for QR code login...")
        logger.info("📱 Please scan the QR code with WhatsApp mobile app")

        start_time = time.time()
        check_interval = 2  # Check every 2 seconds

        while time.time() - start_time < timeout:
            await asyncio.sleep(check_interval)

            is_logged_in = await self._check_login_status()
            if is_logged_in:
                logger.info("✓ Login successful!")
                self._is_logged_in = True
                return True

            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0:
                logger.info(f"Still waiting for login... ({elapsed}s/{timeout}s)")

        logger.error("Login timeout - QR code not scanned")
        return False

    def validate_phone_number(self, phone_number: str) -> Tuple[bool, str]:
        """
        Validate phone number format

        Args:
            phone_number: Phone number to validate

        Returns:
            Tuple of (is_valid: bool, cleaned_number: str)
        """
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone_number)
        
        # Remove leading + or 00
        cleaned = re.sub(r'^(\+|00)', '', cleaned)
        
        # Check if all digits
        if not cleaned.isdigit():
            return False, "Phone number must contain only digits"
        
        # Check length (minimum 7 digits, maximum 15 with country code)
        if len(cleaned) < 7:
            return False, "Phone number too short"
        
        if len(cleaned) > 15:
            return False, "Phone number too long"
        
        return True, cleaned

    async def send_message(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Send a WhatsApp message to a phone number

        Args:
            phone_number: Phone number with country code (e.g., '+1234567890' or '1234567890')
            message: Message text to send

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        if not self._initialized:
            if not await self.initialize():
                return False, "Failed to initialize WhatsApp"

        if not self._is_logged_in:
            return False, "Not logged in. Please scan QR code first."

        # Validate phone number
        is_valid, cleaned_number = self.validate_phone_number(phone_number)
        if not is_valid:
            return False, f"Invalid phone number: {cleaned_number}"

        try:
            logger.info(f"Sending message to {cleaned_number}")

            # Navigate to chat using wa.me link
            chat_url = f"https://web.whatsapp.com/send?phone={cleaned_number}"
            logger.info(f"Navigating to: {chat_url}")

            await self.page.goto(chat_url, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
            await asyncio.sleep(3)  # Wait for chat to load

            # Check if "chat not found" or blocked
            error_selectors = [
                '[data-testid="error-title"]',
                'div[data-testid="chat-info-error"]',
                '[data-testid="contact-not-exist-title"]'
            ]

            for selector in error_selectors:
                try:
                    error_elem = await self.page.query_selector(selector)
                    if error_elem:
                        error_text = await error_elem.inner_text()
                        logger.error(f"WhatsApp error: {error_text}")
                        return False, f"Contact not found: {error_text}"
                except:
                    continue

            # Find message input
            message_input = await self._find_element_by_selectors(
                self.MESSAGE_INPUT_SELECTORS, "message input"
            )

            if not message_input:
                return False, "Could not find message input field"

            # Type the message
            logger.debug("Typing message...")
            await message_input.fill(message)
            await asyncio.sleep(0.5)

            # Find and click send button
            send_button = await self._find_element_by_selectors(
                self.SEND_BUTTON_SELECTORS, "send button"
            )

            if not send_button:
                return False, "Could not find send button"

            logger.debug("Clicking send button...")
            await send_button.click()
            await asyncio.sleep(1)

            logger.info(f"✓ Message sent to {cleaned_number}")
            return True, "Message sent successfully"

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False, str(e)

    async def _find_element_by_selectors(self, selectors: List[str], 
                                          element_name: str) -> Optional[Any]:
        """
        Find element using multiple selector strategies

        Args:
            selectors: List of CSS selectors to try
            element_name: Name of element for logging

        Returns:
            Playwright element or None
        """
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=3000)
                if element:
                    logger.debug(f"Found {element_name}: {selector}")
                    return element
            except:
                continue

        return None

    async def get_chat_list(self, max_chats: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recent chats

        Args:
            max_chats: Maximum number of chats to retrieve

        Returns:
            List of chat dictionaries
        """
        if not self._is_logged_in:
            return []

        try:
            chats = []

            # Wait for chat list
            await self.page.wait_for_selector('[data-testid="chat-list"]', timeout=5000)
            await asyncio.sleep(1)

            # Get chat elements
            chat_elements = await self.page.query_selector_all(
                'div[data-testid="chat-list"] div[role="row"]'
            )

            for i, chat in enumerate(chat_elements[:max_chats]):
                try:
                    name_elem = await chat.query_selector('span[title]')
                    name = await name_elem.get_attribute('title') if name_elem else 'Unknown'

                    chats.append({
                        'index': i,
                        'name': name
                    })
                except:
                    continue

            logger.info(f"Retrieved {len(chats)} chats")
            return chats

        except Exception as e:
            logger.error(f"Error getting chat list: {e}")
            return []

    async def is_logged_in(self) -> bool:
        """Check if logged in"""
        if not self._initialized:
            return False
        return self._is_logged_in

    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

        self.context = None
        self.page = None
        self._playwright = None
        self._is_logged_in = False
        self._initialized = False


# Global instance for reuse
_whatsapp_instance: Optional[WhatsAppClient] = None


def get_whatsapp_client(headless: bool = False) -> WhatsAppClient:
    """
    Get or create WhatsApp client instance

    Args:
        headless: Run browser in headless mode

    Returns:
        WhatsAppClient instance
    """
    global _whatsapp_instance
    if _whatsapp_instance is None:
        _whatsapp_instance = WhatsAppClient(headless=headless)
    return _whatsapp_instance


def reset_whatsapp_client():
    """Reset the global WhatsApp client instance"""
    global _whatsapp_instance
    if _whatsapp_instance:
        asyncio.create_task(_whatsapp_instance.cleanup())
    _whatsapp_instance = None


async def send_whatsapp_message(phone_number: str, message: str,
                                 headless: bool = False) -> Tuple[bool, str]:
    """
    Standalone function to send WhatsApp message

    Args:
        phone_number: Phone number with country code
        message: Message to send
        headless: Run browser in headless mode

    Returns:
        Tuple of (success, error_message)
    """
    client = WhatsAppClient(headless=headless)

    try:
        # Initialize
        if not await client.initialize():
            return False, "Failed to initialize WhatsApp Web"

        # Check if already logged in
        if not client._is_logged_in:
            logger.info("QR code login required")
            if not await client.wait_for_login(timeout=60):
                return False, "Login timeout - QR code not scanned"

        # Send message
        return await client.send_message(phone_number, message)

    finally:
        await client.cleanup()


if __name__ == '__main__':
    # Test the integration
    async def test():
        print("WhatsApp Web Automation Test")
        print("=" * 50)

        client = WhatsAppClient(headless=False)

        if await client.initialize():
            if not client._is_logged_in:
                print("\n📱 Please scan QR code to login...")
                if await client.wait_for_login(timeout=60):
                    print("\n✓ Login successful!")

                    # Test send message
                    test_number = input("Enter phone number (with country code): ")
                    test_message = input("Enter message: ")

                    success, msg = await client.send_message(test_number, test_message)
                    print(f"\nResult: {msg}")
                else:
                    print("\n✗ Login failed")
            else:
                print("\n✓ Already logged in")

                # Test send message
                test_number = input("Enter phone number (with country code): ")
                test_message = input("Enter message: ")

                success, msg = await client.send_message(test_number, test_message)
                print(f"\nResult: {msg}")

        await client.cleanup()

    asyncio.run(test())
