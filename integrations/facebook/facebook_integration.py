"""
Facebook Page Integration Module for AI Automation Dashboard
Uses Meta Graph API for page posting
"""

import os
import logging
import requests
from typing import Optional, Dict, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
FB_PAGE_ID = os.getenv('FB_PAGE_ID')
META_APP_ID = os.getenv('META_APP_ID')
META_APP_SECRET = os.getenv('META_APP_SECRET')

# Graph API endpoints
GRAPH_API_VERSION = 'v21.0'
GRAPH_API_BASE = f'https://graph.facebook.com/{GRAPH_API_VERSION}'


class FacebookPageClient:
    """
    Facebook Page client using Meta Graph API
    """
    
    def __init__(self, access_token: Optional[str] = None, page_id: Optional[str] = None):
        """
        Initialize Facebook Page client
        
        Args:
            access_token: Page access token (defaults to META_ACCESS_TOKEN from .env)
            page_id: Facebook Page ID (defaults to FB_PAGE_ID from .env)
        """
        self.access_token = access_token or META_ACCESS_TOKEN
        self.page_id = page_id or FB_PAGE_ID
        
        if not self.access_token:
            logger.error("META_ACCESS_TOKEN not found in environment")
            raise ValueError("Facebook access token is required")
        
        if not self.page_id:
            logger.error("FB_PAGE_ID not found in environment")
            raise ValueError("Facebook Page ID is required")
        
        logger.info(f"Initialized Facebook client for Page ID: {self.page_id}")
    
    def validate_token(self) -> Tuple[bool, Dict]:
        """
        Validate the access token and get its permissions
        
        Returns:
            Tuple of (is_valid: bool, token_info: dict)
        """
        try:
            logger.info("Validating access token...")
            
            # Debug token endpoint
            debug_url = f"{GRAPH_API_BASE}/debug_token"
            params = {
                'input_token': self.access_token,
                'access_token': f"{META_APP_ID}|{META_APP_SECRET}" if META_APP_ID and META_APP_SECRET else self.access_token
            }
            
            response = requests.get(debug_url, params=params, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            logger.debug(f"Token debug response: {token_data}")
            
            if 'data' not in token_data:
                logger.error("Invalid token debug response")
                return False, {'error': 'Invalid token response'}
            
            data = token_data['data']
            is_valid = data.get('is_valid', False)
            
            if is_valid:
                logger.info(f"✓ Token is valid")
                logger.info(f"  User ID: {data.get('user_id', 'Unknown')}")
                logger.info(f"  Expires: {data.get('expires_at', 'Never')}")
                
                # Get permissions
                permissions = data.get('scopes', [])
                logger.info(f"  Permissions: {permissions}")
            else:
                logger.error("✗ Token is invalid")
                logger.error(f"  Error: {data.get('error', {}).get('message', 'Unknown')}")
            
            return is_valid, data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token validation request failed: {e}")
            return False, {'error': str(e)}
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False, {'error': str(e)}
    
    def get_page_info(self) -> Optional[Dict]:
        """
        Get Facebook Page information
        
        Returns:
            Page info dictionary or None on error
        """
        try:
            logger.info(f"Fetching page info for {self.page_id}...")
            
            url = f"{GRAPH_API_BASE}/{self.page_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,username,category,followers_count,likes'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            page_data = response.json()
            logger.info(f"✓ Page: {page_data.get('name', 'Unknown')}")
            logger.info(f"  Category: {page_data.get('category', 'Unknown')}")
            logger.info(f"  Followers: {page_data.get('followers_count', 'N/A')}")
            
            return page_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get page info: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Failed to get page info: {e}")
            return None
    
    def post_to_page(self, message: str, link: Optional[str] = None,
                     photo_url: Optional[str] = None,
                     publish_immediately: bool = True) -> Tuple[bool, str]:
        """
        Post content to Facebook Page
        
        Args:
            message: Post message/text
            link: Optional link to share
            photo_url: Optional photo URL to attach
            publish_immediately: If True, publish immediately; if False, create as draft
        
        Returns:
            Tuple of (success: bool, message/error: str)
        """
        try:
            logger.info(f"Posting to page {self.page_id}...")
            logger.debug(f"Message: {message[:100]}..." if len(message) > 100 else f"Message: {message}")
            
            url = f"{GRAPH_API_BASE}/{self.page_id}/feed"
            
            params = {
                'access_token': self.access_token,
                'message': message
            }
            
            # Add optional parameters
            if link:
                params['link'] = link
                logger.debug(f"Link: {link}")
            
            if photo_url:
                params['url'] = photo_url
                logger.debug(f"Photo URL: {photo_url}")
            
            if not publish_immediately:
                params['published'] = 'false'
            
            # Make the request
            response = requests.post(url, params=params, timeout=30)
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
            
            # Check for errors
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    error_code = error_data.get('error', {}).get('code', 'Unknown')
                    logger.error(f"Facebook API Error ({error_code}): {error_msg}")
                    return False, f"API Error ({error_code}): {error_msg}"
                except:
                    logger.error(f"HTTP Error {response.status_code}: {response.text}")
                    return False, f"HTTP Error {response.status_code}"
            
            # Parse successful response
            result = response.json()
            post_id = result.get('id', 'Unknown')
            
            logger.info(f"✓ Post created successfully!")
            logger.info(f"  Post ID: {post_id}")
            
            return True, f"Post created: {post_id}"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            logger.error(f"Failed to post: {e}")
            return False, f"Error: {str(e)}"
    
    def post_photo(self, message: str, photo_path_or_url: str,
                   publish_immediately: bool = True) -> Tuple[bool, str]:
        """
        Post a photo to Facebook Page
        
        Args:
            message: Caption for the photo
            photo_path_or_url: Local file path or URL of the photo
            publish_immediately: If True, publish immediately
        
        Returns:
            Tuple of (success: bool, message/error: str)
        """
        try:
            logger.info(f"Posting photo to page {self.page_id}...")
            
            url = f"{GRAPH_API_BASE}/{self.page_id}/photos"
            
            # Check if it's a URL or local file
            if photo_path_or_url.startswith('http'):
                # URL
                params = {
                    'access_token': self.access_token,
                    'url': photo_path_or_url,
                    'published': 'true' if publish_immediately else 'false'
                }
                if message:
                    params['message'] = message
                
                response = requests.post(url, params=params, timeout=30)
            else:
                # Local file
                params = {
                    'access_token': self.access_token,
                    'published': 'true' if publish_immediately else 'false'
                }
                if message:
                    params['message'] = message
                
                with open(photo_path_or_url, 'rb') as f:
                    files = {'source': f}
                    response = requests.post(url, params=params, files=files, timeout=30)
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    return False, f"API Error: {error_msg}"
                except:
                    return False, f"HTTP Error {response.status_code}"
            
            result = response.json()
            post_id = result.get('id', 'Unknown')
            
            logger.info(f"✓ Photo posted successfully! Post ID: {post_id}")
            return True, f"Photo posted: {post_id}"
            
        except FileNotFoundError:
            logger.error(f"Photo file not found: {photo_path_or_url}")
            return False, f"File not found: {photo_path_or_url}"
        except Exception as e:
            logger.error(f"Failed to post photo: {e}")
            return False, f"Error: {str(e)}"
    
    def get_recent_posts(self, limit: int = 5) -> Optional[list]:
        """
        Get recent posts from the Facebook Page
        
        Args:
            limit: Number of posts to retrieve
        
        Returns:
            List of post dictionaries or None on error
        """
        try:
            logger.info(f"Fetching recent posts (limit: {limit})...")
            
            url = f"{GRAPH_API_BASE}/{self.page_id}/posts"
            params = {
                'access_token': self.access_token,
                'limit': limit,
                'fields': 'id,message,created_time,permalink_url,likes.summary(true),comments.summary(true)'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', [])
            
            logger.info(f"✓ Retrieved {len(posts)} posts")
            
            for post in posts:
                logger.debug(f"  Post {post.get('id')}: {post.get('message', '')[:50]}...")
            
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get posts: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get posts: {e}")
            return None


def validate_facebook_credentials() -> Tuple[bool, str]:
    """
    Validate all Facebook credentials from environment
    
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    missing = []
    
    if not META_ACCESS_TOKEN:
        missing.append('META_ACCESS_TOKEN')
    if not FB_PAGE_ID:
        missing.append('FB_PAGE_ID')
    
    if missing:
        return False, f"Missing credentials: {', '.join(missing)}"
    
    # Try to validate token
    try:
        client = FacebookPageClient()
        is_valid, info = client.validate_token()
        
        if is_valid:
            return True, "Credentials validated successfully"
        else:
            error_msg = info.get('error', {}).get('message', 'Token validation failed')
            return False, f"Invalid token: {error_msg}"
            
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def post_to_facebook_page(message: str, link: Optional[str] = None,
                          photo_url: Optional[str] = None) -> Tuple[bool, str]:
    """
    Standalone function to post to Facebook Page
    
    Args:
        message: Post message
        link: Optional link to share
        photo_url: Optional photo URL
    
    Returns:
        Tuple of (success: bool, message/error: str)
    """
    try:
        client = FacebookPageClient()
        return client.post_to_page(message, link=link, photo_url=photo_url)
    except Exception as e:
        logger.error(f"Failed to post to Facebook: {e}")
        return False, str(e)


if __name__ == '__main__':
    # Test the integration
    print("Facebook Page Integration Test")
    print("=" * 50)
    
    # Validate credentials
    is_valid, msg = validate_facebook_credentials()
    print(f"\nCredentials: {msg}")
    
    if is_valid:
        client = FacebookPageClient()
        
        # Get page info
        page_info = client.get_page_info()
        if page_info:
            print(f"\nPage: {page_info.get('name')}")
        
        # Test post
        test_message = f"Test post from AI Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"\nPosting test message...")
        
        success, result = client.post_to_page(test_message)
        print(f"Result: {result}")