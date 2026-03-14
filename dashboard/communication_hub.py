"""
Communication Hub for AI Agency Dashboard - Using Unified Integrations Module

This module provides the complete Communication Hub UI using the integrations.py module.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import time
import asyncio

# Import unified integrations
# Note: Using integrations package
from integrations import (
    send_email, read_inbox as read_gmail, get_user_profile as gmail_authenticate,
    send_whatsapp_message, post_to_linkedin, post_to_facebook_page as post_to_facebook,
    connect_linkedin, get_linkedin_status,
)

# Path configuration
BASE_DIR = Path(__file__).parent
DRAFTS_DIR = BASE_DIR / "Drafts"
APPROVED_DIR = BASE_DIR / "Approved"

# Status check functions
def get_gmail_status():
    """Get Gmail authentication status"""
    cred_file = BASE_DIR / 'credentials.json'
    token_file = BASE_DIR / 'token.json'
    return {
        'configured': cred_file.exists(),
        'authenticated': token_file.exists(),
        'token_exists': token_file.exists()
    }

def get_whatsapp_status():
    """Get WhatsApp connection status"""
    try:
        from integrations import get_whatsapp_status as _get_status
        return _get_status()
    except Exception:
        session_dir = BASE_DIR / '.whatsapp_session'
        return {
            'session_exists': session_dir.exists(),
            'logged_in': False,
            'initialized': False
        }

def get_linkedin_status():
    """Get LinkedIn connection status"""
    import time
    profile_dir = BASE_DIR / '.playwright_profile'
    
    status = {
        'profile_exists': profile_dir.exists(),
        'logged_in': False,
        'initialized': False
    }
    
    if status['profile_exists']:
        # Check for session files that indicate a saved login
        session_indicators = [
            'Login Data',
            'Cookies',
            'Local Storage',
        ]
        
        check_paths = [
            profile_dir,
            profile_dir / "Default",
        ]
        
        for base_path in check_paths:
            for indicator in session_indicators:
                indicator_path = base_path / indicator
                if indicator_path.exists():
                    try:
                        mtime = indicator_path.stat().st_mtime
                        age_days = (time.time() - mtime) / 86400
                        if age_days < 7:  # Session is less than 7 days old
                            status['logged_in'] = True
                            status['likely_logged_in'] = True
                            return status
                    except:
                        pass
        
        status['likely_logged_in'] = False
    
    return status

def get_facebook_status():
    """Get Facebook configuration status"""
    import os
    access_token = os.getenv('META_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    configured = bool(access_token and page_id)
    return {
        'configured': configured,
        'valid': configured,
        'page_id': page_id
    }

def validate_facebook_token():
    """Validate Facebook token"""
    from integrations.facebook.facebook_client import FacebookClient
    try:
        client = FacebookClient()
        success, info = client.validate_token()
        return success, info.get('error', 'Token valid') if not success else f"Valid token for page: {client.page_id}"
    except Exception as e:
        return False, str(e)

def get_all_status():
    """Get status of all integrations"""
    return {
        'gmail': get_gmail_status(),
        'whatsapp': get_whatsapp_status(),
        'linkedin': get_linkedin_status(),
        'facebook': get_facebook_status()
    }

# Cleanup functions
def whatsapp_cleanup():
    pass  # Handled automatically

def linkedin_cleanup():
    pass  # Handled automatically


def render_communication_hub():
    """Render the complete Communication Hub using integrations.py"""
    
    st.markdown('<div class="section-header">Communication Hub</div>', unsafe_allow_html=True)
    
    # Get all integration status
    all_status = get_all_status()
    
    # ── Three Column Layout: LinkedIn | WhatsApp | Gmail ──
    col_li, col_wa, col_gmail = st.columns(3)
    
    # Count approved items
    _approved_li = list(APPROVED_DIR.glob("LinkedIn_Post*.md")) if APPROVED_DIR.exists() else []
    _approved_wa = list(APPROVED_DIR.glob("WA_*.md")) if APPROVED_DIR.exists() else []
    
    # =========================================================================
    # LINKEDIN COLUMN
    # =========================================================================
    with col_li:
        # Get fresh LinkedIn status using imported function
        try:
            li_status = get_linkedin_status()
        except:
            li_status = all_status['linkedin']
        
        # Check multiple indicators for logged in state
        is_ready = (
            li_status.get('logged_in', False) or
            li_status.get('likely_logged_in', False) or
            st.session_state.get('linkedin_connected', False)
        )
        
        st.markdown(
            f'<div class="channel-card">'
            f'<div class="channel-card-header">'
            f'<span class="channel-icon">&#x1F4BC;</span>'
            f'<span class="channel-title">LinkedIn</span>'
            f'<span class="channel-status {"channel-status-ready" if is_ready else "channel-status-idle"}">'
            f'{"READY" if is_ready else "NOT LOGGED IN"}'
            f'</span>'
            f'</div>'
            f'<div class="channel-stat">Approved: <strong>{len(_approved_li)}</strong></div>'
            f'<div class="channel-stat">Drafts: <strong>{len(list(DRAFTS_DIR.glob("LinkedIn*.md"))) if DRAFTS_DIR.exists() else 0}</strong></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Session Status - Auto-expand when not logged in
        with st.expander("🔐 LinkedIn Session", expanded=not is_ready):
            if is_ready:
                st.success("✅ Session active - Ready to post")
                if st.button("🔄 Reconnect", key="linkedin_reconnect_btn", use_container_width=True):
                    try:
                        cleanup_linkedin()
                    except:
                        pass
                    if 'linkedin_connected' in st.session_state:
                        del st.session_state['linkedin_connected']
                    st.rerun()
            else:
                st.warning("⚠️ Not logged in")
                
                # Initialize connection state
                if 'linkedin_connecting' not in st.session_state:
                    st.session_state.linkedin_connecting = False
                if 'linkedin_result' not in st.session_state:
                    st.session_state.linkedin_result = None
                
                result_file = BASE_DIR / ".linkedin_connect_result.txt"
                
                # Check if result from previous connection attempt
                if not st.session_state.linkedin_connecting and result_file.exists():
                    try:
                        content = result_file.read_text(encoding="utf-8").strip()
                        if "|" in content:
                            success_str, msg = content.split("|", 1)
                            success = success_str == "True"
                            st.session_state.linkedin_result = (success, msg)
                            result_file.unlink(missing_ok=True)
                    except:
                        pass
                
                # Check if a connection process is running
                if st.session_state.linkedin_connecting:
                    st.info("🔐 Browser window is opening... Please wait for LinkedIn login.")
                    st.caption("LinkedIn → Enter your email and password → Click Sign in")
                    st.caption("💡 The browser will stay open - please complete login")
                    
                    # Check for result file
                    if result_file.exists():
                        try:
                            content = result_file.read_text(encoding="utf-8").strip()
                            if "|" in content:
                                success_str, msg = content.split("|", 1)
                                success = success_str == "True"
                                st.session_state.linkedin_result = (success, msg)
                                st.session_state.linkedin_connecting = False
                                result_file.unlink(missing_ok=True)
                                st.rerun()
                        except:
                            pass
                    
                    # Auto-refresh while connecting
                    time.sleep(1)
                    st.rerun()
                
                # Show result if available
                if st.session_state.linkedin_result:
                    success, msg = st.session_state.linkedin_result
                    if success:
                        st.success(f"✓ {msg}")
                        st.session_state.linkedin_connected = True
                        st.balloons()
                    else:
                        st.error(f"✗ {msg}")
                    
                    if st.button("🔄 Try Again", key="linkedin_retry_btn", use_container_width=True):
                        st.session_state.linkedin_connecting = False
                        st.session_state.linkedin_result = None
                        st.rerun()
                else:
                    # Connect button - launches external process
                    st.markdown("### 🔗 Connect to LinkedIn")
                    st.markdown("Click below to open LinkedIn in a browser window")
                    st.caption("📝 First time: You'll need to log in. Session will be saved.")
                    
                    if st.button("🔗 Connect LinkedIn", key="linkedin_connect_btn", use_container_width=True, type="primary"):
                        # Delete any old result file
                        result_file.unlink(missing_ok=True)
                        
                        # Launch connection script in separate process
                        launcher_script = BASE_DIR / "linkedin_launcher.py"
                        if launcher_script.exists():
                            subprocess.Popen(
                                [sys.executable, str(launcher_script)],
                                cwd=str(BASE_DIR),
                                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0,
                            )
                            st.session_state.linkedin_connecting = True
                            st.rerun()
                        else:
                            st.error(f"Launcher script not found: {launcher_script}")
                            st.info("💡 Trying direct connection...")
                            try:
                                success, msg = connect_linkedin(headless=False, timeout=120)
                                if success:
                                    st.success(f"✓ {msg}")
                                    st.session_state.linkedin_connected = True
                                    st.balloons()
                                else:
                                    st.error(f"✗ {msg}")
                            except Exception as e:
                                st.error(f"✗ Error: {e}")

            if li_status.get('profile_exists', False):
                st.caption(f"Profile: {li_status['profile_exists']}")
        
        # Post to LinkedIn
        with st.expander("✍️ Post to LinkedIn"):
            # Show approved drafts
            if _approved_li:
                post_options = {f.name: f.read_text(encoding="utf-8") for f in _approved_li}
                selected_post = st.selectbox(
                    "Select approved post",
                    options=list(post_options.keys()),
                    key="linkedin_post_select"
                )

                if selected_post:
                    st.text_area("Post content", value=post_options[selected_post],
                                height=150, key="linkedin_post_content")
            else:
                st.text_area("Post content", placeholder="Write your LinkedIn post here...",
                           height=150, key="linkedin_post_content")

            if st.button("📤 Post to LinkedIn", key="linkedin_post_btn", use_container_width=True):
                content = st.session_state.get("linkedin_post_content", "")
                if not content.strip():
                    st.warning("Please enter post content")
                else:
                    st.info("🔐 Opening browser... Please wait for LinkedIn to load.")
                    with st.spinner("📤 Posting to LinkedIn..."):
                        try:
                            result = post_to_linkedin(content, headless=False, wait_for_login=True)
                            # result is a tuple (success: bool, message: str)
                            if isinstance(result, tuple) and len(result) == 2:
                                success, msg = result
                                if success:
                                    st.success("✅ Post submitted!")
                                    st.toast("LinkedIn post published!", icon="💼")
                                    # Clear the content after successful post
                                    st.session_state.linkedin_post_content = ""
                                else:
                                    st.error(f"✗ {msg}")
                                    st.info("💡 Make sure you're logged in to LinkedIn. Try clicking 'Connect LinkedIn' above.")
                            else:
                                st.error(f"Unexpected response: {result}")
                        except Exception as e:
                            st.error(f"✗ Error: {e}")
                            st.info("💡 Check if LinkedIn is accessible and try again.")
    
    # =========================================================================
    # WHATSAPP COLUMN
    # =========================================================================
    with col_wa:
        # Get fresh WhatsApp status
        try:
            from integrations import get_whatsapp_status as wa_get_status
            wa_status = wa_get_status()
        except:
            wa_status = all_status['whatsapp']
        
        # Check multiple indicators for logged in state
        is_logged_in = (
            wa_status.get('logged_in', False) or 
            wa_status.get('likely_logged_in', False) or
            wa_status.get('whatsapp_connected', False)
        )

        st.markdown(
            f'<div class="channel-card">'
            f'<div class="channel-card-header">'
            f'<span class="channel-icon">&#x1F4F1;</span>'
            f'<span class="channel-title">WhatsApp</span>'
            f'<span class="channel-status {"channel-status-ready" if is_logged_in else "channel-status-idle"}">'
            f'{"READY" if is_logged_in else "NOT LOGGED IN"}'
            f'</span>'
            f'</div>'
            f'<div class="channel-stat">Queued: <strong>{len(_approved_wa)}</strong></div>'
            f'<div class="channel-stat">Session: <strong>{"✅ Active" if is_logged_in else "⚠️ Inactive"}</strong></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Login Section - Always expanded when not logged in
        login_expanded = not is_logged_in
        with st.expander("📱 WhatsApp Login", expanded=login_expanded):
            if is_logged_in:
                st.success("✅ Session active - Ready to send")
                if st.button("🔄 Reconnect", key="whatsapp_reconnect_btn", use_container_width=True):
                    whatsapp_cleanup()
                    if 'whatsapp_connected' in st.session_state:
                        del st.session_state['whatsapp_connected']
                    st.rerun()
            else:
                st.warning("⚠️ Not logged in")
                
                # Initialize connection state
                if 'wa_connecting' not in st.session_state:
                    st.session_state.wa_connecting = False
                if 'wa_result' not in st.session_state:
                    st.session_state.wa_result = None
                
                result_file = BASE_DIR / ".whatsapp_connect_result.txt"
                
                # Check if result from previous connection attempt
                if not st.session_state.wa_connecting and result_file.exists():
                    try:
                        content = result_file.read_text(encoding="utf-8").strip()
                        if "|" in content:
                            success_str, msg = content.split("|", 1)
                            success = success_str == "True"
                            st.session_state.wa_result = (success, msg)
                            result_file.unlink(missing_ok=True)
                    except:
                        pass
                
                # Check if a connection process is running
                if st.session_state.wa_connecting:
                    st.info("📱 Browser window is opening... Please wait for QR code.")
                    st.caption("WhatsApp → Menu/Settings → Linked Devices → Link a Device")
                    
                    # Check for result file
                    if result_file.exists():
                        try:
                            content = result_file.read_text(encoding="utf-8").strip()
                            if "|" in content:
                                success_str, msg = content.split("|", 1)
                                success = success_str == "True"
                                st.session_state.wa_result = (success, msg)
                                st.session_state.wa_connecting = False
                                result_file.unlink(missing_ok=True)
                                st.rerun()
                        except:
                            pass
                    
                    # Auto-refresh while connecting
                    time.sleep(1)
                    st.rerun()
                
                # Show result if available
                if st.session_state.wa_result:
                    success, msg = st.session_state.wa_result
                    if success:
                        st.success(f"✓ {msg}")
                        st.session_state.whatsapp_connected = True
                        st.balloons()
                    else:
                        st.error(f"✗ {msg}")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button("🔄 Try Again", key="wa_retry_btn", use_container_width=True):
                            st.session_state.wa_result = None
                            st.rerun()
                    with col2:
                        if st.button("✓ Done", key="wa_done_btn", use_container_width=True):
                            st.session_state.wa_result = None
                            st.rerun()
                else:
                    # Connect button - launches external process
                    st.markdown("### 🔗 Connect to WhatsApp")
                    
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        connect_clicked = st.button("🔗 Connect WhatsApp", key="whatsapp_connect_btn", use_container_width=True, type="primary")
                    with c2:
                        test_clicked = st.button("🧪 Test Direct", key="whatsapp_test_btn", use_container_width=True)
                    
                    if connect_clicked:
                        # Delete any old result file
                        result_file.unlink(missing_ok=True)
                        
                        # Launch connection script in separate process
                        launcher_script = BASE_DIR / "whatsapp_connect_launcher.py"
                        if launcher_script.exists():
                            subprocess.Popen(
                                [sys.executable, str(launcher_script)],
                                cwd=str(BASE_DIR),
                                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0,
                            )
                            st.session_state.wa_connecting = True
                            st.rerun()
                        else:
                            st.error(f"Launcher script not found: {launcher_script}")
                    
                    if test_clicked:
                        # Direct connection - opens browser immediately
                        st.info("📱 Opening browser directly...")
                        try:
                            from integrations.whatsapp.whatsapp_client import connect_whatsapp as wa_connect
                            success, msg = wa_connect(headless=False, timeout=60)
                            if success:
                                st.success(f"✓ {msg}")
                                st.session_state.whatsapp_connected = True
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"✗ {msg}")
                        except Exception as e:
                            st.error(f"✗ Error: {e}")

                st.caption("💡 First connection will display QR code to scan")

            if wa_status.get('session_exists', False):
                st.caption(f"Session directory exists: {wa_status['session_exists']}")
        
        # Quick Send
        with st.expander("✉️ Quick Send Message"):
            contact = st.text_input(
                "Contact",
                placeholder="Phone with country code (e.g., +923001234567)",
                key="whatsapp_contact_input"
            )
            message = st.text_area(
                "Message",
                placeholder="Type your message here...",
                height=80,
                key="whatsapp_message_input"
            )

            if st.button("🚀 Send Now", key="whatsapp_send_btn", use_container_width=True,
                         disabled=not (contact.strip() and message.strip())):
                with st.spinner("📱 Sending WhatsApp message..."):
                    result = send_whatsapp_message(contact.strip(), message.strip())
                    if result:
                        st.success("✅ Message sent!")
                        st.toast("✓ Message sent", icon="📱")
                    else:
                        st.error("Failed to send. Check browser for QR code or errors.")
                        st.info("📱 Please scan the QR code in the browser window that opened")
    
    # =========================================================================
    # GMAIL COLUMN
    # =========================================================================
    with col_gmail:
        gmail_status = all_status['gmail']
        is_authenticated = gmail_status.get('authenticated', False)
        
        st.markdown(
            f'<div class="channel-card">'
            f'<div class="channel-card-header">'
            f'<span class="channel-icon">&#x1F4E7;</span>'
            f'<span class="channel-title">Gmail</span>'
            f'<span class="channel-status {"channel-status-ready" if is_authenticated else "channel-status-idle"}">'
            f'{"AUTHENTICATED" if is_authenticated else "NOT AUTHENTICATED"}'
            f'</span>'
            f'</div>'
            f'<div class="channel-stat">Status: <strong>{"✅ Ready" if is_authenticated else "⚠️ Setup required"}</strong></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Configuration
        with st.expander("⚙️ Gmail Configuration"):
            if gmail_status.get('configured', False):
                st.success("✅ credentials.json found")
                
                if is_authenticated:
                    st.success("✅ Gmail authenticated")
                    if st.button("🔄 Re-authenticate", key="gmail_reauth_btn", use_container_width=True):
                        gmail_authenticate()
                        st.rerun()
                else:
                    st.warning("⚠️ Authentication required")
                    if st.button("🔐 Connect Gmail", key="gmail_auth_btn", use_container_width=True):
                        with st.spinner("Starting OAuth..."):
                            success, msg = gmail_authenticate()
                            if success:
                                st.success(f"✅ {msg}")
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
            else:
                st.error("❌ credentials.json not found")
                st.info("""
                **Setup:**
                1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                2. Create project, enable Gmail API
                3. Create OAuth 2.0 credentials (Desktop app)
                4. Download credentials.json to project root
                """)
        
        # Read Inbox
        if is_authenticated:
            with st.expander("📬 Recent Emails", expanded=True):
                if st.button("🔄 Refresh", key="gmail_refresh_btn", use_container_width=True):
                    st.session_state["gmail_refresh"] = True
                
                if st.session_state.get("gmail_refresh") or True:
                    with st.spinner("Fetching emails..."):
                        emails = read_gmail(max_results=10)
                        if emails:
                            for email in emails[:5]:
                                st.markdown(
                                    f'<div class="card">'
                                    f'<div class="card-title">{email["subject"]}</div>'
                                    f'<div class="card-meta">From: {email["from"]}</div>'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.info("No emails found")
        
        # Send Email
        with st.expander("✉️ Send Email"):
            to_email = st.text_input("To", placeholder="recipient@example.com",
                                    key="gmail_to_input")
            subject = st.text_input("Subject", placeholder="Email subject",
                                   key="gmail_subject_input")
            body = st.text_area("Message", placeholder="Type your message...",
                               height=100, key="gmail_body_input")
            
            if st.button("📤 Send Email", key="gmail_send_btn", use_container_width=True,
                         disabled=not (to_email.strip() and subject.strip() and body.strip())):
                if not is_authenticated:
                    st.error("Please authenticate first")
                else:
                    with st.status("Sending email...", expanded=True) as status:
                        result = send_email(
                            to_email.strip(),
                            subject.strip(),
                            body.strip()
                        )
                        if result:
                            status.update(label="✅ Email sent!", state="complete")
                            st.toast("✓ Email sent", icon="📧")
                            st.session_state["gmail_to_input"] = ""
                            st.session_state["gmail_subject_input"] = ""
                            st.session_state["gmail_body_input"] = ""
                        else:
                            status.update(label="❌ Send failed", state="error")
                            st.error("Failed to send email")
    
    # =========================================================================
    # FACEBOOK SECTION (Full Width)
    # =========================================================================
    st.markdown("---")
    st.markdown('<div class="section-header">Facebook Page</div>', unsafe_allow_html=True)
    
    fb_status = all_status['facebook']
    fb_configured = fb_status.get('configured', False)
    
    col_fb1, col_fb2 = st.columns([2, 1])
    
    with col_fb1:
        st.markdown(
            f'<div class="channel-card">'
            f'<div class="channel-card-header">'
            f'<span class="channel-icon">&#x1F4F1;</span>'
            f'<span class="channel-title">Facebook Page Poster</span>'
            f'<span class="channel-status {"channel-status-ready" if fb_configured else "channel-status-idle"}">'
            f'{"READY" if fb_configured else "NOT CONFIGURED"}'
            f'</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Configuration
        with st.expander("⚙️ Facebook Configuration", expanded=not fb_configured):
            if fb_configured:
                st.success("✅ Facebook configured in .env")
                
                if st.button("🔍 Validate Token", key="facebook_validate_btn", use_container_width=True):
                    with st.spinner("Validating..."):
                        success, msg = validate_facebook_token()
                        if success:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
            else:
                st.error("❌ Facebook credentials not configured")
                st.info("""
                **Setup:**
                1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
                2. Get Page Access Token
                3. Add to `.env`:
                   - `META_ACCESS_TOKEN=your_token`
                   - `FB_PAGE_ID=your_page_id`
                """)
        
        # Post to Facebook - Browser Automation (No API required)
        with st.expander("✍️ Post via Browser (No API)"):
            st.caption("Uses browser automation - no Graph API permissions needed")

            page_url = st.text_input(
                "Facebook Page URL",
                placeholder="https://www.facebook.com/your-page-name",
                value="https://www.facebook.com/profile.php?id=61582749851167",
                key="fb_browser_page_url"
            )
            message = st.text_area(
                "Post Message",
                placeholder="What's on your mind?",
                height=100,
                key="fb_browser_post_input"
            )

            if st.button("📤 Post via Browser", key="fb_browser_post_btn",
                        use_container_width=True, disabled=not message.strip()):
                if not page_url:
                    st.error("Please enter your Facebook Page URL")
                else:
                    # Launch external script for reliable execution
                    progress_bar = st.progress(0, text="Starting...")
                    status_text = st.empty()
                    
                    try:
                        import subprocess
                        import sys
                        
                        # Create a temporary script to run the post
                        temp_script = BASE_DIR / "temp_fb_post.py"
                        temp_script.write_text(f'''
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from integrations.facebook.facebook_browser import FacebookBrowser

async def main():
    fb = FacebookBrowser()
    try:
        connected, msg = await fb.connect(wait_for_login=True)
        if not connected:
            print(f"CONNECT_FAILED|{{msg}}")
            await fb.close()
            return
        print("CONNECTED")
        success, result = await fb.post_to_page("{page_url}", "{message.replace('"', '\\"')}")
        await fb.close()
        if success:
            print(f"SUCCESS|{{result}}")
        else:
            print(f"POST_FAILED|{{result}}")
    except Exception as e:
        print(f"ERROR|{{str(e)}}")
        await fb.close()

if __name__ == "__main__":
    asyncio.run(main())
''')
                        
                        # Run the script
                        status_text.info("🔄 Opening browser...")
                        progress_bar.progress(25, text="Connecting...")
                        
                        result = subprocess.run(
                            [sys.executable, str(temp_script)],
                            cwd=str(BASE_DIR),
                            capture_output=True,
                            text=True,
                            timeout=180
                        )
                        
                        # Parse output
                        output = result.stdout.strip()
                        status_text.info(f"Output: {output}")
                        
                        if "SUCCESS" in output:
                            progress_bar.progress(100, text="✅ Done!")
                            msg = output.split("|", 1)[1] if "|" in output else "Success"
                            st.toast(f"✓ {msg}", icon="📘")
                            st.success("Post published successfully!")
                            st.session_state["fb_browser_post_input"] = ""
                        elif "CONNECT_FAILED" in output:
                            progress_bar.progress(0, text="❌ Connection failed")
                            msg = output.split("|", 1)[1] if "|" in output else "Unknown error"
                            st.error(f"Connection failed: {msg}")
                            st.info("📘 Browser will open - please log in if needed")
                        elif "POST_FAILED" in output:
                            progress_bar.progress(0, text="❌ Post failed")
                            msg = output.split("|", 1)[1] if "|" in output else "Unknown error"
                            st.error(f"Post failed: {msg}")
                        elif "ERROR" in output:
                            progress_bar.progress(0, text="❌ Error")
                            msg = output.split("|", 1)[1] if "|" in output else "Unknown error"
                            st.error(f"Error: {msg}")
                        else:
                            progress_bar.progress(0, text="❌ Unknown result")
                            st.error(f"Unexpected output: {output}")
                            if result.stderr:
                                st.code(result.stderr)
                        
                        # Clean up
                        temp_script.unlink(missing_ok=True)
                        
                    except subprocess.TimeoutExpired:
                        progress_bar.progress(0, text="❌ Timeout")
                        st.error("Operation timed out after 3 minutes")
                        st.info("📘 Check if browser is waiting for login")
                    except Exception as e:
                        progress_bar.progress(0, text="❌ Error")
                        st.error(f"Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

        # Post to Facebook - Graph API (if configured)
        if fb_configured:
            with st.expander("✍️ Post via Graph API"):
                message = st.text_area(
                    "Post Message",
                    placeholder="What's on your mind?",
                    height=100,
                    key="facebook_post_input"
                )
                link = st.text_input("Link (optional)", placeholder="https://example.com",
                                    key="facebook_link_input")

                if st.button("📤 Post via API", key="facebook_post_btn", 
                            use_container_width=True, disabled=not message.strip()):
                    with st.status("Posting to Facebook...", expanded=True) as status:
                        success, msg = post_to_facebook(
                            message.strip(),
                            link=link.strip() if link else None
                        )
                        if success:
                            status.update(label="✅ Post published!", state="complete")
                            st.toast(f"✓ {msg}", icon="📘")
                            st.session_state["facebook_post_input"] = ""
                        else:
                            status.update(label="❌ Post failed", state="error")
                            st.error(f"Error: {msg}")
    
    with col_fb2:
        # Recent Posts (placeholder - would need API call to get posts)
        with st.expander("📜 Recent Posts", expanded=True):
            if fb_configured and fb_status.get('valid', False):
                st.info(f"Page: {fb_status.get('page_name', 'Unknown')}")
                st.caption(f"Page ID: {fb_status.get('page_id', '')}")
            else:
                st.info("Configure Facebook to see page info")


if __name__ == '__main__':
    st.set_page_config(page_title="Communication Hub Test", layout="wide")
    render_communication_hub()
