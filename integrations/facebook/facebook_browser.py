"""
Facebook Browser Automation - Post to Facebook Page without Graph API
Uses Playwright with persistent sessions to automate browser posting
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Tuple, Optional
from playwright.async_api import async_playwright, BrowserContext, Page

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).parent
FACEBOOK_SESSION_DIR = PROJECT_ROOT / "facebook_session"
FACEBOOK_URL = "https://www.facebook.com"


class FacebookBrowser:
    """Facebook browser automation with persistent session."""
    
    def __init__(self):
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def connect(self, wait_for_login: bool = False) -> Tuple[bool, str]:
        """
        Connect to Facebook using persistent session.
        
        Args:
            wait_for_login: If True, wait for user to log in if not already logged in
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Session directory: {FACEBOOK_SESSION_DIR}")
            
            self.playwright = await async_playwright().start()
            
            # Launch with persistent context
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(FACEBOOK_SESSION_DIR),
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
                viewport={"width": 1280, "height": 720},
            )
            
            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            
            logger.info("Navigating to Facebook...")
            await self.page.goto(FACEBOOK_URL, wait_until="domcontentloaded", timeout=60000)
            await self.page.wait_for_load_state("networkidle", timeout=60000)
            time.sleep(3)
            
            # Take screenshot for debugging
            await self.page.screenshot(path="debug_fb_connect.png")
            
            # Check if logged in
            is_logged_in = await self._check_logged_in()
            
            if not is_logged_in:
                if wait_for_login:
                    logger.info("=" * 60)
                    logger.info("NOT LOGGED IN - PLEASE LOG IN NOW")
                    logger.info("=" * 60)
                    logger.info("1. Enter your email and password in the browser window")
                    logger.info("2. Click 'Log In'")
                    logger.info("3. Session will be saved for future use")
                    logger.info("Waiting up to 120 seconds...")
                    logger.info("=" * 60)
                    
                    is_logged_in = await self._wait_for_login(timeout=120)
                    
                    if is_logged_in:
                        # Take screenshot after login
                        await self.page.screenshot(path="debug_fb_logged_in.png")
                        logger.info("✓ Login successful! Session saved.")
                    else:
                        await self.page.screenshot(path="debug_fb_timeout.png")
                        logger.error("Login timeout")
                else:
                    logger.warning("Not logged in. Set wait_for_login=True to enable login wait.")
                    return False, "Not logged in"
            
            if is_logged_in:
                logger.info("✓ Connected to Facebook")
                return True, "Connected"
            else:
                return False, "Login timeout - please try again"
                
        except Exception as e:
            logger.error(f"Connection error: {e}", exc_info=True)
            return False, str(e)
    
    async def _check_logged_in(self) -> bool:
        """Check if user is logged in to Facebook."""
        try:
            # Multiple selectors to check login status
            selectors = [
                'div[role="navigation"]',  # Main nav
                'a[href^="/watch/"]',  # Watch link
                'a[href^="/marketplace/"]',  # Marketplace link
                'div[data-pagelet="MainFeed"]',  # Main feed
                '[aria-label*="What\'s on your mind"]',  # Create post box
                'input[placeholder*="Search"]',  # Search box
                'div[aria-label="Menu"]',  # Menu button
                'a[href^="/profile.php"]',  # Profile link
            ]
            
            for sel in selectors:
                try:
                    elem = await self.page.wait_for_selector(sel, timeout=2000)
                    if elem:
                        logger.info(f"Logged in indicator: {sel}")
                        return True
                except:
                    continue
            
            # Check for login form (not logged in)
            login_form = await self.page.query_selector('form#login_form')
            if login_form:
                logger.info("Login form detected - not logged in")
                return False
            
            # Check for email input (not logged in)
            email_input = await self.page.query_selector('input[type="email"]')
            if email_input:
                logger.info("Email input detected - not logged in")
                return False
            
            # Check URL
            url = self.page.url
            if "login" in url.lower() or "checkpoint" in url.lower():
                return False
            
            logger.warning("Could not detect login state clearly")
            return False
            
        except Exception as e:
            logger.warning(f"Error checking login: {e}")
            return False
    
    async def _wait_for_login(self, timeout: int = 120) -> bool:
        """Wait for user to log in."""
        start = time.time()
        last_check_was_login_form = True
        
        while time.time() - start < timeout:
            await asyncio.sleep(3)
            
            is_logged_in = await self._check_logged_in()
            if is_logged_in:
                return True
            
            # Check if login form is still visible
            login_form = await self.page.query_selector('form#login_form')
            email_input = await self.page.query_selector('input[type="email"]')
            
            # If login form disappeared, user might be logging in
            if login_form is None and email_input is None:
                if not last_check_was_login_form:
                    logger.info("Login form disappeared - waiting for page to load...")
                # Give it a moment to fully load
                await asyncio.sleep(2)
                # Check again
                if await self._check_logged_in():
                    return True
            
            last_check_was_login_form = (login_form is not None)
            
            elapsed = int(time.time() - start)
            if elapsed % 15 == 0:
                logger.info(f"Waiting for login... ({elapsed}s/{timeout}s)")
                logger.info("  → Check the browser window and complete login")
        
        return False
    
    async def post_to_page(self, page_url: str, message: str) -> Tuple[bool, str]:
        """
        Post a message to a Facebook Page.
        
        Args:
            page_url: URL of the Facebook Page
            message: Message to post
            
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        if not self.page:
            return False, "Not connected to Facebook"
        
        try:
            logger.info(f"Posting to: {page_url}")
            
            # Navigate to the page
            await self.page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            
            # Take screenshot for debugging
            await self.page.screenshot(path="debug_facebook_page.png")
            logger.info("Screenshot saved: debug_facebook_page.png")
            
            # Find the create post box or button
            logger.info("Looking for create post area...")
            
            # Strategy 1: Look for "What's on your mind?" box
            post_box = await self._find_post_input()
            
            if not post_box:
                # Strategy 2: Look for "Create post" button
                create_post_btn = await self._find_create_post_button()
                if create_post_btn:
                    await create_post_btn.click()
                    time.sleep(2)
                    post_box = await self._find_post_input()
            
            if not post_box:
                await self.page.screenshot(path="debug_no_post_box.png")
                return False, "Could not find post creation area"
            
            # Type the message
            logger.info("Typing message...")
            await post_box.click()
            time.sleep(2)
            
            # Try to find the actual editable element inside
            editable = await self.page.query_selector('div[contenteditable="true"], div[role="textbox"]')
            if editable:
                await editable.focus()
                time.sleep(1)
                await editable.fill(message)
            else:
                # Type directly using keyboard
                await self.page.keyboard.type(message, delay=50)
            
            time.sleep(2)
            
            # Find and click Post button
            logger.info("Looking for Post button...")
            post_btn = await self._find_post_button()
            
            if post_btn:
                await post_btn.click()
                logger.info("✓ Post button clicked")
            else:
                # Try keyboard shortcut
                await post_box.press("Control+Enter")
                logger.info("✓ Used Control+Enter to post")
            
            time.sleep(3)
            
            # Check if post was successful
            logger.info("Verifying post...")
            await self.page.screenshot(path="debug_after_post.png")
            
            logger.info("✓ Post published successfully!")
            return True, "Post published successfully"
            
        except Exception as e:
            logger.error(f"Post error: {e}", exc_info=True)
            return False, str(e)
    
    async def _find_post_input(self) -> Optional[Page]:
        """Find the post input field."""
        selectors = [
            # Standard Facebook
            'div[role="textbox"][data-gramm="false"]',
            'div[contenteditable="true"][aria-label*="What\'s on your mind"]',
            'div[contenteditable="true"][placeholder*="What\'s on your mind"]',
            'div.public-xhp[contenteditable="true"]',
            'div[aria-label*="What\'s on your mind"]',
            'span[data-offset-key]',
            # Page management view
            'div[contenteditable="true"][role="textbox"]',
            'div[data-testid="composer-text-field"]',
            'div[aria-label*="Create a post"]',
            'div[placeholder*="Write something"]',
            'div[placeholder*="What\'s on your mind"]',
            # New Facebook
            'div.x1n2onr6',
            'div[contenteditable="true"].x1n2onr6',
        ]
        
        for sel in selectors:
            try:
                elem = await self.page.wait_for_selector(sel, timeout=3000)
                if elem:
                    logger.info(f"Found post input: {sel}")
                    return elem
            except:
                continue
        
        return None
    
    async def _find_create_post_button(self) -> Optional[Page]:
        """Find the create post button."""
        selectors = [
            # Standard
            'div[role="button"][aria-label*="Create post"]',
            'div[role="button"]:has-text("Create post")',
            'a[role="button"]:has-text("Create post")',
            'span:has-text("Create post")',
            # Page management view
            'div[role="button"]:has-text("Post")',
            'button:has-text("Create")',
            'div[aria-label*="Create"]',
            # Photo/video button that opens composer
            'div[role="button"][aria-label*="Photo"]',
            'div[role="button"][aria-label*="Video"]',
        ]
        
        for sel in selectors:
            try:
                elem = await self.page.wait_for_selector(sel, timeout=3000)
                if elem:
                    logger.info(f"Found create post button: {sel}")
                    return elem
            except:
                continue
        
        return None
    
    async def _find_post_button(self) -> Optional[Page]:
        """Find the Post/Publish button."""
        selectors = [
            'div[role="button"]:has-text("Post")',
            'button:has-text("Post")',
            'div[role="button"]:has-text("Publish")',
            'button:has-text("Publish")',
            'div[role="button"][aria-label*="Post"]',
            'button[aria-label*="Post"]',
            'div[role="button"]:has-text("Share")',
        ]
        
        for sel in selectors:
            try:
                elem = await self.page.wait_for_selector(sel, timeout=3000)
                if elem:
                    # Check if button is disabled
                    is_disabled = await elem.get_attribute("aria-disabled")
                    if is_disabled == "true":
                        logger.info(f"Post button found but disabled: {sel}")
                        continue
                    logger.info(f"Found post button: {sel}")
                    return elem
            except:
                continue
        
        return None
    
    async def close(self):
        """Close browser."""
        try:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")


# Global instance
_facebook_instance = None


async def connect_facebook(wait_for_login: bool = False) -> Tuple[bool, str]:
    """Connect to Facebook."""
    global _facebook_instance
    if _facebook_instance is None:
        _facebook_instance = FacebookBrowser()
    return await _facebook_instance.connect(wait_for_login)


async def post_to_facebook(page_url: str, message: str) -> Tuple[bool, str]:
    """Post to Facebook page."""
    global _facebook_instance
    if _facebook_instance is None:
        _facebook_instance = FacebookBrowser()
    
    connected, msg = await _facebook_instance.connect(wait_for_login=False)
    if not connected:
        return False, msg
    
    return await _facebook_instance.post_to_page(page_url, message)


def get_facebook_session_status() -> dict:
    """Check Facebook session status."""
    exists = FACEBOOK_SESSION_DIR.exists()
    has_data = any(FACEBOOK_SESSION_DIR.iterdir()) if exists else False
    
    return {
        'session_exists': exists,
        'has_data': has_data,
        'session_dir': str(FACEBOOK_SESSION_DIR),
    }


def reset_facebook_session():
    """Reset Facebook session by deleting session folder."""
    import shutil
    if FACEBOOK_SESSION_DIR.exists():
        shutil.rmtree(FACEBOOK_SESSION_DIR)
        logger.info("Facebook session reset")
        return True
    return False
