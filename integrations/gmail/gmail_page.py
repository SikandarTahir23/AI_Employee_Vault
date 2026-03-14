"""
Gmail Integration Page for Streamlit Dashboard
"""

import streamlit as st
from gmail_integration import (
    init_gmail_service,
    send_email,
    read_inbox,
    get_user_profile
)


def gmail_page():
    """Render the Gmail integration page"""
    st.title("📧 Gmail Integration")
    
    # Initialize session state
    if 'gmail_service' not in st.session_state:
        st.session_state.gmail_service = None
    
    # Sidebar - Authentication
    with st.sidebar:
        st.header("Authentication")
        
        if st.session_state.gmail_service is None:
            if st.button("🔐 Connect Gmail", use_container_width=True):
                with st.spinner("Authenticating with Gmail..."):
                    service = init_gmail_service()
                    if service:
                        st.session_state.gmail_service = service
                        st.success("Connected successfully!")
                        st.rerun()
                    else:
                        st.error("Authentication failed. Check credentials.json")
        else:
            profile = get_user_profile(st.session_state.gmail_service)
            if profile:
                st.success(f"✅ Connected: {profile['emailAddress']}")
                if st.button("🔓 Disconnect", use_container_width=True):
                    st.session_state.gmail_service = None
                    st.rerun()
    
    # Main content
    if st.session_state.gmail_service is None:
        st.info("👈 Connect your Gmail account from the sidebar to get started")
        st.markdown("""
        ### Setup Instructions:
        1. Place your `credentials.json` in the project directory
        2. Click "Connect Gmail" in the sidebar
        3. Authorize the application in your browser
        4. You'll be redirected back automatically
        """)
        return
    
    # Tabs for different functions
    tab1, tab2 = st.tabs(["📤 Send Email", "📥 Read Inbox"])
    
    # Send Email Tab
    with tab1:
        st.subheader("Compose Email")
        
        with st.form("email_form"):
            to_email = st.text_input("To", placeholder="recipient@example.com")
            subject = st.text_input("Subject", placeholder="Email subject")
            body = st.text_area("Message", placeholder="Write your message here...", height=200)
            
            submitted = st.form_submit_button("Send Email", use_container_width=True)
            
            if submitted:
                if not to_email or not subject or not body:
                    st.error("Please fill in all fields")
                else:
                    with st.spinner("Sending email..."):
                        success = send_email(
                            st.session_state.gmail_service,
                            to_email,
                            subject,
                            body
                        )
                        if success:
                            st.success("✅ Email sent successfully!")
                        else:
                            st.error("❌ Failed to send email. Check logs for details.")
    
    # Read Inbox Tab
    with tab2:
        st.subheader("Inbox")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Search", value="is:inbox", 
                                         placeholder="Gmail search query (e.g., 'from:example.com')")
        with col2:
            max_emails = st.number_input("Max Results", min_value=1, max_value=50, value=10)
        
        if st.button("🔄 Refresh Inbox", use_container_width=True):
            with st.spinner("Loading emails..."):
                emails = read_inbox(
                    st.session_state.gmail_service,
                    max_results=max_emails,
                    query=search_query
                )
                st.session_state.last_emails = emails
        
        if 'last_emails' in st.session_state and st.session_state.last_emails:
            st.divider()
            for email in st.session_state.last_emails:
                with st.expander(f"📩 {email['subject'] or '(No Subject)'}"):
                    st.write(f"**From:** {email['from']}")
                    st.write(f"**Date:** {email['date']}")
                    st.write(f"**Snippet:** {email['snippet']}")
        elif 'last_emails' in st.session_state:
            st.info("No emails found matching your criteria")
        else:
            st.info("Click 'Refresh Inbox' to load emails")


if __name__ == '__main__':
    gmail_page()