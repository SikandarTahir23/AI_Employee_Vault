"""
Quick test of WhatsApp sender with existing session.
"""

import asyncio
from whatsapp_sender import WhatsAppSender

async def test():
    sender = WhatsAppSender()
    
    print("Connecting to existing session...")
    connected = await sender.connect()
    
    if not connected:
        print("Failed to connect!")
        return
    
    print("\nSending test message...")
    success, result = await sender.send_message("+923162063441", "Test message from dashboard integration")
    
    if success:
        print(f"\n✓ SUCCESS: {result}")
    else:
        print(f"\n✗ FAILED: {result}")
    
    await sender.close()

if __name__ == "__main__":
    asyncio.run(test())
