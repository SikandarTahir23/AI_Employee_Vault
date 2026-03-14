# AI Employee Vault 🤖

A comprehensive AI-powered employee dashboard with multi-platform social media automation, email integration, and task management.

## Features

- **📘 Facebook Automation** - Post to Facebook Pages via browser automation (no API permissions required)
- **💼 LinkedIn Automation** - Auto-post and connection management
- **📱 WhatsApp Automation** - Send messages via WhatsApp Web with persistent sessions
- **📧 Gmail Integration** - Send and receive emails with OAuth 2.0
- **📋 Task Management** - Kanban board with AI-powered task processing
- **🔍 Financial Tracking** - Invoice and accounting status monitoring
- **🤖 AI Agent** - Autonomous task processing and briefings

## Project Structure

```
AI_Employee_Vault/
├── dashboard/              # Streamlit dashboard application
│   ├── app.py             # Main dashboard entry point
│   └── communication_hub.py  # Communication integrations UI
├── integrations/           # Platform integrations
│   ├── facebook/          # Facebook automation
│   ├── whatsapp/          # WhatsApp Web automation
│   ├── linkedin/          # LinkedIn automation
│   └── gmail/             # Gmail API integration
├── utils/                  # Utility modules
│   ├── agent_brain.py     # AI agent logic
│   ├── odoo_mcp_bridge.py # Odoo integration
│   └── vault_sync.py      # File synchronization
├── scripts/                # Standalone scripts
├── sessions/               # Browser session storage (gitignored)
│   ├── facebook_session/
│   ├── whatsapp_session/
│   └── linkedin_session/
├── watchers/               # Background monitoring services
├── .env                    # Environment variables (gitignored)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI_Employee_Vault
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example
copy .env.example .env

# Edit .env with your credentials
```

Required environment variables:

```env
# Facebook (optional - browser automation works without API)
META_ACCESS_TOKEN=your_token
FB_PAGE_ID=your_page_id

# Gmail (for email integration)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_secret

# LinkedIn (credentials stored in browser session)
```

## Usage

### Start the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will be available at `http://localhost:8501`

### Platform-Specific Usage

#### Facebook Posting

1. Navigate to the **Facebook Page** section
2. Expand **"Post via Browser (No API)"**
3. Enter your Facebook Page URL
4. Type your message
5. Click **"Post via Browser"**

First time: You'll need to log in. The session is saved for future use.

#### WhatsApp Messaging

1. Navigate to the **WhatsApp** section
2. Click **"Connect WhatsApp"** to scan QR code
3. Once connected, use **"Quick Send Message"** to send messages

#### LinkedIn Posting

1. Navigate to the **LinkedIn** section
2. Click **"Connect LinkedIn"** and log in
3. Use **"Post to LinkedIn"** to publish content

#### Gmail Integration

1. Navigate to the **Gmail** section
2. Click **"Connect Gmail"** for OAuth authentication
3. Send emails or read your inbox

## Background Watchers

The dashboard includes several background services:

- **Gmail Bridge** - Monitors Gmail for new messages
- **Desktop Watcher** - Monitors desktop for file changes
- **Agent Brain** - Processes tasks autonomously
- **Social Media Agent** - Manages social media posting
- **Odoo Bridge** - Syncs with Odoo ERP

Start/stop watchers from the dashboard sidebar.

## Security

- ✅ All credentials stored in `.env` (gitignored)
- ✅ Browser sessions stored locally (gitignored)
- ✅ OAuth 2.0 for Gmail and Facebook
- ✅ No hardcoded secrets in source code

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
flake8 .
```

## Troubleshooting

### Browser Automation Issues

If browser automation fails:

```bash
# Reinstall Playwright browsers
playwright install chromium

# Clear session folders
rm -rf sessions/facebook_session
rm -rf sessions/whatsapp_session
rm -rf sessions/linkedin_session
```

### Session Expired

If sessions expire frequently:

1. Delete the session folder for the affected platform
2. Reconnect through the dashboard
3. Ensure "Remember me" is checked during login

### Import Errors

If you see import errors after refactoring:

```bash
# Ensure you're in the project root
cd AI_Employee_Vault

# Reinstall in development mode
pip install -e .
```

## License

Proprietary - AI Employee Vault

## Support

For issues or questions, please open an issue on the GitHub repository.
