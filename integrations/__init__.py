"""
AI Agency Dashboard - Integration Modules Package

This package contains all external service integrations:
- Gmail API (OAuth 2.0)
- WhatsApp Web (Playwright automation)
- LinkedIn (Playwright automation)
- Facebook Page (Meta Graph API + Browser automation)
"""

import sys
from pathlib import Path

# Add parent directory to path
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Gmail imports
try:
    from .gmail.gmail_client import GmailClient, send_email, read_inbox, get_user_profile
    from .gmail.gmail_integration import GmailIntegration
except ImportError as e:
    print(f"Warning: Could not import Gmail modules: {e}")
    def send_email(*args, **kwargs): return False
    def read_inbox(*args, **kwargs): return []
    def get_user_profile(*args, **kwargs): return {}

# WhatsApp imports
try:
    from .whatsapp.whatsapp_client import WhatsAppClient, connect_whatsapp, send_whatsapp_message, get_whatsapp_status
    from .whatsapp.whatsapp_sender import WhatsAppSender
except ImportError as e:
    print(f"Warning: Could not import WhatsApp modules: {e}")
    def connect_whatsapp(*args, **kwargs): return (False, "Not available")
    def send_whatsapp_message(*args, **kwargs): return False
    def get_whatsapp_status(*args, **kwargs): return {}

# LinkedIn imports
try:
    from .linkedin.linkedin_client import LinkedInClient, post_to_linkedin, connect_linkedin, get_linkedin_status
    from .linkedin.linkedin_automation import LinkedInAutomation
except ImportError as e:
    print(f"Warning: Could not import LinkedIn modules: {e}")
    def post_to_linkedin(*args, **kwargs): return (False, "Not available")
    def connect_linkedin(*args, **kwargs): return (False, "Not available")
    def get_linkedin_status(*args, **kwargs): return {}

# Facebook imports
try:
    from .facebook.facebook_client import FacebookClient, post_to_facebook_page, validate_facebook_token
    from .facebook.facebook_browser import FacebookBrowser, connect_facebook, post_to_facebook
except ImportError as e:
    print(f"Warning: Could not import Facebook modules: {e}")
    def post_to_facebook_page(*args, **kwargs): return (False, "Not available")
    def post_to_facebook(*args, **kwargs): return (False, "Not available")
    def validate_facebook_token(*args, **kwargs): return (False, "Not available")

__all__ = [
    # Gmail
    'GmailClient', 'GmailIntegration',
    'send_email', 'read_inbox', 'get_user_profile',
    
    # WhatsApp
    'WhatsAppClient', 'WhatsAppSender',
    'connect_whatsapp', 'send_whatsapp_message', 'get_whatsapp_status',
    
    # LinkedIn
    'LinkedInClient', 'LinkedInAutomation',
    'post_to_linkedin', 'connect_linkedin', 'get_linkedin_status',
    
    # Facebook
    'FacebookClient', 'FacebookBrowser',
    'post_to_facebook_page', 'post_to_facebook', 'validate_facebook_token',
]

__version__ = '2.0.0'
