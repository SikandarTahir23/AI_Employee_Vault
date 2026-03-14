"""
Facebook OAuth Token Generator

This script helps you get a fresh Facebook Page Access Token automatically.

How it works:
1. Opens Facebook OAuth dialog in your browser
2. You authorize the app
3. Script extracts the token
4. Updates your .env file automatically

Requirements:
- A Facebook App (create at https://developers.facebook.com/)
- App ID and App Secret in .env file
"""

import os
import sys
import webbrowser
import http.server
import socketserver
import urllib.parse
import urllib.request
import json
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

# Load existing env variables
load_dotenv()

# Configuration
PORT = 8888
REDIRECT_URI = f"http://localhost:{PORT}/callback"
FACEBOOK_OAUTH_URL = "https://www.facebook.com/v21.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v21.0/oauth/access_token"
GRAPH_API_URL = "https://graph.facebook.com/v21.0"

# Required permissions for posting to pages
PERMISSIONS = [
    "pages_show_list",
    "pages_read_engagement", 
    "pages_manage_posts",
    "public_profile"
]

class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP server to handle OAuth callback"""
    
    access_code = None
    error = None
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/callback":
            params = urllib.parse.parse_qs(parsed.query)
            
            if "error" in params:
                self.error = params["error"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                html = """<html><body>
                    <h1 style="color: red;">Authorization Failed</h1>
                    <p>Please close this window and try again.</p>
                    <script>setTimeout(() => window.close(), 3000)</script>
                    </body></html>"""
                self.wfile.write(html.encode('utf-8'))
            elif "code" in params:
                self.access_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                html = """<html><body>
                    <h1 style="color: green;">Success!</h1>
                    <p>Authorization successful. You can close this window.</p>
                    <script>setTimeout(() => window.close(), 3000)</script>
                    </body></html>"""
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging


def get_app_credentials():
    """Get Facebook App ID and Secret from user or .env"""
    app_id = os.getenv("META_APP_ID")
    app_secret = os.getenv("META_APP_SECRET")
    
    if not app_id or not app_secret:
        print("\n" + "=" * 60)
        print("FACEBOOK APP CREDENTIALS NOT FOUND")
        print("=" * 60)
        print("\nYou need a Facebook App to get tokens.")
        print("\nCreate an app:")
        print("1. Go to: https://developers.facebook.com/apps/")
        print("2. Click 'Create App'")
        print("3. Select 'Business' or 'Other'")
        print("4. Fill in app details")
        print("5. Get App ID and App Secret from Dashboard")
        print("\nAdd to your .env file:")
        print("  META_APP_ID=your_app_id")
        print("  META_APP_SECRET=your_app_secret")
        
        print("\n" + "-" * 60)
        print("Or enter them now:")
        app_id = input("App ID: ").strip()
        app_secret = input("App Secret: ").strip()
    
    if not app_id or not app_secret:
        raise ValueError("Facebook App ID and Secret are required")
    
    return app_id, app_secret


def start_oauth_flow(app_id):
    """Open Facebook OAuth dialog in browser"""
    params = {
        "client_id": app_id,
        "redirect_uri": REDIRECT_URI,
        "scope": ",".join(PERMISSIONS),
        "response_type": "code"
    }
    
    url = f"{FACEBOOK_OAUTH_URL}?{urllib.parse.urlencode(params)}"
    
    print("\nOpening Facebook authorization page...")
    print("Please log in and authorize the app.")
    webbrowser.open(url)


def get_user_access_token(app_id, app_secret, code):
    """Exchange authorization code for user access token"""
    params = {
        "client_id": app_id,
        "client_secret": app_secret,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    
    url = f"{FACEBOOK_TOKEN_URL}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            if "access_token" in data:
                return data["access_token"]
            else:
                raise ValueError(f"Error getting token: {data}")
    except Exception as e:
        raise ValueError(f"Failed to get access token: {e}")


def extend_token(user_token, app_id, app_secret):
    """Exchange short-lived token for long-lived token (60 days)"""
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": user_token
    }
    
    url = f"{FACEBOOK_TOKEN_URL}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            if "access_token" in data:
                print(f"\n✓ Long-lived token obtained (expires in {data.get('expires_in', 'N/A')} seconds)")
                return data["access_token"]
            else:
                raise ValueError(f"Error extending token: {data}")
    except Exception as e:
        raise ValueError(f"Failed to extend token: {e}")


def get_page_access_token(user_token, page_id):
    """Get page access token from user token"""
    url = f"{GRAPH_API_URL}/me/accounts?access_token={user_token}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            if "data" in data:
                for page in data["data"]:
                    if page["id"] == page_id:
                        print(f"\n✓ Page access token obtained for: {page.get('name', 'Unknown')}")
                        return page["access_token"]
                
                # If specific page not found, return first available
                if data["data"]:
                    print(f"\n⚠ Page ID {page_id} not found. Using first available page: {data['data'][0].get('name', 'Unknown')}")
                    return data["data"][0]["access_token"]
                
                raise ValueError("No pages found for this user")
            else:
                raise ValueError(f"Error getting pages: {data}")
    except Exception as e:
        raise ValueError(f"Failed to get page token: {e}")


def update_env_file(page_token, page_id):
    """Update .env file with new token"""
    env_path = Path(__file__).parent / ".env"
    
    # Read existing content
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Update or add META_ACCESS_TOKEN
    token_found = False
    for i, line in enumerate(lines):
        if line.startswith("META_ACCESS_TOKEN="):
            lines[i] = f"META_ACCESS_TOKEN={page_token}\n"
            token_found = True
            break
    
    if not token_found:
        lines.append(f"\nMETA_ACCESS_TOKEN={page_token}\n")
    
    # Ensure FB_PAGE_ID is set
    page_id_found = any(line.startswith("FB_PAGE_ID=") for line in lines)
    if not page_id_found:
        lines.append(f"FB_PAGE_ID={page_id}\n")
    
    # Write back
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"\n✓ Updated .env file with new token")


def main():
    print("\n" + "=" * 60)
    print("FACEBOOK OAUTH TOKEN GENERATOR")
    print("=" * 60)
    
    try:
        # Get app credentials
        app_id, app_secret = get_app_credentials()
        print(f"\n✓ Using App ID: {app_id[:20]}...")
        
        # Get existing page ID or ask for it
        page_id = os.getenv("FB_PAGE_ID")
        if not page_id:
            print("\nWhat's your Facebook Page ID?")
            print("Find it at: https://findmyfbid.in/")
            page_id = input("Page ID: ").strip()
        
        print(f"\n✓ Using Page ID: {page_id}")
        
        # Start HTTP server for callback
        handler = OAuthCallbackHandler
        httpd = socketserver.TCPServer(("", PORT), handler)
        
        # Run server in background thread
        server_thread = threading.Thread(target=httpd.handle_request)
        server_thread.daemon = True
        server_thread.start()
        
        # Start OAuth flow
        start_oauth_flow(app_id)
        
        # Wait for callback
        print(f"\nWaiting for authorization callback on port {PORT}...")
        print("(The browser window should have opened)")
        
        timeout = 120  # 2 minutes
        start_time = time.time()
        
        while OAuthCallbackHandler.access_code is None and OAuthCallbackHandler.error is None:
            if time.time() - start_time > timeout:
                raise TimeoutError("Authorization timed out. Please try again.")
            time.sleep(0.5)
        
        if OAuthCallbackHandler.error:
            raise ValueError(f"Authorization failed: {OAuthCallbackHandler.error}")
        
        print(f"\n✓ Authorization code received")
        
        # Exchange code for user token
        print("\nExchanging authorization code for access token...")
        user_token = get_user_access_token(app_id, app_secret, OAuthCallbackHandler.access_code)
        
        # Extend to long-lived token
        print("\nExtending to long-lived token (60 days)...")
        long_lived_token = extend_token(user_token, app_id, app_secret)
        
        # Get page access token
        print(f"\nGetting page access token for page {page_id}...")
        page_token = get_page_access_token(long_lived_token, page_id)
        
        # Update .env file
        update_env_file(page_token, page_id)
        
        # Test the token
        print("\n" + "=" * 60)
        print("TESTING NEW TOKEN")
        print("=" * 60)
        
        from integrations.facebook_client import FacebookClient
        
        # Reload env to get new token
        load_dotenv(override=True)
        
        client = FacebookClient()
        success, info = client.validate_token()
        
        if success:
            print(f"\n✓ Token is valid!")
            print(f"✓ Page: {info}")
        else:
            print(f"\n⚠ Token validation returned: {info}")
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print("\nYour Facebook token has been refreshed.")
        print("You can now post to Facebook from the dashboard.")
        print("\nTest with: python test_facebook_post.py")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your Facebook App is set to 'Live' (not Development)")
        print("2. Add your Facebook account as a Developer/Admin in the app")
        print("3. Make sure App ID and Secret are correct")
        print("4. Try again with a different browser")
        sys.exit(1)


if __name__ == "__main__":
    main()
