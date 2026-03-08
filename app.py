import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
import subprocess
import threading
import time
import os
import sys
import signal
import shutil
from pathlib import Path
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Always use the same Python interpreter that is running this script
_PY = sys.executable

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Tabraiz Haider | CEO Command",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# AUTO-REFRESH every 30 seconds
# ──────────────────────────────────────────────
st_autorefresh(interval=30000, key="datarefresh")

# ──────────────────────────────────────────────
# CLEAN CSS — Professional SaaS Theme
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    div.block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }

    /* ── Sticky Header ── */
    .sticky-header {
        position: sticky;
        top: 0; z-index: 999;
        background: #0D1117;
        padding: 12px 0;
        border-bottom: 1px solid #1C2028;
        margin: -1rem -1rem 0 -1rem;
        padding-left: 1rem; padding-right: 1rem;
    }
    .sticky-header h1 {
        margin: 0; padding: 0;
        font-size: 1.1rem; font-weight: 600;
        color: #E6EDF3;
        letter-spacing: -0.01em;
    }
    .sticky-header .subtitle {
        color: #6E7681; font-size: 0.72rem;
        margin-top: 1px; letter-spacing: 0.02em;
    }

    /* ── Metric cards — slim ── */
    div[data-testid="stMetric"] {
        background: transparent;
        border: 1px solid #1C2028;
        border-radius: 8px;
        padding: 14px 16px;
    }
    div[data-testid="stMetric"] label {
        color: #6E7681 !important;
        font-size: 0.68rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        color: #E6EDF3 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        font-size: 0.65rem !important;
    }

    /* ── Sidebar — minimal ── */
    section[data-testid="stSidebar"] {
        background: #0D1117 !important;
        border-right: 1px solid #1C2028;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    .sb-name {
        font-size: 0.92rem; font-weight: 600; color: #E6EDF3;
        letter-spacing: -0.01em;
    }
    .sb-role {
        font-size: 0.65rem; color: #6E7681; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin-top: 1px;
    }
    .sb-divider {
        border: none; height: 1px; background: #1C2028; margin: 14px 0;
    }
    .sb-label {
        color: #6E7681; font-size: 0.65rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin-bottom: 2px;
    }
    .sb-value {
        color: #C9D1D9; font-size: 0.82rem; font-weight: 500;
    }
    .sb-badge {
        display: inline-block; font-size: 0.6rem; font-weight: 600;
        padding: 2px 8px; border-radius: 10px;
        letter-spacing: 0.04em;
    }
    .sb-badge-live { background: #1B3D2F; color: #3FB950; }
    .sb-badge-on   { background: #1C1D3E; color: #A78BFA; }
    .sb-badge-off  { background: #161B22; color: #6E7681; }
    .sb-footer {
        color: #484F58; font-size: 0.62rem; text-align: center; margin-top: 8px;
    }

    /* ── Section headers — understated ── */
    .section-header {
        font-size: 0.78rem; font-weight: 600; color: #8B949E;
        text-transform: uppercase; letter-spacing: 0.06em;
        margin: 32px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1C2028;
    }

    /* ── Unified card style ── */
    .card {
        background: #0D1117;
        border: 1px solid #1C2028;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .card-title {
        color: #E6EDF3; font-weight: 500; font-size: 0.84rem;
        line-height: 1.35;
    }
    .card-meta {
        color: #6E7681; font-size: 0.7rem; margin-top: 3px;
    }
    .card-body {
        color: #8B949E; font-size: 0.76rem; margin-top: 6px;
        line-height: 1.45;
    }

    /* ── Tags — subtle ── */
    .tag {
        display: inline-block;
        font-size: 0.58rem; font-weight: 600;
        padding: 1px 6px; border-radius: 3px;
        letter-spacing: 0.04em; margin-right: 6px;
        vertical-align: middle;
    }
    .tag-ai     { background: #1C1D3E; color: #A78BFA; }
    .tag-social { background: #0C2D48; color: #58A6FF; }
    .tag-finance{ background: #2D2306; color: #E3B341; }
    .tag-plan   { background: #1C1D3E; color: #A78BFA; }

    /* ── Priority badges ── */
    .pri {
        display: inline-block; font-size: 0.58rem; font-weight: 600;
        padding: 1px 6px; border-radius: 3px;
        letter-spacing: 0.04em; margin-right: 6px;
        vertical-align: middle;
    }
    .pri-high   { background: #3D1518; color: #F85149; }
    .pri-medium { background: #2D2306; color: #E3B341; }
    .pri-low    { background: #1B3D2F; color: #3FB950; }

    /* ── Kanban ── */
    .kanban-col-header {
        font-size: 0.68rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.06em;
        padding: 8px 12px;
        border: 1px solid #1C2028;
        border-radius: 8px 8px 0 0;
        background: #0D1117;
    }
    .kanban-col-header .dot {
        display: inline-block; width: 8px; height: 8px;
        border-radius: 50%; margin-right: 6px;
        vertical-align: middle;
    }
    .dot-todo  { background: #D29922; }
    .dot-doing { background: #58A6FF; }
    .dot-done  { background: #3FB950; }
    .kanban-col-header .count {
        color: #6E7681; font-weight: 500; margin-left: 4px;
    }
    .kanban-body {
        border: 1px solid #1C2028;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 10px; min-height: 180px;
        background: transparent;
    }
    .kanban-card {
        background: #0D1117;
        border: 1px solid #1C2028;
        border-radius: 6px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    .kanban-card-title {
        color: #C9D1D9; font-weight: 500; font-size: 0.78rem;
    }
    .kanban-card-meta {
        color: #484F58; font-size: 0.65rem; margin-top: 3px;
    }

    /* ── Financial row ── */
    .fin-row {
        display: flex; gap: 16px; flex-wrap: wrap;
        margin-bottom: 8px;
    }
    .fin-item {
        flex: 1; min-width: 120px;
        border: 1px solid #1C2028; border-radius: 8px;
        padding: 12px 14px;
        background: transparent;
    }
    .fin-value {
        font-size: 1.1rem; font-weight: 600; color: #E6EDF3;
    }
    .fin-value.green { color: #3FB950; }
    .fin-value.amber { color: #E3B341; }
    .fin-value.blue  { color: #58A6FF; }
    .fin-label {
        color: #6E7681; font-size: 0.62rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.05em;
        margin-top: 2px;
    }

    /* ── Plan steps ── */
    .plan-step {
        color: #8B949E; font-size: 0.76rem; margin-left: 8px;
        line-height: 1.5;
    }

    /* ── Charts ── */
    .js-plotly-plot { border-radius: 8px; }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        font-weight: 600 !important; color: #C9D1D9 !important;
        font-size: 0.82rem !important;
    }

    /* ── Footer ── */
    .footer-text {
        text-align: center; color: #484F58; font-size: 0.65rem;
        margin-top: 48px; padding: 14px 0;
        border-top: 1px solid #1C2028;
    }

    /* ── Console Log ── */
    .console-log {
        background: #010409;
        border: 1px solid #1C2028;
        border-radius: 8px;
        padding: 14px 16px;
        font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
        font-size: 0.72rem;
        color: #8B949E;
        max-height: 360px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-break: break-all;
        line-height: 1.55;
    }

    /* ── Draft Card ── */
    .draft-card {
        background: #0D1117;
        border: 1px solid #1C2028;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        transition: border-color 0.15s;
    }
    .draft-card:hover {
        border-color: #30363D;
    }
    .draft-card .draft-title {
        color: #E6EDF3; font-weight: 500; font-size: 0.84rem;
    }
    .draft-card .draft-meta {
        color: #6E7681; font-size: 0.68rem; margin-top: 3px;
    }
    .draft-card .draft-status {
        display: inline-block; font-size: 0.58rem; font-weight: 600;
        padding: 1px 6px; border-radius: 3px;
        letter-spacing: 0.04em;
    }
    .draft-status-draft { background: #0C2D48; color: #58A6FF; }
    .draft-status-posted { background: #1B3D2F; color: #3FB950; }

    /* ── Watcher Status ── */
    .status-running {
        display: inline-block; font-size: 0.6rem; font-weight: 600;
        padding: 2px 8px; border-radius: 10px;
        background: #1B3D2F; color: #3FB950;
        letter-spacing: 0.04em;
    }
    .status-stopped {
        display: inline-block; font-size: 0.6rem; font-weight: 600;
        padding: 2px 8px; border-radius: 10px;
        background: #161B22; color: #6E7681;
        letter-spacing: 0.04em;
    }

    /* ── Channel Cards (LinkedIn / WhatsApp) ── */
    .channel-card {
        background: #0D1117;
        border: 1px solid #21262D;
        border-radius: 10px;
        padding: 18px 20px;
        height: 100%;
    }
    .channel-card-header {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 12px;
    }
    .channel-icon {
        font-size: 1.4rem; line-height: 1;
    }
    .channel-title {
        color: #E6EDF3; font-weight: 600; font-size: 0.88rem;
    }
    .channel-status {
        font-size: 0.62rem; font-weight: 600;
        padding: 2px 8px; border-radius: 10px;
        letter-spacing: 0.04em;
        margin-left: auto;
    }
    .channel-status-ready { background: #1B3D2F; color: #3FB950; }
    .channel-status-idle  { background: #161B22; color: #6E7681; }
    .channel-stat {
        color: #6E7681; font-size: 0.7rem; margin-bottom: 4px;
    }
    .channel-stat strong { color: #C9D1D9; }

    /* ── WhatsApp Task List ── */
    .wa-task {
        background: #0D1117;
        border: 1px solid #1C2028;
        border-left: 3px solid #25D366;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .wa-task-title { color: #E6EDF3; font-size: 0.8rem; font-weight: 500; }
    .wa-task-meta  { color: #6E7681; font-size: 0.66rem; margin-top: 2px; }

    /* ── AI Post Creator ── */
    .ai-creator-wrap {
        background: linear-gradient(135deg, #0D1117 0%, #111827 100%);
        border: 1px solid #21262D;
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
    }
    .ai-creator-wrap::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #A78BFA, #58A6FF, #3FB950);
    }
    .ai-creator-title {
        color: #E6EDF3;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .ai-creator-sub {
        color: #6E7681;
        font-size: 0.7rem;
        margin-bottom: 16px;
    }
    .ai-preview-box {
        background: #010409;
        border: 1px solid #21262D;
        border-radius: 8px;
        padding: 16px;
        margin-top: 12px;
        font-size: 0.78rem;
        color: #C9D1D9;
        line-height: 1.65;
        white-space: pre-wrap;
    }
    .ai-badge {
        display: inline-flex; align-items: center; gap: 4px;
        font-size: 0.58rem; font-weight: 700;
        padding: 2px 8px; border-radius: 10px;
        background: linear-gradient(90deg, #1a0d2e, #0c1a2e);
        color: #A78BFA;
        letter-spacing: 0.06em;
        border: 1px solid #3d2a6e;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
READINGS_DIR = BASE_DIR / "Readings"
BRIEFING_FILE = BASE_DIR / "CEO_Briefing_Feb_17.md"
ACCOUNTING_FILE = BASE_DIR / "accounting_status.json"
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"
IN_PROGRESS_DIR = BASE_DIR / "In_Progress"
DONE_DIR = BASE_DIR / "Done"
PLANS_DIR = BASE_DIR / "Plans"
DRAFTS_DIR = BASE_DIR / "Drafts"
COMMANDS_DIR = BASE_DIR / "Commands"
APPROVED_DIR = BASE_DIR / "Approved"
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "agent_activity.log"

COMMANDS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
APPROVED_DIR.mkdir(exist_ok=True)

WATCHERS = {
    "Gmail Bridge": "watchers/gmail_bridge.py",
    "Desktop Watcher": "watchers/desktop_watcher.py",
    "Agent Brain": "agent_brain.py",
    "Social Media Agent": "social_media_agent.py",
    "Odoo Bridge": "odoo_mcp_bridge.py",
}


# ──────────────────────────────────────────────
# PROCESS MANAGEMENT HELPERS
# ──────────────────────────────────────────────
# IMPORTANT: On Windows, CREATE_NEW_CONSOLE is incompatible with
# capture_output=True / PIPE (causes WinError 87 — invalid parameter).
# Solution: route output through a temp file instead of PIPE.
_CREATE_NEW_CONSOLE = 0x00000010  # subprocess.CREATE_NEW_CONSOLE


def _safe_run(cmd, cwd=None, timeout=150):
    """Run a command in an isolated process and capture output via temp file.
    Avoids WinError 87 by never using PIPE with CREATE_NEW_CONSOLE."""
    import tempfile
    cwd = cwd or str(BASE_DIR)
    # Ensure paths with spaces are handled — use list form (no shell=True needed)
    if os.name == "nt":
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log",
                                         delete=False, encoding="utf-8") as tf:
            tmp_path = tf.name
        try:
            with open(tmp_path, "w", encoding="utf-8") as out_f:
                proc = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdout=out_f,
                    stderr=out_f,
                    creationflags=_CREATE_NEW_CONSOLE,
                    # Do NOT set close_fds=True when redirecting to a file handle
                )
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.terminate()
                    raise
            output = Path(tmp_path).read_text(encoding="utf-8", errors="replace")
            return proc.returncode, output
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass
    else:
        result = subprocess.run(
            cmd, cwd=cwd, timeout=timeout,
            capture_output=True, text=True,
            start_new_session=True,
        )
        return result.returncode, result.stdout + result.stderr


def _safe_popen(cmd, cwd=None, stdout=None, stderr=None, detach=False):
    """Launch a fire-and-forget background process (no output capture).

    WinError 87 rules (Windows):
      1. CREATE_NEW_CONSOLE is incompatible with PIPE or file handles.
      2. CREATE_NEW_CONSOLE (0x10) and DETACHED_PROCESS (0x08) are
         MUTUALLY EXCLUSIVE — combining them causes WinError 87.
      3. Always use subprocess.DEVNULL for stdout/stderr.
    """
    cwd = cwd or str(BASE_DIR)
    if os.name == "nt":
        # Pick ONE flag — never combine CREATE_NEW_CONSOLE + DETACHED_PROCESS
        if detach:
            flags = 0x00000008  # DETACHED_PROCESS only
        else:
            flags = _CREATE_NEW_CONSOLE  # visible console window
        return subprocess.Popen(
            cmd, cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
    else:
        return subprocess.Popen(
            cmd, cwd=cwd,
            stdout=stdout or subprocess.DEVNULL,
            stderr=stderr or subprocess.DEVNULL,
            start_new_session=True,
        )


def start_watcher(name, script_path):
    """Start a background watcher process, redirect output to log file."""
    full_path = BASE_DIR / script_path
    if not full_path.exists():
        st.toast(f"{name}: script not found ({script_path})", icon="\u274c")
        return
    # Log the launch event — then close handle before Popen to avoid WinError 87
    with open(LOG_FILE, "a", encoding="utf-8") as _lf:
        _lf.write(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] Starting {name}...\n")
    proc = _safe_popen(
        [_PY, str(full_path)],
        cwd=str(BASE_DIR),
    )
    st.session_state[f"watcher_{name}_pid"] = proc.pid
    st.session_state[f"watcher_{name}_proc"] = proc


def stop_watcher(name):
    """Stop a running watcher process."""
    proc = st.session_state.get(f"watcher_{name}_proc")
    if proc:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            # Windows fallback
            try:
                pid = st.session_state.get(f"watcher_{name}_pid")
                if pid:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                   capture_output=True, timeout=10)
            except Exception:
                pass
    # Clean up log handle
    log_handle = st.session_state.get(f"watcher_{name}_log")
    if log_handle:
        try:
            log_handle.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Stopped {name}.\n")
            log_handle.flush()
            log_handle.close()
        except Exception:
            pass
    for key in [f"watcher_{name}_pid", f"watcher_{name}_proc", f"watcher_{name}_log"]:
        st.session_state.pop(key, None)


def is_watcher_running(name):
    """Check if a watcher process is still alive."""
    proc = st.session_state.get(f"watcher_{name}_proc")
    if proc and proc.poll() is None:
        return True
    return False


def load_briefing():
    if BRIEFING_FILE.exists():
        return BRIEFING_FILE.read_text(encoding="utf-8")
    return ""


def _mock_accounting():
    """Inline mock financial data — used when accounting_status.json is missing.
    This ensures the financial metrics row always renders with realistic data."""
    return {
        "last_synced": datetime.now().isoformat(),
        "company": "Multicraft Agency",
        "currency": "PKR",
        "fiscal_month": datetime.now().strftime("%B %Y"),
        "bank_balance": {"balance": 842000, "account": "HBL Business — **4471"},
        "invoices": [
            {"id": "INV-2026-0041", "client": "CloudNeurix", "description": "AI Dashboard Dev",
             "amount": 350000, "status": "paid", "issue_date": "2026-01-28", "due_date": "2026-02-12", "paid_date": "2026-02-10"},
            {"id": "INV-2026-0042", "client": "FoodPanda Partner", "description": "Mobile UI/UX",
             "amount": 220000, "status": "paid", "issue_date": "2026-02-01", "due_date": "2026-02-15", "paid_date": "2026-02-14"},
            {"id": "INV-2026-0043", "client": "Tech Starter PK", "description": "SaaS Consultation",
             "amount": 150000, "status": "overdue", "issue_date": "2026-02-03", "due_date": "2026-02-13", "paid_date": None},
            {"id": "INV-2026-0044", "client": "Elegant Couture", "description": "E-Commerce Dev",
             "amount": 480000, "status": "pending", "issue_date": "2026-02-10", "due_date": "2026-02-28", "paid_date": None},
        ],
        "expenses": [
            {"id": "EXP-001", "description": "Cloud Hosting (AWS)", "amount": 45000, "category": "Infrastructure", "date": "2026-02-01"},
            {"id": "EXP-002", "description": "Freelance Designer", "amount": 35000, "category": "Contractors", "date": "2026-02-05"},
            {"id": "EXP-003", "description": "Software Licenses", "amount": 18500, "category": "Software", "date": "2026-02-08"},
            {"id": "EXP-004", "description": "Office Internet (Fiber)", "amount": 6500, "category": "Utilities", "date": "2026-02-01"},
            {"id": "EXP-005", "description": "Marketing & Ads", "amount": 22000, "category": "Marketing", "date": "2026-02-12"},
        ],
    }


def load_accounting():
    if ACCOUNTING_FILE.exists():
        try:
            with open(ACCOUNTING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Validate it has the keys we need; fall back to mock if not
            if "invoices" in data and "expenses" in data:
                return data
        except Exception:
            pass
    return _mock_accounting()


def parse_email_file(filepath):
    text = filepath.read_text(encoding="utf-8")
    subject = re.search(r"^#\s*Email:\s*(.+)", text, re.MULTILINE)
    sender = re.search(r"\*\*From:\*\*\s*(.+)", text)
    date = re.search(r"\*\*Date:\*\*\s*(.+)", text)
    status = re.search(r"\*\*Status:\*\*\s*(.+)", text)
    summary = re.search(r"## Summary\n(.+)", text)
    return {
        "Subject": subject.group(1).strip() if subject else filepath.stem,
        "From": sender.group(1).strip() if sender else "Unknown",
        "Date": date.group(1).strip() if date else "",
        "Status": status.group(1).strip() if status else "Unknown",
        "Summary": summary.group(1).strip()[:120] + "..." if summary else "",
    }


def load_emails():
    emails = []
    if READINGS_DIR.exists():
        for f in sorted(READINGS_DIR.glob("EMAIL_*.md")):
            emails.append(parse_email_file(f))
    return pd.DataFrame(emails)


def parse_inbox_intelligence(briefing_text):
    rows = []
    pattern = r"\|\s*\*\*(\w+)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|"
    for m in re.finditer(pattern, briefing_text):
        rows.append({
            "Priority": m.group(1),
            "Sender": m.group(2).strip(),
            "Subject": m.group(3).strip(),
            "Action Required": m.group(4).strip(),
        })
    return pd.DataFrame(rows)


def load_kanban_files(directory):
    items = []
    if not directory.exists():
        return items
    for f in sorted(directory.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        text = f.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s*(.+)", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f.stem
        tag = ""
        if f.name.startswith("AI_TASK"):
            tag = "ai"
        elif f.name.startswith("SOCIAL_TASK"):
            tag = "social"
        elif f.name.startswith("ACCT_TASK"):
            tag = "finance"
        items.append({"title": title, "file": f.name, "tag": tag})
    for sub in directory.iterdir():
        if sub.is_dir():
            for f in sorted(sub.glob("*.md")):
                if f.name == ".gitkeep":
                    continue
                text = f.read_text(encoding="utf-8")
                title_match = re.search(r"^#\s*(.+)", text, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else f.stem
                tag = "social" if f.name.startswith("SOCIAL") else ""
                items.append({"title": title, "file": f"{sub.name}/{f.name}", "tag": tag})
    return items


def load_plans():
    plans = []
    if not PLANS_DIR.exists():
        return plans
    for f in sorted(PLANS_DIR.glob("PLAN_*.md")):
        text = f.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s*Execution Plan:\s*(.+)", text, re.MULTILINE)
        sender_match = re.search(r"\*\*Sender:\*\*\s*(.+)", text)
        status_match = re.search(r"\*\*Status:\*\*\s*(.+)", text)
        steps = re.findall(r"^\d+\.\s*(.+)", text, re.MULTILINE)
        plans.append({
            "title": title_match.group(1).strip() if title_match else f.stem,
            "sender": sender_match.group(1).strip() if sender_match else "",
            "status": status_match.group(1).strip() if status_match else "Not Started",
            "steps": steps[:5],
            "file": f.name,
        })
    return plans


def load_social_summary():
    path = READINGS_DIR / "Social_Summary.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def fmt_pkr(amount):
    return f"PKR {amount:,.0f}"


# ── Load all data ──
briefing_raw = load_briefing()
accounting = load_accounting()
df_emails = load_emails()
df_inbox = parse_inbox_intelligence(briefing_raw)

kanban_todo = load_kanban_files(NEEDS_ACTION_DIR)
kanban_doing = load_kanban_files(IN_PROGRESS_DIR)
kanban_done = load_kanban_files(DONE_DIR)
plans = load_plans()
social_summary = load_social_summary()

total_emails = len(df_emails)
unread_count = (df_emails["Status"].str.lower() == "unread").sum() if not df_emails.empty else 0
high_priority = (df_inbox["Priority"] == "HIGH").sum() if not df_inbox.empty else 0

# load_accounting() always returns data (real JSON or inline mock)
invoices = accounting.get("invoices", [])
expenses = accounting.get("expenses", [])
total_invoiced = sum(i["amount"] for i in invoices)
collected = sum(i["amount"] for i in invoices if i["status"] == "paid")
total_expenses = sum(e["amount"] for e in expenses)
net_profit = collected - total_expenses
bank_balance = accounting.get("bank_balance", {}).get("balance", 0)
overdue_count = sum(1 for i in invoices if i["status"] == "overdue")
outstanding = sum(i["amount"] for i in invoices if i["status"] in ("pending", "overdue"))
_data_source = "Live JSON" if ACCOUNTING_FILE.exists() else "Mock Data"

# ──────────────────────────────────────────────
# SIDEBAR — Minimalist
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sb-name">Tabraiz Haider</p>', unsafe_allow_html=True)
    st.markdown('<p class="sb-role">CEO Command</p>', unsafe_allow_html=True)
    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    st.markdown('<p class="sb-label">Status</p>', unsafe_allow_html=True)
    st.markdown(
        f'<span class="sb-badge sb-badge-live">LIVE</span> &nbsp; '
        f'<span class="sb-value" style="font-size:0.72rem;">{datetime.now().strftime("%b %d, %Y")}</span>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Background Watchers ──
    with st.expander("Background Watchers"):
        for watcher_name, watcher_script in WATCHERS.items():
            running = is_watcher_running(watcher_name)
            badge = '<span class="status-running">RUNNING</span>' if running else '<span class="status-stopped">STOPPED</span>'
            st.markdown(f'<span class="sb-value" style="font-size:0.76rem;">{watcher_name}</span> {badge}', unsafe_allow_html=True)
            w_col1, w_col2 = st.columns(2)
            with w_col1:
                if st.button("Start", key=f"start_{watcher_name}", disabled=running, use_container_width=True):
                    start_watcher(watcher_name, watcher_script)
                    st.toast(f"{watcher_name} started", icon="\u2705")
                    st.rerun()
            with w_col2:
                if st.button("Stop", key=f"stop_{watcher_name}", disabled=not running, use_container_width=True):
                    stop_watcher(watcher_name)
                    st.toast(f"{watcher_name} stopped", icon="\u26d4")
                    st.rerun()

        st.markdown("---")
        sa_col1, sa_col2 = st.columns(2)
        with sa_col1:
            if st.button("Start All", key="start_all_watchers", use_container_width=True):
                for wn, ws in WATCHERS.items():
                    if not is_watcher_running(wn):
                        start_watcher(wn, ws)
                st.toast("All watchers started", icon="\u2705")
                st.rerun()
        with sa_col2:
            if st.button("Stop All", key="stop_all_watchers", use_container_width=True):
                for wn in WATCHERS:
                    if is_watcher_running(wn):
                        stop_watcher(wn)
                st.toast("All watchers stopped", icon="\u26d4")
                st.rerun()

    # ── Quick Actions ──
    with st.expander("Quick Actions"):
        autopilot = st.toggle("Autonomous Posting Mode", value=False, key="autopilot_toggle")
        if autopilot:
            st.markdown('<span class="sb-badge sb-badge-on">AUTO-PILOT ON</span>', unsafe_allow_html=True)
            st.caption("LinkedIn Agent runs every 24h")
            # Only spawn the thread once per session — guard with a thread object stored in state
            if st.session_state.get("autopilot_thread") is None or \
               not st.session_state["autopilot_thread"].is_alive():

                def autopilot_loop():
                    # Sleep first — don't run immediately on toggle-on,
                    # wait a full 24h cycle before the first auto-post.
                    time.sleep(86400)
                    while st.session_state.get("autopilot_toggle", False):
                        try:
                            _safe_run(
                                [_PY, str(BASE_DIR / "linkedin_agent.py")],
                                timeout=120,
                            )
                            st.session_state["autopilot_last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        except Exception:
                            pass
                        time.sleep(86400)

                _t = threading.Thread(target=autopilot_loop, daemon=True, name="autopilot_loop")
                _t.start()
                st.session_state["autopilot_thread"] = _t

            if st.session_state.get("autopilot_last_run"):
                st.caption(f"Last run: {st.session_state['autopilot_last_run']}")
            else:
                st.caption("First run in 24h")
        else:
            st.markdown('<span class="sb-badge sb-badge-off">OFF</span>', unsafe_allow_html=True)
            # Don't delete the thread object — let the daemon die naturally
            # (the while-loop checks autopilot_toggle which is now False)
            st.session_state.pop("autopilot_thread", None)

        st.markdown("---")

        if st.button("Execute All Approved", key="execute_approved_btn", use_container_width=True):
            with st.spinner("Running LinkedIn poster and WhatsApp sender..."):
                errors = []
                try:
                    rc, out = _safe_run(
                        [_PY, str(BASE_DIR / "linkedin_poster.py")],
                        timeout=120,
                    )
                    if rc == 0:
                        st.success("LinkedIn: Post submitted")
                    else:
                        errors.append(f"LinkedIn: {out[-300:] if out else 'Unknown error'}")
                except subprocess.TimeoutExpired:
                    errors.append("LinkedIn: Timed out after 120s")
                except Exception as e:
                    errors.append(f"LinkedIn: {e}")
                try:
                    rc, out = _safe_run(
                        [_PY, str(BASE_DIR / "whatsapp_sender.py")],
                        timeout=120,
                    )
                    if rc == 0:
                        st.success("WhatsApp: Messages sent")
                    else:
                        errors.append(f"WhatsApp: {out[-300:] if out else 'Unknown error'}")
                except subprocess.TimeoutExpired:
                    errors.append("WhatsApp: Timed out after 120s")
                except Exception as e:
                    errors.append(f"WhatsApp: {e}")
                for err in errors:
                    st.error(err)
            st.toast("Execute All Approved completed", icon="\u2705")

        if st.button("Run Full Audit", key="run_audit_btn", use_container_width=True):
            with st.status("Running Odoo Audit...", expanded=True) as status:
                st.write("Connecting to Odoo bridge...")
                try:
                    rc, out = _safe_run(
                        [_PY, str(BASE_DIR / "odoo_mcp_bridge.py")],
                        timeout=180,
                    )
                    st.write("Generating audit report...")
                    if rc == 0:
                        st.write(out[-500:] if len(out) > 500 else (out or "Done."))
                        status.update(label="Audit complete!", state="complete")
                    else:
                        st.write(out[-300:] if out else "Unknown error")
                        status.update(label="Audit failed", state="error")
                except subprocess.TimeoutExpired:
                    status.update(label="Audit timed out", state="error")
                except Exception as e:
                    st.write(str(e))
                    status.update(label="Audit failed", state="error")
            st.toast("Full audit completed", icon="\u2705")

        if st.button("System Health Check", key="health_check_btn", use_container_width=True):
            with st.status("Running Health Check...", expanded=True) as status:
                st.write("Checking scripts...")
                all_scripts = list(WATCHERS.values()) + [
                    "linkedin_poster.py", "whatsapp_sender.py",
                    "linkedin_agent.py", "vault_sync.py",
                ]
                missing = []
                for s in all_scripts:
                    full = BASE_DIR / s
                    if full.exists():
                        st.write(f"  \u2705 {s}")
                    else:
                        st.write(f"  \u274c {s} — MISSING")
                        missing.append(s)

                st.write("Checking watchers...")
                for wn in WATCHERS:
                    r = is_watcher_running(wn)
                    icon = "\u2705" if r else "\u26aa"
                    st.write(f"  {icon} {wn}: {'Running' if r else 'Stopped'}")

                st.write("Checking git status...")
                try:
                    rc_g, git_out = _safe_run(
                        ["git", "status", "--short"],
                        timeout=10,
                    )
                    changes = git_out.strip()
                    if changes:
                        st.write(f"  {len(changes.splitlines())} uncommitted change(s)")
                    else:
                        st.write("  Working tree clean")
                except Exception:
                    st.write("  Could not check git status")

                if missing:
                    status.update(label=f"Health check: {len(missing)} script(s) missing", state="error")
                else:
                    status.update(label="Health check complete!", state="complete")
            st.toast("Health check completed", icon="\u2705")

        if st.button("Sync Vault", key="sync_vault_btn", use_container_width=True):
            with st.spinner("Syncing vault..."):
                try:
                    rc, out = _safe_run(
                        [_PY, str(BASE_DIR / "vault_sync.py"), "sync"],
                        timeout=60,
                    )
                    if rc == 0:
                        st.success("Vault synced")
                    else:
                        st.error(out[-300:] if out else "Sync failed")
                except Exception as e:
                    st.error(f"Sync error: {e}")
            st.toast("Vault sync completed", icon="\u2705")

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown(
        f'<p class="sb-footer">Auto-refresh 30s &middot; {datetime.now().strftime("%H:%M:%S")}</p>',
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# STICKY HEADER — Thin, clean
# ──────────────────────────────────────────────
st.markdown(
    f"""<div class="sticky-header">
        <h1>Tabraiz Haider &nbsp;|&nbsp; CEO Command</h1>
        <div class="subtitle">{datetime.now().strftime('%A, %B %d, %Y')} &middot; AI Employee Vault</div>
    </div>""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# FINANCIAL ROW — Slim cards
# ──────────────────────────────────────────────
profit_class = "green" if net_profit > 0 else "amber"
st.markdown(f"""
<div class="fin-row">
    <div class="fin-item">
        <div class="fin-value {profit_class}">{fmt_pkr(net_profit)}</div>
        <div class="fin-label">Net Profit</div>
    </div>
    <div class="fin-item">
        <div class="fin-value amber">{fmt_pkr(outstanding)}</div>
        <div class="fin-label">Outstanding</div>
    </div>
    <div class="fin-item">
        <div class="fin-value blue">{fmt_pkr(bank_balance)}</div>
        <div class="fin-label">Bank Balance</div>
    </div>
    <div class="fin-item">
        <div class="fin-value">{fmt_pkr(collected)}</div>
        <div class="fin-label">Collected</div>
    </div>
    <div class="fin-item">
        <div class="fin-value">{fmt_pkr(total_expenses)}</div>
        <div class="fin-label">Expenses</div>
    </div>
</div>
""", unsafe_allow_html=True)
_src_color = "#3FB950" if _data_source == "Live JSON" else "#F0883E"
st.markdown(
    f'<p style="color:{_src_color};font-size:0.62rem;text-align:right;margin:-6px 0 4px;'
    f'letter-spacing:0.04em;">&#9679; Accounting: {_data_source} &middot; '
    f'Last sync: {accounting.get("last_synced","—")[:16]}</p>',
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# OPERATIONAL METRICS
# ──────────────────────────────────────────────
o1, o2, o3, o4, o5 = st.columns(5)
o1.metric("Emails", total_emails)
o2.metric("Unread", unread_count)
o3.metric("High Priority", high_priority,
          delta="Attention" if high_priority > 0 else "Clear",
          delta_color="inverse" if high_priority > 0 else "normal")
o4.metric("To Do", len(kanban_todo))
o5.metric("In Progress", len(kanban_doing))

# ──────────────────────────────────────────────
# AGENT CONSOLE — Live Logs
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">Agent Console</div>', unsafe_allow_html=True)
with st.expander("Live Agent Logs", expanded=False):
    if LOG_FILE.exists():
        try:
            log_lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
            last_50 = log_lines[-50:] if len(log_lines) > 50 else log_lines
            log_content = "\n".join(last_50)
        except Exception:
            log_content = "Error reading log file."
    else:
        log_content = "No log entries yet. Start a watcher to generate logs."
    st.markdown(f'<div class="console-log">{log_content}</div>', unsafe_allow_html=True)
    if st.button("Clear Logs", key="clear_logs_btn"):
        try:
            LOG_FILE.write_text("", encoding="utf-8")
            st.toast("Logs cleared", icon="\U0001f9f9")
            st.rerun()
        except Exception as e:
            st.error(f"Could not clear logs: {e}")

# ──────────────────────────────────────────────
# KANBAN BOARD
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">Task Board</div>', unsafe_allow_html=True)

col_todo, col_doing, col_done = st.columns(3)

TAG_HTML = {
    "ai": '<span class="tag tag-ai">AI</span>',
    "social": '<span class="tag tag-social">SOCIAL</span>',
    "finance": '<span class="tag tag-finance">FINANCE</span>',
}


def render_kanban(col, dot_class, label, count, items):
    with col:
        st.markdown(
            f'<div class="kanban-col-header">'
            f'<span class="dot {dot_class}"></span>{label}'
            f'<span class="count">{count}</span></div>',
            unsafe_allow_html=True,
        )
        html = ""
        if items:
            for item in items:
                tag = TAG_HTML.get(item["tag"], "")
                html += (
                    f'<div class="kanban-card">'
                    f'<div class="kanban-card-title">{tag}{item["title"]}</div>'
                    f'<div class="kanban-card-meta">{item["file"]}</div>'
                    f'</div>'
                )
        else:
            html = '<p style="color:#484F58; font-size:0.75rem; text-align:center; padding:24px 0;">No items</p>'
        st.markdown(f'<div class="kanban-body">{html}</div>', unsafe_allow_html=True)


render_kanban(col_todo, "dot-todo", "Needs Action", len(kanban_todo), kanban_todo)
render_kanban(col_doing, "dot-doing", "In Progress", len(kanban_doing), kanban_doing)
render_kanban(col_done, "dot-done", "Done", len(kanban_done), kanban_done)

# ──────────────────────────────────────────────
# UNIFIED COMMUNICATION HUB
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">Communications</div>', unsafe_allow_html=True)

# ── Channel Status Row ──
ch_li, ch_wa = st.columns(2)

# Count approved items for each channel
_approved_li = [f for f in APPROVED_DIR.glob("LinkedIn_Post*.md")] if APPROVED_DIR.exists() else []
_approved_wa = [f for f in APPROVED_DIR.glob("WA_*.md")
                if f.name != ".gitkeep"] if APPROVED_DIR.exists() else []

with ch_li:
    st.markdown(
        f'<div class="channel-card">'
        f'<div class="channel-card-header">'
        f'<span class="channel-icon">&#x1F4BC;</span>'
        f'<span class="channel-title">LinkedIn</span>'
        f'<span class="channel-status channel-status-ready">READY</span>'
        f'</div>'
        f'<div class="channel-stat">Approved posts: <strong>{len(_approved_li)}</strong></div>'
        f'<div class="channel-stat">Drafts: <strong>{len([f for f in DRAFTS_DIR.glob("LinkedIn*.md")] if DRAFTS_DIR.exists() else [])}</strong></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.button("▶ Run LinkedIn Poster", key="run_li_poster_btn", use_container_width=True):
        with st.status("Running LinkedIn Poster...", expanded=True) as _li_st:
            st.write("Launching isolated process...")
            try:
                _rc, _out = _safe_run(
                    [_PY, str(BASE_DIR / "linkedin_poster.py")],
                    timeout=150,
                )
                if _rc == 0:
                    st.write(_out[-400:] if len(_out) > 400 else (_out or "Done."))
                    _li_st.update(label="LinkedIn post sent!", state="complete")
                    st.toast("LinkedIn post published!", icon="\U0001f4bc")
                else:
                    st.write(_out[-300:] if _out else "Unknown error")
                    _li_st.update(label="LinkedIn poster failed", state="error")
            except subprocess.TimeoutExpired:
                _li_st.update(label="Timed out after 150s", state="error")
            except Exception as _e:
                st.write(str(_e))
                _li_st.update(label="Failed", state="error")

with ch_wa:
    # Check whatsapp_sender.py exists as proxy for "Ready"
    _wa_ready = (BASE_DIR / "whatsapp_sender.py").exists()
    _wa_status_cls = "channel-status-ready" if _wa_ready else "channel-status-idle"
    _wa_status_txt = "READY" if _wa_ready else "NOT FOUND"
    st.markdown(
        f'<div class="channel-card">'
        f'<div class="channel-card-header">'
        f'<span class="channel-icon">&#x1F4F1;</span>'
        f'<span class="channel-title">WhatsApp</span>'
        f'<span class="channel-status {_wa_status_cls}">{_wa_status_txt}</span>'
        f'</div>'
        f'<div class="channel-stat">Queued messages: <strong>{len(_approved_wa)}</strong></div>'
        f'<div class="channel-stat">Bridge: <strong>{"&#x2705; whatsapp_sender.py" if _wa_ready else "&#x274c; missing"}</strong></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.button("▶ Run WhatsApp Sender", key="run_wa_sender_btn",
                 use_container_width=True, disabled=not _wa_ready):
        with st.status("Running WhatsApp Sender...", expanded=True) as _wa_st:
            st.write("Launching isolated process (opens WhatsApp Web)...")
            try:
                _rc, _out = _safe_run(
                    [_PY, str(BASE_DIR / "whatsapp_sender.py")],
                    timeout=600,
                )
                if _rc == 0:
                    st.write(_out[-400:] if len(_out) > 400 else (_out or "Done."))
                    _wa_st.update(label="WhatsApp messages sent!", state="complete")
                    st.toast("WhatsApp messages sent!", icon="\U0001f4f1")
                else:
                    st.write(_out[-300:] if _out else "Unknown error")
                    _wa_st.update(label="WhatsApp sender failed", state="error")
            except subprocess.TimeoutExpired:
                _wa_st.update(label="Timed out after 10 min", state="error")
            except Exception as _e:
                st.write(str(_e))
                _wa_st.update(label="Failed", state="error")

st.markdown("<br>", unsafe_allow_html=True)

# ── Three-column layout: Inbox | WhatsApp Tasks | Social ──
hub_inbox, hub_wa, hub_social = st.columns(3)

with hub_inbox:
    st.markdown("**📧 Inbox**")
    if not df_inbox.empty:
        for _, row in df_inbox.iterrows():
            p = row["Priority"]
            p_class = {"HIGH": "pri-high", "MEDIUM": "pri-medium", "LOW": "pri-low"}.get(p, "pri-low")
            st.markdown(
                f'<div class="card">'
                f'<div><span class="pri {p_class}">{p}</span>'
                f'<span class="card-meta">{row["Sender"]}</span></div>'
                f'<div class="card-title">{row["Subject"]}</div>'
                f'<div class="card-body">{row["Action Required"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No inbox data.")

with hub_wa:
    st.markdown("**💬 WhatsApp Tasks**")
    # Scan Needs_Action for WhatsApp/messaging tasks
    _wa_tasks = []
    if NEEDS_ACTION_DIR.exists():
        for _f in sorted(NEEDS_ACTION_DIR.glob("*.md")):
            if _f.name == ".gitkeep":
                continue
            _txt = _f.read_text(encoding="utf-8", errors="replace")
            _pri_m = re.search(r"\*\*Priority:\*\*\s*(.+)", _txt)
            _src_m = re.search(r"\*\*Sender:\*\*\s*(.+)", _txt)
            _stat_m = re.search(r"\*\*Status:\*\*\s*(.+)", _txt)
            _title_m = re.search(r"^#\s*(?:AI Task:|ACCT Task:)?\s*(.+)", _txt, re.MULTILINE)
            _wa_tasks.append({
                "title": _title_m.group(1).strip() if _title_m else _f.stem,
                "priority": _pri_m.group(1).strip() if _pri_m else "—",
                "sender": _src_m.group(1).strip() if _src_m else "—",
                "status": _stat_m.group(1).strip() if _stat_m else "Pending",
                "file": _f,
            })

    if _wa_tasks:
        for _t in _wa_tasks:
            _p_color = {"HIGH": "#F85149", "MEDIUM": "#F0883E", "LOW": "#3FB950"}.get(_t["priority"], "#6E7681")
            st.markdown(
                f'<div class="wa-task">'
                f'<div class="wa-task-title">{_t["title"]}</div>'
                f'<div class="wa-task-meta">'
                f'<span style="color:{_p_color};">{_t["priority"]}</span> &middot; '
                f'{_t["sender"]} &middot; {_t["status"]}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No pending tasks.")

    # ── AI Reply Composer ──
    st.markdown("**Quick Reply**")
    _reply_contact = st.text_input(
        "Contact name or number",
        placeholder="e.g. Hamza Naeem or +92300...",
        key="wa_reply_contact",
        label_visibility="collapsed",
    )
    _reply_msg = st.text_area(
        "Message",
        placeholder="Type your WhatsApp reply here...",
        height=100,
        key="wa_reply_msg",
        label_visibility="collapsed",
    )
    if st.button("📤 Queue & Send Reply", key="wa_send_reply_btn", use_container_width=True,
                 disabled=not (_reply_contact.strip() and _reply_msg.strip())):
        # Write a message file to Approved/ that whatsapp_sender.py can pick up
        _ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        _msg_file = APPROVED_DIR / f"WA_Reply_{_ts}.md"
        _msg_content = (
            f"# WhatsApp Reply — {_reply_contact.strip()}\n\n"
            f"- **To:** {_reply_contact.strip()}\n"
            f"- **Sent:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"- **Status:** Pending\n\n"
            f"## Message\n\n{_reply_msg.strip()}\n\n"
            f"---\n*Queued via CEO Dashboard*\n"
        )
        _msg_file.write_text(_msg_content, encoding="utf-8")
        # Launch sender immediately in isolated process
        try:
            _safe_popen(
                [_PY, str(BASE_DIR / "whatsapp_sender.py")],
                cwd=str(BASE_DIR),
                detach=True,
            )
            st.success(f"WhatsApp reply queued and sender launched for {_reply_contact.strip()}")
            st.toast(f"Reply sent to {_reply_contact.strip()}", icon="\U0001f4f1")
        except Exception as _re:
            st.error(f"Message queued but sender failed to launch: {_re}")
        st.rerun()

with hub_social:
    st.markdown("**📊 Social**")
    if social_summary:
        msg_match = re.search(r"Total Messages \| (\d+)", social_summary)
        biz_match = re.search(r"Business Inquiries \| (\d+)", social_summary)
        notif_match = re.search(r"Notifications \| (\d+)", social_summary)
        st.markdown(
            f'<div class="card">'
            f'<div class="card-title"><span class="tag tag-social">SOCIAL</span>Activity Overview</div>'
            f'<div class="card-body">'
            f'Messages: <strong style="color:#C9D1D9;">{msg_match.group(1) if msg_match else "0"}</strong> &middot; '
            f'Inquiries: <strong style="color:#C9D1D9;">{biz_match.group(1) if biz_match else "0"}</strong> &middot; '
            f'Alerts: <strong style="color:#C9D1D9;">{notif_match.group(1) if notif_match else "0"}</strong>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        with st.expander("Full Social Summary"):
            st.markdown(social_summary)
    else:
        st.info("No social data yet.")

# ──────────────────────────────────────────────
# DRAFT MANAGEMENT
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">Draft Management</div>', unsafe_allow_html=True)
if DRAFTS_DIR.exists():
    draft_files = sorted(DRAFTS_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    draft_files = [f for f in draft_files if f.name != ".gitkeep"]
    if draft_files:
        # Summary row
        all_rows = []
        for f in draft_files:
            text = f.read_text(encoding="utf-8")
            brand_m = re.search(r"\*\*Brand:\*\*\s*(.+)", text)
            gen_m = re.search(r"\*\*Generated:\*\*\s*(.+)", text)
            stat_m = re.search(r"\*\*Status:\*\*\s*(.+)", text)
            all_rows.append({
                "brand": brand_m.group(1).strip() if brand_m else "\u2014",
                "generated": gen_m.group(1).strip() if gen_m else "\u2014",
                "status": stat_m.group(1).strip() if stat_m else "\u2014",
                "file": f.name,
                "path": f,
            })
        posted_count = sum(1 for r in all_rows if r["status"] == "Posted")
        draft_count = sum(1 for r in all_rows if r["status"] == "Draft")
        st.markdown(
            f'<div class="card"><div class="card-body">'
            f'Total: <strong style="color:#C9D1D9;">{len(all_rows)}</strong> &middot; '
            f'Posted: <strong style="color:#3FB950;">{posted_count}</strong> &middot; '
            f'Drafts: <strong style="color:#58A6FF;">{draft_count}</strong>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        # Check if we are editing a draft
        editing_draft = st.session_state.get("editing_draft", None)

        if editing_draft and Path(editing_draft).exists():
            # ── Editing mode ──
            edit_path = Path(editing_draft)
            st.markdown(f'**Editing:** `{edit_path.name}`')
            current_content = edit_path.read_text(encoding="utf-8")
            edited_text = st.text_area(
                "Draft Content",
                value=current_content,
                height=300,
                key="draft_editor_area",
                label_visibility="collapsed",
            )
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("Save", key="save_draft_btn", use_container_width=True):
                    edit_path.write_text(edited_text, encoding="utf-8")
                    st.toast("Draft saved", icon="\U0001f4be")
                    st.rerun()
            with btn_col2:
                if st.button("Save & Approve", key="save_approve_btn", use_container_width=True):
                    # Update status in content
                    approved_text = re.sub(
                        r"\*\*Status:\*\*\s*.+",
                        "**Status:** Approved",
                        edited_text,
                    )
                    edit_path.write_text(approved_text, encoding="utf-8")
                    # Move to Approved/
                    dest = APPROVED_DIR / edit_path.name
                    shutil.move(str(edit_path), str(dest))
                    st.session_state["editing_draft"] = None
                    st.toast("Draft approved and moved", icon="\u2705")
                    st.rerun()
            with btn_col3:
                if st.button("Cancel", key="cancel_edit_btn", use_container_width=True):
                    st.session_state["editing_draft"] = None
                    st.rerun()
        else:
            # Clear stale editing state
            if editing_draft:
                st.session_state["editing_draft"] = None

            # ── List mode ──
            for idx, row in enumerate(all_rows):
                stat_class = "draft-status-posted" if row["status"] == "Posted" else "draft-status-draft"
                st.markdown(
                    f'<div class="draft-card">'
                    f'<span class="draft-status {stat_class}">{row["status"]}</span> '
                    f'<span class="draft-title">{row["brand"]}</span>'
                    f'<div class="draft-meta">{row["file"]} &middot; {row["generated"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button("Edit", key=f"edit_draft_{idx}", use_container_width=False):
                    st.session_state["editing_draft"] = str(row["path"])
                    st.rerun()
    else:
        st.info("No drafts found.")
else:
    st.info("Drafts folder not found.")

# Approved drafts summary
if APPROVED_DIR.exists():
    approved_files = [f for f in sorted(APPROVED_DIR.glob("*.md")) if f.name != ".gitkeep"]
    if approved_files:
        with st.expander(f"Approved Drafts ({len(approved_files)})"):
            for af in approved_files:
                st.markdown(f'<div class="card"><div class="card-title">{af.name}</div></div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# AI POST CREATOR
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">AI Post Creator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ai-creator-wrap">'
    '<div class="ai-creator-title"><span class="ai-badge">&#9889; AI</span>&nbsp; LinkedIn Post Generator</div>'
    '<div class="ai-creator-sub">Type a 1-line prompt — get a publish-ready LinkedIn post instantly.</div>'
    '</div>',
    unsafe_allow_html=True,
)

# Prompt input row
ai_col1, ai_col2 = st.columns([2, 5])
with ai_col1:
    ai_brand = st.selectbox(
        "Brand",
        options=["multicraft_agency"],
        format_func=lambda k: "Multicraft Agency",
        key="ai_brand_select",
        label_visibility="collapsed",
    )
with ai_col2:
    ai_prompt = st.text_input(
        "Post prompt",
        placeholder="e.g.  We just launched an AI dashboard for a fintech client",
        key="ai_post_prompt",
        label_visibility="collapsed",
    )

gen_col, pub_col, clr_col = st.columns([2, 2, 1])

with gen_col:
    generate_clicked = st.button(
        "✦ Generate Draft",
        key="ai_generate_btn",
        use_container_width=True,
        type="primary",
    )
with pub_col:
    publish_clicked = st.button(
        "⚡ Publish Now",
        key="ai_publish_btn",
        use_container_width=True,
        disabled="ai_generated_content" not in st.session_state,
    )
with clr_col:
    if st.button("Clear", key="ai_clear_btn", use_container_width=True):
        for k in ["ai_generated_content", "ai_saved_path"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── Generate ──
if generate_clicked:
    topic = ai_prompt.strip() if ai_prompt.strip() else None
    # Import generate_post directly — no subprocess, instant, no dashboard freeze
    try:
        import importlib.util
        _spec = importlib.util.spec_from_file_location(
            "linkedin_agent", str(BASE_DIR / "linkedin_agent.py")
        )
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        content = _mod.generate_post(ai_brand, topic)
        saved_path = _mod.save_draft(content, ai_brand)
        st.session_state["ai_generated_content"] = content
        st.session_state["ai_saved_path"] = str(saved_path)
        st.toast(f"Draft generated: {saved_path.name}", icon="\u2728")
    except Exception as e:
        st.error(f"Generation failed: {e}")

# ── Preview & Edit ──
if "ai_generated_content" in st.session_state:
    st.markdown("**Preview & Edit**")

    # Extract just the post body (strip the markdown metadata header for display)
    _raw = st.session_state["ai_generated_content"]
    # Find the first --- separator (after the metadata block) and show from there
    _body_match = re.search(r"---\n\n(.+)", _raw, re.DOTALL)
    _display = _body_match.group(1).strip() if _body_match else _raw

    edited_post = st.text_area(
        "Edit your post",
        value=_display,
        height=260,
        key="ai_editor_area",
        label_visibility="collapsed",
        help="Edit freely — click Save Draft or Publish Now when ready.",
    )

    save_edit_col, _ = st.columns([2, 5])
    with save_edit_col:
        if st.button("Save Edits to Draft", key="ai_save_edit_btn", use_container_width=True):
            # Rebuild the full file content with the edited body
            _header = _raw.split("---")[0] + "---\n\n"
            _footer = "\n\n---\n\n> Auto-generated by LinkedIn Agent — AI Employee Vault\n> Review and personalize before posting.\n"
            _updated = _header + edited_post.strip() + _footer
            _path = Path(st.session_state["ai_saved_path"])
            if _path.exists():
                _path.write_text(_updated, encoding="utf-8")
                st.session_state["ai_generated_content"] = _updated
                st.toast("Draft saved", icon="\U0001f4be")
            else:
                st.warning("Draft file not found — may have been moved.")

    if "ai_saved_path" in st.session_state:
        st.caption(f"Saved to: `{Path(st.session_state['ai_saved_path']).name}`")

# ── Publish Now ──
if publish_clicked and "ai_generated_content" in st.session_state:
    # First write the current editor content back to the draft file
    _raw2 = st.session_state["ai_generated_content"]
    _path2 = Path(st.session_state.get("ai_saved_path", ""))
    if _path2.exists():
        # Merge any in-editor edits if the text_area value differs
        _area_val = st.session_state.get("ai_editor_area", "")
        if _area_val:
            _header2 = _raw2.split("---")[0] + "---\n\n"
            _footer2 = "\n\n---\n\n> Auto-generated by LinkedIn Agent — AI Employee Vault\n> Review and personalize before posting.\n"
            _path2.write_text(_header2 + _area_val.strip() + _footer2, encoding="utf-8")
        # Move to Approved so linkedin_poster.py picks it up
        _approved_dest = APPROVED_DIR / _path2.name
        shutil.copy2(str(_path2), str(_approved_dest))

    # Launch poster via _safe_run (temp-file output, no WinError 87)
    with st.status("Publishing to LinkedIn...", expanded=True) as _pub_status:
        st.write("Launching LinkedIn poster (isolated process)...")
        try:
            _rc, _out = _safe_run(
                [_PY, str(BASE_DIR / "linkedin_poster.py")],
                timeout=150,
            )
            if _rc == 0:
                st.write("Post submitted to LinkedIn.")
                _pub_status.update(label="Published!", state="complete")
                st.toast("Post published to LinkedIn!", icon="\U0001f680")
                for k in ["ai_generated_content", "ai_saved_path"]:
                    st.session_state.pop(k, None)
            else:
                st.write(f"Error: {_out[-300:] if _out else 'Unknown error'}")
                _pub_status.update(label="Publish failed", state="error")
        except subprocess.TimeoutExpired:
            _pub_status.update(label="Timed out after 150s", state="error")
            st.warning("LinkedIn poster timed out. Check logs.")
        except Exception as _e:
            st.write(str(_e))
            _pub_status.update(label="Publish failed", state="error")

# ──────────────────────────────────────────────
# CHARTS
# ──────────────────────────────────────────────
chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown('<div class="section-header">Email Distribution</div>', unsafe_allow_html=True)
    if not df_inbox.empty:
        sender_counts = df_inbox["Sender"].value_counts().reset_index()
        sender_counts.columns = ["Sender", "Count"]
        fig_pie = px.pie(
            sender_counts, names="Sender", values="Count", hole=0.5,
            color_discrete_sequence=["#6E7681", "#8B949E", "#A78BFA", "#58A6FF", "#3FB950"],
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#8B949E", font_size=11,
            legend=dict(font=dict(size=10)),
            margin=dict(t=10, b=10, l=10, r=10), height=300,
        )
        fig_pie.update_traces(
            textinfo="label+percent", textfont_size=10,
            marker=dict(line=dict(color="#0D1117", width=1.5)),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No email data.")

with chart_right:
    st.markdown('<div class="section-header">Expense Breakdown</div>', unsafe_allow_html=True)
    if expenses:
        by_cat = {}
        for e in expenses:
            by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]
        cat_df = pd.DataFrame(list(by_cat.items()), columns=["Category", "Amount"])
        cat_df = cat_df.sort_values("Amount", ascending=True)
        fig_exp = px.bar(
            cat_df, x="Amount", y="Category", orientation="h", text="Amount",
            color_discrete_sequence=["#8B949E"],
        )
        fig_exp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#8B949E", font_size=11, showlegend=False,
            xaxis=dict(showgrid=True, gridcolor="#1C2028"),
            yaxis=dict(showgrid=False),
            margin=dict(t=10, b=10, l=10, r=10), height=300,
        )
        fig_exp.update_traces(
            texttemplate="PKR %{x:,.0f}", textposition="outside",
            marker_line_color="#0D1117", marker_line_width=1,
        )
        st.plotly_chart(fig_exp, use_container_width=True)
    else:
        st.info("No accounting data.")

# ──────────────────────────────────────────────
# AI STRATEGY
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">AI Strategy</div>', unsafe_allow_html=True)
if plans:
    for p in plans:
        steps_html = "".join(f'<div class="plan-step">{i+1}. {s}</div>' for i, s in enumerate(p["steps"]))
        st.markdown(
            f'<div class="card">'
            f'<div class="card-title"><span class="tag tag-plan">PLAN</span>{p["title"]}</div>'
            f'<div class="card-meta">{p["sender"]} &middot; {p["status"]} &middot; {p["file"]}</div>'
            f'<div style="margin-top:6px;">{steps_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("No execution plans. Run agent_brain.py to generate.")

# ──────────────────────────────────────────────
# ODOO QUICK COMMAND
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">Odoo Command</div>', unsafe_allow_html=True)
cmd_left, cmd_right = st.columns([5, 1])
with cmd_left:
    odoo_cmd = st.text_input(
        "Command Odoo Agent",
        placeholder="e.g. Generate invoice for CloudNeurix — PKR 150,000",
        key="odoo_command_input",
        label_visibility="collapsed",
    )
with cmd_right:
    send = st.button("Send", key="odoo_cmd_btn", use_container_width=True)
if send:
    if odoo_cmd.strip():
        cmd_file = COMMANDS_DIR / "odoo_cmd.md"
        cmd_content = (
            f"# Odoo Command\n\n"
            f"**Sent:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"**From:** CEO Dashboard\n\n"
            f"## Command\n\n{odoo_cmd.strip()}\n\n"
            f"---\n*Status: Pending*\n"
        )
        cmd_file.write_text(cmd_content, encoding="utf-8")
        st.success("Command saved.")
    else:
        st.warning("Enter a command first.")

# ──────────────────────────────────────────────
# CEO BRIEFING & AI RECOMMENDATION
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">Briefing</div>', unsafe_allow_html=True)
with st.expander("CEO Briefing — February 17, 2026"):
    st.markdown(briefing_raw)

rec_match = re.search(r"## AI Recommendation\n\n(.+?)(?:\n---|\Z)", briefing_raw, re.DOTALL)
if rec_match:
    st.info(rec_match.group(1).strip())

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown(
    '<p class="footer-text">'
    'Tabraiz Haider &middot; CEO Command &middot; AI Employee Vault &middot; GIAIC Hackathon 0'
    '</p>',
    unsafe_allow_html=True,
)
