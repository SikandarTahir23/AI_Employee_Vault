# Gmail Integration Setup Guide

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Place credentials.json:**
   Put your `credentials.json` file in the project directory:
   ```
   AI_Employee_Vault/
   ├── credentials.json    <-- Place it here
   ├── gmail_integration.py
   ├── gmail_page.py
   └── app.py
   ```

## Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: **Desktop app**
   - Download the JSON file as `credentials.json`

## First-Time Authentication

1. Run your Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Navigate to the Gmail page and click "Connect Gmail"

3. A browser window will open asking you to:
   - Sign in to your Google account
   - Grant permissions to the application

4. After authorization, you'll be redirected and `token.json` will be created automatically

5. **Important:** The `token.json` file contains your refresh token. Keep it secure!

## Usage

### In Streamlit Dashboard

```python
from gmail_page import gmail_page

# Add to your main app
gmail_page()
```

### In Python Code

```python
from gmail_integration import (
    init_gmail_service,
    send_email,
    read_inbox
)

# Initialize service
service = init_gmail_service()

# Send email
send_email(service, "to@example.com", "Subject", "Body text")

# Read inbox
emails = read_inbox(service, max_results=10)
for email in emails:
    print(f"{email['subject']} - {email['from']}")
```

## Troubleshooting

### "credentials.json not found"
- Ensure the file is in the project directory
- Check the filename is exactly `credentials.json`

### "Token expired"
- Delete `token.json` and re-authenticate
- The token will be refreshed automatically on next run

### "Access blocked" / "App not verified"
- This is normal for development apps
- Click "Advanced" > "Go to [app name] (unsafe)"
- To avoid this, verify your app in Google Cloud Console

### Redirect URI mismatch
- Ensure `http://localhost:8090` is in your OAuth credentials
- The script uses port 8090 by default

## Security Notes

⚠️ **Important:**
- Never commit `credentials.json` or `token.json` to version control
- Add them to your `.gitignore`:
  ```
  credentials.json
  token.json
  ```
- Regenerate your client secret if it has been exposed publicly
- Store tokens securely - they provide access to your Gmail

## API Scopes

This integration requests:
- `gmail.send` - Send emails
- `gmail.readonly` - Read inbox

To modify scopes, edit the `SCOPES` list in `gmail_integration.py`.
