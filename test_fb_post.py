
from meta_automation import MetaAutomation
import os
from dotenv import load_dotenv

def test_fb_post():
    print("="*60)
    print("  FB POSTING TEST - SIKANDAR TAHIR")
    print("="*60)
    
    load_dotenv()
    
    try:
        meta = MetaAutomation()
        
        # Check if credentials are loaded
        if not meta.access_token or not meta.fb_page_id:
            print("ERROR: META_ACCESS_TOKEN or FB_PAGE_ID not found in .env")
            return

        print(f"Credentials loaded for Page ID: {meta.fb_page_id}")
        
        test_message = f"Test Post from AI Agency Dashboard - {os.urandom(4).hex()}"
        print(f"Attempting to post: {test_message}")
        
        result = meta.post_to_facebook(message=test_message)
        
        if result.get("success"):
            print("\nSUCCESS!")
            print(f"Post ID: {result.get('post_id')}")
            print(f"Post URL: {result.get('post_url')}")
            print("Logged to Obsidian: Yes")
        else:
            print(f"\nFAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_fb_post()
