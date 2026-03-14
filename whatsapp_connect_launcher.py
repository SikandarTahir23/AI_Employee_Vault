"""
WhatsApp Connection Launcher - Runs independently from Streamlit
This script is called by the Streamlit app to handle WhatsApp connection
"""
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from whatsapp_client import connect_whatsapp, cleanup_whatsapp

if __name__ == "__main__":
    print("Starting WhatsApp connection...")
    success, msg = connect_whatsapp(headless=False, timeout=60)
    
    # Write result to a temp file for Streamlit to read
    result_file = project_root / ".whatsapp_connect_result.txt"
    with open(result_file, "w", encoding="utf-8") as f:
        f.write(f"{success}|{msg}")
    
    print(f"Result: {success} - {msg}")
    cleanup_whatsapp()
