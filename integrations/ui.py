"""
Communication Hub UI Components for Streamlit Dashboard

Provides UI components for all communication channels:
- Gmail
- WhatsApp
- LinkedIn
- Facebook

Usage:
    from integrations.ui import render_communication_hub
    
    render_communication_hub()
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from .manager import IntegrationManager, get_integration_manager

# Path configuration
BASE_DIR = Path(__file__).parent.parent
DRAFTS_DIR = BASE_DIR / "Drafts"
APPROVED_DIR = BASE_DIR / "Approved"
DONE_DIR = BASE_DIR / "Done"


def render_linkedin_column(manager: IntegrationManager):
    """Render LinkedIn integration column"""
    st.markdown(
        f'<div class="channel-card">'
        f'<div class="channel-card-header">'
        f'<span class="channel-icon">&#x1F4BC;</span>'
        f'<span class="channel-title">LinkedIn</span>'
        f'<span class="channel-status {"channel-status-ready" if manager.linkedin_is_initialized() else "channel-status-idle"}">'
        f'{"READY" if manager.linkedin_is_initialized() else "NOT INITIALIZED"}'
        f'</span>'
        f'</div>'
        f'<div class="channel-stat">Approved posts: <strong>{len(list(APPROVED_DIR.glob("LinkedIn_Post*.md"))) if APPROVED_DIR.exists() else 0}</strong></div>'
        f'<div class="channel-stat">Drafts: <strong>{len(list(DRAFTS_DIR.glob("LinkedIn*.md"))) if DRAFTS_DIR.exists() else 0}</strong></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Session Status
    session_status = manager.linkedin_get_session_status()

    with st.expander("🔐 LinkedIn Session"):
        if session_status['is_logged_in']:
            st.success("✅ Session active - Ready to post")
            st.caption(f"Profile: {session_status['profile_dir']}")
        else:
            st.warning("⚠️ Not logged in")
            if st.button("🚀 Login to LinkedIn", key="linkedin_login_btn", use_container_width=True):
                with st.spinner("Opening browser for login..."):
                    success, msg = manager.linkedin_initialize(headless=False)
                    if success:
                        if manager.linkedin_is_initialized():
                            st.success("LinkedIn initialized!")
                            if not manager.linkedin_is_logged_in():
                                st.info("Please log in to LinkedIn in the browser window")
                                with st.spinner("⏳ Waiting for login (2 minutes)..."):
                                    success, msg = manager.linkedin_wait_for_login(timeout=120)
                                    if success:
                                        st.success("✅ Login successful!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Login timeout")
                        else:
                            st.error(f"Initialization failed: {msg}")
                    else:
                        st.error(f"Error: {msg}")

            if session_status['profile_exists']:
                st.caption(f"Existing profile: {session_status['profile_dir']}")
                if st.button("🔄 Re-initialize Session", key="linkedin_reinit_btn", use_container_width=True):
                    manager.linkedin_cleanup()
                    st.rerun()

    # Post to LinkedIn
    with st.expander("✍️ Post to LinkedIn"):
        st.caption("Post content directly to LinkedIn")
        
        # Show approved drafts
        approved_posts = list(APPROVED_DIR.glob("LinkedIn_Post*.md")) if APPROVED_DIR.exists() else []
        if approved_posts:
            post_options = {f.name: f for f in approved_posts}
            selected_post = st.selectbox(
                "Select approved post",
                options=list(post_options.keys()),
                key="linkedin_post_select"
            )
            
            if selected_post:
                post_file = post_options[selected_post]
                content = post_file.read_text(encoding="utf-8")
                st.text_area("Post content", value=content, height=150, key="linkedin_post_content")
        
        if st.button("📤 Post to LinkedIn", key="linkedin_post_btn", use_container_width=True,
                     disabled=not manager.linkedin_is_initialized()):
            if not manager.linkedin_is_logged_in():
                st.error("Please login first")
            else:
                content = st.session_state.get("linkedin_post_content", "")
                if not content.strip():
                    st.warning("Please enter post content")
                else:
                    with st.spinner("📤 Posting to LinkedIn..."):
                        success, msg = manager.linkedin_post(content, headless=False)
                        if success:
                            st.success("✅ Post submitted!")
                            st.toast("LinkedIn post published!", icon="💼")
                        else:
                            st.error(f"Error: {msg}")


def render_whatsapp_column(manager: IntegrationManager):
    """Render WhatsApp integration column"""
    session_status = manager.whatsapp_get_session_status()
    is_logged_in = manager.whatsapp_is_initialized()
    
    st.markdown(
        f'<div class="channel-card">'
        f'<div class="channel-card-header">'
        f'<span class="channel-icon">&#x1F4F1;</span>'
        f'<span class="channel-title">WhatsApp</span>'
        f'<span class="channel-status {"channel-status-ready" if is_logged_in else "channel-status-idle"}">'
        f'{"READY" if is_logged_in else "NOT LOGGED IN"}'
        f'</span>'
        f'</div>'
        f'<div class="channel-stat">Queued: <strong>{len(list(APPROVED_DIR.glob("WA_*.md"))) if APPROVED_DIR.exists() else 0}</strong></div>'
        f'<div class="channel-stat">Session: <strong>{"✅ Active" if is_logged_in else "⚠️ Inactive"}</strong></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # QR Scanner Section
    with st.expander("📱 WhatsApp Login"):
        if is_logged_in:
            st.success("✅ Session active - Ready to send messages")
            st.caption(f"Session: {session_status['session_dir']}")
            
            if st.button("🔄 Re-login (Reset Session)", key="whatsapp_relogin_btn", use_container_width=True):
                manager.whatsapp_cleanup()
                st.rerun()
        else:
            st.warning("⚠️ Not logged in - Scan QR code to authenticate")
            
            if st.button("🔐 Open QR Scanner", key="whatsapp_qr_btn", use_container_width=True):
                with st.spinner("Initializing WhatsApp..."):
                    success, msg = manager.whatsapp_initialize(headless=False)
                    if success:
                        if manager.whatsapp_is_initialized():
                            if not manager.whatsapp_is_logged_in():
                                st.info("📱 Please scan the QR code in the browser window")
                                with st.status("Waiting for QR scan...", expanded=True) as status:
                                    success, msg = manager.whatsapp_wait_for_login(timeout=60)
                                    if success:
                                        status.update(label="✅ Login successful!", state="complete")
                                        st.rerun()
                                    else:
                                        status.update(label="❌ Login timeout", state="error")
                            else:
                                st.success("✅ Already logged in!")
                                st.rerun()
                        else:
                            st.error(f"Initialization failed: {msg}")
                    else:
                        st.error(f"Error: {msg}")

    # Quick Send Section
    with st.expander("✉️ Quick Send Message"):
        st.caption("Send a WhatsApp message directly")
        
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
            if not is_logged_in:
                st.error("Please login first")
            else:
                with st.status("Sending message...", expanded=True) as status:
                    success, msg = manager.whatsapp_send_message(contact.strip(), message.strip())
                    if success:
                        status.update(label="✅ Message sent!", state="complete")
                        st.toast(f"✓ {msg}", icon="📱")
                    else:
                        status.update(label="❌ Send failed", state="error")
                        st.error(f"Error: {msg}")


def render_gmail_column(manager: IntegrationManager):
    """Render Gmail integration column"""
    is_configured, config_msg = manager.gmail_is_configured()
    is_authenticated = manager.gmail_is_authenticated()
    
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

    # Configuration Section
    with st.expander("⚙️ Gmail Configuration"):
        if is_configured:
            st.success(config_msg)
            
            if is_authenticated:
                profile = manager.gmail_get_profile()
                if profile:
                    st.success(f"✅ Authenticated as: {profile.get('email', 'Unknown')}")
                    st.caption(f"Total messages: {profile.get('messages_total', 'N/A')}")
                    
                    if st.button("🔄 Re-authenticate", key="gmail_reauth_btn", use_container_width=True):
                        manager._gmail_client = None
                        st.rerun()
            else:
                st.warning("⚠️ Authentication required")
                if st.button("🔐 Connect Gmail", key="gmail_auth_btn", use_container_width=True):
                    with st.spinner("Starting OAuth authentication..."):
                        success, msg = manager.gmail_authenticate()
                        if success:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
        else:
            st.error(config_msg)
            st.info("""
            **Setup Instructions:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a project and enable Gmail API
            3. Create OAuth 2.0 credentials (Desktop app)
            4. Download credentials.json
            5. Place it in the project root directory
            6. Run: `python setup_gmail_auth.py`
            """)

    # Read Inbox Section
    if is_authenticated:
        with st.expander("📬 Recent Emails", expanded=True):
            if st.button("🔄 Refresh Inbox", key="gmail_refresh_btn", use_container_width=True):
                st.session_state["gmail_refresh"] = True
            
            if st.session_state.get("gmail_refresh") or True:
                with st.spinner("Fetching emails..."):
                    success, emails = manager.gmail_read_inbox(max_results=10)
                    if success:
                        if emails:
                            for email in emails[:5]:
                                with st.container():
                                    st.markdown(
                                        f'<div class="card">'
                                        f'<div class="card-title">{email["subject"]}</div>'
                                        f'<div class="card-meta">From: {email["from"]}</div>'
                                        f'<div class="card-meta">Date: {email["date"][:25] if email["date"] else "Unknown"}</div>'
                                        f'</div>',
                                        unsafe_allow_html=True,
                                    )
                        else:
                            st.info("No emails found")
                    else:
                        st.error("Failed to fetch emails")

    # Send Email Section
    with st.expander("✉️ Send Email"):
        st.caption("Send an email via Gmail")
        
        to_email = st.text_input(
            "To",
            placeholder="recipient@example.com",
            key="gmail_to_input"
        )
        subject = st.text_input(
            "Subject",
            placeholder="Email subject",
            key="gmail_subject_input"
        )
        body = st.text_area(
            "Message",
            placeholder="Type your message here...",
            height=100,
            key="gmail_body_input"
        )
        
        if st.button("📤 Send Email", key="gmail_send_btn", use_container_width=True,
                     disabled=not (to_email.strip() and subject.strip() and body.strip())):
            if not is_authenticated:
                st.error("Please authenticate first")
            else:
                with st.status("Sending email...", expanded=True) as status:
                    success, msg = manager.gmail_send_email(
                        to_email.strip(),
                        subject.strip(),
                        body.strip()
                    )
                    if success:
                        status.update(label="✅ Email sent!", state="complete")
                        st.toast(f"✓ {msg}", icon="📧")
                        # Clear inputs
                        st.session_state["gmail_to_input"] = ""
                        st.session_state["gmail_subject_input"] = ""
                        st.session_state["gmail_body_input"] = ""
                    else:
                        status.update(label="❌ Send failed", state="error")
                        st.error(f"Error: {msg}")


def render_facebook_section(manager: IntegrationManager):
    """Render Facebook integration section (full width)"""
    is_configured, config_msg = manager.facebook_is_configured()
    
    st.markdown("---")
    st.markdown('<div class="section-header">Facebook Page</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(
            f'<div class="channel-card">'
            f'<div class="channel-card-header">'
            f'<span class="channel-icon">&#x1F4F1;</span>'
            f'<span class="channel-title">Facebook Page Poster</span>'
            f'<span class="channel-status {"channel-status-ready" if is_configured else "channel-status-idle"}">'
            f'{"READY" if is_configured else "NOT CONFIGURED"}'
            f'</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Configuration
        with st.expander("⚙️ Facebook Configuration", expanded=not is_configured):
            if is_configured:
                st.success(config_msg)
                
                # Validate token
                if st.button("🔍 Validate Token", key="facebook_validate_btn", use_container_width=True):
                    with st.spinner("Validating..."):
                        success, info = manager.facebook_validate()
                        if success:
                            st.success("✅ Token is valid")
                            page_info = manager.facebook_get_page_info()
                            if page_info:
                                st.info(f"**Page:** {page_info.get('name', 'Unknown')}")
                                st.caption(f"Followers: {page_info.get('followers_count', 'N/A')}")
                        else:
                            st.error(f"❌ Invalid token: {info.get('error', 'Unknown')}")
            else:
                st.error(config_msg)
                st.info("""
                **Setup Instructions:**
                1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
                2. Get Page Access Token for your Facebook Page
                3. Add to `.env` file:
                   - `META_ACCESS_TOKEN=your_token`
                   - `FB_PAGE_ID=your_page_id`
                   - `META_APP_ID=your_app_id`
                   - `META_APP_SECRET=your_app_secret`
                """)
        
        # Post to Facebook
        with st.expander("✍️ Post to Facebook Page"):
            message = st.text_area(
                "Post Message",
                placeholder="What's on your mind?",
                height=100,
                key="facebook_post_input"
            )
            link = st.text_input(
                "Link (optional)",
                placeholder="https://example.com",
                key="facebook_link_input"
            )
            
            if st.button("📤 Post to Facebook", key="facebook_post_btn", use_container_width=True,
                         disabled=not message.strip()):
                if not is_configured:
                    st.error("Please configure Facebook first")
                else:
                    with st.status("Posting to Facebook...", expanded=True) as status:
                        success, msg = manager.facebook_post(
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
    
    with col2:
        # Recent Posts
        with st.expander("📜 Recent Posts", expanded=True):
            if is_configured:
                with st.spinner("Fetching posts..."):
                    posts = manager.facebook_get_recent_posts(limit=5)
                    if posts:
                        for post in posts:
                            with st.container():
                                msg = post.get('message', '')[:100] + '...' if len(post.get('message', '')) > 100 else post.get('message', 'No message')
                                st.markdown(
                                    f'<div class="card">'
                                    f'<div class="card-body">{msg}</div>'
                                    f'<div class="card-meta">👍 {post.get("likes", 0)} | 💬 {post.get("comments", 0)}</div>'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.info("No posts found")
            else:
                st.info("Configure Facebook to see recent posts")


def render_communication_hub():
    """
    Render the complete Communication Hub
    
    This is the main entry point for the Communication Hub UI.
    """
    st.markdown('<div class="section-header">Communication Hub</div>', unsafe_allow_html=True)
    
    # Get integration manager
    manager = get_integration_manager()
    
    # Three column layout for LinkedIn, WhatsApp, Gmail
    col_li, col_wa, col_gmail = st.columns(3)
    
    with col_li:
        render_linkedin_column(manager)
    
    with col_wa:
        render_whatsapp_column(manager)
    
    with col_gmail:
        render_gmail_column(manager)
    
    # Full-width Facebook section
    render_facebook_section(manager)


if __name__ == '__main__':
    # Test the UI components
    st.set_page_config(page_title="Communication Hub Test", layout="wide")
    render_communication_hub()
