"""
WhatsApp Integration Page for Streamlit Dashboard
"""

import streamlit as st
import asyncio
from whatsapp_integration import (
    WhatsAppAutomation,
    get_whatsapp_instance,
    reset_whatsapp_instance
)


def run_async(coro):
    """Run async function in Streamlit"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def whatsapp_page():
    """Render the WhatsApp integration page"""
    st.title("💬 WhatsApp Automation")
    
    # Initialize session state
    if 'whatsapp' not in st.session_state:
        st.session_state.whatsapp = None
    if 'whatsapp_logged_in' not in st.session_state:
        st.session_state.whatsapp_logged_in = False
    
    # Sidebar - Connection Control
    with st.sidebar:
        st.header("Connection")
        
        if st.session_state.whatsapp is None:
            if st.button("🔗 Connect WhatsApp", use_container_width=True):
                with st.spinner("Starting WhatsApp Web..."):
                    whatsapp = WhatsAppAutomation(headless=False)
                    st.session_state.whatsapp = whatsapp
                    st.rerun()
        else:
            if not st.session_state.whatsapp_logged_in:
                st.info("Not logged in yet")
                
                if st.button("📱 Check Login Status", use_container_width=True):
                    async def check():
                        is_logged = await st.session_state.whatsapp._check_login_status()
                        st.session_state.whatsapp_logged_in = is_logged
                        if is_logged:
                            st.success("✓ Logged in!")
                        else:
                            st.warning("Please scan QR code in browser window")
                    
                    run_async(check())
                
                st.warning("⚠️ A browser window should be open. Please scan the QR code with your WhatsApp mobile app.")
            else:
                st.success("✅ Connected & Logged In")
                
                if st.button("📋 Get Recent Chats", use_container_width=True):
                    async def get_chats():
                        chats = await st.session_state.whatsapp.get_chat_list(max_chats=10)
                        if chats:
                            st.session_state.recent_chats = chats
                        else:
                            st.warning("No chats found")
                    
                    run_async(get_chats())
                
                if 'recent_chats' in st.session_state:
                    st.subheader("Recent Chats")
                    for chat in st.session_state.recent_chats:
                        st.text(f"• {chat['name']}")
                
                st.divider()
                if st.button("🔌 Disconnect", use_container_width=True):
                    async def disconnect():
                        await st.session_state.whatsapp.cleanup()
                        st.session_state.whatsapp = None
                        st.session_state.whatsapp_logged_in = False
                        if 'recent_chats' in st.session_state:
                            del st.session_state.recent_chats
                        st.rerun()
                    
                    run_async(disconnect())
    
    # Main content
    if st.session_state.whatsapp is None:
        st.info("👈 Click 'Connect WhatsApp' in the sidebar to start")
        st.markdown("""
        ### Setup Instructions:
        1. Click "Connect WhatsApp" in the sidebar
        2. A browser window will open with WhatsApp Web
        3. Scan the QR code with your WhatsApp mobile app:
           - Open WhatsApp on phone
           - Tap Menu (⋮) or Settings
           - Select "Linked Devices"
           - Tap "Link a Device"
           - Scan the QR code
        4. Once logged in, you can send messages below
        """)
        return
    
    # Check login status on page load
    if not st.session_state.whatsapp_logged_in:
        async def auto_check():
            is_logged = await st.session_state.whatsapp._check_login_status()
            st.session_state.whatsapp_logged_in = is_logged
            return is_logged
        
        is_logged = run_async(auto_check())
        
        if not is_logged:
            st.warning("⚠️ Please scan the QR code in the browser window that opened")
            st.markdown("""
            **To scan QR code:**
            1. Open WhatsApp on your phone
            2. Go to Settings/Menu → Linked Devices
            3. Tap "Link a Device"
            4. Point camera at the QR code in the browser window
            """)
            
            if st.button("🔄 I've scanned the QR code"):
                st.rerun()
            return
    
    # Send Message Section
    st.subheader("📤 Send Message")
    
    with st.form("whatsapp_form"):
        phone = st.text_input(
            "Phone Number", 
            placeholder="+1234567890",
            help="Include country code (e.g., +1 for US, +91 for India)"
        )
        message = st.text_area(
            "Message", 
            placeholder="Type your message here...",
            height=150
        )
        
        submitted = st.form_submit_button("🚀 Send Message", use_container_width=True, 
                                          disabled=not st.session_state.whatsapp_logged_in)
        
        if submitted:
            if not phone:
                st.error("Please enter a phone number")
            elif not message:
                st.error("Please enter a message")
            else:
                with st.spinner("Sending message..."):
                    async def send():
                        return await st.session_state.whatsapp.send_message(phone, message)
                    
                    success, result_msg = run_async(send())
                    
                    if success:
                        st.success(f"✅ {result_msg}")
                    else:
                        st.error(f"❌ {result_msg}")
    
    # Info section
    st.divider()
    st.markdown("""
    ### 💡 Tips:
    - **Phone format:** Include country code without spaces (e.g., +1234567890)
    - **First time:** You must scan QR code on first connection
    - **Session saved:** Login persists across restarts
    - **Browser window:** Don't close the browser window during automation
    """)


if __name__ == '__main__':
    whatsapp_page()