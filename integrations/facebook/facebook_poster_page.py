"""
Facebook Poster - Streamlit Dashboard Page
Post to Facebook Page using browser automation (no Graph API required)
"""

import streamlit as st
import asyncio
from pathlib import Path

from facebook_browser import (
    FacebookBrowser, 
    get_facebook_session_status, 
    reset_facebook_session
)

# Page config
st.set_page_config(
    page_title="Facebook Poster",
    page_icon="📘",
    layout="centered"
)

# CSS
st.markdown("""
<style>
    .success-box {
        background: linear-gradient(135deg, #000000 0%, #051405 100%);
        border: 2px solid #39FF14;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
    }
    .error-box {
        background: linear-gradient(135deg, #000000 0%, #140505 100%);
        border: 2px solid #FF3939;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
    }
    .info-box {
        background: linear-gradient(135deg, #000000 0%, #0a1f2f 100%);
        border: 2px solid #58A6FF;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📘 Facebook Page Poster")
st.markdown("---")

# Session status
status = get_facebook_session_status()

with st.sidebar:
    st.header("Session Info")
    if status['session_exists']:
        st.success("✅ Session Found")
        st.code(str(status['session_dir']))
    else:
        st.info("ℹ️ No Session - Will create on first login")
    
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("""
    1. Enter your Facebook Page URL
    2. Type your post message
    3. Click 'Post to Facebook'
    4. Browser will open and post automatically
    """)
    
    st.markdown("---")
    if st.button("🗑️ Reset Session", type="secondary"):
        reset_facebook_session()
        st.success("Session reset! You'll need to login again.")
        st.rerun()

# Main form
with st.form("fb_form"):
    page_url = st.text_input(
        "Facebook Page URL",
        placeholder="https://www.facebook.com/your-page-name",
        help="Full URL of your Facebook Page"
    )
    
    message = st.text_area(
        "Post Message",
        placeholder="What's on your mind?",
        height=150,
        help="Your post content"
    )
    
    submit = st.form_submit_button("📤 Post to Facebook", use_container_width=True)

if submit:
    if not page_url:
        st.error("⚠️ Please enter a Facebook Page URL")
        st.stop()
    elif not message:
        st.error("⚠️ Please enter a message")
        st.stop()
    
    # Validate URL
    if "facebook.com" not in page_url.lower():
        st.error("⚠️ Please enter a valid Facebook URL")
        st.stop()
    
    st.info("📘 Browser will open. If not logged in, please login to Facebook.")
    
    # Progress area
    progress_area = st.empty()
    status_area = st.empty()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        fb = FacebookBrowser()
        
        # Connect
        with progress_area:
            st.info("🔄 Connecting to Facebook...")
        
        connected, msg = loop.run_until_complete(fb.connect(wait_for_login=True))
        
        if not connected:
            st.error(f"❌ Connection failed: {msg}")
            st.info("📘 Check the browser window - you may need to log in to Facebook")
            loop.close()
            st.stop()
        
        with status_area:
            st.success("✅ Connected to Facebook!")
        
        # Post
        with progress_area:
            st.info(f"📤 Posting to your page...")
        
        success, result = loop.run_until_complete(fb.post_to_page(page_url, message))
        
        if success:
            st.markdown(f"""
            <div class="success-box">
                <h3 style="color: #39FF14; margin-top: 0;">✅ Post Published!</h3>
                <p><strong>Page:</strong> {page_url}</p>
                <p><strong>Message:</strong> {message[:100]}{'...' if len(message) > 100 else ''}</p>
                <p style="color: #39FF14;">{result}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-box">
                <h3 style="color: #FF3939; margin-top: 0;">❌ Post Failed</h3>
                <p>{result}</p>
                <p>Check the debug screenshots for details.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Close browser
        loop.run_until_complete(fb.close())
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    finally:
        loop.close()
        progress_area.empty()
        status_area.empty()

# Footer
st.markdown("---")
st.caption("Uses browser automation - no Graph API permissions required")
