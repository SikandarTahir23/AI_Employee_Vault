"""
Unified Integration Layer for AI Agency Dashboard

This module provides a simple, unified interface for all communication services:
- Gmail API
- WhatsApp Web (Playwright)
- LinkedIn Automation
- Facebook Graph API

Usage:
    from integrations.whatsapp.whatsapp_sender import send_whatsapp_message, post_to_linkedin, post_to_facebook
"""

import os
import sys
import asyncio
import base64
import logging
import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# PATH CONFIGURATION
# =============================================================================
PROJECT_ROOT = Path(__file__).parent
CREDENTIALS_FILE = PROJECT_ROOT / 'credentials.json'
TOKEN_FILE = PROJECT_ROOT / 'token.json'
WHATSAPP_SESSION_DIR = PROJECT_ROOT / ".whatsapp_session"
LINKEDIN_PROFILE_DIR = PROJECT_ROOT / ".playwright_profile"

# =============================================================================
# GMAIL INTEGRATION
# =============================================================================

_gmail_service = None
_gmail_authenticated = False


def _get_gmail_service():
    """Get or create Gmail API service"""
    global _gmail_service, _gmail_authenticated
    
    if _gmail_authenticated and _gmail_service:
        return _gmail_service
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        
        creds = None
        
        # Load existing token
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
                logger.info("Loaded existing Gmail token")
            except Exception as e:
                logger.warning(f"Error loading Gmail token: {e}")
                TOKEN_FILE.unlink(missing_ok=True)
                creds = None
        
        # Refresh or authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing Gmail token...")
                    creds.refresh(Request())
                    with open(TOKEN_FILE, 'w') as f:
                        f.write(creds.to_json())
                except Exception as e:
                    logger.warning(f"Gmail token refresh failed: {e}")
                    creds = None
            
            if not creds:
                if not CREDENTIALS_FILE.exists():
                    logger.error("credentials.json not found for Gmail")
                    return None
                
                logger.info("Starting Gmail OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                
                # Try multiple ports
                for port in [8090, 8091, 8092, 0]:
                    try:
                        creds = flow.run_local_server(port=port, open_browser=True)
                        break
                    except OSError:
                        if port == 0:
                            raise
                        logger.warning(f"Port {port} in use, trying next...")
                
                # Save token
                with open(TOKEN_FILE, 'w') as f:
                    f.write(creds.to_json())
                logger.info("Gmail token saved")
        
        _gmail_service = build('gmail', 'v1', credentials=creds)
        _gmail_authenticated = True
        logger.info("Gmail API service created")
        return _gmail_service
        
    except Exception as e:
        logger.error(f"Gmail authentication failed: {e}")
        return None


def send_email(to: str, subject: str, body: str, 
               from_email: Optional[str] = None,
               html: bool = False) -> Tuple[bool, str]:
    """
    Send an email via Gmail API
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        from_email: Optional sender email (defaults to authenticated account)
        html: If True, send as HTML
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    service = _get_gmail_service()
    if not service:
        return False, "Gmail not authenticated. Please run gmail_authenticate() first."
    
    try:
        message = EmailMessage()
        message['to'] = to
        message['subject'] = subject
        
        if from_email:
            message['from'] = from_email
        else:
            # Get authenticated user email
            try:
                profile = service.users().getProfile(userId='me').execute()
                message['from'] = profile.get('emailAddress', '')
            except:
                message['from'] = ''
        
        if html:
            message.add_alternative(body, subtype='html')
        else:
            message.set_content(body)
        
        # Encode and send
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': encoded_message}
        ).execute()
        
        msg_id = sent_message['id']
        logger.info(f"Email sent successfully! Message ID: {msg_id}")
        return True, f"Email sent (ID: {msg_id})"
        
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def read_gmail(max_results: int = 10, 
               query: str = 'is:inbox') -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Read emails from Gmail inbox
    
    Args:
        max_results: Maximum number of emails to retrieve
        query: Gmail search query (default: 'is:inbox')
    
    Returns:
        Tuple of (success: bool, emails: list)
        Each email dict contains: id, subject, from, to, date, snippet
    """
    service = _get_gmail_service()
    if not service:
        return False, []
    
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            logger.info("No messages found")
            return True, []
        
        emails = []
        for msg in messages:
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                headers = message.get('payload', {}).get('headers', [])
                email_data = {
                    'id': message['id'],
                    'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), ''),
                    'from': next((h['value'] for h in headers if h['name'] == 'From'), ''),
                    'to': next((h['value'] for h in headers if h['name'] == 'To'), ''),
                    'date': next((h['value'] for h in headers if h['name'] == 'Date'), ''),
                    'snippet': message.get('snippet', '')
                }
                emails.append(email_data)
                
            except Exception as e:
                logger.warning(f"Error fetching message {msg['id']}: {e}")
                continue
        
        logger.info(f"Retrieved {len(emails)} emails")
        return True, emails
        
    except Exception as e:
        error_msg = f"Failed to read Gmail: {str(e)}"
        logger.error(error_msg)
        return False, []


def gmail_authenticate() -> Tuple[bool, str]:
    """
    Force Gmail re-authentication
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    global _gmail_service, _gmail_authenticated
    
    # Clear existing auth
    _gmail_service = None
    _gmail_authenticated = False
    
    # Get fresh service
    service = _get_gmail_service()
    
    if service:
        try:
            profile = service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'Unknown')
            return True, f"Authenticated as {email}"
        except:
            return True, "Authenticated"
    else:
        return False, "Authentication failed"


def get_gmail_status() -> Dict[str, Any]:
    """Get Gmail authentication status"""
    return {
        'configured': CREDENTIALS_FILE.exists(),
        'authenticated': _gmail_authenticated,
        'token_exists': TOKEN_FILE.exists()
    }


# =============================================================================
# WHATSAPP INTEGRATION
# =============================================================================
# Re-export from whatsapp_client for backward compatibility
try:
    from integrations.whatsapp.whatsapp_client import (
        connect_whatsapp,
        send_whatsapp_message as _send_whatsapp,
        get_whatsapp_status as _get_whatsapp_status,
        cleanup_whatsapp as whatsapp_cleanup,
        check_login_status,
        reset_whatsapp,
        USER_DATA_DIR as WHATSAPP_SESSION_DIR,
    )
    
    # Wrapper for send_whatsapp_message to match original signature
    def send_whatsapp_message(phone_number: str, message: str,
                              headless: bool = False,
                              timeout: int = 60) -> Tuple[bool, str]:
        """
        Send a WhatsApp message via whatsapp_client
        
        Args:
            phone_number: Phone number with country code (e.g., '+1234567890')
            message: Message text to send
            headless: Run browser in headless mode
            timeout: Timeout for login (not used in sync version)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        return _send_whatsapp(phone_number, message, headless=headless)
    
    # Wrapper for get_whatsapp_status to match original signature
    def get_whatsapp_status() -> Dict[str, Any]:
        """Get WhatsApp connection status"""
        return _get_whatsapp_status()
    
    logger.info("WhatsApp integration loaded from whatsapp_client.py")
    
except ImportError as e:
    logger.warning(f"Could not import whatsapp_client: {e}")
    logger.info("Using fallback WhatsApp integration")
    
    # Fallback implementation
    _whatsapp_context = None
    _whatsapp_page = None
    _whatsapp_playwright = None
    _whatsapp_logged_in = False
    
    def connect_whatsapp(headless: bool = False, timeout: int = 60) -> Tuple[bool, str]:
        return False, "WhatsApp client not available"
    
    def send_whatsapp_message(phone_number: str, message: str,
                              headless: bool = False,
                              timeout: int = 60) -> Tuple[bool, str]:
        return False, "WhatsApp client not available"
    
    def get_whatsapp_status() -> Dict[str, Any]:
        return {
            'session_exists': False,
            'logged_in': False,
            'initialized': False
        }
    
    def whatsapp_cleanup():
        pass
    
    def check_login_status() -> bool:
        return False
    
    def reset_whatsapp():
        pass


# =============================================================================
# LINKEDIN INTEGRATION
# =============================================================================

_linkedin_context = None
_linkedin_page = None
_linkedin_playwright = None
_linkedin_logged_in = False


def _init_linkedin(headless: bool = False):
    """Initialize LinkedIn with Playwright (sync version)"""
    global _linkedin_context, _linkedin_page, _linkedin_playwright, _linkedin_logged_in
    
    if _linkedin_page:
        return True
    
    try:
        from playwright.sync_api import sync_playwright
        
        logger.info("Initializing LinkedIn...")
        
        # Create profile directory
        LINKEDIN_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Close existing Chrome to avoid conflicts
        try:
            import subprocess
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                          capture_output=True, timeout=5)
            time.sleep(1)
        except:
            pass
        
        # Launch Playwright
        _linkedin_playwright = sync_playwright().start()
        
        # Launch browser with persistent context
        _linkedin_context = _linkedin_playwright.chromium.launch_persistent_context(
            user_data_dir=str(LINKEDIN_PROFILE_DIR),
            headless=headless,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ],
            viewport={'width': 1280, 'height': 720},
            timeout=60000
        )
        
        _linkedin_page = _linkedin_context.pages[0] if _linkedin_context.pages else _linkedin_context.new_page()
        
        # Navigate to LinkedIn feed
        _linkedin_page.goto("https://www.linkedin.com/feed/", 
                           wait_until='domcontentloaded', 
                           timeout=60000)
        
        try:
            _linkedin_page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        
        _linkedin_page.wait_for_timeout(3000)
        
        # Check login status
        _linkedin_logged_in = "/login" not in _linkedin_page.url
        
        logger.info("LinkedIn initialized")
        return True
        
    except Exception as e:
        logger.error(f"LinkedIn initialization failed: {e}")
        return False


def _linkedin_wait_for_login(timeout: int = 120) -> bool:
    """Wait for manual LinkedIn login"""
    global _linkedin_logged_in
    
    logger.info("Waiting for LinkedIn login...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        time.sleep(3)
        
        if _linkedin_page and "/login" not in _linkedin_page.url:
            if "/feed" in _linkedin_page.url:
                logger.info("LinkedIn login successful!")
                _linkedin_logged_in = True
                return True
        
        elapsed = int(time.time() - start_time)
        if elapsed % 15 == 0:
            logger.info(f"Waiting for LinkedIn login... ({elapsed}s/{timeout}s)")
    
    logger.error("LinkedIn login timeout")
    return False


def post_to_linkedin(content: str, headless: bool = False) -> Tuple[bool, str]:
    """
    Post content to LinkedIn
    
    Args:
        content: Post content (text, can include emojis and hashtags)
        headless: Run browser in headless mode
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    global _linkedin_logged_in
    
    # Initialize
    if not _init_linkedin(headless):
        return False, "Failed to initialize LinkedIn"
    
    if not _linkedin_logged_in:
        if not _linkedin_wait_for_login(timeout=120):
            return False, "LinkedIn not logged in. Please log in."
    
    try:
        logger.info(f"Posting to LinkedIn ({len(content)} chars)...")
        
        page = _linkedin_page
        
        # Click "Start a post" - multiple strategies
        modal_opened = False
        strategies = [
            lambda: page.get_by_text("Start a post").first.click(force=True, timeout=5000),
            lambda: page.locator(".share-box-feed-entry__trigger").first.click(force=True, timeout=5000),
            lambda: page.evaluate("""
                () => {
                    const all = document.querySelectorAll('*');
                    let best = null;
                    for (const el of all) {
                        const text = (el.textContent || '').trim();
                        if (text.includes('Start a post') && el.children.length < 3) {
                            if (!best || text.length < best.textContent.trim().length) {
                                best = el;
                            }
                        }
                    }
                    if (best) { best.click(); return true; }
                    return false;
                }
            """),
            lambda: page.locator("[aria-label*='Start a post']").first.click(force=True, timeout=5000),
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                strategy()
                page.wait_for_timeout(2000)
                
                # Check if modal opened
                modal_selectors = ["div[role='dialog']", "div.artdeco-modal"]
                for selector in modal_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=3000)
                        modal_opened = True
                        logger.info(f"Post modal opened (strategy {i+1})")
                        break
                    except:
                        continue
                
                if modal_opened:
                    break
            except Exception as e:
                logger.debug(f"Strategy {i+1} failed: {type(e).__name__}")
        
        if not modal_opened:
            return False, "Could not open post composer"
        
        page.wait_for_timeout(1000)
        
        # Click editor
        editor_clicked = False
        editor_strategies = [
            lambda: page.get_by_role("textbox").first.click(force=True, timeout=5000),
            lambda: page.locator("div[contenteditable='true']").first.click(force=True, timeout=5000),
            lambda: page.locator("div.ql-editor").first.click(force=True, timeout=5000),
        ]
        
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
        page.evaluate("text => navigator.clipboard.writeText(text)", content)
        page.wait_for_timeout(300)
        page.keyboard.press("Control+v")
        page.wait_for_timeout(1000)
        
        # Click Post button
        try:
            post_btn = page.get_by_role("button", name="Post", exact=True).or_(
                page.locator("button.share-actions__primary-action")
            )
            post_btn.first.click(timeout=30000)
        except Exception as e:
            return False, f"Could not click Post button: {e}"
        
        # Wait for confirmation
        page.wait_for_timeout(5000)
        
        # Screenshot
        try:
            screenshot_path = str(PROJECT_ROOT / "linkedin_post_confirmation.png")
            page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
        except:
            pass
        
        logger.info("LinkedIn post submitted!")
        return True, "Post submitted successfully"
        
    except Exception as e:
        error_msg = f"Failed to post to LinkedIn: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def get_linkedin_status() -> Dict[str, Any]:
    """Get LinkedIn connection status"""
    return {
        'profile_exists': LINKEDIN_PROFILE_DIR.exists(),
        'logged_in': _linkedin_logged_in,
        'initialized': _linkedin_page is not None
    }


def linkedin_cleanup():
    """Clean up LinkedIn resources"""
    global _linkedin_context, _linkedin_page, _linkedin_playwright, _linkedin_logged_in
    
    try:
        if _linkedin_context:
            _linkedin_context.close()
        if _linkedin_playwright:
            _linkedin_playwright.stop()
    except Exception as e:
        logger.warning(f"LinkedIn cleanup error: {e}")
    
    _linkedin_context = None
    _linkedin_page = None
    _linkedin_playwright = None
    _linkedin_logged_in = False


# =============================================================================
# FACEBOOK INTEGRATION
# =============================================================================

def _get_facebook_client():
    """Get Facebook Graph API client"""
    access_token = os.getenv('META_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    
    if not access_token or not page_id:
        logger.error("Facebook credentials not found in .env")
        return None
    
    return {
        'access_token': access_token,
        'page_id': page_id,
        'api_version': 'v21.0'
    }


def post_to_facebook(message: str, 
                     link: Optional[str] = None,
                     photo_url: Optional[str] = None) -> Tuple[bool, str]:
    """
    Post to Facebook Page via Graph API
    
    Args:
        message: Post message/text
        link: Optional link to share
        photo_url: Optional photo URL to attach
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    fb_config = _get_facebook_client()
    if not fb_config:
        return False, "Facebook credentials not configured. Check .env file."
    
    try:
        import requests
        
        api_base = f'https://graph.facebook.com/{fb_config["api_version"]}'
        url = f"{api_base}/{fb_config['page_id']}/feed"
        
        params = {
            'access_token': fb_config['access_token'],
            'message': message
        }
        
        if link:
            params['link'] = link
        
        if photo_url:
            params['url'] = photo_url
        
        logger.info(f"Posting to Facebook Page {fb_config['page_id']}...")
        
        response = requests.post(url, params=params, timeout=30)
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return False, f"Facebook API Error: {error_msg}"
            except:
                return False, f"HTTP Error {response.status_code}"
        
        result = response.json()
        post_id = result.get('id', 'Unknown')
        
        logger.info(f"Facebook post created! Post ID: {post_id}")
        return True, f"Post created: {post_id}"
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Facebook request failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to post to Facebook: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def get_facebook_status() -> Dict[str, Any]:
    """Get Facebook configuration status"""
    access_token = os.getenv('META_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    
    configured = bool(access_token and page_id)
    
    if configured:
        # Try to validate token
        try:
            import requests
            api_base = f'https://graph.facebook.com/v21.0/{page_id}'
            params = {'access_token': access_token, 'fields': 'id,name'}
            response = requests.get(api_base, params=params, timeout=10)
            
            if response.status_code == 200:
                page_data = response.json()
                return {
                    'configured': True,
                    'valid': True,
                    'page_name': page_data.get('name', 'Unknown'),
                    'page_id': page_id
                }
        except:
            pass
        
        return {
            'configured': True,
            'valid': False,
            'page_id': page_id
        }
    
    return {
        'configured': False,
        'valid': False
    }


def validate_facebook_token() -> Tuple[bool, str]:
    """Validate Facebook access token"""
    fb_config = _get_facebook_client()
    if not fb_config:
        return False, "Facebook credentials not configured"
    
    try:
        import requests
        
        # Get page info to validate token
        api_base = f'https://graph.facebook.com/v21.0/{fb_config["page_id"]}'
        params = {
            'access_token': fb_config['access_token'],
            'fields': 'id,name'
        }
        
        response = requests.get(api_base, params=params, timeout=10)
        
        if response.status_code == 200:
            page_data = response.json()
            return True, f"Valid token for page: {page_data.get('name', 'Unknown')}"
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Invalid token')
            return False, error_msg
            
    except Exception as e:
        return False, f"Validation error: {str(e)}"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_all_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all integrations"""
    return {
        'gmail': get_gmail_status(),
        'whatsapp': get_whatsapp_status(),
        'linkedin': get_linkedin_status(),
        'facebook': get_facebook_status()
    }


def cleanup_all():
    """Clean up all resources"""
    whatsapp_cleanup()
    linkedin_cleanup()


# =============================================================================
# MAIN (Testing)
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("           INTEGRATIONS MODULE TEST")
    print("=" * 70)
    
    # Get status
    status = get_all_status()
    
    print("\nIntegration Status:\n")
    
    for service, info in status.items():
        print(f"{service.upper()}:")
        for key, value in info.items():
            icon = "✓" if value else "✗" if value is False else "•"
            print(f"  {icon} {key}: {value}")
        print()
    
    print("=" * 70)
