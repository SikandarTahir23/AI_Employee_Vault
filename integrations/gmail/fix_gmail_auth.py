"""
Gmail Authentication Fix Script
Run this once to authenticate with Gmail and generate token.json
"""

import os
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")

def main():
    print("=" * 60)
    print("  Gmail Authentication Setup")
    print("=" * 60)
    print()
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[ERROR] credentials.json not found at {CREDENTIALS_FILE}")
        print("Please download it from Google Cloud Console and place it in the root folder.")
        input("\nPress Enter to exit...")
        return
    
    creds = None
    if os.path.exists(TOKEN_FILE):
        print("[INFO] Existing token found. Refreshing...")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            print("[AUTH] Refreshing expired token...")
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            print("[OK] Token refreshed successfully!")
            input("\nPress Enter to exit...")
            return
        elif creds and creds.valid:
            print("[OK] Token is valid. Gmail sync should work now.")
            input("\nPress Enter to exit...")
            return
        else:
            print("[INFO] Token invalid or expired. Re-authenticating...")
    
    print("[AUTH] Starting Google OAuth sign-in...")
    print()
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    
    # Use fixed port for predictable redirect URI
    auth_url, _ = flow.authorization_url(prompt="consent")
    
    print("=" * 60)
    print("  IMPORTANT: Complete authentication below")
    print("=" * 60)
    print()
    print(f"1. Open this URL in your browser:")
    print(f"   {auth_url}")
    print()
    print(f"2. Sign in with your Google account")
    print(f"3. Grant permissions when prompted")
    print(f"4. Copy the authorization code from the redirect URL")
    print()
    
    # Try to open browser automatically
    webbrowser.open(auth_url)
    
    print("5. Paste the authorization code below:")
    print()
    auth_code = input("   Authorization code: ").strip()
    
    if not auth_code:
        print("[ERROR] No authorization code provided.")
        input("\nPress Enter to exit...")
        return
    
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        
        print()
        print("[OK] Authentication successful!")
        print(f"[OK] Token saved to: {TOKEN_FILE}")
        print()
        print("You can now use Gmail sync in the AI Employee Vault.")
        
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        print("Please try again or check your credentials.json file.")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
