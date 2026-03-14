"""
WhatsApp Web Automation using Playwright
- Persistent session storage
- QR code login support
- Contact search and message sending
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Page, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Session directory for persistent storage
SESSION_DIR = Path(__file__).parent / "whatsapp_session"


class WhatsAppAutomation:
    """WhatsApp Web automation with persistent session support."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def connect_whatsapp(self) -> bool:
        """
        Connect to WhatsApp Web.
        
        - Opens WhatsApp Web in a browser
        - Shows QR code for login if not already authenticated
        - Detects successful login
        - Saves session persistently
        
        Returns:
            bool: True if login successful, False otherwise
        """
        logger.info("Initializing Playwright...")
        self.playwright = sync_playwright().start()
        
        # Create persistent context to save session
        logger.info(f"Creating persistent browser context in: {SESSION_DIR}")
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        self.page = self.context.pages[0]
        
        # Navigate to WhatsApp Web
        logger.info("Navigating to WhatsApp Web...")
        self.page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
        
        # Check if already logged in
        if self._is_logged_in():
            logger.info("Already logged in! Session loaded from persistent storage.")
            return True
        
        # Wait for QR code and login
        logger.info("Waiting for QR code scan...")
        logger.info("Please scan the QR code with your WhatsApp mobile app.")
        
        # Wait for login (max 60 seconds)
        login_success = self._wait_for_login(timeout=60)
        
        if login_success:
            logger.info("Login successful! Session saved.")
            # Give time for chat list to load
            time.sleep(2)
            return True
        else:
            logger.error("Login timeout. QR code not scanned in time.")
            return False

    def _is_logged_in(self) -> bool:
        """Check if user is already logged in by looking for chat elements."""
        try:
            # Look for the main chat panel or settings menu
            self.page.wait_for_selector(
                'div[data-testid="default-user"]',
                timeout=3000
            )
            return False
        except:
            # If default-user (welcome screen) is not found, might be logged in
            try:
                self.page.wait_for_selector(
                    'div[data-testid="chat-list"]',
                    timeout=3000
                )
                return True
            except:
                pass
            try:
                # Check for settings menu (logged in indicator)
                self.page.wait_for_selector(
                    'div[role="button"][aria-label="Settings"]',
                    timeout=3000
                )
                return True
            except:
                return False

    def _wait_for_login(self, timeout: int = 60) -> bool:
        """
        Wait for user to scan QR code and login.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if login detected, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self._is_logged_in():
                return True
            
            # Check if QR code is displayed
            try:
                self.page.wait_for_selector(
                    'canvas',
                    timeout=2000
                )
                logger.info("QR code is displayed. Waiting for scan...")
            except:
                pass
            
            time.sleep(2)
        
        return False

    def send_whatsapp_message(self, contact_name: str, message: str) -> bool:
        """
        Send a message to a contact.
        
        Args:
            contact_name: Name or phone number of the contact
            message: Message to send
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.page:
            logger.error("Not connected to WhatsApp. Call connect_whatsapp() first.")
            return False
        
        logger.info(f"Searching for contact: {contact_name}")
        
        # Click on search box
        try:
            search_box = self.page.wait_for_selector(
                'div[contenteditable="true"][data-tab="3"]',
                timeout=10000
            )
            search_box.click()
            time.sleep(1)
            
            # Type contact name
            search_box.fill(contact_name)
            time.sleep(2)
            
            # Wait for search results and click on the first match
            logger.info("Waiting for search results...")
            
            # Look for contact in search results
            contact_found = self._select_contact_from_search(contact_name)
            
            if not contact_found:
                logger.error(f"Contact '{contact_name}' not found.")
                return False
            
            # Wait for chat to load
            time.sleep(2)
            
            # Type and send message
            logger.info(f"Sending message to {contact_name}...")
            self._type_and_send_message(message)
            
            logger.info("Message sent successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False

    def _select_contact_from_search(self, contact_name: str) -> bool:
        """
        Select contact from search results.
        
        Args:
            contact_name: Name of contact to select
            
        Returns:
            bool: True if contact selected, False otherwise
        """
        try:
            # Wait for search results to appear
            time.sleep(1)
            
            # Click on the first search result (contact)
            contact_selector = 'div[role="button"]:has-text("{}")'.format(contact_name)
            
            # Try multiple selectors for contact results
            selectors_to_try = [
                f'span:has-text("{contact_name}")',
                f'div:has-text("{contact_name}")',
                'div[role="button"] >> nth=0',
            ]
            
            for selector in selectors_to_try:
                try:
                    contact = self.page.wait_for_selector(selector, timeout=3000)
                    contact.click()
                    logger.info(f"Contact '{contact_name}' selected.")
                    return True
                except:
                    continue
            
            # Fallback: click first result
            first_result = self.page.wait_for_selector(
                'div[role="button"] >> nth=0',
                timeout=5000
            )
            first_result.click()
            logger.info("First search result selected.")
            return True
            
        except Exception as e:
            logger.error(f"Could not select contact: {str(e)}")
            return False

    def _type_and_send_message(self, message: str) -> None:
        """
        Type message in chat input and send.
        
        Args:
            message: Message text to send
        """
        # Find message input box
        input_box = self.page.wait_for_selector(
            'div[contenteditable="true"][data-tab="10"]',
            timeout=10000
        )
        
        # Clear any existing text and type new message
        input_box.click()
        time.sleep(0.5)
        input_box.fill(message)
        time.sleep(0.5)
        
        # Press Enter to send
        input_box.press("Enter")
        
        # Wait for message to be sent
        time.sleep(1)

    def keep_alive(self, duration: int = 300) -> None:
        """
        Keep the browser open for a specified duration.
        
        Args:
            duration: Time in seconds to keep browser open (default: 300)
        """
        logger.info(f"Keeping browser alive for {duration} seconds...")
        logger.info("Close the browser window manually when done.")
        
        try:
            # Wait until context is closed or timeout
            self.context.pages[0].wait_for_load_state()
            time.sleep(duration)
        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
        finally:
            self.close()

    def close(self) -> None:
        """Close browser and cleanup resources."""
        logger.info("Closing browser...")
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed.")


def main():
    """Main function to demonstrate WhatsApp automation."""
    # Initialize automation
    whatsapp = WhatsAppAutomation(headless=False)
    
    try:
        # Connect and login
        if whatsapp.connect_whatsapp():
            logger.info("Connected to WhatsApp Web!")
            
            # Get contact and message from user
            contact = input("\nEnter contact name or phone number: ").strip()
            message = input("Enter your message: ").strip()
            
            if contact and message:
                # Send message
                success = whatsapp.send_whatsapp_message(contact, message)
                
                if success:
                    print("\n✓ Message sent successfully!")
                else:
                    print("\n✗ Failed to send message.")
            
            # Keep browser open for manual interaction
            whatsapp.keep_alive(duration=60)
        else:
            logger.error("Failed to connect to WhatsApp Web.")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        whatsapp.close()


if __name__ == "__main__":
    main()
