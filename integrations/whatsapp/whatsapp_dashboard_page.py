"""
WhatsApp Message Sender - Streamlit Dashboard
"""

import streamlit as st
import asyncio
from pathlib import Path

from whatsapp_sender import WhatsAppSender, get_session_status

st.set_page_config(page_title="WhatsApp Sender", page_icon="📱", layout="centered")

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
</style>
""", unsafe_allow_html=True)

st.title("📱 WhatsApp Message Sender")
st.markdown("---")

# Session status
status = get_session_status()
with st.sidebar:
    st.header("Session")
    if status['session_exists']:
        st.success("✅ Session Found")
        st.code(str(status['session_dir']))
    else:
        st.error("❌ No Session")

# Form
with st.form("wa_form"):
    phone = st.text_input("Phone Number", placeholder="+923162063441")
    message = st.text_area("Message", placeholder="Type your message...", height=100)
    submit = st.form_submit_button("📤 Send Message", use_container_width=True)

if submit:
    if not phone:
        st.error("⚠️ Enter phone number")
        st.stop()
    elif not message:
        st.error("⚠️ Enter message")
        st.stop()
    
    st.info("📱 Browser will open. If QR code appears, scan it with your phone.")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        sender = WhatsAppSender()
        
        with st.spinner("🔄 Connecting..."):
            connected, msg = loop.run_until_complete(sender.connect())
        
        if not connected:
            st.error(f"❌ Connection failed: {msg}")
            st.info("📱 Check the browser window - scan QR code if shown")
            loop.close()
            st.stop()
        
        with st.spinner(f"📤 Sending to {phone}..."):
            success, result = loop.run_until_complete(sender.send_message(phone, message))
        
        if success:
            st.markdown(f"""
            <div class="success-box">
                <h3 style="color: #39FF14; margin-top: 0;">✅ Sent!</h3>
                <p><strong>To:</strong> {phone}</p>
                <p>{result}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-box">
                <h3 style="color: #FF3939; margin-top: 0;">❌ Failed</h3>
                <p>{result}</p>
            </div>
            """, unsafe_allow_html=True)
        
        loop.run_until_complete(sender.close())
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    finally:
        loop.close()

st.markdown("---")
st.caption("Uses whatsapp_session folder for persistent login")
