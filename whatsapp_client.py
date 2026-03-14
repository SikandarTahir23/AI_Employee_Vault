"""
WhatsApp Web Client — Fixed Version for AI Agency Dashboard
Uses Playwright with persistent context for reliable session storage

Features:
- Persistent session storage (survives browser restarts)
- QR code login detection and forced display
- Multiple selector strategies for resilience
- Phone number validation
- Comprehensive logging for Streamlit dashboard
- Sync and async APIs

Usage:
    from whatsapp_client import connect_whatsapp, send_whatsapp_message, get_whatsapp_status
"""

import os
import sys
import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dotenv import load_dotenv

# Force UTF-8 on Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

try:
    from playwright.sync_api import sync_playwright, BrowserContext, Page, TimeoutError as PwTimeout
except ImportError:
    print("[ERROR] playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================
PROJECT_ROOT = Path(__file__).parent
WHATSAPP_URL = "https://web.whatsapp.com"
USER_DATA_DIR = PROJECT_ROOT / ".whatsapp_session"
LOGS_DIR = PROJECT_ROOT / "logs"
DEFAULT_TIMEOUT = 60000  # 60 seconds

# Chrome executable (Windows) - will fallback to Playwright Chromium if not found
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not Path(CHROME_EXE).exists():
    CHROME_EXE = None  # Use Playwright's built-in Chromium

# Ensure directories exist
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# SELECTORS (Updated for 2024 WhatsApp Web)
# =============================================================================
SELECTORS = {
    # QR Code detection (not logged in)
    "qr_code": [
        'div[data-ref]',
        'canvas',
        'img[alt="QR Code"]',
        '[data-testid="qrcode"]',
        'div[data-testid="qrcode"]',
        'div[data-testid="qr-container"]',
    ],
    # Main interface (logged in)
    "main_interface": [
        '[data-testid="chat-list"]',
        'div[data-testid="chat-list"]',
        '[data-testid="default-user"]',
        '.DTThI',
        'div[role="navigation"]',
    ],
    # Message input
    "message_input": [
        'div[contenteditable="true"][data-tab="10"]',
        'div[contenteditable="true"][data-tab="6"]',
        'div[contenteditable="true"]',
        '[data-testid="compose-input"]',
        'footer div[contenteditable="true"]',
        'div.selectable-text[contenteditable="true"]',
        'div[role="textbox"]',
    ],
    # Send button
    "send_button": [
        'button[data-testid="compose-btn-send"]',
        'button[aria-label="Send"]',
        'button[aria-label="Send message"]',
        'div[data-testid="send-button"]',
        'svg[data-icon="send"]',
    ],
    # Search box
    "search_box": [
        'div[role="searchbox"] input',
        '[data-testid="search"] input',
        'input[title="Search or start new chat"]',
    ],
    # Contact results
    "contact_result": [
        'span[title]',
        'div[role="listitem"]',
        'div[role="row"]',
    ],
    # Error states
    "error": [
        '[data-testid="error-title"]',
        'div[data-testid="chat-info-error"]',
        '[data-testid="contact-not-exist-title"]',
    ],
}


# =============================================================================
# GLOBAL STATE
# =============================================================================
_whatsapp_context: Optional[BrowserContext] = None
_whatsapp_page: Optional[Page] = None
_whatsapp_playwright = None
_whatsapp_logged_in = False
_whatsapp_initialized = False


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def close_chrome():
    """Close all Chrome instances to avoid conflicts."""
    try:
        import subprocess
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"],
                      capture_output=True, timeout=5)
        logger.info("Closed all Chrome instances")
    except Exception as e:
        logger.debug(f"Could not close Chrome: {e}")


def clean_locks():
    """Remove stale lock files from profile directory."""
    lock_patterns = ["lock", "singleton", ".lock"]
    for lock in USER_DATA_DIR.rglob("*"):
        if lock.is_file() and any(p in lock.name.lower() for p in lock_patterns):
            try:
                lock.unlink()
                logger.debug(f"Removed lock file: {lock.name}")
            except Exception as e:
                logger.debug(f"Could not remove {lock.name}: {e}")


def find_element_by_selectors(page: Page, selectors: List[str], 
                               timeout: int = 3000, 
                               description: str = "element") -> Optional[Any]:
    """Find element using multiple selector strategies."""
    for selector in selectors:
        try:
            element = page.wait_for_selector(selector, timeout=timeout)
            if element:
                logger.debug(f"Found {description}: {selector}")
                return element
        except:
            continue
    return None


# =============================================================================
# CORE FUNCTIONS
# =============================================================================
def connect_whatsapp(headless: bool = False, timeout: int = 60) -> Tuple[bool, str]:
    """
    Connect to WhatsApp Web and display QR code if not logged in.
    
    This function:
    1. Launches browser with persistent context
    2. Opens WhatsApp Web
    3. Detects if already logged in
    4. If not logged in, displays QR code and waits for scan
    5. Saves session for future use
    
    Args:
        headless: Run browser in headless mode (False recommended for QR login)
        timeout: Maximum time to wait for QR code scan (seconds)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    global _whatsapp_context, _whatsapp_page, _whatsapp_playwright, _whatsapp_logged_in, _whatsapp_initialized
    
    logger.info("=" * 60)
    logger.info("WHATSAPP CONNECTION INITIATED")
    logger.info("=" * 60)
    
    try:
        # Close existing Chrome to avoid conflicts
        close_chrome()
        clean_locks()

        logger.info(f"Session directory: {USER_DATA_DIR}")
        logger.info(f"Chrome executable: {CHROME_EXE or 'Playwright Chromium (default)'}")

        # Launch Playwright with persistent context
        _whatsapp_playwright = sync_playwright().start()

        logger.info("Launching browser with persistent context...")
        
        # Build launch arguments
        launch_args = {
            "user_data_dir": str(USER_DATA_DIR),
            "headless": headless,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            "viewport": {"width": 1280, "height": 720},
            "timeout": DEFAULT_TIMEOUT,
        }
        
        # Only add executable_path if Chrome exists
        if CHROME_EXE:
            launch_args["executable_path"] = CHROME_EXE
        
        _whatsapp_context = _whatsapp_playwright.chromium.launch_persistent_context(**launch_args)
        
        _whatsapp_page = _whatsapp_context.pages[0] if _whatsapp_context.pages else _whatsapp_context.new_page()
        
        logger.info(f"Navigating to {WHATSAPP_URL}...")
        _whatsapp_page.goto(WHATSAPP_URL, timeout=DEFAULT_TIMEOUT, wait_until="domcontentloaded")
        
        # Wait for page to stabilize
        time.sleep(2)
        
        # Check login status
        logger.info("Checking login status...")
        _whatsapp_logged_in = _check_login_status(_whatsapp_page)
        
        if _whatsapp_logged_in:
            logger.info("✓ Already logged in (session restored)")
            _whatsapp_initialized = True
            return True, "Already logged in (session restored)"
        
        # Not logged in - wait for QR code scan
        logger.info("⚠ QR code login required")
        logger.info("📱 Please scan the QR code with WhatsApp mobile app")
        logger.info(f"Waiting up to {timeout} seconds...")
        
        # Wait for QR code to appear
        try:
            qr_element = find_element_by_selectors(
                _whatsapp_page, 
                SELECTORS["qr_code"], 
                timeout=10000, 
                description="QR code"
            )
            if qr_element:
                logger.info("✓ QR code displayed in browser")
        except Exception as e:
            logger.warning(f"Could not confirm QR display: {e}")
        
        # Wait for login
        login_success = _wait_for_login(_whatsapp_page, timeout=timeout)
        
        if login_success:
            logger.info("✓ Login successful!")
            _whatsapp_initialized = True
            return True, "Login successful"
        else:
            logger.error("✗ Login timeout - QR code not scanned")
            return False, "Login timeout - QR code not scanned"
            
    except Exception as e:
        logger.error(f"Connection failed: {e}", exc_info=True)
        cleanup_whatsapp()
        return False, f"Connection failed: {e}"


def _check_login_status(page: Page) -> bool:
    """
    Check if WhatsApp Web is logged in.
    
    Returns:
        True if logged in, False if QR code is shown
    """
    try:
        # Wait a bit for page to stabilize
        page.wait_for_timeout(2000)
        
        # Try to find main interface first (logged in)
        for selector in SELECTORS["main_interface"]:
            try:
                page.wait_for_selector(selector, timeout=3000)
                logger.debug(f"Found main interface: {selector}")
                return True
            except:
                continue
        
        # Check for QR code (not logged in)
        for selector in SELECTORS["qr_code"]:
            try:
                element = page.query_selector(selector)
                if element:
                    logger.debug(f"QR code detected: {selector}")
                    return False
            except:
                continue
        
        # Fallback: check page title
        title = page.title()
        if "WhatsApp" in title:
            logger.info("Could not detect QR, assuming logged in")
            return True
        
        return False
        
    except Exception as e:
        logger.warning(f"Error checking login status: {e}")
        return False


def _wait_for_login(page: Page, timeout: int = 60) -> bool:
    """
    Wait for user to scan QR code and login.
    
    Args:
        page: Playwright page object
        timeout: Maximum time to wait in seconds
    
    Returns:
        True if login successful, False if timeout
    """
    logger.info("Waiting for QR code login...")
    
    start_time = time.time()
    check_interval = 2  # Check every 2 seconds
    
    while time.time() - start_time < timeout:
        time.sleep(check_interval)
        
        is_logged_in = _check_login_status(page)
        if is_logged_in:
            logger.info("✓ Login successful!")
            return True
        
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0:
            logger.info(f"Still waiting for login... ({elapsed}s/{timeout}s)")
    
    logger.error("Login timeout")
    return False


def send_whatsapp_message(phone_number: str, message: str, 
                          headless: bool = False) -> Tuple[bool, str]:
    """
    Send a WhatsApp message (convenience function).
    
    Args:
        phone_number: Phone number with country code (e.g., '+1234567890')
        message: Message text to send
        headless: Run browser in headless mode
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    global _whatsapp_context, _whatsapp_page, _whatsapp_logged_in
    
    logger.info(f"Send request: {phone_number}")
    
    # Connect if not already connected
    if not _whatsapp_initialized or not _whatsapp_logged_in:
        logger.info("Not connected, initiating connection...")
        success, msg = connect_whatsapp(headless=headless, timeout=60)
        if not success:
            return False, msg
    
    if not _whatsapp_page:
        return False, "WhatsApp not initialized"
    
    # Validate phone number
    is_valid, cleaned_number = _validate_phone_number(phone_number)
    if not is_valid:
        return False, f"Invalid phone number: {cleaned_number}"
    
    try:
        logger.info(f"Sending message to {cleaned_number}")
        
        # Navigate to chat using wa.me link
        chat_url = f"https://web.whatsapp.com/send?phone={cleaned_number}"
        logger.info(f"Navigating to: {chat_url}")
        
        _whatsapp_page.goto(chat_url, timeout=DEFAULT_TIMEOUT, wait_until="domcontentloaded")
        time.sleep(3)  # Wait for chat to load
        
        # Check for errors
        error_elem = find_element_by_selectors(
            _whatsapp_page, 
            SELECTORS["error"], 
            timeout=3000, 
            description="error"
        )
        if error_elem:
            error_text = error_elem.inner_text()
            logger.error(f"WhatsApp error: {error_text}")
            return False, f"Contact not found: {error_text}"
        
        # Find message input
        message_input = find_element_by_selectors(
            _whatsapp_page, 
            SELECTORS["message_input"], 
            timeout=5000, 
            description="message input"
        )
        if not message_input:
            return False, "Could not find message input field"
        
        # Type the message
        logger.debug("Typing message...")
        message_input.fill(message)
        time.sleep(0.5)
        
        # Find and click send button
        send_button = find_element_by_selectors(
            _whatsapp_page, 
            SELECTORS["send_button"], 
            timeout=5000, 
            description="send button"
        )
        if not send_button:
            return False, "Could not find send button"
        
        logger.debug("Clicking send button...")
        send_button.click()
        time.sleep(1)
        
        logger.info(f"✓ Message sent to {cleaned_number}")
        return True, "Message sent successfully"
        
    except Exception as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return False, str(e)


def _validate_phone_number(phone_number: str) -> Tuple[bool, str]:
    """
    Validate phone number format.
    
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


def get_whatsapp_status() -> Dict[str, Any]:
    """
    Get WhatsApp connection status.
    
    This function checks if the session directory exists and has valid login data.
    It does NOT open a browser - just checks for session files.

    Returns:
        Dictionary with status information
    """
    global _whatsapp_logged_in, _whatsapp_initialized
    import time

    status = {
        'session_exists': USER_DATA_DIR.exists(),
        'logged_in': _whatsapp_logged_in,
        'initialized': _whatsapp_initialized,
        'context_exists': _whatsapp_context is not None,
        'page_exists': _whatsapp_page is not None,
        'session_dir': str(USER_DATA_DIR),
    }

    # If not initialized, check if session directory has data
    if not _whatsapp_initialized and status['session_exists']:
        # Check if there's any session data (Chrome profile files)
        has_session_data = any(USER_DATA_DIR.iterdir())
        status['has_session_data'] = has_session_data
        
        # Check for specific Chrome session files that indicate a saved login
        # These files exist when WhatsApp Web has saved the login session
        # They can be in the root or in the 'Default' subdirectory
        session_indicators = [
            'Login Data',  # Chrome's password/session storage
            'Cookies',     # Cookie storage
            'Local Storage',  # Local storage
        ]
        
        # Check both root and Default subdirectory
        check_paths = [
            USER_DATA_DIR,
            USER_DATA_DIR / "Default",
        ]
        
        status['likely_logged_in'] = False
        for base_path in check_paths:
            if status['likely_logged_in']:
                break
            for indicator in session_indicators:
                indicator_path = base_path / indicator
                if indicator_path.exists():
                    # Check if it's a recent file (modified in last 7 days)
                    try:
                        mtime = indicator_path.stat().st_mtime
                        age_days = (time.time() - mtime) / 86400
                        if age_days < 7:  # Session is less than 7 days old
                            status['likely_logged_in'] = True
                            status['session_age_days'] = age_days
                            break
                    except:
                        pass

    return status


def check_login_status() -> bool:
    """
    Check current login status without blocking.
    
    Returns:
        True if logged in, False otherwise
    """
    global _whatsapp_logged_in
    
    if not _whatsapp_page:
        return False
    
    _whatsapp_logged_in = _check_login_status(_whatsapp_page)
    return _whatsapp_logged_in


def cleanup_whatsapp():
    """Clean up WhatsApp resources."""
    global _whatsapp_context, _whatsapp_page, _whatsapp_playwright, _whatsapp_logged_in, _whatsapp_initialized
    
    try:
        if _whatsapp_context:
            _whatsapp_context.close()
        if _whatsapp_playwright:
            _whatsapp_playwright.stop()
        logger.info("Browser resources cleaned up")
    except Exception as e:
        logger.warning(f"Cleanup error: {e}")
    
    _whatsapp_context = None
    _whatsapp_page = None
    _whatsapp_playwright = None
    _whatsapp_logged_in = False
    _whatsapp_initialized = False


def reset_whatsapp():
    """Reset WhatsApp state and cleanup."""
    logger.info("Resetting WhatsApp state...")
    cleanup_whatsapp()


# =============================================================================
# ASYNC VERSION (for integrations.py compatibility)
# =============================================================================
class WhatsAppClient:
    """Async WhatsApp client for integrations.py"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None
        self._is_logged_in = False
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize browser and load WhatsApp Web."""
        if self._initialized:
            return self._is_logged_in
        
        try:
            from playwright.async_api import async_playwright
            
            logger.info("Initializing WhatsApp Web automation...")
            USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            self._playwright = await async_playwright().start()
            
            self.context = await self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=self.headless,
                executable_path=CHROME_EXE,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-features=IsolateOrigins,site-per-process'
                ],
                viewport={'width': 1280, 'height': 720},
                timeout=DEFAULT_TIMEOUT
            )
            
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            
            await self.page.goto(WHATSAPP_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
            await self.page.wait_for_load_state('networkidle', timeout=DEFAULT_TIMEOUT)
            
            self._is_logged_in = await self._check_login_status()
            self._initialized = True
            
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            await self.cleanup()
            return False
    
    async def _check_login_status(self) -> bool:
        """Check login status."""
        await asyncio.sleep(2)
        
        # Check main interface
        for selector in SELECTORS["main_interface"]:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                return True
            except:
                continue
        
        # Check QR code
        for selector in SELECTORS["qr_code"]:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    return False
            except:
                continue
        
        return True
    
    async def wait_for_login(self, timeout: int = 60) -> bool:
        """Wait for QR code login."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            await asyncio.sleep(2)
            
            if await self._check_login_status():
                self._is_logged_in = True
                return True
            
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0:
                logger.info(f"Still waiting for login... ({elapsed}s/{timeout}s)")
        
        return False
    
    async def send_message(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """Send a message."""
        if not self._initialized:
            if not await self.initialize():
                return False, "Failed to initialize"
        
        if not self._is_logged_in:
            return False, "Not logged in"
        
        is_valid, cleaned_number = _validate_phone_number(phone_number)
        if not is_valid:
            return False, f"Invalid phone number: {cleaned_number}"
        
        try:
            chat_url = f"https://web.whatsapp.com/send?phone={cleaned_number}"
            await self.page.goto(chat_url, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
            await asyncio.sleep(3)
            
            # Find message input
            message_input = None
            for selector in SELECTORS["message_input"]:
                try:
                    message_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if message_input:
                        break
                except:
                    continue
            
            if not message_input:
                return False, "Could not find message input"
            
            await message_input.fill(message)
            await asyncio.sleep(0.5)
            
            # Find send button
            send_button = None
            for selector in SELECTORS["send_button"]:
                try:
                    send_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if send_button:
                        break
                except:
                    continue
            
            if not send_button:
                return False, "Could not find send button"
            
            await send_button.click()
            await asyncio.sleep(1)
            
            return True, "Message sent successfully"
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False, str(e)
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            if self.context:
                await self.context.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
        
        self.context = None
        self.page = None
        self._playwright = None
        self._is_logged_in = False
        self._initialized = False


# =============================================================================
# MAIN (for testing)
# =============================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("WhatsApp Web Automation - Test Mode")
    print("=" * 60)
    
    # Test connection
    print("\n1. Testing connection...")
    success, msg = connect_whatsapp(headless=False, timeout=60)
    print(f"   Result: {msg}")
    
    if success:
        print("\n2. Testing message send...")
        test_number = input("   Enter phone number (with country code): ")
        test_message = input("   Enter message: ")
        
        success, msg = send_whatsapp_message(test_number, test_message)
        print(f"   Result: {msg}")
    
    print("\n3. Cleanup...")
    cleanup_whatsapp()
    
    print("\nTest complete!")
