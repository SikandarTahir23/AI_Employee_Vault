"""
LinkedIn Connection - Opens browser and waits for login
This script is called by Streamlit to handle LinkedIn connection separately
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from integrations.linkedin_client import LinkedInClient

if __name__ == "__main__":
    print("=" * 60)
    print("LinkedIn Connection")
    print("=" * 60)
    
    client = LinkedInClient(headless=False)
    
    try:
        # Initialize browser
        print("\n1. Opening browser...")
        if not client.initialize():
            print("   ✗ Failed to initialize")
            sys.exit(1)
        
        # Check if already logged in
        if client._is_logged_in:
            print("   ✓ Already logged in!")
            result = "True|Already logged in"
        else:
            print("   ⚠ Login required")
            print("\n2. Waiting for login (up to 2 minutes)...")
            print("   Please log in to LinkedIn in the browser window")
            print("   Close the browser window when done")
            
            if client.wait_for_login(timeout=120):
                result = "True|Login successful"
            else:
                result = "False|Login timeout or cancelled"
        
        # Write result to file for Streamlit to read
        result_file = project_root / ".linkedin_connect_result.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(result)
        
        print(f"\n3. Result: {result}")
        
        # Keep browser open for a few more seconds so user can see confirmation
        import time
        time.sleep(2)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        result_file = project_root / ".linkedin_connect_result.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(f"False|{e}")
    
    finally:
        client.cleanup()
        print("\nDone!")
        input("Press Enter to exit...")
