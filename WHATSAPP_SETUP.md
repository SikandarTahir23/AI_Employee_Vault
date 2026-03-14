# WhatsApp Web Automation Setup Guide

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## Usage in Streamlit Dashboard

### Add to your main `app.py`:

```python
import streamlit as st
from whatsapp_page import whatsapp_page

# In your sidebar or navigation
if st.sidebar.button("WhatsApp"):
    st.session_state.page = "whatsapp"

# In your main content area
if st.session_state.get("page") == "whatsapp":
    whatsapp_page()
```

### Direct function usage:

```python
from whatsapp_integration import send_whatsapp_message

# Send a message (creates new browser session)
success, message = await send_whatsapp_message(
    phone_number="+1234567890",
    message="Hello from AI Dashboard!"
)
```

## First-Time Setup

1. **Run your Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Navigate to WhatsApp page**

3. **Click "Connect WhatsApp"** - A browser window opens

4. **Scan QR code** with your phone:
   - Open WhatsApp on phone
   - Tap **Menu (⋮)** or **Settings**
   - Select **Linked Devices**
   - Tap **Link a Device**
   - Point camera at QR code in browser

5. **Session saved** - Future runs will auto-login

## Configuration

### Environment Variables (.env)

```env
# Optional: Browser settings
WHATSAPP_HEADLESS=false
WHATSAPP_TIMEOUT=60000
```

### Session Storage

Browser session is stored in:
```
AI_Employee_Vault/.whatsapp_session/
```

This directory contains your login cookies and is automatically created.

## API Reference

### `WhatsAppAutomation` Class

```python
from whatsapp_integration import WhatsAppAutomation

# Initialize
automation = WhatsAppAutomation(headless=False)
await automation.initialize()

# Wait for login (if not already logged in)
await automation.wait_for_login(timeout=60)

# Send message
success, error_msg = await automation.send_message(
    phone_number="+1234567890",
    message="Hello!"
)

# Get recent chats
chats = await automation.get_chat_list(max_chats=10)

# Cleanup
await automation.cleanup()
```

### `send_whatsapp_message()` Function

```python
from whatsapp_integration import send_whatsapp_message

# One-liner to send message
success, msg = await send_whatsapp_message(
    phone_number="+1234567890",
    message="Hello World",
    headless=False
)
```

## Troubleshooting

### "QR code not showing"
- Close the browser window completely
- Delete `.whatsapp_session/` directory
- Reconnect and try again

### "Message not sending"
- Ensure you're logged in (check browser window)
- Verify phone number format (include country code)
- Check if contact exists on WhatsApp

### "Browser won't open"
- Run `playwright install chromium`
- Check firewall/antivirus settings
- Try running as administrator

### "Session expired"
- Delete `.whatsapp_session/` directory
- Re-authenticate with QR code

### Selectors not working
- WhatsApp Web updates frequently
- Check debug logs for selector errors
- Update selectors in `_find_message_input()` and `_find_send_button()`

## Debug Logs

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Logs show:
- Browser launch status
- Login detection
- Selector matches
- Send button clicks

## Security Notes

⚠️ **Important:**
- Never commit `.whatsapp_session/` to version control
- Session contains authentication cookies
- Log out from Linked Devices if session compromised
- Use with caution for automation (WhatsApp ToS)

## Phone Number Format

| Country | Format | Example |
|---------|--------|---------|
| USA | +1 | +1234567890 |
| India | +91 | +919876543210 |
| UK | +44 | +447123456789 |
| Brazil | +55 | +5511987654321 |

**Rules:**
- Include `+` prefix
- Include country code
- No spaces or dashes
- No leading zeros

## Limitations

- Requires active internet connection
- Browser window must remain open during automation
- WhatsApp Web may rate-limit frequent messages
- Not suitable for bulk messaging (violates ToS)

## Best Practices

1. **Reuse sessions** - Don't create new browser instances for each message
2. **Add delays** - Wait 2-3 seconds between messages
3. **Handle errors** - Always check return values
4. **Test first** - Send test messages before automation
5. **Respect ToS** - Don't use for spam or bulk messaging
