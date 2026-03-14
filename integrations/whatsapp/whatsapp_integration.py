"""
WhatsApp Web Integration Module for AI Automation Dashboard
Uses Playwright for browser automation with persistent sessions
"""

import os
import asyncio
import logging
from typing import Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WHATSAPP_URL = "https://web.whatsapp.com"
USER_DATA_DIR = Path(__file__).parent / ".whatsapp_session"
DEFAULT_TIMEOUT = 60000  # 60 seconds


class WhatsAppAutomation:
    """
    WhatsApp Web automation using Playwright with persistent sessions
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize WhatsApp automation
        
        Args:
            headless: Run browser in headless mode (False recommended for QR login)
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None
        self._is_logged_in = False
        
    async def initialize(self) -> bool:
        """
        Initialize browser and load WhatsApp Web
        
        Returns:
            True if initialization successful, False otherwise
        """
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
                    '--disable-web-security',
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
            
            # Check for QR code element (not logged in)
            qr_selectors = [
                'div[data-ref]',
                'canvas',
                'img[alt="QR Code"]',
                '[data-testid="qrcode"]',
                'div[data-testid="qrcode"]'
            ]
            
            # Check for main chat interface (logged in)
            main_selectors = [
                '[data-testid="default-user"]',
                '[data-testid="chat-list"]',
                'div[data-testid="chat-list"]',
                '.DTThI'  # Chat list container class
            ]
            
            # Try to find main interface first
            for selector in main_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    logger.debug(f"Found main interface: {selector}")
                    return True
                except:
                    continue
            
            # Check for QR code
            for selector in qr_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        logger.debug(f"QR code detected: {selector}")
                        return False
                except:
                    continue
            
            # Fallback: check page title or URL
            title = await self.page.title()
            if "WhatsApp" in title:
                # Assume logged in if we can't detect QR
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
    
    async def send_message(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Send a WhatsApp message to a phone number
        
        Args:
            phone_number: Phone number with country code (e.g., '+1234567890')
            message: Message text to send
        
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        if not self._is_logged_in:
            return False, "Not logged in. Please scan QR code first."
        
        try:
            logger.info(f"Sending message to {phone_number}")
            
            # Clean phone number (remove +, spaces, dashes)
            clean_number = ''.join(c for c in phone_number if c.isdigit())
            if not clean_number:
                return False, "Invalid phone number"
            
            # Navigate to chat using wa.me link
            chat_url = f"https://web.whatsapp.com/send?phone={clean_number}"
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
            
            # Wait for message input box with multiple selector strategies
            message_input = await self._find_message_input()
            
            if not message_input:
                logger.error("Could not find message input field")
                return False, "Could not find message input field"
            
            # Type the message
            logger.debug("Typing message...")
            await message_input.fill(message)
            await asyncio.sleep(0.5)
            
            # Find and click send button
            send_button = await self._find_send_button()
            
            if not send_button:
                logger.error("Could not find send button")
                return False, "Could not find send button"
            
            logger.debug("Clicking send button...")
            await send_button.click()
            await asyncio.sleep(1)
            
            logger.info(f"✓ Message sent to {phone_number}")
            return True, "Message sent successfully"
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False, str(e)
    
    async def _find_message_input(self) -> Optional:
        """
        Find the message input field using multiple strategies
        
        Returns:
            Playwright element or None
        """
        selectors = [
            'div[contenteditable="true"][data-tab="10"]',
            'div[contenteditable="true"][data-tab="6"]',
            'div[contenteditable="true"]',
            '[data-testid="compose-input"]',
            'footer div[contenteditable="true"]',
            'div.selectable-text[contenteditable="true"]',
            'div._3Uu1_',  # Old selector
            'div[role="textbox"]'
        ]
        
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=3000)
                if element:
                    logger.debug(f"Found message input: {selector}")
                    return element
            except:
                continue
        
        return None
    
    async def _find_send_button(self) -> Optional:
        """
        Find the send button using multiple strategies
        
        Returns:
            Playwright element or None
        """
        selectors = [
            'button[data-testid="compose-btn-send"]',
            'button[aria-label="Send"]',
            'div[data-testid="send-button"]',
            'button._2Uces',  # Old selector
            'svg[data-icon="send"]',
            'button[aria-label="Send message"]'
        ]
        
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=3000)
                if element:
                    logger.debug(f"Found send button: {selector}")
                    return element
            except:
                continue
        
        return None
    
    async def get_chat_list(self, max_chats: int = 10) -> list:
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
        
        self.browser = None
        self.context = None
        self.page = None
        self._is_logged_in = False


# Global instance for Streamlit session state
_whatsapp_instance: Optional[WhatsAppAutomation] = None


def get_whatsapp_instance(headless: bool = False) -> WhatsAppAutomation:
    """
    Get or create WhatsApp automation instance
    
    Args:
        headless: Run browser in headless mode
    
    Returns:
        WhatsAppAutomation instance
    """
    global _whatsapp_instance
    
    if _whatsapp_instance is None:
        _whatsapp_instance = WhatsAppAutomation(headless=headless)
    
    return _whatsapp_instance


def reset_whatsapp_instance():
    """Reset the global WhatsApp instance"""
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
    automation = WhatsAppAutomation(headless=headless)
    
    try:
        # Initialize
        if not await automation.initialize():
            return False, "Failed to initialize WhatsApp Web"
        
        # Check if already logged in
        if not automation._is_logged_in:
            logger.info("QR code login required")
            if not await automation.wait_for_login(timeout=60):
                return False, "Login timeout - QR code not scanned"
        
        # Send message
        return await automation.send_message(phone_number, message)
        
    finally:
        await automation.cleanup()


if __name__ == '__main__':
    # Test the integration
    async def test():
        print("WhatsApp Web Automation Test")
        print("=" * 50)
        
        automation = WhatsAppAutomation(headless=False)
        
        if await automation.initialize():
            if not automation._is_logged_in:
                print("\n📱 Please scan QR code to login...")
                if await automation.wait_for_login(timeout=60):
                    print("\n✓ Login successful!")
                    
                    # Test send message
                    test_number = input("Enter phone number (with country code): ")
                    test_message = input("Enter message: ")
                    
                    success, msg = await automation.send_message(test_number, test_message)
                    print(f"\nResult: {msg}")
                else:
                    print("\n✗ Login failed")
            else:
                print("\n✓ Already logged in")
                
                # Test send message
                test_number = input("Enter phone number (with country code): ")
                test_message = input("Enter message: ")
                
                success, msg = await automation.send_message(test_number, test_message)
                print(f"\nResult: {msg}")
        
        await automation.cleanup()
    
    asyncio.run(test())
