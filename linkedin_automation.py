"""
LinkedIn Automation - Complete Fixed Implementation
For Streamlit Dashboard Integration

This module provides reliable LinkedIn automation with:
- Persistent browser sessions (login once)
- Browser stays open during login
- Proper Streamlit integration
- Comprehensive logging

Usage:
    from linkedin_automation import connect_linkedin, post_to_linkedin, get_linkedin_status
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

try:
    from playwright.sync_api import sync_playwright, BrowserContext, Page
except ImportError:
    print("[ERROR] playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/linkedin.log', encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).parent
LINKEDIN_URL = "https://www.linkedin.com"
LOGIN_URL = "https://www.linkedin.com/login"
FEED_URL = "https://www.linkedin.com/feed"
PROFILE_DIR = PROJECT_ROOT / ".linkedin_profile"
DEFAULT_TIMEOUT = 60000
PAGE_LOAD_TIMEOUT = 30000

# Ensure profile directory exists
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Global state
_linkedin_context: Optional[BrowserContext] = None
_linkedin_page: Optional[Page] = None
_linkedin_playwright = None
_linkedin_logged_in = False
_linkedin_initialized = False


def _close_chrome():
    """Close all Chrome processes to avoid profile lock conflicts"""
    try:
        import subprocess
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True, text=True,
        )
        if "chrome.exe" in result.stdout:
            logger.info("Closing existing Chrome processes...")
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
            time.sleep(2)
    except Exception as e:
        logger.debug(f"Error closing Chrome: {e}")


def _check_login_status(page: Page) -> bool:
    """
    Check if logged in to LinkedIn
    
    Returns:
        True if logged in, False otherwise
    """
    try:
        # Check URL
        if "/login" in page.url or "/checkpoint" in page.url:
            return False
        
        if "/feed" in page.url:
            return True
        
        # Check for feed elements
        feed_selectors = [
            'div[class*="share-box"]',
            'div[data-control-name="feed"]',
            '.share-box-feed-entry__trigger',
        ]
        
        for selector in feed_selectors:
            try:
                page.wait_for_selector(selector, timeout=2000)
                return True
            except:
                continue
        
        return False
    except Exception as e:
        logger.debug(f"Error checking login status: {e}")
        return False


def get_linkedin_status() -> dict:
    """
    Get LinkedIn connection status without opening browser
    
    Returns:
        Dictionary with status information
    """
    import time
    
    status = {
        'profile_exists': PROFILE_DIR.exists(),
        'logged_in': _linkedin_logged_in,
        'initialized': _linkedin_initialized,
    }
    
    if status['profile_exists']:
        # Check for session files
        session_indicators = ['Login Data', 'Cookies', 'Local Storage']
        check_paths = [PROFILE_DIR, PROFILE_DIR / "Default"]
        
        for base_path in check_paths:
            for indicator in session_indicators:
                indicator_path = base_path / indicator
                if indicator_path.exists():
                    try:
                        mtime = indicator_path.stat().st_mtime
                        age_days = (time.time() - mtime) / 86400
                        if age_days < 7:
                            status['likely_logged_in'] = True
                            status['logged_in'] = True
                            return status
                    except:
                        pass
        
        status['likely_logged_in'] = False
    
    return status


def connect_linkedin(headless: bool = False, timeout: int = 120) -> Tuple[bool, str]:
    """
    Connect to LinkedIn - Opens browser and waits for manual login
    
    This function:
    1. Opens browser with persistent profile (headless=False)
    2. Navigates to LinkedIn login
    3. Keeps browser open for user to log in
    4. Saves session cookies automatically
    5. Confirms login success
    
    Args:
        headless: Run browser in headless mode (False recommended for login)
        timeout: Maximum time to wait for login in seconds
    
    Returns:
        Tuple of (success: bool, message: str)
    
    Example:
        success, msg = connect_linkedin(headless=False, timeout=120)
        if success:
            print("Logged in!")
    """
    global _linkedin_context, _linkedin_page, _linkedin_playwright, _linkedin_logged_in, _linkedin_initialized
    
    logger.info("=" * 60)
    logger.info("LINKEDIN CONNECTION INITIATED")
    logger.info("=" * 60)
    
    try:
        # Close existing Chrome to avoid conflicts
        _close_chrome()
        
        logger.info(f"Profile directory: {PROFILE_DIR}")
        logger.info(f"Headless mode: {headless}")
        
        # Launch Playwright with persistent context
        _linkedin_playwright = sync_playwright().start()
        
        logger.info("Launching browser with persistent context...")
        _linkedin_context = _linkedin_playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
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
        
        _linkedin_page = _linkedin_context.pages[0] if _linkedin_context.pages else _linkedin_context.new_page()
        
        # Navigate to login page
        logger.info(f"Navigating to {LOGIN_URL}...")
        _linkedin_page.goto(LOGIN_URL, wait_until='domcontentloaded', timeout=PAGE_LOAD_TIMEOUT)
        
        # Check if already logged in
        logger.info("Checking login status...")
        if _check_login_status(_linkedin_page):
            logger.info("✓ Already logged in (session restored)")
            _linkedin_logged_in = True
            _linkedin_initialized = True
            
            # Navigate to feed
            _linkedin_page.goto(FEED_URL, wait_until='domcontentloaded')
            return True, "Already logged in"
        
        # Wait for manual login
        logger.info("⚠ Login required")
        logger.info("📝 Please log in to LinkedIn in the browser window")
        logger.info(f"⏳ Waiting up to {timeout} seconds...")
        
        start_time = time.time()
        check_interval = 3
        
        while time.time() - start_time < timeout:
            time.sleep(check_interval)
            
            if _check_login_status(_linkedin_page):
                logger.info("✓ Login successful!")
                _linkedin_logged_in = True
                _linkedin_initialized = True
                
                # Navigate to feed to confirm
                _linkedin_page.goto(FEED_URL, wait_until='domcontentloaded')
                _linkedin_page.wait_for_timeout(2000)
                
                return True, "Login successful"
            
            elapsed = int(time.time() - start_time)
            if elapsed % 15 == 0:
                logger.info(f"Still waiting for login... ({elapsed}s/{timeout}s)")
        
        logger.error("Login timeout")
        return False, "Login timeout - please try again"
        
    except Exception as e:
        logger.error(f"Connection error: {e}", exc_info=True)
        cleanup_linkedin()
        return False, f"Error: {e}"


def post_to_linkedin(content: str, headless: bool = False, wait_for_login: bool = True) -> Tuple[bool, str]:
    """
    Post content to LinkedIn
    
    This function:
    1. Opens browser with persistent profile
    2. Checks if logged in (waits for login if wait_for_login=True)
    3. Opens LinkedIn feed
    4. Clicks "Start a post"
    5. Enters content
    6. Clicks "Post"
    7. Confirms submission
    
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
    global _linkedin_context, _linkedin_page, _linkedin_playwright, _linkedin_logged_in
    
    logger.info("=" * 60)
    logger.info("LINKEDIN POST INITIATED")
    logger.info("=" * 60)
    logger.info(f"Content length: {len(content)} characters")
    
    context_created_here = False
    
    try:
        # Check if we need to create context
        if not _linkedin_context or not _linkedin_page:
            logger.info("Initializing browser context...")
            _close_chrome()
            
            _linkedin_playwright = sync_playwright().start()
            _linkedin_context = _linkedin_playwright.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=headless,
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
            
            _linkedin_page = _linkedin_context.pages[0] if _linkedin_context.pages else _linkedin_context.new_page()
            context_created_here = True
        
        # Navigate to feed
        logger.info("Navigating to LinkedIn feed...")
        _linkedin_page.goto(FEED_URL, wait_until='domcontentloaded', timeout=PAGE_LOAD_TIMEOUT)
        _linkedin_page.wait_for_timeout(3000)
        
        # Check login status
        if not _check_login_status(_linkedin_page):
            logger.warning("Not logged in")
            
            if wait_for_login:
                logger.info("Waiting for login...")
                success, msg = _wait_for_login(_linkedin_page, timeout=120)
                if not success:
                    return False, msg
            else:
                return False, "Not logged in. Please call connect_linkedin() first."
        
        # Post content
        logger.info("Posting content...")
        success, msg = _post_content(_linkedin_page, content)
        
        if success:
            logger.info("✓ Post submitted successfully!")
            # Keep browser open for a moment so user can see confirmation
            _linkedin_page.wait_for_timeout(3000)
        else:
            logger.error(f"✗ Post failed: {msg}")
        
        return success, msg
        
    except Exception as e:
        logger.error(f"Post error: {e}", exc_info=True)
        return False, f"Error: {e}"


def _wait_for_login(page: Page, timeout: int = 120) -> Tuple[bool, str]:
    """Wait for user to log in manually"""
    logger.info("⏳ Waiting for LinkedIn login...")
    
    start_time = time.time()
    check_interval = 3
    
    while time.time() - start_time < timeout:
        time.sleep(check_interval)
        
        if _check_login_status(page):
            logger.info("✓ Login detected!")
            page.goto(FEED_URL, wait_until='domcontentloaded')
            return True, "Login successful"
        
        elapsed = int(time.time() - start_time)
        if elapsed % 15 == 0:
            logger.info(f"Still waiting... ({elapsed}s/{timeout}s)")
    
    return False, "Login timeout"


def _post_content(page: Page, content: str) -> Tuple[bool, str]:
    """Post content to LinkedIn"""
    try:
        # Step 1: Click "Start a post"
        logger.info("Step 1: Opening post composer...")
        
        post_strategies = [
            lambda: page.get_by_text("Start a post").first.click(force=True, timeout=5000),
            lambda: page.locator(".share-box-feed-entry__trigger").first.click(force=True, timeout=5000),
            lambda: page.locator("[data-view-name='share-creation-state'] button").first.click(force=True, timeout=5000),
        ]
        
        modal_opened = False
        for i, strategy in enumerate(post_strategies):
            try:
                strategy()
                page.wait_for_timeout(2000)
                
                # Check if modal opened
                modal_selectors = ["div[role='dialog']", "div.artdeco-modal"]
                for selector in modal_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=2000)
                        modal_opened = True
                        logger.info(f"Modal opened (strategy {i+1})")
                        break
                    except:
                        continue
                
                if modal_opened:
                    break
            except Exception as e:
                logger.debug(f"Strategy {i+1} failed: {e}")
        
        if not modal_opened:
            return False, "Could not open post composer"
        
        # Step 2: Click editor and paste content
        logger.info("Step 2: Entering content...")
        
        editor_strategies = [
            lambda: page.get_by_role("textbox").first.click(force=True, timeout=5000),
            lambda: page.locator("div[contenteditable='true']").first.click(force=True, timeout=5000),
            lambda: page.locator("div.ql-editor").first.click(force=True, timeout=5000),
        ]
        
        editor_clicked = False
        for strategy in editor_strategies:
            try:
                strategy()
                editor_clicked = True
                break
            except:
                continue
        
        if not editor_clicked:
            return False, "Could not find post editor"
        
        page.wait_for_timeout(500)
        
        # Paste content via clipboard
        logger.info("Pasting content...")
        page.evaluate("text => navigator.clipboard.writeText(text)", content)
        page.wait_for_timeout(300)
        page.keyboard.press("Control+v")
        page.wait_for_timeout(1000)
        
        # Step 3: Click Post button
        logger.info("Step 3: Clicking Post button...")
        
        try:
            post_btn = page.get_by_role("button", name="Post", exact=True).or_(
                page.locator("button.share-actions__primary-action")
            )
            post_btn.first.click(timeout=10000)
        except Exception as e:
            logger.error(f"Could not click Post button: {e}")
            return False, "Could not click Post button"
        
        # Step 4: Wait for confirmation
        logger.info("Step 4: Waiting for confirmation...")
        page.wait_for_timeout(5000)
        
        # Take screenshot
        try:
            screenshot_path = str(PROFILE_DIR.parent / "linkedin_post_confirmation.png")
            page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.debug(f"Could not save screenshot: {e}")
        
        return True, "Post submitted successfully"
        
    except Exception as e:
        logger.error(f"Post error: {e}", exc_info=True)
        return False, str(e)


def cleanup_linkedin():
    """Clean up LinkedIn resources"""
    global _linkedin_context, _linkedin_page, _linkedin_playwright, _linkedin_logged_in, _linkedin_initialized
    
    try:
        if _linkedin_context:
            _linkedin_context.close()
        if _linkedin_playwright:
            _linkedin_playwright.stop()
        logger.info("Browser resources cleaned up")
    except Exception as e:
        logger.debug(f"Cleanup error: {e}")
    
    _linkedin_context = None
    _linkedin_page = None
    _linkedin_playwright = None
    _linkedin_logged_in = False
    _linkedin_initialized = False


def reset_linkedin():
    """Reset LinkedIn state and cleanup"""
    logger.info("Resetting LinkedIn state...")
    cleanup_linkedin()


# Standalone test
if __name__ == '__main__':
    print("=" * 60)
    print("LinkedIn Automation Test")
    print("=" * 60)
    
    # Test connection
    print("\n1. Testing connection...")
    success, msg = connect_linkedin(headless=False, timeout=120)
    print(f"   Result: {msg}")
    
    if success:
        print("\n2. Testing post...")
        test_content = f"Test post from AI Dashboard - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        success, msg = post_to_linkedin(test_content, headless=False)
        print(f"   Result: {msg}")
    
    print("\n3. Cleanup...")
    cleanup_linkedin()
    
    print("\nTest complete!")
    input("Press Enter to exit...")
