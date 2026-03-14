# AI Agency Dashboard - Integration Setup Guide

Complete setup instructions for all communication integrations.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Gmail Integration Setup](#gmail-integration-setup)
3. [WhatsApp Integration Setup](#whatsapp-integration-setup)
4. [LinkedIn Integration Setup](#linkedin-integration-setup)
5. [Facebook Integration Setup](#facebook-integration-setup)
6. [Troubleshooting](#troubleshooting)
7. [Testing](#testing)

---

## Prerequisites

### Required Python Packages

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install playwright
pip install python-dotenv requests
pip install streamlit
```

### Install Playwright Browsers

```bash
playwright install chromium
```

---

## Gmail Integration Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"NEW PROJECT"**
3. Enter project name (e.g., "AI Agency Dashboard")
4. Click **"CREATE"**

### Step 2: Enable Gmail API

1. Go to [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
2. Click **"ENABLE"**

### Step 3: Create OAuth 2.0 Credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: **AI Agency Dashboard**
   - User support email: Your email
   - Developer contact: Your email
   - Click **"SAVE AND CONTINUE"**
   - Scopes: Skip this step
   - Test users: Add your email address
   - Click **"SAVE AND CONTINUE"**
4. Select **"Desktop app"** as application type
5. Click **"CREATE"**
6. Download the credentials JSON file

### Step 4: Place credentials.json

1. Rename the downloaded file to `credentials.json`
2. Place it in the project root:
   ```
   AI_Employee_Vault/
   ├── credentials.json    ← Place here
   ├── app.py
   ├── integrations/
   └── ...
   ```

### Step 5: Run Authentication

```bash
python setup_gmail_auth.py
```

Follow the browser prompts:
1. Click the URL shown in terminal
2. Sign in with your Google account
3. Click **"Allow"** to grant permissions
4. You'll be redirected to localhost (showing error - this is normal!)
5. Close that tab and return to terminal

### Step 6: Verify

```bash
python -c "from integrations.gmail_client import GmailClient; c = GmailClient(); print(c.authenticate())"
```

**Expected output:** `(True, "Authenticated as your@email.com")`

---

## WhatsApp Integration Setup

### Step 1: No Configuration Needed

WhatsApp uses browser automation with persistent sessions. No API keys required!

### Step 2: First-Time Login

1. Start the Streamlit dashboard
2. Go to **Communication Hub** → **WhatsApp**
3. Click **"Initialize WhatsApp"**
4. A browser window will open showing a QR code
5. Scan the QR code with your WhatsApp mobile app:
   - Open WhatsApp on phone
   - Tap **Menu** (⋮) or **Settings** (iOS)
   - Tap **Linked devices**
   - Tap **Link a device**
   - Scan the QR code

### Step 3: Session Persistence

After first login, the session is saved in `.whatsapp_session/` directory. Subsequent runs will automatically restore the session.

### Troubleshooting

**QR code not appearing:**
- Close all Chrome windows
- Delete `.whatsapp_session/` directory
- Run initialization again

**Session expired:**
- Re-run initialization and scan QR code again

---

## LinkedIn Integration Setup

### Step 1: No Configuration Needed

LinkedIn uses browser automation with persistent sessions. No API keys required!

### Step 2: First-Time Login

1. Start the Streamlit dashboard
2. Go to **Communication Hub** → **LinkedIn**
3. Click **"Initialize LinkedIn"**
4. A browser window will open to LinkedIn login
5. Log in with your LinkedIn credentials
6. Complete any 2FA if enabled
7. Close the browser window when you see your feed

### Step 3: Session Persistence

After first login, the session is saved in `.playwright_profile/` directory. Subsequent runs will automatically restore the session.

### Troubleshooting

**Login not persisting:**
- Make sure you fully log in (not just SSO)
- Wait 5 seconds after login before closing browser
- Check that `.playwright_profile/` directory exists

**"Not logged in" error:**
- Click **"Login to LinkedIn"** button in dashboard
- Complete login in the browser window
- Try posting again

---

## Facebook Integration Setup

### Step 1: Get Facebook Page Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app (or create one)
3. Click **"Get Token"** → **"Get Page Access Token"**
4. Select your Facebook Page
5. Copy the generated access token

### Step 2: Update .env File

Add these to your `.env` file:

```env
META_ACCESS_TOKEN=your_page_access_token_here
FB_PAGE_ID=your_page_id_here
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
```

### Step 3: Find Your Page ID

1. Go to your Facebook Page
2. Click **"About"**
3. Scroll to find **Page ID**
4. Or use: [Find My FB ID](https://findmyfbid.in/)

### Step 4: Validate Credentials

```bash
python -c "from integrations.facebook_client import validate_facebook_credentials; print(validate_facebook_credentials())"
```

**Expected output:** `(True, "Credentials validated successfully")`

### Token Expiration

- Short-lived tokens: ~1 hour
- Long-lived tokens: 60 days

To extend token:
1. Go to [Access Token Debugger](https://developers.facebook.com/tools/debug/access_token/)
2. Click **"Extend Access Token"**
3. Update `.env` with new token

---

## Troubleshooting

### Common Issues

#### Gmail: "credentials.json not found"

**Solution:**
```bash
# Check file exists
ls credentials.json

# Check file location
python -c "from integrations.gmail_client import CREDENTIALS_FILE; print(CREDENTIALS_FILE)"
```

#### Gmail: "Token expired"

**Solution:**
```bash
# Delete old token and re-authenticate
rm token.json
python setup_gmail_auth.py
```

#### WhatsApp: "Not logged in"

**Solution:**
1. Close all Chrome windows
2. Delete `.whatsapp_session/` directory
3. Re-initialize and scan QR code

#### WhatsApp: Browser opens but no QR code

**Solution:**
- Wait 10-15 seconds for page to load
- Refresh the page manually
- Check internet connection

#### LinkedIn: "Could not open post composer"

**Solution:**
- LinkedIn updates UI frequently
- Try logging out and back in
- Check for LinkedIn UI updates

#### LinkedIn: Post fails silently

**Solution:**
- Check `debug_linkedin_modal.png` for screenshots
- Ensure you're logged in
- Try manual post to verify account status

#### Facebook: "Invalid token"

**Solution:**
1. Token may have expired
2. Generate new token from Graph API Explorer
3. Update `.env` file
4. Restart Streamlit

#### Facebook: "Page ID not found"

**Solution:**
- Verify Page ID is correct (numeric only)
- Ensure you have admin access to the page
- Check token has page management permissions

---

## Testing

### Test All Integrations

```bash
# Gmail
python integrations/gmail_client.py

# WhatsApp
python integrations/whatsapp_client.py

# LinkedIn
python integrations/linkedin_client.py

# Facebook
python integrations/facebook_client.py
```

### Test via Streamlit

1. Start dashboard: `streamlit run app.py`
2. Go to **Communication Hub**
3. Test each integration:
   - **Gmail:** Click "Connect Gmail" → Read inbox
   - **WhatsApp:** Initialize → Send test message
   - **LinkedIn:** Initialize → Post test content
   - **Facebook:** Validate → Post test message

### Integration Manager Test

```bash
python integrations/manager.py
```

Shows status of all integrations.

---

## Quick Reference

### File Locations

| Integration | Config File | Session Directory |
|-------------|-------------|-------------------|
| Gmail | `credentials.json`, `token.json` | N/A |
| WhatsApp | N/A | `.whatsapp_session/` |
| LinkedIn | N/A | `.playwright_profile/` |
| Facebook | `.env` | N/A |

### Environment Variables

```env
# Gmail (via credentials.json)
# No env vars needed

# WhatsApp
# No env vars needed

# LinkedIn
# No env vars needed

# Facebook
META_ACCESS_TOKEN=...
FB_PAGE_ID=...
META_APP_ID=...
META_APP_SECRET=...
```

### Support URLs

- **Gmail API:** https://developers.google.com/gmail/api
- **WhatsApp Web:** https://web.whatsapp.com
- **LinkedIn:** https://www.linkedin.com/
- **Facebook Graph API:** https://developers.facebook.com/docs/graph-api

---

## Security Notes

1. **Never commit credentials:**
   - `credentials.json` - Add to `.gitignore`
   - `token.json` - Add to `.gitignore`
   - `.env` - Already in `.gitignore`

2. **Token Security:**
   - Store tokens securely
   - Use minimum required scopes
   - Refresh tokens before expiration

3. **Rate Limiting:**
   - Gmail: 250 quota units/day
   - Facebook: Varies by endpoint
   - WhatsApp/LinkedIn: Manual limits (avoid spam)

---

## Version Information

- **Python:** 3.9+
- **Playwright:** 1.40+
- **Google API Client:** 2.0+
- **Streamlit:** 1.28+

---

**Last Updated:** March 12, 2026
**Version:** 1.0.0
