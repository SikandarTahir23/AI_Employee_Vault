# Unified Integration Layer - AI Agency Dashboard

A simplified, unified Python service layer for all communication integrations.

## 📁 Files Created

```
AI_Employee_Vault/
├── integrations.py          # Main unified integration module
├── communication_hub.py     # Streamlit UI components
├── app.py                   # Updated to use new integration layer
└── UNIFIED_INTEGRATIONS.md  # This file
```

## 🚀 Quick Start

### 1. Import the Module

```python
from integrations import (
    send_email,
    read_gmail,
    send_whatsapp_message,
    post_to_linkedin,
    post_to_facebook
)
```

### 2. Use the Functions

#### Send Email (Gmail)
```python
success, message = send_email(
    to="recipient@example.com",
    subject="Hello",
    body="This is a test email"
)

if success:
    print(f"Email sent: {message}")
else:
    print(f"Failed: {message}")
```

#### Read Gmail
```python
success, emails = read_gmail(max_results=10)

if success:
    for email in emails:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
else:
    print("Failed to read Gmail")
```

#### Send WhatsApp Message
```python
success, message = send_whatsapp_message(
    phone_number="+923001234567",
    message="Hello from AI Dashboard!"
)

if success:
    print(f"Message sent: {message}")
else:
    print(f"Failed: {message}")
```

#### Post to LinkedIn
```python
success, message = post_to_linkedin(
    content="Hello LinkedIn! #AI #Automation"
)

if success:
    print(f"Posted: {message}")
else:
    print(f"Failed: {message}")
```

#### Post to Facebook
```python
success, message = post_to_facebook(
    message="Hello Facebook!",
    link="https://example.com"
)

if success:
    print(f"Posted: {message}")
else:
    print(f"Failed: {message}")
```

## 📋 Function Reference

### `send_email(to, subject, body, from_email=None, html=False)`

Send an email via Gmail API.

**Parameters:**
- `to` (str): Recipient email address
- `subject` (str): Email subject
- `body` (str): Email body text
- `from_email` (str, optional): Sender email (defaults to authenticated account)
- `html` (bool): If True, send as HTML

**Returns:** `Tuple[bool, str]` - (success, message)

---

### `read_gmail(max_results=10, query='is:inbox')`

Read emails from Gmail inbox.

**Parameters:**
- `max_results` (int): Maximum emails to retrieve
- `query` (str): Gmail search query

**Returns:** `Tuple[bool, List[Dict]]` - (success, emails)

Each email dict contains:
- `id`: Gmail message ID
- `subject`: Email subject
- `from`: Sender email
- `to`: Recipient email
- `date`: Email date
- `snippet`: Email preview text

---

### `send_whatsapp_message(phone_number, message, headless=False, timeout=60)`

Send a WhatsApp message via WhatsApp Web.

**Parameters:**
- `phone_number` (str): Phone number with country code (e.g., "+1234567890")
- `message` (str): Message text
- `headless` (bool): Run browser in headless mode
- `timeout` (int): Timeout in seconds

**Returns:** `Tuple[bool, str]` - (success, message)

**Note:** First call will open browser for QR code login. Session is persisted.

---

### `post_to_linkedin(content, headless=False)`

Post content to LinkedIn.

**Parameters:**
- `content` (str): Post content (text, emojis, hashtags)
- `headless` (bool): Run browser in headless mode

**Returns:** `Tuple[bool, str]` - (success, message)

**Note:** Opens browser for login on first use. Session is persisted.

---

### `post_to_facebook(message, link=None, photo_url=None)`

Post to Facebook Page via Graph API.

**Parameters:**
- `message` (str): Post message
- `link` (str, optional): Link to share
- `photo_url` (str, optional): Photo URL to attach

**Returns:** `Tuple[bool, str]` - (success, message)

**Note:** Requires `META_ACCESS_TOKEN` and `FB_PAGE_ID` in `.env`

---

## 🔧 Helper Functions

### Authentication

```python
from integrations import gmail_authenticate

# Force Gmail re-authentication
success, message = gmail_authenticate()
```

### Status Checks

```python
from integrations import (
    get_gmail_status,
    get_whatsapp_status,
    get_linkedin_status,
    get_facebook_status,
    get_all_status
)

# Get all integration statuses
status = get_all_status()
print(status['gmail'])      # Gmail status
print(status['whatsapp'])   # WhatsApp status
print(status['linkedin'])   # LinkedIn status
print(status['facebook'])   # Facebook status
```

### Token Validation

```python
from integrations import validate_facebook_token

# Validate Facebook token
success, message = validate_facebook_token()
```

### Cleanup

```python
from integrations import cleanup_all

# Clean up all browser resources
cleanup_all()
```

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit Dashboard (app.py)    │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    communication_hub.py          │   │
│  │    (UI Components)               │   │
│  └─────────────────────────────────┘   │
│              │                          │
│              ▼                          │
│  ┌─────────────────────────────────┐   │
│  │    integrations.py               │   │
│  │    (Unified Service Layer)       │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │         │         │
         ▼         ▼         ▼
    Gmail API  WhatsApp  LinkedIn  Facebook
               Web                 Graph API
```

## 🔐 Setup Requirements

### Gmail
1. Create Google Cloud project
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to project root
5. Run dashboard - authentication happens automatically

### WhatsApp
- No setup required!
- First message opens QR scanner
- Session persisted automatically

### LinkedIn
- No setup required!
- First post opens browser for login
- Session persisted automatically

### Facebook
Add to `.env`:
```env
META_ACCESS_TOKEN=your_page_token
FB_PAGE_ID=your_page_id
```

## 🧪 Testing

### Test All Integrations
```bash
python integrations.py
```

### Test Individual Functions

```python
# Test Gmail
from integrations import send_email, read_gmail

# Authenticate first
from integrations import gmail_authenticate
gmail_authenticate()

# Send test email
send_email("test@example.com", "Test", "Hello")

# Read inbox
read_gmail(max_results=5)
```

## 📝 Migration Guide

### From Old Modules to New Layer

**Before:**
```python
from gmail_integration import authenticate_gmail, send_email
service = authenticate_gmail()
send_email(service, to, subject, body)
```

**After:**
```python
from integrations import send_email
send_email(to, subject, body)  # Auto-authenticates
```

**Before:**
```python
from whatsapp_integration import send_whatsapp_message
result = send_whatsapp_message(phone, message, progress_callback=cb)
```

**After:**
```python
from integrations import send_whatsapp_message
success, msg = send_whatsapp_message(phone, message)
```

**Before:**
```python
from linkedin_poster import post_to_linkedin
post_to_linkedin(content)
```

**After:**
```python
from integrations import post_to_linkedin
success, msg = post_to_linkedin(content)
```

**Before:**
```python
from facebook_integration import post_to_facebook_page
success, msg = post_to_facebook_page(message, link)
```

**After:**
```python
from integrations import post_to_facebook
success, msg = post_to_facebook(message, link)
```

## ⚠️ Important Notes

1. **Automatic Authentication**: Functions auto-authenticate on first use
2. **Session Persistence**: Browser sessions are saved automatically
3. **Error Handling**: All functions return `(success, message)` tuple
4. **Logging**: All operations are logged to console
5. **Cleanup**: Call `cleanup_all()` when done (or on app shutdown)

## 🐛 Troubleshooting

### "Gmail not authenticated"
Run: `python setup_gmail_auth.py`

### "WhatsApp not logged in"
Send a message - browser will open for QR scan

### "LinkedIn not logged in"
Call `post_to_linkedin()` - browser will open for login

### "Facebook credentials not configured"
Add `META_ACCESS_TOKEN` and `FB_PAGE_ID` to `.env`

## 📖 Additional Documentation

- `INTEGRATION_SETUP.md` - Detailed setup for each service
- `INTEGRATION_ARCHITECTURE.md` - Full architecture documentation
- `setup_gmail_auth.py` - Gmail OAuth setup script

---

**Created:** March 12, 2026  
**Version:** 1.0.0  
**Author:** AI Automation Engineer
