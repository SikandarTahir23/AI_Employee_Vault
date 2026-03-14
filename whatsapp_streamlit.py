"""
Streamlit Dashboard for WhatsApp Automation
"""

import streamlit as st
import logging
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from whatsapp_automation import WhatsAppAutomation, SESSION_DIR

# Configure logging for Streamlit
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="WhatsApp Automation Dashboard",
    page_icon="📱",
    layout="wide"
)

# Session state initialization
if 'whatsapp' not in st.session_state:
    st.session_state.whatsapp = None
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []


class StreamlitLogHandler(logging.Handler):
    """Custom logging handler to capture logs for Streamlit."""
    
    def emit(self, record):
        msg = self.format(record)
        st.session_state.log_messages.append(msg)
        # Keep only last 100 messages
        if len(st.session_state.log_messages) > 100:
            st.session_state.log_messages = st.session_state.log_messages[-100:]


# Add custom log handler
if not any(isinstance(h, StreamlitLogHandler) for h in logger.handlers):
    streamlit_handler = StreamlitLogHandler()
    streamlit_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(streamlit_handler)


def main():
    st.title("📱 WhatsApp Automation Dashboard")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Session Info")
        
        # Show session directory
        st.info(f"Session stored in:\n`{SESSION_DIR}`")
        
        # Delete session button
        if st.button("🗑️ Delete Saved Session", type="secondary"):
            import shutil
            if SESSION_DIR.exists():
                shutil.rmtree(SESSION_DIR)
                st.success("Session deleted! You'll need to scan QR code again.")
                st.session_state.connected = False
                st.session_state.whatsapp = None
                st.rerun()
            else:
                st.warning("No session found.")
        
        st.markdown("---")
        st.markdown("**Status:**")
        if st.session_state.connected:
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Connection section
        st.subheader("🔗 Connection")
        
        if not st.session_state.connected:
            if st.button("📲 Connect to WhatsApp", type="primary"):
                with st.spinner("Starting browser... Please wait."):
                    try:
                        whatsapp = WhatsAppAutomation(headless=False)
                        connected = whatsapp.connect_whatsapp()
                        
                        if connected:
                            st.session_state.whatsapp = whatsapp
                            st.session_state.connected = True
                            st.success("✅ Connected to WhatsApp Web!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to connect. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.success("Already connected to WhatsApp Web!")
            
            # Send message section
            st.subheader("✉️ Send Message")
            
            contact_name = st.text_input(
                "Contact Name or Phone Number",
                placeholder="e.g., John Doe or +1234567890"
            )
            message = st.text_area(
                "Message",
                placeholder="Type your message here...",
                height=100
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                send_disabled = not contact_name or not message
                if st.button("📤 Send Message", disabled=send_disabled, type="primary"):
                    with st.spinner("Sending message..."):
                        success = st.session_state.whatsapp.send_whatsapp_message(
                            contact_name, 
                            message
                        )
                        if success:
                            st.success("✅ Message sent successfully!")
                        else:
                            st.error("❌ Failed to send message. Check logs below.")
            
            with col_btn2:
                if st.button("🔍 Open Chat Only"):
                    with st.spinner("Opening chat..."):
                        success = st.session_state.whatsapp.send_whatsapp_message(
                            contact_name,
                            ""  # Empty message to just open chat
                        )
                        if success:
                            st.success(f"Chat with '{contact_name}' opened!")
                        else:
                            st.error("Could not find contact.")
            
            # Keep browser open option
            st.markdown("---")
            st.subheader("⏱️ Browser Control")
            
            duration = st.slider(
                "Keep browser open (seconds)",
                min_value=30,
                max_value=600,
                value=60,
                step=30
            )
            
            if st.button("⏰ Keep Browser Open"):
                with st.spinner(f"Browser will stay open for {duration} seconds..."):
                    st.session_state.whatsapp.keep_alive(duration=duration)
                    st.info("You can now interact with WhatsApp Web manually!")
    
    with col2:
        # Live logs
        st.subheader("📋 Live Logs")
        
        log_container = st.container()
        with log_container:
            if st.session_state.log_messages:
                # Display last 20 log messages
                for log_msg in st.session_state.log_messages[-20:]:
                    if "ERROR" in log_msg:
                        st.error(log_msg)
                    elif "SUCCESS" in log_msg or "successful" in log_msg.lower():
                        st.success(log_msg)
                    elif "INFO" in log_msg:
                        st.info(log_msg)
                    else:
                        st.text(log_msg)
            else:
                st.text("No logs yet...")
        
        # Auto-refresh logs
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Note:** First time login requires QR code scan. "
        "Subsequent runs will use the saved session."
    )


if __name__ == "__main__":
    main()
