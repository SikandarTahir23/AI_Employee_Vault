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
PROFILE_DIR = BASE_DIR / ".playwright_profile"

APPROVED_DIR.mkdir(exist_ok=True)
DONE_DIR.mkdir(exist_ok=True)
PROFILE_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def close_chrome():
    """Kill any running Chrome/Chromium instances to avoid profile lock conflicts."""
    import time as _t
    killed = False
    try:
        if sys.platform == "win32":
            for proc_name in ["chrome.exe", "chromium.exe"]:
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", proc_name],
                    capture_output=True, text=True,
                )
                if result.returncode == 0:
                    killed = True
            if killed:
                print("[INFO] Closed Chrome/Chromium to free profile lock...")
                _t.sleep(3)  # wait for profile lock to release
        else:
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
    except Exception:
        pass


def get_browser_context(playwright):
    """Launch persistent Chromium context with saved profile."""
    # Remove stale lock files that prevent browser from opening
    lock_file = PROFILE_DIR / "lockfile"
    default_lock = PROFILE_DIR / "Default" / "LOCK"
    for lf in [lock_file, default_lock]:
        if lf.exists():
            try:
                lf.unlink()
                print(f"[INFO] Removed stale lock: {lf.name}")
            except Exception:
                pass

    # Use bundled Chromium (most stable) — system Chrome causes profile conflicts
    return playwright.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-sync",
            "--no-zygote",
        ],
        viewport={"width": 1280, "height": 900},
        ignore_default_args=["--enable-automation"],
    )


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
    """Open browser for QR code scan, then save session."""
    print("[INFO] Opening browser for WhatsApp Web login...")
    print("[INFO] Scan the QR code, then close the browser window.")
    close_chrome()

    with sync_playwright() as p:
        context = get_browser_context(p)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://web.whatsapp.com/", timeout=60000, wait_until="domcontentloaded")

        try:
            page.wait_for_event("close", timeout=300000)
        except Exception:
            pass

        try:
            context.close()
        except Exception:
            pass

    print("[OK] Session saved. You can now run without --login.")


# ──────────────────────────────────────────────
# SEND MESSAGE
# ──────────────────────────────────────────────
def send_whatsapp(contact, message):
    """Launch browser and send a single WhatsApp message. Used for direct calls."""
    print(f"[INFO] Sending to '{contact}' via WhatsApp Web...")

    with sync_playwright() as p:
        try:
            context = get_browser_context(p)
        except Exception as e:
            print(f"[ERROR] Could not launch browser: {e}")
            return False

        page = context.pages[0] if context.pages else context.new_page()

        try:
            for attempt in range(3):
                try:
                    print(f"[INFO] Navigating to WhatsApp Web (attempt {attempt+1}/3)...")
                    page.goto("https://web.whatsapp.com/", timeout=300000, wait_until="domcontentloaded")
                    break
                except Exception as nav_err:
                    if attempt < 2:
                        print(f"[WARN] Navigation failed, relaunching browser in 5s...")
                        import time as _t
                        try:
                            context.close()
                        except Exception:
                            pass
                        _t.sleep(5)
                        try:
                            context = get_browser_context(p)
                            page = context.pages[0] if context.pages else context.new_page()
                        except Exception:
                            raise nav_err
                    else:
                        raise nav_err

            print("[INFO] Waiting for WhatsApp to load (up to 5 min for first-time session restore)...")
            page.wait_for_selector(
                'div[contenteditable="true"][data-tab="3"], '
                'div[title="Search input textbox"], '
                'div[aria-label="Search input textbox"], '
                '[data-testid="chat-list-search"]',
                timeout=300000,
            )
            page.wait_for_timeout(2000)

            search_box = page.locator(
                'div[contenteditable="true"][data-tab="3"], '
                'div[title="Search input textbox"], '
                'div[aria-label="Search input textbox"]'
            )
            search_box.first.click(timeout=15000)
            page.keyboard.press("Control+a")
            page.keyboard.press("Delete")
            page.keyboard.type(contact, delay=50)
            page.wait_for_timeout(2500)

            contact_result = page.locator(
                f'span[title="{contact}"], span.matched-text'
            )
            contact_result.first.click(timeout=15000)
            page.wait_for_timeout(1000)

            msg_box = page.locator(
                'div[contenteditable="true"][data-tab="10"], '
                'div[title="Type a message"], '
                'footer div[contenteditable="true"]'
            )
            msg_box.first.click(timeout=10000)

            lines = message.split("\n")
            for i, line in enumerate(lines):
                if i > 0:
                    page.keyboard.press("Shift+Enter")
                page.keyboard.type(line, delay=10)

            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            print("[INFO] Waiting 8s for message to deliver...")
            page.wait_for_timeout(8000)
            print(f"[OK] Message sent to {contact}!")
            success = True

        except PwTimeout as e:
            print(f"[ERROR] Timeout: {e}")
            print("[HINT] WhatsApp Web may have updated its UI. Check selectors.")
            success = False
        except Exception as e:
            print(f"[ERROR] {e}")
            success = False
        finally:
            try:
                context.close()
            except Exception:
                pass

        return success


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
# MAIN PROCESSING
# ──────────────────────────────────────────────
def process_approved():
    """Find all approved .md WA files and send — one browser session for all messages."""
    files = sorted(APPROVED_DIR.glob("WA_*.md"))
    if not files:
        print("[INFO] No approved WA messages found.")
        return

    print(f"[INFO] Found {len(files)} approved message(s)\n")

    # Parse all files first, skip invalid
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

    # Kill any stale Chrome to avoid profile lock
    close_chrome()

    # Open browser ONCE for all messages
    sent = 0
    with sync_playwright() as p:
        try:
            context = get_browser_context(p)
        except Exception as e:
            print(f"[ERROR] Could not launch browser: {e}")
            return

        page = context.pages[0] if context.pages else context.new_page()

        # Navigate to WhatsApp Web — ERR_ABORTED on first try is normal (redirect)
        # On failure: close entire context, wait, relaunch fresh
        loaded = False
        for attempt in range(3):
            try:
                print(f"[INFO] Navigating to WhatsApp Web (attempt {attempt+1}/3)...")
                page.goto("https://web.whatsapp.com/", timeout=300000, wait_until="domcontentloaded")
                break
            except Exception as nav_err:
                if attempt < 2:
                    print(f"[WARN] Navigation failed, relaunching browser in 5s...")
                    import time as _t
                    try:
                        context.close()
                    except Exception:
                        pass
                    _t.sleep(5)
                    # Relaunch fresh context + page
                    try:
                        context = get_browser_context(p)
                        page = context.pages[0] if context.pages else context.new_page()
                    except Exception as relaunch_err:
                        print(f"[ERROR] Relaunch failed: {relaunch_err}")
                        return
                else:
                    print(f"[ERROR] Could not reach WhatsApp Web: {nav_err}")
                    try:
                        context.close()
                    except Exception:
                        pass
                    return

        print("[INFO] Waiting for WhatsApp to load (up to 5 min for first-time session restore)...")
        try:
            page.wait_for_selector(
                'div[contenteditable="true"][data-tab="3"], '
                'div[title="Search input textbox"], '
                'div[aria-label="Search input textbox"], '
                '[data-testid="chat-list-search"]',
                timeout=300000,
            )
            page.wait_for_timeout(2000)
            loaded = True
            print("[OK] WhatsApp Web loaded.")
        except Exception as e:
            print(f"[ERROR] WhatsApp did not load in time: {e}")
            context.close()
            return

        # Send each message in the same session
        for f, contact, message in tasks:
            print(f"\n--- Sending to: {contact} ({f.name}) ---")
            try:
                # Search for contact
                search_box = page.locator(
                    'div[contenteditable="true"][data-tab="3"], '
                    'div[title="Search input textbox"], '
                    'div[aria-label="Search input textbox"]'
                )
                search_box.first.click(timeout=15000)
                # Clear previous search
                page.keyboard.press("Control+a")
                page.keyboard.press("Delete")
                page.keyboard.type(contact, delay=50)
                page.wait_for_timeout(2500)

                # Click contact result
                contact_result = page.locator(
                    f'span[title="{contact}"], '
                    f'span[title^="{contact[:8]}"], '
                    'span.matched-text'
                )
                contact_result.first.click(timeout=15000)
                page.wait_for_timeout(1000)

                # Type message
                msg_box = page.locator(
                    'div[contenteditable="true"][data-tab="10"], '
                    'div[title="Type a message"], '
                    'footer div[contenteditable="true"]'
                )
                msg_box.first.click(timeout=10000)

                lines = message.split("\n")
                for i, line in enumerate(lines):
                    if i > 0:
                        page.keyboard.press("Shift+Enter")
                    page.keyboard.type(line, delay=10)

                page.wait_for_timeout(500)
                page.keyboard.press("Enter")
                print(f"[INFO] Message sent — waiting 8s for delivery...")
                page.wait_for_timeout(8000)

                # Archive
                dest = DONE_DIR / f.name
                shutil.move(str(f), str(dest))
                print(f"[OK] {f.name} moved to Done/")
                sent += 1

            except PwTimeout as e:
                print(f"[ERROR] Timeout for {contact}: {e}")
            except Exception as e:
                print(f"[ERROR] Failed for {contact}: {e}")

        try:
            context.close()
        except Exception:
            pass

    print(f"\n[DONE] Sent {sent}/{len(tasks)} message(s).")


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
