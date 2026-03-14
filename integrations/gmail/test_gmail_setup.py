"""Quick Gmail Setup Test"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Gmail Setup Check")
print("=" * 60)

# Check credentials.json
cred_file = Path(__file__).parent / "credentials.json"
token_file = Path(__file__).parent / "token.json"

print(f"\ncredentials.json: {'✓ Found' if cred_file.exists() else '✗ NOT FOUND'}")
print(f"token.json: {'✓ Found' if token_file.exists() else '✗ NOT FOUND (will be created on first auth)'}")

if not cred_file.exists():
    print("\n⚠️  credentials.json not found!")
    print("\nSetup Instructions:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create OAuth 2.0 Client ID (Desktop app)")
    print("3. Download credentials.json")
    print("4. Place it in: " + str(Path(__file__).parent))
    print("5. Run: python setup_gmail_auth.py")
else:
    print("\n✓ credentials.json found!")
    print("\nRun this to authenticate:")
    print("  python setup_gmail_auth.py")
    
    # Try to authenticate
    print("\nAttempting authentication...")
    from integrations import gmail_authenticate
    success, msg = gmail_authenticate()
    if success:
        print(f"✓ Authentication successful: {msg}")
    else:
        print(f"✗ Authentication failed: {msg}")

print("\n" + "=" * 60)
