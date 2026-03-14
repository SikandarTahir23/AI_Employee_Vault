"""
Quick send test
"""

import asyncio
from whatsapp_sender import WhatsAppSender

async def test():
    sender = WhatsAppSender()
    
    print("Connecting...")
    ok, msg = await sender.connect()
    
    if not ok:
        print(f"Connect failed: {msg}")
        return
    
    print("Sending test message...")
    success, result = await sender.send_message("+923162063441", "Test from dashboard")
    
    if success:
        print(f"✓ SUCCESS: {result}")
    else:
        print(f"✗ FAILED: {result}")
    
    await sender.close()

if __name__ == "__main__":
    asyncio.run(test())
