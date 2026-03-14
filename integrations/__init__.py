"""
AI Agency Dashboard - Integration Modules Package

This package contains all external service integrations:
- Gmail API (OAuth 2.0)
- WhatsApp Web (Playwright automation)
- LinkedIn (Playwright automation)
- Facebook Page (Meta Graph API)
"""

import sys
from pathlib import Path

# Add parent directory to path to import root whatsapp_client
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from .gmail_client import GmailClient, send_email, read_inbox, get_user_profile
from .whatsapp_client import WhatsAppClient, send_whatsapp_message
from .linkedin_client import LinkedInClient, post_to_linkedin
from .facebook_client import FacebookClient, post_to_facebook_page

# Import connect_whatsapp and related functions from root whatsapp_client.py
try:
    from whatsapp_client import (
        connect_whatsapp,
        send_whatsapp_message as sync_send_whatsapp,
        get_whatsapp_status as wa_get_status,
        cleanup_whatsapp,
        check_login_status,
        reset_whatsapp,
    )
except ImportError:
    # Fallback if root whatsapp_client.py doesn't exist
    def connect_whatsapp(headless: bool = False, timeout: int = 60):
        return False, "WhatsApp client not available"
    
    def cleanup_whatsapp():
        pass
    
    def check_login_status():
        return False
    
    def reset_whatsapp():
        pass
    
    def wa_get_status():
        return {'session_exists': False, 'logged_in': False, 'initialized': False}

# Import connect_linkedin from linkedin_client
try:
    from .linkedin_client import connect_linkedin, login_to_linkedin, cleanup_persistent_linkedin, get_persistent_client
except ImportError:
    def connect_linkedin(headless: bool = False, timeout: int = 120):
        return False, "LinkedIn client not available"

    def login_to_linkedin(headless: bool = False):
        return False, "LinkedIn client not available"

    def cleanup_persistent_linkedin():
        pass

    def get_persistent_client():
        return None

# Also import from new linkedin_automation.py for better compatibility
try:
    from linkedin_automation import (
        connect_linkedin as wa_connect_linkedin,
        post_to_linkedin as wa_post_linkedin,
        get_linkedin_status as wa_get_li_status,
        cleanup_linkedin,
    )
    
    # Use the new implementation if available
    connect_linkedin = wa_connect_linkedin
    post_to_linkedin = wa_post_linkedin
    get_linkedin_status = wa_get_li_status
    
except ImportError:
    pass  # Use the old implementation

__all__ = [
    'GmailClient', 'send_email', 'read_inbox', 'get_user_profile',
    'WhatsAppClient', 'send_whatsapp_message',
    'LinkedInClient', 'post_to_linkedin',
    'FacebookClient', 'post_to_facebook_page',
    'connect_whatsapp', 'cleanup_whatsapp', 'check_login_status',
    'reset_whatsapp', 'get_whatsapp_status',
    'connect_linkedin', 'login_to_linkedin', 'cleanup_persistent_linkedin',
]

# Alias for get_whatsapp_status
get_whatsapp_status = wa_get_status

__version__ = '1.0.0'
