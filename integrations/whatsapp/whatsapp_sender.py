"""
WhatsApp Sender - Fixed with Reliable Selectors
Based on actual page screenshot analysis
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Tuple
from playwright.async_api import async_playwright, BrowserContext, Page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
USER_DATA_DIR = PROJECT_ROOT / "whatsapp_session"


class WhatsAppSender:
    """Send WhatsApp messages using persistent session."""
    
    def __init__(self):
        self.playwright = None
        self.context: BrowserContext = None
        self.page: Page = None
    
    async def connect(self) -> Tuple[bool, str]:
        """Connect to WhatsApp Web."""
        try:
            logger.info(f"Session: {USER_DATA_DIR}")
            
            self.playwright = await async_playwright().start()
            
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=False,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
                viewport={"width": 1280, "height": 720},
            )
            
            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            
            logger.info("Navigating to WhatsApp...")
            await self.page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
            await self.page.wait_for_load_state("networkidle", timeout=60000)
            time.sleep(3)
            
            # Check login status
            is_logged_in = await self._check_logged_in()
            
            if not is_logged_in:
                logger.info("Waiting for QR scan (60s)...")
                is_logged_in = await self._wait_for_login(60)
            
            if is_logged_in:
                logger.info("✓ Connected")
                return True, "Connected"
            return False, "Not logged in"
            
        except Exception as e:
            logger.error(f"Connect error: {e}")
            return False, str(e)
    
    async def _check_logged_in(self) -> bool:
        """Check if logged in using multiple strategies."""
        # Strategy 1: Look for search box with placeholder
        selectors = [
            'input[placeholder*="Search"]',
            'input[placeholder*="search"]',
            'div[contenteditable="true"]',
            'a[title="Status"]',
            'a[title="Communities"]',
            'span[data-icon="search"]',
        ]
        
        for sel in selectors:
            try:
                elem = await self.page.query_selector(sel)
                if elem:
                    logger.info(f"Logged in indicator: {sel}")
                    return True
            except:
                pass
        
        # Strategy 2: Check URL - if we're on web.whatsapp.com without qr param, likely logged in
        url = self.page.url
        if "web.whatsapp.com" in url and "qr" not in url:
            # Check page content
            content = await self.page.content()
            if "Search or start a new chat" in content or "chat-list" in content:
                logger.info("Logged in (detected by page content)")
                return True
        
        # Strategy 3: Check for QR code
        qr_selectors = ['div[data-ref]', 'canvas[height="198"]']
        for sel in qr_selectors:
            try:
                elem = await self.page.query_selector(sel)
                if elem:
                    logger.info(f"QR code detected")
                    return False
            except:
                pass
        
        # Default: assume logged in
        logger.warning("Assuming logged in")
        return True
    
    async def _wait_for_login(self, timeout: int = 60) -> bool:
        """Wait for QR scan."""
        start = time.time()
        while time.time() - start < timeout:
            if await self._check_logged_in():
                return True
            await asyncio.sleep(2)
        return False
    
    async def send_message(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """Send message."""
        if not self.page:
            return False, "Not connected"
        
        try:
            clean = phone_number.replace("+", "").replace("-", "").replace(" ", "")
            
            logger.info(f"Opening chat: {clean}")
            await self.page.goto(f"https://web.whatsapp.com/send?phone={clean}", 
                               wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            
            # Check for contact not found
            error = await self.page.query_selector('div[data-testid="contact-not-exist-title"]')
            if error:
                return False, "Contact not found"
            
            # Find message input - use very broad selectors
            input_found = None
            selectors = [
                'footer div[contenteditable="true"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"]',
                '[data-testid="compose-input"]',
            ]
            
            for sel in selectors:
                try:
                    elem = await self.page.wait_for_selector(sel, timeout=2000)
                    if elem:
                        input_found = elem
                        logger.info(f"Input: {sel}")
                        break
                except:
                    pass
            
            if not input_found:
                await self.page.screenshot(path="debug_input.png")
                return False, "No input field found"
            
            # Type message
            await input_found.click()
            time.sleep(1)
            await input_found.fill(message)
            time.sleep(1)
            
            # Send
            send_btn = await self.page.query_selector('button[aria-label="Send"]')
            if send_btn:
                await send_btn.click()
            else:
                await input_found.press("Enter")
            
            time.sleep(2)
            logger.info("✓ Sent")
            return True, "Sent"
            
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False, str(e)
    
    async def close(self):
        """Close."""
        try:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass


_sender = None


async def send_whatsapp_from_dashboard(phone: str, msg: str) -> Tuple[bool, str]:
    """Send from dashboard."""
    global _sender
    if _sender is None:
        _sender = WhatsAppSender()
    
    ok, result = await _sender.connect()
    if not ok:
        return False, result
    return await _sender.send_message(phone, msg)


def get_session_status() -> dict:
    """Get status."""
    exists = USER_DATA_DIR.exists()
    return {
        'session_exists': exists,
        'has_data': any(USER_DATA_DIR.iterdir()) if exists else False,
        'session_dir': str(USER_DATA_DIR),
    }
