"""
Meta (Facebook & Instagram) Automation Module
Sikandar Tahir | AI Agency Dashboard

Handles posting to Facebook Pages and Instagram Business accounts via Meta Graph API.
"""

import requests
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "")
IG_BUSINESS_ACCOUNT_ID = os.getenv("IG_BUSINESS_ACCOUNT_ID", "")
META_APP_ID = os.getenv("META_APP_ID", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")

# Base URLs
GRAPH_API_BASE = "https://graph.facebook.com/v18.0"

# Obsidian Vault for logging
BASE_DIR = Path(__file__).resolve().parent
VAULT_DIR = BASE_DIR / "AI_EMPLOYEE_VAULT"
VAULT_DIR.mkdir(parents=True, exist_ok=True)


class MetaAutomationError(Exception):
    """Custom exception for Meta API errors."""
    pass


class MetaAutomation:
    """
    Meta Graph API Automation for Facebook & Instagram posting.
    
    Usage:
        meta = MetaAutomation()
        result = meta.post_to_facebook("Hello World!", image_path="image.jpg")
        result = meta.post_to_instagram("Hello World!", image_path="image.jpg")
        result = meta.post_to_both("Hello World!", image_path="image.jpg")
    """
    
    def __init__(self, 
                 access_token: str = None,
                 fb_page_id: str = None,
                 ig_account_id: str = None):
        """
        Initialize Meta Automation client.
        
        Args:
            access_token: Meta Access Token (defaults to .env value)
            fb_page_id: Facebook Page ID (defaults to .env value)
            ig_account_id: Instagram Business Account ID (defaults to .env value)
        """
        self.access_token = access_token or META_ACCESS_TOKEN
        self.fb_page_id = fb_page_id or FB_PAGE_ID
        self.ig_account_id = ig_account_id or IG_BUSINESS_ACCOUNT_ID
        
        # Validate credentials
        if not self.access_token:
            raise MetaAutomationError(
                "META_ACCESS_TOKEN not found. Please set it in .env file or pass it directly."
            )
    
    def _make_request(self, url: str, method: str = "GET", 
                      data: Dict = None, files: Dict = None) -> Dict:
        """
        Make a request to Meta Graph API.
        
        Args:
            url: Full API endpoint URL
            method: HTTP method (GET, POST)
            data: Request payload
            files: Files to upload
            
        Returns:
            JSON response as dict
            
        Raises:
            MetaAutomationError: If API request fails
        """
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=data, timeout=30)
            else:
                if files:
                    response = requests.post(url, data=data, files=files, timeout=60)
                else:
                    response = requests.post(url, data=data, timeout=30)
            
            result = response.json()
            
            # Check for API errors
            if "error" in result:
                error_msg = result["error"].get("message", "Unknown API error")
                error_code = result["error"].get("code", "unknown")
                raise MetaAutomationError(f"API Error [{error_code}]: {error_msg}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise MetaAutomationError(f"Network error: {str(e)}")
        except Exception as e:
            raise MetaAutomationError(f"Request failed: {str(e)}")
    
    def post_to_facebook(self, message: str, image_path: str = None, 
                         link: str = None) -> Dict[str, Any]:
        """
        Post to Facebook Page.
        
        Args:
            message: Post caption/text
            image_path: Optional path to image file
            link: Optional link to share
            
        Returns:
            Dict with post_id, url, and success status
        """
        if not self.fb_page_id:
            raise MetaAutomationError(
                "FB_PAGE_ID not found. Please set it in .env file."
            )
        
        endpoint = f"{GRAPH_API_BASE}/{self.fb_page_id}/feed"
        
        data = {
            "message": message,
            "access_token": self.access_token,
        }
        
        if link:
            data["link"] = link
        
        files = {}
        if image_path:
            if not Path(image_path).exists():
                raise MetaAutomationError(f"Image not found: {image_path}")
            files["source"] = open(image_path, "rb")
        
        try:
            result = self._make_request(endpoint, "POST", data=data, files=files if files else None)
            
            post_id = result.get("id")
            post_url = f"https://www.facebook.com/{self.fb_page_id}/posts/{post_id.split('_')[1]}" if post_id else None
            
            response_data = {
                "success": True,
                "platform": "facebook",
                "post_id": post_id,
                "post_url": post_url,
                "timestamp": datetime.now().isoformat(),
                "message": message,
            }
            
            # Log to Obsidian
            self._log_to_obsidian(response_data)
            
            return response_data
            
        finally:
            if files and "source" in files:
                files["source"].close()
    
    def post_to_instagram(self, caption: str, image_path: str = None) -> Dict[str, Any]:
        """
        Post to Instagram Business Account.
        
        Note: Instagram requires images to be publicly accessible URLs.
        For local files, they need to be uploaded to a server first.
        
        Args:
            caption: Post caption
            image_path: Path to image file (will be uploaded)
            
        Returns:
            Dict with post_id, url, and success status
        """
        if not self.ig_account_id:
            raise MetaAutomationError(
                "IG_BUSINESS_ACCOUNT_ID not found. Please set it in .env file."
            )
        
        # Step 1: Create media container
        container_endpoint = f"{GRAPH_API_BASE}/{self.ig_account_id}/media"
        
        # For local images, we need to upload to a publicly accessible URL
        # This is a limitation of Instagram Graph API
        image_url = self._upload_image_for_instagram(image_path) if image_path else None
        
        if not image_url:
            raise MetaAutomationError(
                "Instagram requires a publicly accessible image URL. "
                "Please upload your image to a server or use a URL."
            )
        
        container_data = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token,
        }
        
        container_result = self._make_request(container_endpoint, "POST", data=container_data)
        creation_id = container_result.get("id")
        
        if not creation_id:
            raise MetaAutomationError("Failed to create Instagram media container")
        
        # Step 2: Publish the media
        publish_endpoint = f"{GRAPH_API_BASE}/{self.ig_account_id}/media_publish"
        publish_data = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }
        
        publish_result = self._make_request(publish_endpoint, "POST", data=publish_data)
        post_id = publish_result.get("id")
        
        post_url = f"https://www.instagram.com/p/{post_id}" if post_id else None
        
        response_data = {
            "success": True,
            "platform": "instagram",
            "post_id": post_id,
            "post_url": post_url,
            "timestamp": datetime.now().isoformat(),
            "caption": caption,
        }
        
        # Log to Obsidian
        self._log_to_obsidian(response_data)
        
        return response_data
    
    def _upload_image_for_instagram(self, image_path: str) -> str:
        """
        Upload local image to get a publicly accessible URL.
        
        For production, you would upload to your server or cloud storage.
        This is a placeholder that returns the local path (won't work for IG API).
        
        Args:
            image_path: Local path to image
            
        Returns:
            Public URL string
        """
        # TODO: Implement actual upload to cloud storage (S3, Cloudinary, etc.)
        # For now, return None to indicate this needs implementation
        return None
    
    def post_to_both(self, message: str, image_path: str = None,
                     instagram_caption: str = None) -> Dict[str, Any]:
        """
        Post to both Facebook and Instagram.
        
        Args:
            message: Post message (used for Facebook)
            image_path: Optional path to image file
            instagram_caption: Optional different caption for Instagram
            
        Returns:
            Dict with results from both platforms
        """
        results = {
            "facebook": None,
            "instagram": None,
            "success_count": 0,
            "errors": [],
        }
        
        # Post to Facebook
        try:
            fb_result = self.post_to_facebook(message, image_path)
            results["facebook"] = fb_result
            results["success_count"] += 1
        except MetaAutomationError as e:
            results["errors"].append(f"Facebook: {str(e)}")
        
        # Post to Instagram (only if image provided)
        if image_path:
            try:
                ig_caption = instagram_caption or message
                ig_result = self.post_to_instagram(ig_caption, image_path)
                results["instagram"] = ig_result
                results["success_count"] += 1
            except MetaAutomationError as e:
                results["errors"].append(f"Instagram: {str(e)}")
        
        return results
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information for verification.
        
        Returns:
            Dict with Facebook Page and Instagram account info
        """
        info = {
            "facebook": None,
            "instagram": None,
        }
        
        # Get Facebook Page info
        if self.fb_page_id:
            try:
                fb_endpoint = f"{GRAPH_API_BASE}/{self.fb_page_id}"
                fb_data = {
                    "fields": "id,name,username,followers_count",
                    "access_token": self.access_token,
                }
                info["facebook"] = self._make_request(fb_endpoint, "GET", fb_data)
            except MetaAutomationError as e:
                info["facebook"] = {"error": str(e)}
        
        # Get Instagram Account info
        if self.ig_account_id:
            try:
                ig_endpoint = f"{GRAPH_API_BASE}/{self.ig_account_id}"
                ig_data = {
                    "fields": "id,username,followers_count,media_count",
                    "access_token": self.access_token,
                }
                info["instagram"] = self._make_request(ig_endpoint, "GET", ig_data)
            except MetaAutomationError as e:
                info["instagram"] = {"error": str(e)}
        
        return info
    
    def _log_to_obsidian(self, post_data: Dict[str, Any]) -> str:
        """
        Create a markdown log entry in the Obsidian vault.
        
        Args:
            post_data: Post result data
            
        Returns:
            Path to created log file
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Create dated subfolder
        log_folder = VAULT_DIR / "Social_Posts" / date_str
        log_folder.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        platform = post_data.get("platform", "unknown")
        safe_time = time_str.replace(":", "-")
        filename = f"Meta_{platform}_{date_str}_{safe_time}.md"
        filepath = log_folder / filename
        
        # Create markdown content
        content = f"""---
type: social_post
platform: {platform}
status: published
date: {date_str}
time: {time_str}
tags:
  - social_media
  - meta
  - {platform}
  - sikandar_tahir_agency
---

# Social Media Post Log

## Platform
**{platform.title()}**

## Timestamp
📅 **Date:** {date_str}  
⏰ **Time:** {time_str}

## Post URL
🔗 [{post_data.get('post_url', 'N/A')}]({post_data.get('post_url', 'N/A')})

## Post ID
`{post_data.get('post_id', 'N/A')}`

## Content
```
{post_data.get('message', post_data.get('caption', 'N/A'))}
```

## Metadata
- **Success:** {post_data.get('success', False)}
- **API Version:** v18.0
- **Logged by:** AI Employee Vault

---
*Auto-generated by Sikandar Tahir AI Agency Dashboard*
"""
        
        # Write file
        filepath.write_text(content, encoding="utf-8")
        
        return str(filepath)
    
    def validate_credentials(self) -> Tuple[bool, str]:
        """
        Validate Meta API credentials.
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            info = self.get_account_info()
            
            fb_status = "✓" if info.get("facebook") and "error" not in info.get("facebook", {}) else "✗"
            ig_status = "✓" if info.get("instagram") and "error" not in info.get("instagram", {}) else "✗"
            
            message = f"Facebook: {fb_status} | Instagram: {ig_status}"
            is_valid = fb_status == "✓" or ig_status == "✓"
            
            return is_valid, message
            
        except Exception as e:
            return False, f"Validation failed: {str(e)}"


# ──────────────────────────────────────────────
# CONVENIENCE FUNCTIONS
# ──────────────────────────────────────────────
def post_to_facebook(message: str, image_path: str = None, link: str = None) -> Dict:
    """Quick function to post to Facebook."""
    meta = MetaAutomation()
    return meta.post_to_facebook(message, image_path, link)


def post_to_instagram(caption: str, image_path: str = None) -> Dict:
    """Quick function to post to Instagram."""
    meta = MetaAutomation()
    return meta.post_to_instagram(caption, image_path)


def post_to_both(message: str, image_path: str = None) -> Dict:
    """Quick function to post to both platforms."""
    meta = MetaAutomation()
    return meta.post_to_both(message, image_path)


def validate_meta_credentials() -> Tuple[bool, str]:
    """Quick function to validate credentials."""
    try:
        meta = MetaAutomation()
        return meta.validate_credentials()
    except Exception as e:
        return False, str(e)


# ──────────────────────────────────────────────
# CLI TESTING
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  META AUTOMATION TEST")
    print("  Sikandar Tahir | AI Agency Dashboard")
    print("=" * 60)
    
    # Validate credentials
    print("\n[1] Validating credentials...")
    is_valid, message = validate_meta_credentials()
    print(f"    Result: {message}")
    
    if not is_valid:
        print("\n[!] Credentials not configured. Please update .env file.")
        print("\nRequired environment variables:")
        print("  - META_ACCESS_TOKEN")
        print("  - FB_PAGE_ID (for Facebook posting)")
        print("  - IG_BUSINESS_ACCOUNT_ID (for Instagram posting)")
    else:
        print("\n[OK] Credentials validated!")
        
        # Get account info
        print("\n[2] Fetching account info...")
        meta = MetaAutomation()
        info = meta.get_account_info()
        
        if info.get("facebook"):
            fb = info["facebook"]
            print(f"\n    Facebook Page:")
            print(f"      - Name: {fb.get('name', 'N/A')}")
            print(f"      - Username: @{fb.get('username', 'N/A')}")
            print(f"      - Followers: {fb.get('followers_count', 'N/A')}")
        
        if info.get("instagram"):
            ig = info["instagram"]
            print(f"\n    Instagram Account:")
            print(f"      - Username: @{ig.get('username', 'N/A')}")
            print(f"      - Followers: {ig.get('followers_count', 'N/A')}")
            print(f"      - Posts: {ig.get('media_count', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("  TEST COMPLETE")
    print("=" * 60)
