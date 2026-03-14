"""
Gmail OAuth 2.0 Setup Script

This script helps you set up Gmail API authentication for the AI Agency Dashboard.

Usage:
    python setup_gmail_auth.py

Prerequisites:
    1. Go to Google Cloud Console: https://console.cloud.google.com/
    2. Create a new project or select existing
    3. Enable Gmail API
    4. Create OAuth 2.0 credentials (Desktop app)
    5. Download credentials.json and place it in the project root
"""

import os
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Scopes for Gmail API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Path configuration
PROJECT_ROOT = Path(__file__).parent
CREDENTIALS_FILE = PROJECT_ROOT / 'credentials.json'
TOKEN_FILE = PROJECT_ROOT / 'token.json'


def print_setup_instructions():
    """Print detailed setup instructions"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    GMAIL API OAUTH 2.0 SETUP INSTRUCTIONS                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  STEP 1: Create Google Cloud Project                                         ║
║  ───────────────────────────────────────                                     ║
║  1. Go to: https://console.cloud.google.com/                                 ║
║  2. Click "Select a project" → "NEW PROJECT"                                 ║
║  3. Enter project name (e.g., "AI Agency Dashboard")                         ║
║  4. Click "CREATE"                                                           ║
║                                                                              ║
║  STEP 2: Enable Gmail API                                                    ║
║  ───────────────────────────────                                             ║
║  1. Go to: https://console.cloud.google.com/apis/library/gmail.googleapis.com║
║  2. Click "ENABLE"                                                           ║
║                                                                              ║
║  STEP 3: Create OAuth 2.0 Credentials                                        ║
║  ────────────────────────────────────────────                                ║
║  1. Go to: https://console.cloud.google.com/apis/credentials                 ║
║  2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"                         ║
║  3. Select "Desktop app" as application type                                 ║
║  4. Click "CREATE"                                                           ║
║  5. Download the credentials JSON file                                       ║
║                                                                              ║
║  STEP 4: Place credentials.json                                              ║
║  ────────────────────────────────────                                        ║
║  Save the downloaded file as 'credentials.json' in:                          ║
║  {CREDENTIALS_PATH}                                                          ║
║                                                                              ║
║  STEP 5: Run this script again                                               ║
║  ────────────────────────────────────                                        ║
║  After placing credentials.json, run: python setup_gmail_auth.py             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def check_credentials_file() -> bool:
    """Check if credentials.json exists"""
    if not CREDENTIALS_FILE.exists():
        print(f"\n❌ ERROR: credentials.json not found at: {CREDENTIALS_FILE}")
        print("\nPlease follow the setup instructions above.")
        return False
    
    # Validate JSON structure
    try:
        import json
        with open(CREDENTIALS_FILE) as f:
            data = json.load(f)
        
        if 'installed' not in data and 'web' not in data:
            print("\n❌ ERROR: Invalid credentials.json format")
            print("Expected 'installed' or 'web' OAuth credentials")
            return False
        
        print(f"\n✓ credentials.json found and valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON in credentials.json: {e}")
        return False


def run_oauth_flow() -> bool:
    """Run OAuth 2.0 flow"""
    print("\n" + "=" * 70)
    print("Starting OAuth 2.0 Authentication Flow")
    print("=" * 70)
    
    try:
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES
        )
        
        print("\n📋 Requesting permissions:")
        for scope in SCOPES:
            print(f"   • {scope}")
        
        print("\n🌐 Opening browser for authentication...")
        print("   If browser doesn't open automatically, copy and paste the URL")
        print("   that appears below into your browser.\n")
        
        # Run local server for OAuth
        creds = flow.run_local_server(
            port=8090,
            open_browser=True,
            authorization_prompt_message=(
                "\n🔑 Please visit this URL to authorize: {url}\n"
                "After authorization, you'll be redirected to localhost:8090\n"
                "The browser will show 'This site can't be reached' - this is NORMAL!\n"
                "Just close that tab and return here.\n"
            )
        )
        
        # Save token
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Authentication successful!")
        print(f"💾 Token saved to: {TOKEN_FILE}")
        
        # Get user info
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print(f"\n📧 Authenticated as: {profile.get('emailAddress')}")
        print(f"📊 Total messages: {profile.get('messagesTotal', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure credentials.json is valid")
        print("  2. Check that Gmail API is enabled")
        print("  3. Try running the script again")
        return False


def test_authentication() -> bool:
    """Test the authentication by loading token and making API call"""
    print("\n" + "=" * 70)
    print("Testing Authentication")
    print("=" * 70)
    
    if not TOKEN_FILE.exists():
        print("\n❌ No token.json found. Run authentication first.")
        return False
    
    try:
        # Load token
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # Refresh if needed
        if creds.expired and creds.refresh_token:
            print("\n🔄 Refreshing token...")
            creds.refresh(Request())
        
        # Test API call
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print(f"\n✅ Token is valid!")
        print(f"📧 Authenticated as: {profile.get('emailAddress')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Token validation failed: {e}")
        print("  You may need to re-authenticate.")
        # Remove invalid token
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
        return False


def main():
    """Main setup function"""
    print("\n" + "=" * 70)
    print("           GMAIL API OAUTH 2.0 SETUP")
    print("=" * 70)
    print(f"\nProject root: {PROJECT_ROOT}")
    print(f"Credentials: {CREDENTIALS_FILE}")
    print(f"Token: {TOKEN_FILE}")
    
    # Check if already authenticated
    if TOKEN_FILE.exists():
        print("\n⚠️  Existing token found")
        choice = input("\nDo you want to test existing token? (y/n): ").strip().lower()
        
        if choice == 'y':
            if test_authentication():
                print("\n✅ Gmail API is ready to use!")
                return
            else:
                print("\n🔄 Will run new authentication...")
        else:
            print("\n🔄 Will run new authentication...")
    
    # Check credentials file
    if not check_credentials_file():
        print_setup_instructions()
        return
    
    # Run OAuth flow
    if run_oauth_flow():
        print("\n" + "=" * 70)
        print("✅ GMAIL SETUP COMPLETE!")
        print("=" * 70)
        print("\nYou can now use Gmail integration in the dashboard.")
        print("\nNext steps:")
        print("  1. Restart the Streamlit dashboard")
        print("  2. Go to Communication Hub → Gmail")
        print("  3. Click 'Connect Gmail' to start using")
    else:
        print("\n" + "=" * 70)
        print("❌ GMAIL SETUP FAILED")
        print("=" * 70)
        print("\nPlease check the error messages above and try again.")


if __name__ == '__main__':
    main()
