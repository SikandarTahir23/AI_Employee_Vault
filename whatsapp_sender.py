"""
WhatsApp Sender — Browser Automation
Reads approved .md files from Approved/ and sends WhatsApp messages via WhatsApp Web.
"""

import os
import re
import sys
import io
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Force UTF-8 stdout/stderr on Windows to handle emojis in message content
if sys.stdout and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
except ImportError:
    print("[ERROR] playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
APPROVED_DIR = BASE_DIR / "Approved"
DONE_DIR = BASE_DIR / "Done"
PROFILE_DIR = BASE_DIR / ".whatsapp_session"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

APPROVED_DIR.mkdir(exist_ok=True)
DONE_DIR.mkdir(exist_ok=True)
PROFILE_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def close_chrome():
    """Close all Chrome instances."""
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)


def clean_locks():
    """Remove stale lock files from profile."""
    for lock in PROFILE_DIR.rglob("*"):
        if lock.is_file() and any(x in lock.name.lower() for x in ["lock", "singleton"]):
            try:
                lock.unlink()
            except:
                pass


def parse_message_file(filepath):
    """Extract To and Message from an approved .md file."""
    text = filepath.read_text(encoding="utf-8")
    to_match = re.search(r"\*\*To:\*\*\s*(.+)", text)
    msg_match = re.search(r"## Message\s*\n+([\s\S]+?)(?:\n---|\Z)", text)
    if not to_match:
        return None, None
    contact = to_match.group(1).strip()
    message = msg_match.group(1).strip() if msg_match else ""
    return contact, message


# ──────────────────────────────────────────────
# LOGIN FLOW
# ──────────────────────────────────────────────
def login_flow():
    """Open browser for QR code scan."""
    print("[INFO] Opening browser for WhatsApp Web login...")
    print("[INFO] Scan the QR code with your phone")
    print("[INFO] Wait until you see your chat list")
    print("[INFO] Then close the browser window\n")
    
    close_chrome()
    clean_locks()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_EXE,
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        
        page = browser.new_page()
        page.goto("https://web.whatsapp.com/", timeout=60000)
        
        print("[WAIT] Waiting for you to scan QR code and load chats...")
        print("[ACTION] Scan QR code now, wait for chat list, then close browser\n")
        
        # Wait for user to close browser or 5 minutes
        try:
            page.wait_for_event("close", timeout=300000)
        except:
            pass
        
        try:
            browser.close()
        except:
            pass

    print("[OK] Session saved. You can now run without --login.")


# ──────────────────────────────────────────────
# SEND MESSAGE
# ──────────────────────────────────────────────
def send_message(page, contact, message):
    """Send a single WhatsApp message."""
    print(f"\n[INFO] Sending to: {contact}")
    
    try:
        # Click search box
        search = page.locator('[data-testid="chat-list-search"]').first
        search.click(timeout=10000)
        
        # Clear previous search
        page.keyboard.press("Control+a")
        page.keyboard.press("Delete")
        
        # Type contact name
        page.keyboard.type(contact, delay=50)
        page.wait_for_timeout(2000)
        
        # Select first result
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)
        
        # Wait for message input
        msg_box = page.locator('[data-testid="compose-box-input"]').first
        msg_box.click(timeout=10000)
        
        # Type message
        lines = message.split("\n")
        for i, line in enumerate(lines):
            if i > 0:
                page.keyboard.press("Shift+Enter")
            page.keyboard.type(line, delay=20)
        
        page.wait_for_timeout(500)
        
        # Send
        send_btn = page.locator('[data-testid="compose-btn-send"]').first
        send_btn.click(timeout=10000)
        
        page.wait_for_timeout(3000)
        print(f"[OK] Message sent to {contact}!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send: {e}")
        return False


# ──────────────────────────────────────────────
# MAIN PROCESSING
# ──────────────────────────────────────────────
def process_approved():
    """Find all approved .md WA files and send."""
    files = sorted(APPROVED_DIR.glob("WA_*.md"))
    if not files:
        print("[INFO] No approved WA messages found.")
        return

    print(f"[INFO] Found {len(files)} approved message(s)\n")

    # Parse all files first
    tasks = []
    for f in files:
        contact, message = parse_message_file(f)
        if not contact:
            print(f"  [SKIP] {f.name} — no **To:** field found")
            continue
        if not message:
            print(f"  [SKIP] {f.name} — no ## Message content found")
            continue
        tasks.append((f, contact, message))

    if not tasks:
        print("[INFO] Nothing to send.")
        return

    close_chrome()
    clean_locks()

    sent = 0
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_EXE,
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        
        page = browser.new_page()
        
        print("[INFO] Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com/", timeout=60000)
        
        # Check if logged in (no QR code)
        print("[INFO] Checking login status...")
        try:
            qr = page.locator('canvas').first
            qr.wait_for(timeout=8000)
            print("\n[ERROR] QR code detected - not logged in!")
            print("[ACTION] Run with --login first to scan QR code\n")
            try:
                browser.close()
            except:
                pass
            return
        except:
            print("[OK] Already logged in!")
        
        # Wait for chat list
        print("[INFO] Waiting for chat list to load...")
        try:
            page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
            page.wait_for_timeout(3000)
            print("[OK] Chat list loaded!")
        except Exception as e:
            print(f"[WARN] Chat list wait: {e}")
            page.screenshot(path="debug_wa_chatlist.png")
        
        # Send each message
        for f, contact, message in tasks:
            print(f"\n--- Processing: {f.name} ---")
            
            if send_message(page, contact, message):
                # Move to Done
                dest = DONE_DIR / f.name
                shutil.move(str(f), str(dest))
                print(f"[INFO] Moved {f.name} to Done/")
                sent += 1
            
            page.wait_for_timeout(2000)
        
        try:
            browser.close()
        except:
            pass

    print(f"\n[DONE] Sent {sent}/{len(tasks)} message(s).")


# ──────────────────────────────────────────────
# WATCH MODE
# ──────────────────────────────────────────────
def watch_loop():
    """Poll Approved/ every 60s and process new files."""
    import time
    print("[INFO] Watch mode — polling Approved/ every 60s. Press Ctrl+C to stop.")
    while True:
        process_approved()
        time.sleep(60)


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  WhatsApp Sender — Browser Automation")
    print("=" * 50)
    print()

    if "--login" in sys.argv:
        login_flow()
    elif "--watch" in sys.argv:
        watch_loop()
    else:
        process_approved()


if __name__ == "__main__":
    main()
