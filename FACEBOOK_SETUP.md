# Facebook Page Integration Setup Guide

## Overview

This integration uses the **Meta Graph API** to post to Facebook Pages programmatically.

## Required Credentials

| Variable | Description | Required |
|----------|-------------|----------|
| `META_ACCESS_TOKEN` | Page Access Token | ✅ Yes |
| `FB_PAGE_ID` | Your Facebook Page ID | ✅ Yes |
| `META_APP_ID` | Meta App ID | ⚠️ For token debug |
| `META_APP_SECRET` | Meta App Secret | ⚠️ For token debug |

## Step-by-Step Setup

### 1. Create a Meta Developer App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. Select use case: **Other** → **Next**
4. Select app type: **Business** → **Next**
5. Fill in app details:
   - App Name: `AI Automation Dashboard`
   - App Contact: Your email
6. Click **Create App**

### 2. Add Facebook Login Product

1. In your app dashboard, find **Add Product**
2. Click **+** next to **Facebook Login**
3. Configure settings:
   - Valid OAuth Redirect URIs: `https://localhost`
   - Save changes

### 3. Get Page Access Token

#### Option A: Using Graph API Explorer (Recommended for Testing)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **Get Token** → **Get User Access Token**
4. Select permissions:
   - ✅ `pages_manage_posts`
   - ✅ `pages_read_engagement`
   - ✅ `pages_show_list`
5. Click **Generate Token**
6. Login and grant permissions
7. In the response, find your page under `data` → find your page
8. Copy the `access_token` value - this is your **Page Access Token**

#### Option B: Exchange User Token for Page Token

```python
import requests

user_token = "YOUR_USER_TOKEN"
page_id = "YOUR_PAGE_ID"

url = "https://graph.facebook.com/v21.0/me/accounts"
params = {"access_token": user_token}

response = requests.get(url, params=params)
data = response.json()

for page in data.get('data', []):
    if page['id'] == page_id:
        page_token = page['access_token']
        print(f"Page Token: {page_token}")
```

### 4. Get Your Page ID

1. **From Graph API Explorer:**
   - Run query: `me/accounts`
   - Find your page in the response
   - Copy the `id` value

2. **From Facebook Page:**
   - Go to your Page
   - Click **About**
   - Find **Facebook Page ID**

3. **From Page URL:**
   - If URL is `facebook.com/123456789`, the ID is `123456789`

### 5. Configure .env File

Create or edit `.env` in your project root:

```env
# Facebook Page Integration
META_ACCESS_TOKEN=EAAGm0P4ZCpsBA... (your page access token)
FB_PAGE_ID=123456789012345
META_APP_ID=1234567890123456
META_APP_SECRET=abcdef1234567890abcdef12345678
```

### 6. Test the Integration

```bash
python facebook_integration.py
```

## Required Permissions

| Permission | Description | Why Needed |
|------------|-------------|------------|
| `pages_manage_posts` | Create, edit, delete posts | Posting content |
| `pages_read_engagement` | Read page engagement | Getting likes/comments |
| `pages_show_list` | List pages user manages | Finding your page |

## Token Expiration

| Token Type | Expiration |
|------------|------------|
| Short-lived User Token | 1-2 hours |
| Long-lived User Token | 60 days |
| Page Access Token | **Never expires** (if from long-lived user token) |

### Get Long-lived Token

```python
import requests

short_token = "YOUR_SHORT_TOKEN"
app_id = "YOUR_APP_ID"
app_secret = "YOUR_APP_SECRET"

url = "https://graph.facebook.com/v21.0/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": app_id,
    "client_secret": app_secret,
    "fb_exchange_token": short_token
}

response = requests.get(url, params=params)
data = response.json()
long_token = data["access_token"]
```

## API Usage

### Post Text Message

```python
from facebook_integration import post_to_facebook_page

success, msg = post_to_facebook_page("Hello from AI Dashboard!")
print(msg)
```

### Post with Link

```python
success, msg = post_to_facebook_page(
    message="Check out this article!",
    link="https://example.com/article"
)
```

### Post with Photo

```python
success, msg = post_to_facebook_page(
    message="Beautiful view!",
    photo_url="https://example.com/image.jpg"
)
```

### Using the Client Class

```python
from facebook_integration import FacebookPageClient

client = FacebookPageClient()

# Validate token
is_valid, info = client.validate_token()

# Get page info
page_info = client.get_page_info()

# Post
success, result = client.post_to_page("Hello World!")

# Get recent posts
posts = client.get_recent_posts(limit=5)
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `OAuthException` | Invalid/expired token | Generate new Page Access Token |
| `(#200) Permissions error` | Missing permissions | Grant `pages_manage_posts` |
| `(#100) Invalid parameter` | Wrong Page ID | Verify Page ID is correct |
| `Error validating token` | Token expired | Refresh Page Access Token |

### Test Token Validity

```bash
curl -G "https://graph.facebook.com/v21.0/debug_token" \
  -d "input_token=YOUR_PAGE_TOKEN" \
  -d "access_token=APP_ID|APP_SECRET"
```

## Testing Checklist

- [ ] Meta Developer App created
- [ ] Facebook Login product added
- [ ] User token generated with permissions
- [ ] Page Access Token obtained
- [ ] Page ID identified
- [ ] `.env` file configured
- [ ] Token validation passes
- [ ] Test post succeeds

## Security Best Practices

⚠️ **Important:**

1. **Never commit `.env`** - Already in `.gitignore`
2. **Use Page Tokens** - Don't use User tokens for posting
3. **Regenerate if exposed** - Tokens can be invalidated
4. **Limit permissions** - Only request what you need
5. **Store securely** - Use environment variables

## Rate Limits

| Endpoint | Rate Limit |
|----------|------------|
| `/feed` (posting) | 200 posts per hour |
| `/photos` | 200 photos per hour |
| Token debug | 200 calls per hour |

## Links

- [Graph API Reference](https://developers.facebook.com/docs/graph-api)
- [Facebook Login](https://developers.facebook.com/docs/facebook-login)
- [Access Token Debug](https://developers.facebook.com/tools/debug/access_token/)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
