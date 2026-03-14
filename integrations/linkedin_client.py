"""
LinkedIn Client Module for AI Automation Dashboard
Uses Playwright for browser automation with persistent sessions

Features:
- Persistent session storage (survives browser restarts)
- Multiple selector strategies for resilience
- Clipboard paste for reliable content insertion
- Screenshot capture for audit trail
- Draft → Approved → Posted workflow
"""

import os
import sys
import io
import glob
import re
import time
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dotenv import load_dotenv

# Force UTF-8 stdout/stderr on Windows (only if not running under Streamlit)
if not os.getenv('STREAMLIT_RUNNING'):
    if sys.stdout and hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        except (ValueError, AttributeError):
            pass  # Skip if stdout is closed (e.g., under Streamlit)
    if sys.stderr and hasattr(sys.stderr, "buffer"):
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except (ValueError, AttributeError):
            pass  # Skip if stderr is closed

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout, Page
except ImportError:
    print("[ERROR] playwright is not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
import logging
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DRAFTS_DIR = PROJECT_ROOT / "Drafts"
APPROVED_DIR = PROJECT_ROOT / "Approved"
DONE_DIR = PROJECT_ROOT / "Done"
PLAYWRIGHT_PROFILE = PROJECT_ROOT / ".playwright_profile"

# Ensure directories exist
APPROVED_DIR.mkdir(exist_ok=True)
DONE_DIR.mkdir(exist_ok=True)

# Timeout settings
DEFAULT_TIMEOUT = 60000  # 60 seconds
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds


class LinkedInClient:
    """
    LinkedIn automation client using Playwright
    
    Features:
    - Persistent session (login once, reuse across restarts)
    - Multiple selector strategies for resilience
    - Clipboard paste for reliable content insertion
    - Screenshot capture for audit trail
    """

    def __init__(self, headless: bool = False):
        """
        Initialize LinkedIn client

        Args:
            headless: Run browser in headless mode (False recommended for visibility)
        """
        self.headless = headless
        self.context = None
        self.page = None
        self._playwright = None
        self._is_logged_in = False
        self._initialized = False

    def _close_chrome(self):
        """Close all Chrome processes to avoid profile lock conflicts"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                capture_output=True, text=True,
            )
            if "chrome.exe" in result.stdout:
                logger.info("Closing existing Chrome processes...")
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
                time.sleep(2)
        except Exception as e:
            logger.warning(f"Error closing Chrome: {e}")

    def initialize(self) -> bool:
        """
        Initialize browser and load LinkedIn

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return self._is_logged_in

        try:
            logger.info("Initializing LinkedIn automation...")

            # Close existing Chrome to avoid profile conflicts
            self._close_chrome()

            # Create profile directory
            PLAYWRIGHT_PROFILE.mkdir(parents=True, exist_ok=True)
            logger.info(f"Profile directory: {PLAYWRIGHT_PROFILE}")

            # Launch Playwright
            self._playwright = sync_playwright().start()

            # Launch browser with persistent context
            self.context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(PLAYWRIGHT_PROFILE),
                headless=self.headless,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled'
                ],
                viewport={'width': 1280, 'height': 720},
                timeout=DEFAULT_TIMEOUT
            )

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

            # Navigate to LinkedIn
            logger.info("Navigating to LinkedIn feed...")
            self.page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded', timeout=PAGE_LOAD_TIMEOUT)
            
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                logger.info("networkidle not reached (normal for LinkedIn)")
            
            self.page.wait_for_timeout(3000)

            # Check login status
            self._is_logged_in = self._check_login_status()
            
            if self._is_logged_in:
                logger.info("✓ Already logged in (session restored)")
            else:
                logger.info("⚠ Login required")

            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.cleanup()
            return False

    def _check_login_status(self) -> bool:
        """
        Check if logged in to LinkedIn

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for login URL or checkpoint
            if "/login" in self.page.url or "/checkpoint" in self.page.url:
                return False

            # Check for feed page
            if "/feed" in self.page.url:
                return True

            # Try to find feed-related elements
            feed_selectors = [
                'div[class*="share-box"]',
                'div[class*="feed"]',
                '[data-control-name="feed"]'
            ]

            for selector in feed_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    return True
                except:
                    continue

            return False

        except Exception as e:
            logger.warning(f"Error checking login status: {e}")
            return False

    def wait_for_login(self, timeout: int = 120) -> bool:
        """
        Wait for user to log in manually

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if login successful, False if timeout
        """
        logger.info("Waiting for login...")
        logger.info("📝 Please log in to LinkedIn in the browser window")

        start_time = time.time()
        check_interval = 3

        while time.time() - start_time < timeout:
            time.sleep(check_interval)

            if self._check_login_status():
                logger.info("✓ Login successful!")
                self._is_logged_in = True
                # Navigate to feed
                self.page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded')
                return True

            elapsed = int(time.time() - start_time)
            if elapsed % 15 == 0:
                logger.info(f"Still waiting for login... ({elapsed}s/{timeout}s)")

        logger.error("Login timeout")
        return False

    def post_content(self, content: str) -> Tuple[bool, str]:
        """
        Post content to LinkedIn

        Args:
            content: Post content (text, can include emojis and hashtags)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self._initialized:
            if not self.initialize():
                return False, "Failed to initialize LinkedIn"

        if not self._is_logged_in:
            return False, "Not logged in. Please log in first."

        try:
            logger.info(f"Posting content ({len(content)} chars)...")

            # Click "Start a post" using multiple strategies
            modal_opened = self._open_post_modal()
            
            if not modal_opened:
                return False, "Could not open post composer"

            # Wait for modal
            self.page.wait_for_timeout(1000)

            # Click editor and paste content
            editor_clicked = self._click_editor()
            
            if not editor_clicked:
                return False, "Could not find post editor"

            # Paste content using clipboard
            logger.info("Pasting content via clipboard...")
            self.page.evaluate("text => navigator.clipboard.writeText(text)", content)
            self.page.wait_for_timeout(300)
            self.page.keyboard.press("Control+v")
            self.page.wait_for_timeout(1000)

            # Fallback: JS insertion if paste didn't work
            editor_text = self.page.evaluate("""
                () => {
                    const el = document.querySelector('div.ql-editor, div[role="textbox"][contenteditable="true"]');
                    return el ? el.innerText.trim() : '';
                }
            """)
            
            if len(editor_text) < 20:
                logger.info("Clipboard paste may not have worked — trying JS insert...")
                self.page.evaluate("""
                    text => {
                        const el = document.querySelector('div.ql-editor, div[role="textbox"][contenteditable="true"]');
                        if (el) {
                            el.focus();
                            el.innerHTML = text.split('\\n').map(l => '<p>' + l + '</p>').join('');
                            el.dispatchEvent(new Event('input', {bubbles: true}));
                        }
                    }
                """, content)
                self.page.wait_for_timeout(500)

            # Click Post button
            logger.info("Clicking Post button...")
            post_clicked = self._click_post_button()
            
            if not post_clicked:
                return False, "Could not click Post button"

            # Wait for confirmation
            logger.info("Waiting for post confirmation...")
            self.page.wait_for_timeout(5000)

            # Screenshot as audit proof
            screenshot_path = str(PROJECT_ROOT / "linkedin_post_confirmation.png")
            try:
                self.page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.warning(f"Could not save screenshot: {e}")

            logger.info("✓ Post submitted to LinkedIn!")
            return True, "Post submitted successfully"

        except PwTimeout as e:
            logger.error(f"Timeout waiting for element: {e}")
            return False, "Timeout - LinkedIn may have updated its UI"
        except Exception as e:
            logger.error(f"Failed to post: {e}")
            return False, str(e)

    def _open_post_modal(self) -> bool:
        """
        Open the post creation modal

        Returns:
            True if modal opened successfully
        """
        logger.info("Looking for 'Start a post'...")

        # Take a screenshot for debugging
        try:
            self.page.screenshot(path=str(PROJECT_ROOT / "debug_before_click.png"))
        except:
            pass

        # Strategy 1: Click the main "Start a post" container at top of feed
        # This is the most reliable - it's the div containing profile image + "Start a post" text
        try:
            # Look for the share box trigger - this is the main container
            share_box = self.page.locator("div.share-box-feed-entry__trigger").first
            share_box.wait_for(state="visible", timeout=8000)
            share_box.click(force=True)
            self.page.wait_for_timeout(3000)
            
            # Check if modal opened
            if self.page.locator("div[role='dialog'], div.artdeco-modal, div.share-creation-state__overlay").first.is_visible(timeout=2000):
                logger.info("Modal opened via share-box trigger")
                return True
        except Exception as e:
            logger.debug(f"Strategy 1 (share-box) failed: {e}")

        # Strategy 2: Click on the input field that says "Start a post"
        try:
            # The input-like element at the top of the feed
            start_post_input = self.page.locator("div.idc__share-textbox, div.share-box-feed-entry__textbox").first
            start_post_input.wait_for(state="visible", timeout=5000)
            start_post_input.click(force=True)
            self.page.wait_for_timeout(2000)
            logger.info("Clicked via textbox selector")
            return True
        except Exception as e:
            logger.debug(f"Strategy 2 (textbox) failed: {e}")

        # Strategy 3: Click on visible "Start a post" text (not hidden elements)
        try:
            # Find all elements with "Start a post" text
            elements = self.page.locator("text=Start a post").all()
            
            for el in elements:
                try:
                    # Check if element is visible (not hidden)
                    if el.is_visible(timeout=1000):
                        bbox = el.bounding_box(timeout=1000)
                        # Only click if it's in a reasonable position (top half of page)
                        if bbox and bbox['y'] < 400:
                            el.click(force=True)
                            self.page.wait_for_timeout(3000)
                            logger.info("Clicked visible 'Start a post' element")
                            return True
                except:
                    continue
        except Exception as e:
            logger.debug(f"Strategy 3 (visible text) failed: {e}")

        # Strategy 4: JS click on visible element
        try:
            result = self.page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    for (const el of elements) {
                        const text = (el.textContent || '').trim();
                        if (text === 'Start a post') {
                            // Check if visible
                            const rect = el.getBoundingClientRect();
                            const style = window.getComputedStyle(el);
                            if (rect.width > 50 && rect.height > 20 && 
                                style.display !== 'none' && 
                                style.visibility !== 'hidden' &&
                                rect.y < 400) {
                                el.click();
                                return true;
                            }
                        }
                    }
                    return false;
                }
            """)
            if result:
                self.page.wait_for_timeout(3000)
                logger.info("JS click on visible element succeeded")
                return True
        except Exception as e:
            logger.debug(f"Strategy 4 (JS visible) failed: {e}")

        # Strategy 5: Try clicking anywhere in the compose area
        try:
            compose_area = self.page.locator("div.share-box-feed-entry").first
            compose_area.wait_for(state="visible", timeout=5000)
            compose_area.click(force=True)
            self.page.wait_for_timeout(2000)
            logger.info("Clicked compose area")
            return True
        except Exception as e:
            logger.debug(f"Strategy 5 (compose area) failed: {e}")

        # Save debug screenshot
        try:
            self.page.screenshot(path=str(PROJECT_ROOT / "debug_linkedin_modal.png"))
        except:
            pass

        logger.error("All strategies failed to open post modal")
        return False

    def _click_editor(self) -> bool:
        """
        Click the post editor

        Returns:
            True if editor clicked successfully
        """
        logger.info("Looking for post editor...")

        strategies = [
            # Strategy 1: Role textbox
            lambda: self.page.get_by_role("textbox").first.click(force=True, timeout=5000),
            # Strategy 2: Contenteditable div
            lambda: self.page.locator("div[contenteditable='true']").first.click(force=True, timeout=5000),
            # Strategy 3: Quill editor
            lambda: self.page.locator("div.ql-editor").first.click(force=True, timeout=5000),
            # Strategy 4: data-placeholder
            lambda: self.page.locator("[data-placeholder]").first.click(force=True, timeout=5000),
        ]

        for i, strategy in enumerate(strategies):
            try:
                logger.debug(f"Trying editor strategy {i+1}...")
                strategy()
                self.page.wait_for_timeout(500)
                return True
            except Exception as e:
                logger.debug(f"Editor strategy {i+1} failed: {type(e).__name__}")

        return False

    def _click_post_button(self) -> bool:
        """
        Click the Post button

        Returns:
            True if Post button clicked successfully
        """
        try:
            post_btn = self.page.get_by_role("button", name="Post", exact=True).or_(
                self.page.locator("button.share-actions__primary-action")
            ).or_(
                self.page.locator("button[aria-label='Post']")
            )
            post_btn.first.click(timeout=30000)
            return True
        except Exception as e:
            logger.error(f"Could not click Post button: {e}")
            return False

    def is_logged_in(self) -> bool:
        """Check if logged in"""
        if not self._initialized:
            return False
        return self._is_logged_in

    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.context:
                self.context.close()
            if self._playwright:
                self._playwright.stop()
            logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

        self.context = None
        self.page = None
        self._playwright = None
        self._is_logged_in = False
        self._initialized = False


# Global instance
_linkedin_instance: Optional[LinkedInClient] = None


def get_linkedin_client(headless: bool = False) -> LinkedInClient:
    """
    Get or create LinkedIn client instance

    Args:
        headless: Run browser in headless mode

    Returns:
        LinkedInClient instance
    """
    global _linkedin_instance
    if _linkedin_instance is None:
        _linkedin_instance = LinkedInClient(headless=headless)
    return _linkedin_instance


def reset_linkedin_client():
    """Reset the global LinkedIn client instance"""
    global _linkedin_instance
    if _linkedin_instance:
        _linkedin_instance.cleanup()
    _linkedin_instance = None


def post_to_linkedin(content: str, headless: bool = False, wait_for_login: bool = True) -> Tuple[bool, str]:
    """
    Standalone function to post to LinkedIn

    This function:
    1. Uses persistent client if available (from connect_linkedin)
    2. Otherwise creates new client with persistent profile
    3. Loads saved session cookies automatically
    4. Opens LinkedIn feed
    5. Creates and publishes the post

    Args:
        content: Post content (text, emojis, hashtags)
        headless: Run browser in headless mode (False recommended)
        wait_for_login: If True and not logged in, wait for user to log in

    Returns:
        Tuple of (success: bool, message: str)

    Example:
        success, msg = post_to_linkedin("Hello LinkedIn! #AI #Automation")
        if success:
            print("Post submitted!")
    """
    global _persistent_client
    
    logger.info("=" * 60)
    logger.info("LINKEDIN POST INITIATED")
    logger.info("=" * 60)
    logger.info(f"Content length: {len(content)} characters")

    # Use persistent client if available (browser already open)
    if _persistent_client is not None:
        logger.info("Using existing browser session...")
        client = _persistent_client
        
        if not client._initialized:
            logger.info("Re-initializing browser...")
            if not client.initialize():
                return False, "Failed to initialize LinkedIn"
        
        # Navigate to feed
        try:
            client.page.goto("https://www.linkedin.com/feed/",
                           wait_until='domcontentloaded',
                           timeout=30000)
            client.page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Could not navigate to feed: {e}")
        
        # Check login status
        if not client._is_logged_in:
            client._is_logged_in = client._check_login_status()
        
        if not client._is_logged_in:
            if wait_for_login:
                logger.info("Not logged in, waiting for login...")
                if not client.wait_for_login(timeout=120):
                    return False, "Not logged in. Please log in first."
            else:
                return False, "Not logged in. Please call connect_linkedin() first."
        
        # Post content
        success, msg = client.post_content(content)
        
        if success:
            logger.info("✓ Post submitted successfully!")
            client.page.wait_for_timeout(3000)  # Let user see confirmation
        
        return success, msg

    # No persistent client - create new one with persistent profile
    logger.info("Creating new browser session with persistent profile...")
    client = LinkedInClient(headless=headless)

    try:
        if not client.initialize():
            return False, "Failed to initialize LinkedIn"

        if not client._is_logged_in:
            if wait_for_login:
                logger.info("Not logged in, waiting for login...")
                if not client.wait_for_login(timeout=120):
                    return False, "Not logged in. Please log in first."
            else:
                return False, "Not logged in. Please call connect_linkedin() first."

        return client.post_content(content)

    finally:
        # Only cleanup if not using persistent client
        if _persistent_client is None:
            client.cleanup()


def login_to_linkedin(headless: bool = False) -> Tuple[bool, str]:
    """
    Open browser for LinkedIn login and wait for user to log in

    Args:
        headless: Run browser in headless mode

    Returns:
        Tuple of (success: bool, message: str)
    """
    client = LinkedInClient(headless=headless)

    try:
        if not client.initialize():
            return False, "Failed to initialize LinkedIn"

        if client._is_logged_in:
            return True, "Already logged in"

        print("\n📝 Please log in to LinkedIn in the browser window")
        print("   The browser will stay open until you complete login")
        print("   Close the browser window when done")

        if client.wait_for_login(timeout=120):
            return True, "Login successful"
        else:
            return False, "Login timeout - please try again"

    finally:
        client.cleanup()


# Global persistent client for Streamlit integration
_persistent_client: Optional[LinkedInClient] = None


def connect_linkedin(headless: bool = False, timeout: int = 120) -> Tuple[bool, str]:
    """
    Connect to LinkedIn - opens browser and waits for manual login

    This function:
    1. Opens browser with persistent profile (headless=False for visibility)
    2. Navigates to LinkedIn login
    3. Keeps browser open for user to log in (does NOT close prematurely)
    4. Saves session cookies automatically via persistent context
    5. Confirms login success

    Args:
        headless: Run browser in headless mode (False recommended for login)
        timeout: Maximum time to wait for login in seconds

    Returns:
        Tuple of (success: bool, message: str)
    """
    global _persistent_client
    
    logger.info("=" * 60)
    logger.info("LINKEDIN CONNECTION INITIATED")
    logger.info("=" * 60)

    # Use persistent client to keep browser open across calls
    if _persistent_client is not None:
        logger.info("Closing existing browser session...")
        _persistent_client.cleanup()
        _persistent_client = None

    _persistent_client = LinkedInClient(headless=headless)
    client = _persistent_client

    try:
        # Initialize browser with persistent profile
        logger.info("Opening browser with persistent profile...")
        logger.info(f"Profile directory: {PLAYWRIGHT_PROFILE}")
        
        if not client.initialize():
            return False, "Failed to initialize LinkedIn"

        # Check if already logged in
        if client._is_logged_in:
            logger.info("✓ Already logged in (session restored)")
            logger.info("Browser will remain open for posting.")
            return True, "Already logged in"

        # Navigate to login page
        logger.info("Navigating to LinkedIn login...")
        try:
            client.page.goto("https://www.linkedin.com/login",
                           wait_until='domcontentloaded',
                           timeout=30000)
        except Exception as e:
            logger.warning(f"Could not navigate to login page: {e}")

        logger.info("⚠ Login required")
        logger.info("📝 Please log in to LinkedIn in the browser window")
        logger.info("🔒 Browser will stay open until login is complete")
        logger.info(f"⏳ Waiting up to {timeout} seconds...")

        # Wait for user to complete login - browser stays open during this time
        if client.wait_for_login(timeout=timeout):
            logger.info("✓ Login successful!")
            logger.info("✓ Session saved to persistent profile")

            # Navigate to feed to confirm
            try:
                client.page.goto("https://www.linkedin.com/feed/",
                               wait_until='domcontentloaded',
                               timeout=30000)
                client.page.wait_for_timeout(2000)
            except Exception as e:
                logger.debug(f"Could not navigate to feed: {e}")

            logger.info("Browser remains open for posting.")
            return True, "Login successful"
        else:
            logger.error("Login timeout")
            return False, "Login timeout - please try again"

    except Exception as e:
        logger.error(f"Connection error: {e}", exc_info=True)
        return False, f"Error: {e}"


def get_persistent_client() -> Optional[LinkedInClient]:
    """Get the persistent LinkedIn client if it exists."""
    return _persistent_client


def cleanup_persistent_linkedin():
    """Clean up the persistent LinkedIn client."""
    global _persistent_client
    if _persistent_client:
        _persistent_client.cleanup()
        _persistent_client = None
        logger.info("Persistent LinkedIn client cleaned up")


if __name__ == '__main__':
    # Test the integration
    print("LinkedIn Automation Test")
    print("=" * 50)

    client = LinkedInClient(headless=False)

    if client.initialize():
        if not client._is_logged_in:
            print("\n📝 Please log in to LinkedIn...")
            if client.wait_for_login(timeout=120):
                print("\n✓ Login successful!")
                
                # Test post
                test_content = f"Test post from AI Dashboard - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                print(f"\nPosting test content...")
                success, msg = client.post_content(test_content)
                print(f"Result: {msg}")
            else:
                print("\n✗ Login failed")
        else:
            print("\n✓ Already logged in")
            
            # Test post
            test_content = f"Test post from AI Dashboard - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            print(f"\nPosting test content...")
            success, msg = client.post_content(test_content)
            print(f"Result: {msg}")

    client.cleanup()
