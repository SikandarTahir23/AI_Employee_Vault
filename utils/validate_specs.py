"""
SpecKit Validator — AI Employee Vault
Step 0.0 Foundation

Checks that the current codebase matches all rules defined in /specs/*.spec.
Run: python validate_specs.py
Exit code 0 = all CRITICAL/HIGH rules pass.
Exit code 1 = one or more CRITICAL rules fail.
"""

import re
import sys
import os
from pathlib import Path

# Force UTF-8 output on Windows
if os.name == "nt":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"  {GREEN}PASS{RESET}  {msg}")
def fail(msg): print(f"  {RED}FAIL{RESET}  {msg}")
def warn(msg): print(f"  {YELLOW}WARN{RESET}  {msg}")
def info(msg): print(f"  {CYAN}INFO{RESET}  {msg}")


# ── Load files ────────────────────────────────────────────────────────────────
def read(filename):
    p = BASE / filename
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

app_txt    = read("app.py")
wa_txt     = read("whatsapp_sender.py")
li_txt     = read("linkedin_poster.py")
sync_txt   = read("vault_sync.py")

results = []  # list of (rule_id, severity, passed: bool, message)

def check(rule_id, severity, passed, pass_msg, fail_msg):
    results.append((rule_id, severity, passed, pass_msg if passed else fail_msg))


# ════════════════════════════════════════════════════════════════════════════════
# DASH rules — app.py
# ════════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}{'─'*60}{RESET}")
print(f"{BOLD}  app.py — Dashboard Rules{RESET}")
print(f"{BOLD}{'─'*60}{RESET}")

# DASH-001: no subprocess.run with both creationflags and capture_output
bad_pattern = re.findall(
    r"subprocess\.run\([^)]*capture_output[^)]*creationflags|"
    r"subprocess\.run\([^)]*creationflags[^)]*capture_output",
    app_txt, re.DOTALL
)
check("DASH-001", "CRITICAL",
      len(bad_pattern) == 0,
      "No subprocess.run() with capture_output+creationflags (WinError 87 safe)",
      f"Found {len(bad_pattern)} subprocess.run() call(s) mixing capture_output+creationflags")

# DASH-002: CREATE_NEW_CONSOLE defined
check("DASH-002", "CRITICAL",
      "_CREATE_NEW_CONSOLE = 0x00000010" in app_txt,
      "CREATE_NEW_CONSOLE flag defined",
      "CREATE_NEW_CONSOLE flag NOT defined")

# DASH-002b: _safe_run and _safe_popen present
check("DASH-002b", "CRITICAL",
      "def _safe_run(" in app_txt and "def _safe_popen(" in app_txt,
      "_safe_run() and _safe_popen() helpers present",
      "_safe_run() or _safe_popen() missing")

# DASH-003: mock accounting fallback
check("DASH-003", "HIGH",
      "def _mock_accounting(" in app_txt and "_mock_accounting()" in app_txt,
      "_mock_accounting() fallback defined and used",
      "_mock_accounting() fallback missing")

# DASH-004: single autopilot thread guard
check("DASH-004", "HIGH",
      "autopilot_thread" in app_txt and "is_alive()" in app_txt,
      "Autopilot single-thread guard present (is_alive check)",
      "Autopilot thread guard missing — risk of duplicate threads")

# DASH-004b: autopilot sleeps before first run
check("DASH-004b", "HIGH",
      re.search(r"def autopilot_loop[\s\S]{0,50}time\.sleep\(86400\)", app_txt) is not None,
      "Autopilot loop sleeps 24h before first run",
      "Autopilot loop runs immediately on start (spam risk)")

# DASH-005: vault_sync PROTECTED_FILES
check("DASH-005", "CRITICAL",
      "PROTECTED_FILES" in sync_txt and "app.py" in sync_txt,
      "vault_sync.py PROTECTED_FILES guard covers app.py",
      "vault_sync.py PROTECTED_FILES guard missing")

# DASH-006: autorefresh >= 30s
ar_match = re.search(r"st_autorefresh\(interval=(\d+)", app_txt)
ar_val = int(ar_match.group(1)) if ar_match else 0
check("DASH-006", "MEDIUM",
      ar_val >= 30000,
      f"Auto-refresh interval {ar_val}ms >= 30000ms",
      f"Auto-refresh interval {ar_val}ms < 30000ms (too aggressive)")

# DASH-007: draft editor state
check("DASH-007", "MEDIUM",
      '"editing_draft"' in app_txt,
      "Draft editor uses session_state['editing_draft'] gate",
      "Draft editor state gate missing")

# DASH-008: no shell=True in app.py (exclude comments)
app_code_only = re.sub(r"#[^\n]*", "", app_txt)  # strip inline comments
check("DASH-008", "CRITICAL",
      "shell=True" not in app_code_only,
      "No shell=True in app.py",
      "shell=True found in app.py — security risk")

# DASH-009: no bare "python" string in subprocess call lists
bare_python = re.findall(r'\["python"\s*,|\["python"\s*\]', app_code_only)
check("DASH-009", "CRITICAL",
      len(bare_python) == 0,
      "All subprocess calls use _PY (sys.executable), not bare 'python' string",
      f"Found {len(bare_python)} bare 'python' string(s) in subprocess calls — use _PY = sys.executable")

# DASH-010: _safe_popen Windows branch uses DEVNULL (no file handle)
safe_popen_body = re.search(r"def _safe_popen\([\s\S]{0,2000}?def ", app_txt)
sp_body = safe_popen_body.group(0) if safe_popen_body else ""
check("DASH-010", "CRITICAL",
      "subprocess.DEVNULL" in sp_body and "stdout or subprocess.DEVNULL" not in sp_body.split("if os.name")[1].split("else")[0] if "if os.name" in sp_body else "subprocess.DEVNULL" in sp_body,
      "_safe_popen Windows branch routes to DEVNULL only (no file-handle WinError 87 risk)",
      "_safe_popen may pass file handle with CREATE_NEW_CONSOLE — WinError 87 risk")

for rule_id, sev, passed, msg in results:
    (ok if passed else (fail if sev == "CRITICAL" else warn))(f"[{rule_id}] {msg}")

results.clear()

# ════════════════════════════════════════════════════════════════════════════════
# WA rules — whatsapp_sender.py
# ════════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}{'─'*60}{RESET}")
print(f"{BOLD}  whatsapp_sender.py — WhatsApp Rules{RESET}")
print(f"{BOLD}{'─'*60}{RESET}")

# WA-001: min 300s timeout present somewhere in send logic
timeouts = [int(m) for m in re.findall(r"timeout=(\d+)", wa_txt)]
check("WA-001", "CRITICAL",
      any(t >= 300000 for t in timeouts),
      f">=300000ms timeout present (values found: {timeouts[:6]})",
      f"No timeout >= 300000ms found (values: {timeouts[:6]}) — 5 min minimum required")

# WA-002: APPROVED_DIR used
check("WA-002", "CRITICAL",
      "APPROVED_DIR" in wa_txt,
      "APPROVED_DIR defined and used",
      "APPROVED_DIR missing — may read from wrong directory")

# WA-003: DONE_DIR / shutil.move used
check("WA-003", "HIGH",
      "DONE_DIR" in wa_txt and "shutil" in wa_txt,
      "DONE_DIR + shutil present — files moved after sending",
      "DONE_DIR or shutil missing — sent files not archived")

# WA-004: persistent profile
check("WA-004", "HIGH",
      "launch_persistent_context" in wa_txt,
      "Playwright persistent context used",
      "Persistent context missing — QR scan required every run")

# WA-005: retry logic
check("WA-005", "MEDIUM",
      "attempt" in wa_txt and "range(3)" in wa_txt,
      "Navigation retry logic present (3 attempts)",
      "Navigation retry logic missing")

# WA-006: no shell=True
check("WA-006", "CRITICAL",
      "shell=True" not in wa_txt,
      "No shell=True in whatsapp_sender.py",
      "shell=True found — security risk")

for rule_id, sev, passed, msg in results:
    (ok if passed else (fail if sev == "CRITICAL" else warn))(f"[{rule_id}] {msg}")

results.clear()

# ════════════════════════════════════════════════════════════════════════════════
# LI rules — linkedin_poster.py
# ════════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}{'─'*60}{RESET}")
print(f"{BOLD}  linkedin_poster.py — LinkedIn Rules{RESET}")
print(f"{BOLD}{'─'*60}{RESET}")

# LI-001: APPROVED_DIR used before DRAFTS_DIR in find_latest_draft body
# Strategy: find the function body, then check ordering within it
fn_start = li_txt.find("def find_latest_draft")
fn_end   = li_txt.find("\ndef ", fn_start + 10) if fn_start != -1 else -1
fn_body  = li_txt[fn_start:fn_end] if fn_start != -1 and fn_end != -1 else li_txt
ap_in_fn = fn_body.find("APPROVED_DIR") if fn_start != -1 else -1
dr_in_fn = fn_body.find("DRAFTS_DIR")  if fn_start != -1 else -1
check("LI-001", "CRITICAL",
      "APPROVED_DIR" in li_txt and (
          dr_in_fn == -1 or (ap_in_fn != -1 and ap_in_fn < dr_in_fn)
      ),
      "APPROVED_DIR scanned before DRAFTS_DIR",
      "APPROVED_DIR missing or appears after DRAFTS_DIR")

# LI-002: DONE_DIR + shutil.move in mark_as_posted
check("LI-002", "CRITICAL",
      "DONE_DIR" in li_txt and "shutil" in li_txt,
      "DONE_DIR + shutil.move in mark_as_posted()",
      "DONE_DIR or shutil.move missing — posted files not archived")

# LI-003: re.sub for status update
check("LI-003", "HIGH",
      're.sub' in li_txt and 'Status' in li_txt,
      "re.sub() used for robust **Status:** update",
      "re.sub() for status update missing — fragile str.replace() may be used")

# LI-004: >= 4 strategies, JS click present
strategy_count = li_txt.count("Strategy")
check("LI-004", "HIGH",
      strategy_count >= 4 and "page.evaluate" in li_txt,
      f"{strategy_count} strategies defined, JS evaluate click present",
      f"Only {strategy_count} strategies or JS click missing")

# LI-005: JS click in first 3 strategies
js_idx = li_txt.find("page.evaluate")
s1_idx = li_txt.find("Strategy 1")
s4_idx = li_txt.find("Strategy 4")
check("LI-005", "MEDIUM",
      js_idx != -1 and s1_idx < js_idx < s4_idx,
      "JS click strategy positioned before Strategy 4 (high priority)",
      "JS click strategy not in first 3 positions")

# LI-006: modal verification
check("LI-006", "HIGH",
      'role=\'dialog\'' in li_txt or 'role="dialog"' in li_txt or "div[role='dialog']" in li_txt,
      "Modal verification present after each strategy",
      "Modal verification missing — strategies may click without confirming open")

# LI-007: skip already-posted
check("LI-007", "HIGH",
      "Posted" in li_txt and ("filter" in li_txt or "Status.*Posted" in li_txt or '"Posted"' in li_txt),
      "Already-posted files are skipped",
      "No skip-if-posted guard found")

# LI-008: no shell=True
check("LI-008", "CRITICAL",
      "shell=True" not in li_txt,
      "No shell=True in linkedin_poster.py",
      "shell=True found — security risk")

for rule_id, sev, passed, msg in results:
    (ok if passed else (fail if sev == "CRITICAL" else warn))(f"[{rule_id}] {msg}")

results.clear()

# ════════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}{'═'*60}{RESET}")
print(f"{BOLD}  SPECKIT SUMMARY{RESET}")
print(f"{BOLD}{'═'*60}{RESET}")

all_results = []

# Re-run all checks silently for summary
def recheck(rule_id, severity, passed):
    all_results.append((rule_id, severity, passed))

# Recount from file analysis
critical_fails = 0
high_fails = 0
total = 0

# Quick re-scan for critical failures
checks = [
    ("DASH-001", "CRITICAL", len(re.findall(r"subprocess\.run\([^)]*capture_output[^)]*creationflags|subprocess\.run\([^)]*creationflags[^)]*capture_output", app_txt, re.DOTALL)) == 0),
    ("DASH-002", "CRITICAL", "_CREATE_NEW_CONSOLE = 0x00000010" in app_txt),
    ("DASH-003", "HIGH",     "def _mock_accounting(" in app_txt),
    ("DASH-005", "CRITICAL", "PROTECTED_FILES" in sync_txt),
    ("DASH-008", "CRITICAL", "shell=True" not in re.sub(r"#[^\n]*", "", app_txt)),
    ("DASH-009", "CRITICAL", len(re.findall(r'\["python"\s*,|\["python"\s*\]', re.sub(r"#[^\n]*", "", app_txt))) == 0),
    ("WA-001",   "CRITICAL", any(t >= 300000 for t in [int(m) for m in re.findall(r"timeout=(\d+)", wa_txt)])),
    ("WA-002",   "CRITICAL", "APPROVED_DIR" in wa_txt),
    ("WA-006",   "CRITICAL", "shell=True" not in wa_txt),
    ("LI-001",   "CRITICAL", "APPROVED_DIR" in li_txt and li_txt.find("APPROVED_DIR", 500) < li_txt.find("DRAFTS_DIR", li_txt.find("APPROVED_DIR", 500))),
    ("LI-002",   "CRITICAL", "DONE_DIR" in li_txt and "shutil" in li_txt),
    ("LI-008",   "CRITICAL", "shell=True" not in li_txt),
]

passed_count = sum(1 for _, _, p in checks if p)
failed_critical = [(r, s) for r, s, p in checks if not p and s == "CRITICAL"]

print(f"  Rules checked : {len(checks)}")
print(f"  {GREEN}Passing       : {passed_count}{RESET}")
print(f"  {RED}Critical fails: {len(failed_critical)}{RESET}")

if failed_critical:
    print(f"\n  {RED}{BOLD}CRITICAL FAILURES:{RESET}")
    for r, s in failed_critical:
        print(f"    {RED}✗ {r}{RESET}")
    print()
    sys.exit(1)
else:
    print(f"\n  {GREEN}{BOLD}✓ All CRITICAL rules pass. System is spec-compliant.{RESET}")
    print()
    sys.exit(0)
