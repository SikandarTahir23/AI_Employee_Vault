"""
Test WhatsApp message from dashboard using saved session.
"""

import asyncio
import logging
from integrations.whatsapp_client import WhatsAppClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test contact and message
CONTACT = "+923162063441"
MESSAGE = "Test message from AI dashboard"

async def main():
    logger.info("=" * 60)
    logger.info("WHATSAPP DASHBOARD TEST")
    logger.info("=" * 60)
    
    # Check status first
    from whatsapp_client import get_whatsapp_status
    logger.info("Checking WhatsApp status...")
    status = get_whatsapp_status()
    logger.info(f"Session exists: {status.get('session_exists', False)}")
    logger.info(f"Likely logged in: {status.get('likely_logged_in', False)}")
    
    # Initialize client
    client = WhatsAppClient(headless=False)
    
    logger.info("Initializing WhatsApp client...")
    initialized = await client.initialize()
    
    if not initialized:
        logger.error("Failed to initialize WhatsApp client")
        return
    
    # Check if logged in
    if not client._is_logged_in:
        logger.info("Not logged in, waiting for QR scan...")
        login_success = await client.wait_for_login(timeout=60)
        if not login_success:
            logger.error("Login timeout")
            await client.cleanup()
            return
        logger.info("Login successful!")
    
    # Send test message
    logger.info(f"Sending message to: {CONTACT}")
    logger.info(f"Message: {MESSAGE}")
    logger.info("-" * 60)
    
    success, result = await client.send_message(CONTACT, MESSAGE)
    
    logger.info("-" * 60)
    if success:
        logger.info("=" * 60)
        logger.info("✓ MESSAGE SENT SUCCESSFULLY!")
        logger.info(f"  Contact: {CONTACT}")
        logger.info(f"  Message: {MESSAGE}")
        logger.info("=" * 60)
    else:
        logger.error(f"✗ Failed to send message: {result}")
        logger.info("Note: If QR code appeared, please scan it and try again.")
    
    await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
