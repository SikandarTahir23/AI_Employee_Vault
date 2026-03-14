"""
Meta (Facebook & Instagram) Automation Module
Sikandar Tahir | AI Agency Dashboard

Handles posting to Facebook Pages and Instagram Business accounts via Meta Graph API.
"""

import requests
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
# These should be set in .env file
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "")
IG_BUSINESS_ACCOUNT_ID = os.getenv("IG_BUSINESS_ACCOUNT_ID", "")

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
    Meta Graph API Automation for Sikandar Tahir's Dashboard.
    
    Usage:
        meta = MetaAutomation()
        result = meta.post_to_meta_simultaneously("Hello World!", image_path="image.jpg")
    """
    
    def __init__(self, 
                 access_token: str = None,
                 fb_page_id: str = None,
                 ig_account_id: str = None):
        """
        Initialize Meta Automation client for Sikandar Tahir.
        """
        self.access_token = access_token or META_ACCESS_TOKEN
        self.fb_page_id = fb_page_id or FB_PAGE_ID
        self.ig_account_id = ig_account_id or IG_BUSINESS_ACCOUNT_ID
        
        # Validate critical credentials
        if not self.access_token:
            # We don't raise error here to allow initialization for config purposes
            pass
    
    def _make_request(self, url: str, method: str = "GET", 
                      data: Dict = None, files: Dict = None) -> Dict:
        """Make a request to Meta Graph API using requests."""
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=data, timeout=30)
            else:
                if files:
                    # For files, we don't put everything in 'data' if it's large
                    response = requests.post(url, data=data, files=files, timeout=60)
                else:
                    response = requests.post(url, data=data, timeout=30)
            
            result = response.json()
            
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
        """Post to Sikandar Tahir's Facebook Page."""
        if not self.fb_page_id or not self.access_token:
            raise MetaAutomationError("Facebook configuration missing (Token or Page ID)")
        
        endpoint = f"{GRAPH_API_BASE}/{self.fb_page_id}/feed"
        
        data = {
            "message": message,
            "access_token": self.access_token,
        }
        
        if link:
            data["link"] = link
        
        files = {}
        if image_path:
            p = Path(image_path)
            if not p.exists():
                raise MetaAutomationError(f"Image not found: {image_path}")
            files["source"] = open(str(p), "rb")
        
        try:
            # If image exists, the endpoint changes to /photos
            if image_path:
                endpoint = f"{GRAPH_API_BASE}/{self.fb_page_id}/photos"
                data["caption"] = message  # message becomes caption for photos
                del data["message"]
            
            result = self._make_request(endpoint, "POST", data=data, files=files if files else None)
            
            post_id = result.get("id") or result.get("post_id")
            # Construct URL (PageID_PostID)
            clean_post_id = post_id.split('_')[-1] if '_' in str(post_id) else post_id
            post_url = f"https://www.facebook.com/{self.fb_page_id}/posts/{clean_post_id}"
            
            response_data = {
                "success": True,
                "platform": "facebook",
                "post_id": post_id,
                "post_url": post_url,
                "timestamp": datetime.now().isoformat(),
                "content": message,
            }
            
            self._log_to_obsidian(response_data)
            return response_data
            
        finally:
            if files and "source" in files:
                files["source"].close()
    
    def post_to_instagram(self, caption: str, image_path: str = None) -> Dict[str, Any]:
        """
        Post to Sikandar Tahir's Instagram Business Account.
        IMPORTANT: Instagram requires a public image URL.
        """
        if not self.ig_account_id or not self.access_token:
            raise MetaAutomationError("Instagram configuration missing (Token or Account ID)")
        
        if not image_path:
            raise MetaAutomationError("Instagram requires an image.")

        # In a real scenario, we'd upload to S3/Cloudinary first.
        # For this implementation, we assume image_path might be a URL 
        # OR we provide a clear error if it's a local file.
        image_url = image_path if image_path.startswith("http") else None
        
        if not image_url:
            # This is where we would implement the upload logic.
            # For now, we'll raise a descriptive error for the user.
            raise MetaAutomationError(
                "Instagram Graph API requires a publicly accessible image URL. "
                "Please upload the image to a hosting service (S3/Imgur) first, "
                "or provide a public URL."
            )
        
        # Step 1: Create media container
        container_endpoint = f"{GRAPH_API_BASE}/{self.ig_account_id}/media"
        container_data = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token,
        }
        
        container_result = self._make_request(container_endpoint, "POST", data=container_data)
        creation_id = container_result.get("id")
        
        # Step 2: Publish the media
        publish_endpoint = f"{GRAPH_API_BASE}/{self.ig_account_id}/media_publish"
        publish_data = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }
        
        publish_result = self._make_request(publish_endpoint, "POST", data=publish_data)
        post_id = publish_result.get("id")
        
        response_data = {
            "success": True,
            "platform": "instagram",
            "post_id": post_id,
            "post_url": f"https://www.instagram.com/p/{post_id}/", # This is a guess, usually needs shortcode
            "timestamp": datetime.now().isoformat(),
            "content": caption,
        }
        
        self._log_to_obsidian(response_data)
        return response_data

    def post_to_meta_simultaneously(self, message: str, image_path: str = None, 
                                   instagram_caption: str = None) -> Dict[str, Any]:
        """
        The core requirement: Post to FB and IG simultaneously.
        """
        results = {
            "facebook": {"success": False, "error": None},
            "instagram": {"success": False, "error": None},
            "timestamp": datetime.now().isoformat()
        }
        
        # Facebook
        try:
            results["facebook"] = self.post_to_facebook(message, image_path)
        except Exception as e:
            results["facebook"]["error"] = str(e)
            
        # Instagram
        if image_path:
            try:
                results["instagram"] = self.post_to_instagram(instagram_caption or message, image_path)
            except Exception as e:
                results["instagram"]["error"] = str(e)
        else:
            results["instagram"]["error"] = "Instagram requires an image"
            
        return results
    
    def _log_to_obsidian(self, post_data: Dict[str, Any]) -> str:
        """Create a markdown log entry in the Obsidian vault."""
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")
        
        log_folder = VAULT_DIR / "Social_Posts" / date_str
        log_folder.mkdir(parents=True, exist_ok=True)
        
        platform = post_data.get("platform", "unknown")
        filename = f"Meta_{platform}_{timestamp.strftime('%H%M%S')}.md"
        filepath = log_folder / filename
        
        content = f"""---
type: social_post
platform: {platform}
status: published
date: {date_str}
time: {time_str}
post_url: {post_data.get('post_url', 'N/A')}
post_id: {post_data.get('post_id', 'N/A')}
agent: Sikandar Tahir AI Dashboard
---

# Social Media Post Log: {platform.title()}

**Timestamp:** {date_str} {time_str}
**URL:** [{post_data.get('post_url', 'N/A')}]({post_data.get('post_url', 'N/A')})

## Content
{post_data.get('content', 'N/A')}

---
*Logged for Sikandar Tahir's Knowledge Graph*
"""
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)


def post_to_meta_simultaneously(message: str, image_path: str = None) -> Dict:
    """Convenience function for simultaneous posting."""
    meta = MetaAutomation()
    return meta.post_to_meta_simultaneously(message, image_path)
