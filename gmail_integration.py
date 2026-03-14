"""
Gmail Integration Module for AI Automation Dashboard
Uses Gmail API with OAuth 2.0 authentication
"""

import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

# Path configuration
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def get_credentials_path() -> str:
    """Get the absolute path to credentials.json"""
    # Check current directory first
    if os.path.exists(CREDENTIALS_FILE):
        return os.path.abspath(CREDENTIALS_FILE)
    # Check script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(script_dir, CREDENTIALS_FILE)
    if os.path.exists(cred_path):
        return cred_path
    raise FileNotFoundError(
        f"credentials.json not found. Please place it in:\n"
        f"  - Current directory: {os.getcwd()}\n"
        f"  - Or script directory: {script_dir}"
    )


def get_token_path() -> str:
    """Get the absolute path to token.json"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, TOKEN_FILE)


def authenticate_gmail() -> Optional[build.Resource]:
    """
    Authenticate with Gmail API using OAuth 2.0
    Creates token.json on first login, reuses on subsequent runs
    
    Returns:
        Gmail API service object or None if authentication fails
    """
    creds = None
    token_path = get_token_path()
    
    # Load existing token if available
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logger.info("Loaded existing token.json")
        except Exception as e:
            logger.warning(f"Error loading token: {e}")
            creds = None
    
    # Refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            try:
                logger.info("Starting OAuth flow...")
                cred_path = get_credentials_path()
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred_path, SCOPES
                )
                # Run local server for OAuth
                creds = flow.run_local_server(
                    port=8090,
                    open_browser=True,
                    authorization_prompt_message=(
                        "Please visit this URL to authorize: {url}\n"
                        "After authorization, you'll be redirected to localhost:8090"
                    )
                )
                
                # Save token for future use
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"Token saved to {token_path}")
                
            except FileNotFoundError as e:
                logger.error(str(e))
                return None
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                return None
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API service created successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to build Gmail service: {e}")
        return None


def send_email(service: build.Resource, to: str, subject: str, body: str, 
               from_email: Optional[str] = None) -> bool:
    """
    Send an email using Gmail API
    
    Args:
        service: Gmail API service object
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        from_email: Optional sender email (defaults to authenticated account)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        message = EmailMessage()
        message['to'] = to
        message['subject'] = subject
        message.set_content(body)
        
        if from_email:
            message['from'] = from_email
        
        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send the email
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': encoded_message}
        ).execute()
        
        logger.info(f"Email sent successfully! Message ID: {sent_message['id']}")
        return True
        
    except HttpError as error:
        logger.error(f"Gmail API error: {error}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def read_inbox(service: build.Resource, max_results: int = 10,
               query: str = 'is:inbox') -> List[Dict]:
    """
    Read emails from Gmail inbox
    
    Args:
        service: Gmail API service object
        max_results: Maximum number of emails to retrieve
        query: Gmail search query (default: 'is:inbox')
    
    Returns:
        List of email dictionaries with id, subject, from, date, snippet
    """
    emails = []
    
    try:
        # List messages
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            logger.info("No messages found")
            return emails
        
        # Get message details
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
        return emails
        
    except HttpError as error:
        logger.error(f"Gmail API error: {error}")
        return emails
    except Exception as e:
        logger.error(f"Failed to read inbox: {e}")
        return emails


def get_user_profile(service: build.Resource) -> Optional[Dict]:
    """
    Get the authenticated user's Gmail profile
    
    Args:
        service: Gmail API service object
    
    Returns:
        Dictionary with emailAddress and messagesTotal, or None on error
    """
    try:
        profile = service.users().getProfile(userId='me').execute()
        logger.info(f"Authenticated as: {profile.get('emailAddress')}")
        return profile
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        return None


# Streamlit helper functions
def init_gmail_service() -> Optional[build.Resource]:
    """
    Initialize Gmail service for Streamlit apps
    Handles authentication and returns service object
    """
    if not os.path.exists(get_credentials_path()):
        logger.error("credentials.json not found!")
        return None
    
    return authenticate_gmail()


if __name__ == '__main__':
    # Test the integration
    print("Gmail Integration Test")
    print("=" * 50)
    
    service = authenticate_gmail()
    if service:
        profile = get_user_profile(service)
        if profile:
            print(f"Logged in as: {profile['emailAddress']}")
            print(f"Total messages: {profile['messagesTotal']}")
        
        # Test reading inbox
        emails = read_inbox(service, max_results=5)
        print(f"\nRecent emails: {len(emails)}")
        for email in emails:
            print(f"  - {email['subject']} (from: {email['from']})")