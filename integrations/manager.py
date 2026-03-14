"""
Integration Manager Module for AI Agency Dashboard

Provides a unified interface for all communication integrations:
- Gmail
- WhatsApp
- LinkedIn
- Facebook

Usage with Streamlit:
    from integrations.manager import IntegrationManager
    
    manager = IntegrationManager()
    
    # Gmail
    success, msg = manager.gmail_authenticate()
    success, emails = manager.gmail_read_inbox()
    success, msg = manager.gmail_send_email(to, subject, body)
    
    # WhatsApp
    success, msg = manager.whatsapp_initialize()
    success, msg = manager.whatsapp_send_message(phone, message)
    
    # LinkedIn
    success, msg = manager.linkedin_initialize()
    success, msg = manager.linkedin_post(content)
    
    # Facebook
    success, info = manager.facebook_validate()
    success, msg = manager.facebook_post(message)
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# Import all clients
from .gmail_client import GmailClient, CREDENTIALS_FILE, TOKEN_FILE
from .whatsapp_client import WhatsAppClient, USER_DATA_DIR as WHATSAPP_SESSION_DIR
from .linkedin_client import LinkedInClient, PLAYWRIGHT_PROFILE as LINKEDIN_PROFILE_DIR
from .facebook_client import FacebookClient, validate_facebook_credentials

# Configure logging
logger = logging.getLogger(__name__)


class IntegrationManager:
    """
    Unified manager for all communication integrations
    
    Provides a simple interface for the Streamlit dashboard to interact with
    all external services (Gmail, WhatsApp, LinkedIn, Facebook).
    """

    def __init__(self):
        """Initialize integration manager"""
        self._gmail_client: Optional[GmailClient] = None
        self._whatsapp_client: Optional[WhatsAppClient] = None
        self._linkedin_client: Optional[LinkedInClient] = None
        self._facebook_client: Optional[FacebookClient] = None

    # =========================================================================
    # GMAIL INTEGRATION
    # =========================================================================

    def gmail_is_configured(self) -> Tuple[bool, str]:
        """
        Check if Gmail is configured

        Returns:
            Tuple of (is_configured: bool, message: str)
        """
        if not CREDENTIALS_FILE.exists():
            return False, f"credentials.json not found at {CREDENTIALS_FILE}"
        return True, "credentials.json found"

    def gmail_is_authenticated(self) -> bool:
        """Check if Gmail is authenticated"""
        if self._gmail_client:
            return self._gmail_client.is_authenticated()
        return TOKEN_FILE.exists()

    def gmail_authenticate(self) -> Tuple[bool, str]:
        """
        Authenticate with Gmail

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._gmail_client is None:
            self._gmail_client = GmailClient()
        return self._gmail_client.authenticate()

    def gmail_get_profile(self) -> Optional[Dict[str, Any]]:
        """Get Gmail profile"""
        if self._gmail_client is None:
            self._gmail_client = GmailClient()
        return self._gmail_client.get_profile()

    def gmail_send_email(self, to: str, subject: str, body: str,
                         from_email: Optional[str] = None) -> Tuple[bool, str]:
        """
        Send email via Gmail

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            from_email: Optional sender email

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._gmail_client is None:
            self._gmail_client = GmailClient()

        if not self._gmail_client.is_authenticated():
            success, msg = self._gmail_client.authenticate()
            if not success:
                return False, msg

        return self._gmail_client.send_email(to, subject, body, from_email)

    def gmail_read_inbox(self, max_results: int = 10,
                         query: str = 'is:inbox') -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Read emails from Gmail inbox

        Args:
            max_results: Maximum emails to retrieve
            query: Gmail search query

        Returns:
            Tuple of (success: bool, emails: list)
        """
        if self._gmail_client is None:
            self._gmail_client = GmailClient()

        if not self._gmail_client.is_authenticated():
            success, msg = self._gmail_client.authenticate()
            if not success:
                return False, []

        return self._gmail_client.read_inbox(max_results, query)

    # =========================================================================
    # WHATSAPP INTEGRATION
    # =========================================================================

    def whatsapp_is_initialized(self) -> bool:
        """Check if WhatsApp is initialized and logged in"""
        if self._whatsapp_client:
            return self._whatsapp_client.is_logged_in()
        return False

    def whatsapp_get_session_status(self) -> Dict[str, Any]:
        """Get WhatsApp session status"""
        session_exists = WHATSAPP_SESSION_DIR.exists()
        is_logged_in = self.whatsapp_is_initialized()

        return {
            'session_dir': str(WHATSAPP_SESSION_DIR),
            'session_exists': session_exists,
            'is_logged_in': is_logged_in,
            'message': "Session found" if session_exists else "No session"
        }

    def whatsapp_initialize(self, headless: bool = False) -> Tuple[bool, str]:
        """
        Initialize WhatsApp client

        Args:
            headless: Run browser in headless mode

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._whatsapp_client is None:
            self._whatsapp_client = WhatsAppClient(headless=headless)

        if not self._whatsapp_client.initialize():
            return False, "Failed to initialize WhatsApp"

        if self._whatsapp_client.is_logged_in():
            return True, "WhatsApp ready (session restored)"
        else:
            return True, "QR code scan required"

    async def whatsapp_wait_for_login(self, timeout: int = 60) -> Tuple[bool, str]:
        """
        Wait for QR code login

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._whatsapp_client is None:
            return False, "WhatsApp not initialized"

        if await self._whatsapp_client.wait_for_login(timeout):
            return True, "Login successful"
        else:
            return False, "Login timeout"

    def whatsapp_send_message(self, phone_number: str, message: str,
                              headless: bool = False) -> Tuple[bool, str]:
        """
        Send WhatsApp message

        Args:
            phone_number: Phone number with country code
            message: Message to send
            headless: Run browser in headless mode

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._whatsapp_client is None:
            self._whatsapp_client = WhatsAppClient(headless=headless)

        if not self._whatsapp_client.is_logged_in():
            # Try to initialize
            if not self._whatsapp_client.initialize():
                return False, "Failed to initialize WhatsApp"

            if not self._whatsapp_client.is_logged_in():
                return False, "Not logged in. Please scan QR code first."

        # Run async send_message in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._whatsapp_client.send_message(phone_number, message)
            )
        finally:
            loop.close()

    def whatsapp_cleanup(self):
        """Clean up WhatsApp resources"""
        if self._whatsapp_client:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._whatsapp_client.cleanup())
            finally:
                loop.close()
            self._whatsapp_client = None

    # =========================================================================
    # LINKEDIN INTEGRATION
    # =========================================================================

    def linkedin_is_initialized(self) -> bool:
        """Check if LinkedIn is initialized and logged in"""
        if self._linkedin_client:
            return self._linkedin_client.is_logged_in()
        return False

    def linkedin_is_logged_in(self) -> bool:
        """Check if LinkedIn is logged in"""
        return self.linkedin_is_initialized()

    def linkedin_get_session_status(self) -> Dict[str, Any]:
        """Get LinkedIn session status"""
        profile_exists = LINKEDIN_PROFILE_DIR.exists()
        is_logged_in = self.linkedin_is_initialized()

        return {
            'profile_dir': str(LINKEDIN_PROFILE_DIR),
            'profile_exists': profile_exists,
            'is_logged_in': is_logged_in,
            'message': "Session found" if profile_exists else "No session"
        }

    def linkedin_initialize(self, headless: bool = False) -> Tuple[bool, str]:
        """
        Initialize LinkedIn client

        Args:
            headless: Run browser in headless mode

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._linkedin_client is None:
            self._linkedin_client = LinkedInClient(headless=headless)

        if not self._linkedin_client.initialize():
            return False, "Failed to initialize LinkedIn"

        if self._linkedin_client.is_logged_in():
            return True, "LinkedIn ready (session restored)"
        else:
            return True, "Login required"

    def linkedin_wait_for_login(self, timeout: int = 120) -> Tuple[bool, str]:
        """
        Wait for manual login

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._linkedin_client is None:
            return False, "LinkedIn not initialized"

        if self._linkedin_client.wait_for_login(timeout):
            return True, "Login successful"
        else:
            return False, "Login timeout"

    def linkedin_post(self, content: str, headless: bool = False) -> Tuple[bool, str]:
        """
        Post to LinkedIn

        Args:
            content: Post content
            headless: Run browser in headless mode

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._linkedin_client is None:
            self._linkedin_client = LinkedInClient(headless=headless)

        if not self._linkedin_client.is_logged_in():
            return False, "Not logged in. Please log in first."

        return self._linkedin_client.post_content(content)

    def linkedin_cleanup(self):
        """Clean up LinkedIn resources"""
        if self._linkedin_client:
            self._linkedin_client.cleanup()
            self._linkedin_client = None

    # =========================================================================
    # FACEBOOK INTEGRATION
    # =========================================================================

    def facebook_is_configured(self) -> Tuple[bool, str]:
        """Check if Facebook is configured"""
        return validate_facebook_credentials()

    def facebook_validate(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate Facebook credentials

        Returns:
            Tuple of (success: bool, token_info: dict)
        """
        if self._facebook_client is None:
            try:
                self._facebook_client = FacebookClient()
            except ValueError as e:
                return False, {'error': str(e)}

        return self._facebook_client.validate_token()

    def facebook_get_page_info(self) -> Optional[Dict[str, Any]]:
        """Get Facebook Page info"""
        if self._facebook_client is None:
            try:
                self._facebook_client = FacebookClient()
            except ValueError:
                return None

        return self._facebook_client.get_page_info()

    def facebook_post(self, message: str, link: Optional[str] = None,
                      photo_url: Optional[str] = None) -> Tuple[bool, str]:
        """
        Post to Facebook Page

        Args:
            message: Post message
            link: Optional link to share
            photo_url: Optional photo URL

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._facebook_client is None:
            try:
                self._facebook_client = FacebookClient()
            except ValueError as e:
                return False, str(e)

        return self._facebook_client.post_to_page(message, link=link, photo_url=photo_url)

    def facebook_get_recent_posts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent Facebook posts

        Args:
            limit: Number of posts to retrieve

        Returns:
            List of post dictionaries
        """
        if self._facebook_client is None:
            try:
                self._facebook_client = FacebookClient()
            except ValueError:
                return []

        return self._facebook_client.get_recent_posts(limit)

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all integrations

        Returns:
            Dictionary with status for each integration
        """
        return {
            'gmail': {
                'configured': self.gmail_is_configured()[0],
                'authenticated': self.gmail_is_authenticated(),
                'credentials_file': str(CREDENTIALS_FILE),
                'token_file': str(TOKEN_FILE) if TOKEN_FILE.exists() else None
            },
            'whatsapp': self.whatsapp_get_session_status(),
            'linkedin': self.linkedin_get_session_status(),
            'facebook': {
                'configured': self.facebook_is_configured()[0],
                'validated': self.facebook_validate()[0] if self.facebook_is_configured()[0] else False
            }
        }

    def cleanup_all(self):
        """Clean up all resources"""
        self.whatsapp_cleanup()
        self.linkedin_cleanup()
        self._facebook_client = None
        self._gmail_client = None


# Global instance for Streamlit session state
_manager_instance: Optional[IntegrationManager] = None


def get_integration_manager() -> IntegrationManager:
    """Get or create integration manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = IntegrationManager()
    return _manager_instance


def reset_integration_manager():
    """Reset the integration manager instance"""
    global _manager_instance
    if _manager_instance:
        _manager_instance.cleanup_all()
    _manager_instance = None


if __name__ == '__main__':
    # Test the integration manager
    print("Integration Manager Test")
    print("=" * 50)

    manager = IntegrationManager()

    # Get all status
    status = manager.get_all_status()
    print("\nIntegration Status:")
    for service, info in status.items():
        print(f"\n{service.upper()}:")
        for key, value in info.items():
            print(f  {key}: {value}")
