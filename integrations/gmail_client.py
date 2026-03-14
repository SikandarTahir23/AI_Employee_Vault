"""
Gmail Client Module for AI Automation Dashboard
Uses Gmail API with OAuth 2.0 authentication

Setup Instructions:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a project and enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json and place it in the project root
5. Run: python setup_gmail_auth.py to authenticate
"""

import os
import base64
import json
import logging
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logger = logging.getLogger(__name__)

# Gmail API scopes - request both read and send permissions
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Path configuration
PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / 'credentials.json'
TOKEN_FILE = PROJECT_ROOT / 'token.json'


class GmailClient:
    """
    Gmail API client with OAuth 2.0 authentication
    
    Features:
    - Persistent token storage (token.json)
    - Automatic token refresh
    - Send and read emails
    - Error handling with detailed logging
    """

    def __init__(self):
        """Initialize Gmail client"""
        self.service = None
        self._authenticated = False
        self._user_email = None

    def authenticate(self) -> tuple[bool, str]:
        """
        Authenticate with Gmail API using OAuth 2.0
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check for credentials file
        if not CREDENTIALS_FILE.exists():
            error_msg = (
                f"credentials.json not found at {CREDENTIALS_FILE}\n\n"
                "Setup Instructions:\n"
                "1. Go to: https://console.cloud.google.com/apis/credentials\n"
                "2. Create OAuth 2.0 Client ID (Desktop app)\n"
                "3. Download credentials.json\n"
                "4. Place it in: {PROJECT_ROOT}\n"
                "5. Run: python setup_gmail_auth.py"
            )
            logger.error(error_msg)
            return False, error_msg

        creds = None

        # Load existing token
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                logger.info("Loaded existing token.json")
            except Exception as e:
                logger.warning(f"Error loading token: {e}")
                TOKEN_FILE.unlink(missing_ok=True)
                creds = None

        # Refresh or authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired token...")
                    creds.refresh(Request())
                    self._save_token(creds)
                except Exception as e:
                    logger.warning(f"Token refresh failed: {e}")
                    creds = None

            if not creds:
                try:
                    logger.info("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES
                    )
                    
                    # Try multiple ports to avoid conflicts
                    for port in [8090, 8091, 8092, 0]:  # 0 = ephemeral port
                        try:
                            creds = flow.run_local_server(
                                port=port,
                                open_browser=True,
                                authorization_prompt_message=(
                                    "Please visit this URL to authorize: {url}\n"
                                    "After authorization, you'll be redirected."
                                )
                            )
                            break
                        except OSError as e:
                            if port == 0:  # Last resort failed
                                raise
                            logger.warning(f"Port {port} in use, trying next...")
                    
                    self._save_token(creds)
                    logger.info("OAuth authentication successful")

                except FileNotFoundError:
                    return False, "credentials.json not found"
                except Exception as e:
                    error_msg = f"Authentication failed: {str(e)}"
                    logger.error(error_msg)
                    return False, error_msg

        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self._authenticated = True
            
            # Get user email
            profile = self.service.users().getProfile(userId='me').execute()
            self._user_email = profile.get('emailAddress')
            logger.info(f"Authenticated as: {self._user_email}")
            
            return True, f"Authenticated as {self._user_email}"
            
        except Exception as e:
            error_msg = f"Failed to build Gmail service: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _save_token(self, creds: Credentials):
        """Save token to file"""
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            logger.info(f"Token saved to {TOKEN_FILE}")
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")

    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self._authenticated

    def get_user_email(self) -> Optional[str]:
        """Get authenticated user email"""
        return self._user_email

    def send_email(self, to: str, subject: str, body: str,
                   from_email: Optional[str] = None,
                   html: bool = False) -> tuple[bool, str]:
        """
        Send an email using Gmail API

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            from_email: Optional sender email (defaults to authenticated account)
            html: If True, send as HTML

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.service:
            return False, "Not authenticated. Call authenticate() first."

        try:
            message = EmailMessage()
            message['to'] = to
            message['subject'] = subject
            
            if from_email:
                message['from'] = from_email
            elif self._user_email:
                message['from'] = self._user_email

            if html:
                message.add_alternative(body, subtype='html')
            else:
                message.set_content(body)

            # Encode the message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send the email
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': encoded_message}
            ).execute()

            msg_id = sent_message['id']
            logger.info(f"Email sent successfully! Message ID: {msg_id}")
            return True, f"Email sent (ID: {msg_id})"

        except HttpError as error:
            error_msg = f"Gmail API error: {error}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def read_inbox(self, max_results: int = 10,
                   query: str = 'is:inbox') -> tuple[bool, List[Dict[str, Any]]]:
        """
        Read emails from Gmail inbox

        Args:
            max_results: Maximum number of emails to retrieve
            query: Gmail search query (default: 'is:inbox')

        Returns:
            Tuple of (success: bool, emails: list)
        """
        if not self.service:
            return False, []

        emails = []

        try:
            # List messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                logger.info("No messages found")
                return True, []

            # Get message details
            for msg in messages:
                try:
                    message = self.service.users().messages().get(
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

        except HttpError as error:
            error_msg = f"Gmail API error: {error}"
            logger.error(error_msg)
            return False, []
        except Exception as e:
            error_msg = f"Failed to read inbox: {str(e)}"
            logger.error(error_msg)
            return False, []

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get the authenticated user's Gmail profile

        Returns:
            Dictionary with email info, or None on error
        """
        if not self.service:
            return None

        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'email': profile.get('emailAddress'),
                'messages_total': profile.get('messagesTotal'),
                'threads_total': profile.get('threadsTotal')
            }
        except Exception as e:
            logger.error(f"Failed to get profile: {e}")
            return None


# Standalone helper functions for backward compatibility
_default_client: Optional[GmailClient] = None


def get_gmail_client() -> GmailClient:
    """Get or create default Gmail client"""
    global _default_client
    if _default_client is None:
        _default_client = GmailClient()
    return _default_client


def send_email(to: str, subject: str, body: str,
               from_email: Optional[str] = None) -> bool:
    """
    Send email using default client
    
    Returns:
        True if sent successfully, False otherwise
    """
    client = get_gmail_client()
    if not client.is_authenticated():
        success, _ = client.authenticate()
        if not success:
            return False
    
    success, _ = client.send_email(to, subject, body, from_email)
    return success


def read_inbox(max_results: int = 10, query: str = 'is:inbox') -> List[Dict]:
    """
    Read inbox using default client
    
    Returns:
        List of email dictionaries
    """
    client = get_gmail_client()
    if not client.is_authenticated():
        success, _ = client.authenticate()
        if not success:
            return []
    
    success, emails = client.read_inbox(max_results, query)
    return emails


def get_user_profile() -> Optional[Dict]:
    """Get user profile using default client"""
    client = get_gmail_client()
    if not client.is_authenticated():
        success, _ = client.authenticate()
        if not success:
            return None
    
    return client.get_profile()


if __name__ == '__main__':
    # Test the integration
    print("Gmail Integration Test")
    print("=" * 50)

    client = GmailClient()
    success, msg = client.authenticate()
    print(f"\nAuthentication: {msg}")

    if success:
        profile = client.get_profile()
        print(f"\nLogged in as: {profile['email']}")
        print(f"Total messages: {profile['messages_total']}")

        # Test reading inbox
        success, emails = client.read_inbox(max_results=5)
        print(f"\nRecent emails: {len(emails)}")
        for email in emails:
            print(f"  - {email['subject']} (from: {email['from']})")
