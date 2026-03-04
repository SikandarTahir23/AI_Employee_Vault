"""
LinkedIn Poster — Playwright Browser Automation
Posts the latest LinkedIn draft to linkedin.com using a persistent browser profile.

Usage:
    python linkedin_poster.py                      # post latest draft
    python linkedin_poster.py Drafts/specific.md   # post a specific draft
    python linkedin_poster.py --login              # open browser for manual login

Requirements:
    pip install playwright && playwright install chromium

Notes:
    - First run: use --login to sign into LinkedIn, then close the browser.
    - Subsequent runs reuse the saved session automatically.
    - Uses headless=False so you can observe the browser.
    - LinkedIn updates its DOM frequently — selectors may need updating.
"""

import sys
import io
import glob
import os
import re
import subprocess
import time
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows to handle emojis in post content
if sys.stdout and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
except ImportError:
    print("[ERROR] playwright is not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
DRAFTS_DIR = BASE_DIR / "Drafts"
APPROVED_DIR = BASE_DIR / "Approved"
DONE_DIR = BASE_DIR / "Done"
PLAYWRIGHT_PROFILE = BASE_DIR / ".playwright_profile"

APPROVED_DIR.mkdir(exist_ok=True)
DONE_DIR.mkdir(exist_ok=True)


def close_chrome():
    """Close all Chrome processes to avoid profile lock conflicts."""
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
        capture_output=True, text=True,
    )
    if "chrome.exe" not in result.stdout:
        return
    print("[INFO] Chrome is running — closing it to avoid profile conflicts...")
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    time.sleep(2)


def get_browser_context(playwright):
    """Launch a persistent Chromium context using a dedicated Playwright profile."""
    PLAYWRIGHT_PROFILE.mkdir(parents=True, exist_ok=True)
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(PLAYWRIGHT_PROFILE),
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
        timeout=60000,
    )
    return context


def find_latest_draft():
    """Find the most recently modified LinkedIn draft.
    Prefers Approved/ (ready-to-post) over Drafts/ (still in review).
    Skips files already marked as Posted or Approved+already-sent."""
    # Check Approved/ first — these are CEO-approved and ready
    approved_files = list(APPROVED_DIR.glob("LinkedIn_Post*.md"))
    approved_files = [f for f in approved_files if "**Status:** Posted" not in f.read_text(encoding="utf-8")]
    if approved_files:
        approved_files.sort(key=os.path.getmtime, reverse=True)
        print(f"[INFO] Found {len(approved_files)} approved draft(s) — using latest from Approved/")
        return approved_files[0]

    # Fall back to Drafts/
    pattern = str(DRAFTS_DIR / "LinkedIn_Post*.md")
    files = glob.glob(pattern)
    if not files:
        print("[ERROR] No LinkedIn drafts found in Approved/ or Drafts/")
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    print(f"[INFO] No approved drafts — using latest from Drafts/")
    return Path(files[0])


def extract_post_content(filepath):
    """Extract the post body from a LinkedIn draft markdown file.

    Returns the text between the first '---' separator and the hashtag line,
    stripping the metadata header and footer.
    """
    text = filepath.read_text(encoding="utf-8")
    sections = re.split(r"^---\s*$", text, flags=re.MULTILINE)

    if len(sections) < 3:
        print("[ERROR] Draft format unexpected — could not find content between --- separators")
        return None

    body = sections[1].strip()
    hashtags = sections[2].strip() if len(sections) > 2 else ""

    content = body
    if hashtags:
        content += "\n\n" + hashtags

    # Clean markdown bold markers for plain-text posting
    content = content.replace("**", "")
    # Clean markdown list markers
    content = re.sub(r"^\s*- ", "• ", content, flags=re.MULTILINE)

    return content


def login_flow():
    """Open browser for manual LinkedIn login, then exit."""
    print("[INFO] Opening browser for LinkedIn login...")
    print("[INFO] Sign in to LinkedIn, then close the browser window.")
    print()

    close_chrome()

    with sync_playwright() as p:
        context = get_browser_context(p)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.linkedin.com/login", timeout=60000)
        print("[INFO] Waiting for you to log in... (close browser when done)")
        try:
            # Wait until the user closes the browser
            page.wait_for_event("close", timeout=300000)
        except Exception:
            pass
        try:
            context.close()
        except Exception:
            pass

    print("[OK] Login session saved. You can now run: python linkedin_poster.py")


def post_to_linkedin(content):
    """Launch browser and post content to LinkedIn."""
    close_chrome()
    print("[INFO] Launching browser with persistent Playwright profile...")
    print()

    with sync_playwright() as p:
        try:
            context = get_browser_context(p)
        except Exception as e:
            print(f"[ERROR] Could not launch browser: {e}")
            return False

        page = context.pages[0] if context.pages else context.new_page()

        try:
            # Navigate to LinkedIn feed
            print("[INFO] Navigating to LinkedIn feed...")
            page.goto("https://www.linkedin.com/feed/", timeout=60000, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                print("[INFO] networkidle not reached (normal for LinkedIn) — continuing...")
            page.wait_for_timeout(3000)

            # Check if we need to log in
            if "/login" in page.url or "/checkpoint" in page.url:
                print("[ERROR] Not logged in to LinkedIn.")
                print("[HINT] Run: python linkedin_poster.py --login")
                context.close()
                return False

            # Click "Start a post" — try multiple strategies
            # After clicking, we verify the modal opened before proceeding.
            print("[INFO] Looking for 'Start a post'...")
            modal_opened = False

            start_post_strategies = [
                # Strategy 1: text match
                lambda: (
                    print("[INFO] Strategy 1: text match...") or True,
                    page.wait_for_selector("text=Start a post", timeout=8000),
                    page.get_by_text("Start a post").first.click(force=True, timeout=5000),
                ),
                # Strategy 2: CSS class (share-box trigger)
                lambda: (
                    print("[INFO] Strategy 2: CSS class...") or True,
                    page.locator(".share-box-feed-entry__trigger").first.wait_for(state="visible", timeout=8000),
                    page.locator(".share-box-feed-entry__trigger").first.click(force=True, timeout=5000),
                ),
                # Strategy 3: JS click — proven reliable on 2026 LinkedIn DOM
                # Finds the innermost element containing "Start a post" and clicks it.
                lambda: (
                    print("[INFO] Strategy 3: JavaScript innermost click...") or True,
                    page.evaluate("""
                        (() => {
                            const all = document.querySelectorAll('*');
                            let best = null;
                            for (const el of all) {
                                const text = (el.textContent || '').trim();
                                if (text.includes('Start a post') && el.children.length < 3) {
                                    if (!best || text.length < best.textContent.trim().length) {
                                        best = el;
                                    }
                                }
                            }
                            if (best) { best.click(); return true; }
                            return false;
                        })()
                    """),
                ),
                # Strategy 4: aria-label
                lambda: (
                    print("[INFO] Strategy 4: aria-label...") or True,
                    page.locator("[aria-label*='Start a post']").first.wait_for(state="visible", timeout=8000),
                    page.locator("[aria-label*='Start a post']").first.click(force=True, timeout=5000),
                ),
                # Strategy 5: data-view-name (LinkedIn 2025/2026 feed composer button)
                lambda: (
                    print("[INFO] Strategy 5: data-view-name feed composer...") or True,
                    page.locator("[data-view-name='share-creation-state'] button, "
                                 "button[data-control-name='share.share_feed_entry'], "
                                 ".share-box-feed-entry__closed-share-box button").first.wait_for(state="visible", timeout=8000),
                    page.locator("[data-view-name='share-creation-state'] button, "
                                 "button[data-control-name='share.share_feed_entry'], "
                                 ".share-box-feed-entry__closed-share-box button").first.click(force=True, timeout=5000),
                ),
                # Strategy 6: share prompt button / artdeco pill fallback
                lambda: (
                    print("[INFO] Strategy 6: share prompt fallback...") or True,
                    page.locator("button.share-box-feed-entry__trigger, button.artdeco-pill").first.wait_for(state="visible", timeout=8000),
                    page.locator("button.share-box-feed-entry__trigger, button.artdeco-pill").first.click(force=True, timeout=5000),
                ),
            ]

            for i, strategy in enumerate(start_post_strategies):
                if modal_opened:
                    break
                try:
                    strategy()
                    # Wait for modal to open
                    page.wait_for_timeout(2000)
                    # Verify modal opened: look for dialog/overlay
                    modal_open = page.locator(
                        "div[role='dialog'], "
                        "div.share-creation-state__overlay, "
                        "div.share-box--is-open, "
                        "div.artdeco-modal, "
                        "div[data-test-modal]"
                    ).first
                    try:
                        modal_open.wait_for(state="visible", timeout=5000)
                        print(f"[INFO] Modal opened after strategy {i+1}!")
                        modal_opened = True
                    except Exception:
                        print(f"[INFO] Strategy {i+1} clicked but modal did not open — trying next...")
                        # Debug screenshot
                        page.screenshot(path=str(BASE_DIR / f"debug_strategy_{i+1}.png"))
                except Exception as e:
                    print(f"[INFO] Strategy {i+1} failed: {type(e).__name__}")

            if not modal_opened:
                fail_path = str(BASE_DIR / "failure_capture.png")
                page.screenshot(path=fail_path)
                print(f"[ERROR] Could not open post modal. Screenshot saved: failure_capture.png")
                context.close()
                return False

            page.wait_for_timeout(1000)

            # Type content into the post editor — multi-strategy
            print("[INFO] Looking for post editor...")
            editor_clicked = False

            # Editor Strategy 1: role textbox
            if not editor_clicked:
                try:
                    ed = page.get_by_role("textbox").first
                    ed.wait_for(state="visible", timeout=8000)
                    print("[INFO] Found editor via role=textbox — clicking...")
                    ed.click(force=True, timeout=5000)
                    editor_clicked = True
                except Exception:
                    print("[INFO] role=textbox failed, trying contenteditable...")

            # Editor Strategy 2: any contenteditable div
            if not editor_clicked:
                try:
                    ed = page.locator("div[contenteditable='true']").first
                    ed.wait_for(state="visible", timeout=8000)
                    print("[INFO] Found editor via contenteditable — clicking...")
                    ed.click(force=True, timeout=5000)
                    editor_clicked = True
                except Exception:
                    print("[INFO] contenteditable failed, trying ql-editor...")

            # Editor Strategy 3: Quill editor class
            if not editor_clicked:
                try:
                    ed = page.locator("div.ql-editor").first
                    ed.wait_for(state="visible", timeout=8000)
                    print("[INFO] Found editor via ql-editor — clicking...")
                    ed.click(force=True, timeout=5000)
                    editor_clicked = True
                except Exception:
                    print("[INFO] ql-editor failed, trying data-placeholder...")

            # Editor Strategy 4: any element with data-placeholder
            if not editor_clicked:
                try:
                    ed = page.locator("[data-placeholder]").first
                    ed.wait_for(state="visible", timeout=8000)
                    print("[INFO] Found editor via data-placeholder — clicking...")
                    ed.click(force=True, timeout=5000)
                    editor_clicked = True
                except Exception:
                    pass

            if not editor_clicked:
                fail_path = str(BASE_DIR / "failure_capture.png")
                page.screenshot(path=fail_path)
                print(f"[ERROR] Could not find post editor. Screenshot saved: failure_capture.png")
                context.close()
                return False

            print("[INFO] Typing post content...")
            page.wait_for_timeout(500)
            for i, line in enumerate(content.split("\n")):
                if i > 0:
                    page.keyboard.press("Enter")
                page.keyboard.type(line, delay=10)

            page.wait_for_timeout(1000)

            # Click Post button
            print("[INFO] Clicking Post button...")
            post_btn = page.get_by_role("button", name="Post", exact=True).or_(
                page.locator("button.share-actions__primary-action")
            ).or_(
                page.locator("button[aria-label='Post']")
            )
            post_btn.first.click(timeout=30000)

            # Wait for confirmation popup to appear
            print("[INFO] Waiting for post confirmation...")
            time.sleep(5)

            # Screenshot as audit proof
            screenshot_path = str(BASE_DIR / "post_confirmation.png")
            page.screenshot(path=screenshot_path)
            print(f"[OK] Screenshot saved: post_confirmation.png")

            print("[OK] Post submitted to LinkedIn!")
            success = True

        except PwTimeout as e:
            fail_path = str(BASE_DIR / "failure_capture.png")
            try:
                page.screenshot(path=fail_path)
                print(f"[INFO] Failure screenshot saved: failure_capture.png")
            except Exception:
                pass
            print(f"[ERROR] Timeout waiting for element: {e}")
            print("[HINT] LinkedIn may have updated its UI. Check selectors in linkedin_poster.py.")
            success = False
        except Exception as e:
            fail_path = str(BASE_DIR / "failure_capture.png")
            try:
                page.screenshot(path=fail_path)
                print(f"[INFO] Failure screenshot saved: failure_capture.png")
            except Exception:
                pass
            print(f"[ERROR] Failed to post: {e}")
            success = False
        finally:
            context.close()

        return success


def mark_as_posted(filepath):
    """Update the draft file status to Posted and move it to Done/."""
    import shutil
    text = filepath.read_text(encoding="utf-8")
    # Update status regardless of current value (Draft or Approved)
    updated = re.sub(r"\*\*Status:\*\*\s*\S+", "**Status:** Posted", text)
    updated += f"\n\n---\n*Posted: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    filepath.write_text(updated, encoding="utf-8")
    print(f"[OK] Marked {filepath.name} as Posted")
    # Move to Done/ for audit trail
    dest = DONE_DIR / filepath.name
    shutil.move(str(filepath), str(dest))
    print(f"[OK] Moved to Done/{filepath.name}")


def main():
    print("=" * 50)
    print("  LinkedIn Poster — Browser Automation")
    print("=" * 50)
    print()

    # Login mode
    if "--login" in sys.argv:
        login_flow()
        return

    # Determine which draft to post
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        filepath = Path(sys.argv[1])
        if not filepath.is_absolute():
            filepath = BASE_DIR / filepath
        if not filepath.exists():
            print(f"[ERROR] File not found: {filepath}")
            sys.exit(1)
    else:
        filepath = find_latest_draft()
        if not filepath:
            sys.exit(1)

    print(f"[INFO] Draft: {filepath.name}")

    # Check if already posted
    text = filepath.read_text(encoding="utf-8")
    if "**Status:** Posted" in text:
        print("[WARN] This draft is already marked as Posted. Skipping.")
        sys.exit(0)

    # Extract content
    content = extract_post_content(filepath)
    if not content:
        sys.exit(1)

    print(f"[INFO] Content length: {len(content)} chars")
    print(f"[INFO] Preview: {content[:100]}...")
    print()

    # Post to LinkedIn
    if post_to_linkedin(content):
        mark_as_posted(filepath)
        print("\n[DONE] LinkedIn post complete.")
    else:
        print("\n[FAILED] Could not post to LinkedIn. Draft remains as Draft.")
        sys.exit(1)


if __name__ == "__main__":
    main()
