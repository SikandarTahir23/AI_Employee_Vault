"""
Agent Brain — Autonomous Task Generator
Scans Readings/ emails and CEO_Briefing for HIGH priority items,
then creates actionable task files in Needs_Action/ and plans in Plans/.
"""

import re
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
READINGS_DIR = BASE_DIR / "Readings"
BRIEFING_FILE = BASE_DIR / "CEO_Briefing_Feb_17.md"
TASKS_DIR = BASE_DIR / "Needs_Action"
PLANS_DIR = BASE_DIR / "Plans"
POLL_INTERVAL = 300  # seconds (5 minutes)

# Suggested actions keyed by lowercase keyword found in subject/summary
ACTION_HINTS = {
    "connect": "Accept or decline the connection request promptly",
    "cart": "Complete the purchase or dismiss the cart before it expires",
    "ramadan": "Review the time-sensitive event and decide on participation today",
    "order": "Complete or cancel the pending order before expiry",
    "hiring": "Review job listings and apply to relevant positions",
    "updated our terms": "Read the updated terms of service for compliance",
    "test on real devices": "Set up a production build and run device testing",
    "welcome": "Complete the onboarding steps to get started",
}

# Step-by-step plans keyed by keyword
PLAN_TEMPLATES = {
    "connect": [
        "Open LinkedIn and navigate to the pending invitation",
        "Review the sender's profile (company, role, mutual connections)",
        "If aligned with business goals, accept and send a welcome message",
        "If not relevant, decline the invitation",
        "Log the decision in the vault for future reference",
    ],
    "cart": [
        "Open the GoDaddy email and click through to the cart",
        "Review the items in the cart (domain, hosting, etc.)",
        "Evaluate if the purchase aligns with current priorities and budget",
        "If yes, complete the checkout process",
        "If no, abandon the cart and dismiss the notification",
    ],
    "ramadan": [
        "Open the Binance email and review the Ramadan event details",
        "Check the event timeline (7-day campaign starting Feb 18)",
        "Assess potential rewards vs time commitment",
        "If participating, set daily reminders for event activities",
        "If skipping, archive the email and move on",
    ],
    "order": [
        "Open the email and review the pending order details",
        "Verify the items, pricing, and delivery timeline",
        "Complete payment if the order is still needed",
        "Cancel the order if it is no longer relevant",
    ],
}


def get_action_hint(subject, summary):
    """Return a suggested action based on keywords in subject/summary."""
    text = f"{subject} {summary}".lower()
    for keyword, action in ACTION_HINTS.items():
        if keyword in text:
            return action
    return "Review this item immediately and take appropriate action"


def parse_briefing_priorities():
    """Extract HIGH priority rows from the CEO Briefing Inbox Intelligence table."""
    high_items = []
    if not BRIEFING_FILE.exists():
        return high_items

    content = BRIEFING_FILE.read_text(encoding="utf-8")
    pattern = r"\|\s*\*\*(\w+)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|"
    for m in re.finditer(pattern, content):
        priority = m.group(1).strip().upper()
        if priority == "HIGH":
            high_items.append({
                "priority": priority,
                "sender": m.group(2).strip(),
                "subject": m.group(3).strip(),
                "action": m.group(4).strip(),
            })
    return high_items


def parse_email_files():
    """Parse all email markdown files in Readings/ and return a lookup by subject."""
    emails = {}
    if not READINGS_DIR.exists():
        return emails

    for f in READINGS_DIR.glob("EMAIL_*.md"):
        text = f.read_text(encoding="utf-8")
        subject_match = re.search(r"^#\s*Email:\s*(.+)", text, re.MULTILINE)
        sender_match = re.search(r"\*\*From:\*\*\s*(.+)", text)
        date_match = re.search(r"\*\*Date:\*\*\s*(.+)", text)
        summary_match = re.search(r"## Summary\n(.+)", text)

        subject = subject_match.group(1).strip() if subject_match else f.stem
        emails[subject.lower()] = {
            "subject": subject,
            "from": sender_match.group(1).strip() if sender_match else "Unknown",
            "date": date_match.group(1).strip() if date_match else "",
            "summary": summary_match.group(1).strip() if summary_match else "",
            "file": f.name,
        }
    return emails


def sanitize_filename(name):
    """Remove characters that are invalid in filenames."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip().replace(' ', '_')[:80]


def create_task_file(item, email_detail):
    """Create a task markdown file in Task/ for a high-priority item."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(item["subject"])
    filename = f"AI_TASK_{safe_name}.md"
    filepath = TASKS_DIR / filename

    if filepath.exists():
        return None  # already created

    summary = email_detail.get("summary", "") if email_detail else ""
    action_hint = get_action_hint(item["subject"], summary)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    content = f"""# AI Task: {item['subject']}

- **Priority:** HIGH
- **Sender:** {item['sender']}
- **Detected:** {now}
- **Source Email:** {email_detail.get('file', 'N/A') if email_detail else 'CEO Briefing'}
- **Status:** Pending

---

AI has detected this as urgent. Suggested action: {action_hint}

---

**Original Action from Briefing:** {item['action']}

> Auto-generated by Agent Brain — AI Employee Vault
"""

    filepath.write_text(content, encoding="utf-8")
    return filename


def get_plan_steps(subject):
    """Return a list of plan steps based on subject keywords."""
    text = subject.lower()
    for keyword, steps in PLAN_TEMPLATES.items():
        if keyword in text:
            return steps
    return [
        "Review the original email and understand the full context",
        "Identify the key decision or action required",
        "Gather any additional information needed",
        "Execute the action or delegate appropriately",
        "Confirm completion and update the task status",
    ]


def create_plan_file(item, email_detail):
    """Create a plan markdown file in Plans/ for a high-priority item."""
    PLANS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(item["subject"])
    filename = f"PLAN_{safe_name}.md"
    filepath = PLANS_DIR / filename

    if filepath.exists():
        return None

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = email_detail.get("summary", "") if email_detail else ""
    action_hint = get_action_hint(item["subject"], summary)
    steps = get_plan_steps(item["subject"])
    steps_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))

    content = f"""# Execution Plan: {item['subject']}

- **Priority:** HIGH
- **Sender:** {item['sender']}
- **Created:** {now}
- **Related Task:** AI_TASK_{safe_name}.md
- **Status:** Not Started

---

## Objective

{action_hint}

## Context

- **Original Briefing Action:** {item['action']}
- **Email Summary:** {summary if summary else 'N/A'}

---

## Step-by-Step Plan

{steps_md}

---

## Success Criteria

- [ ] Action has been completed or a clear decision has been made
- [ ] Task file status updated to Done
- [ ] No follow-up items remaining

---

> Auto-generated by Agent Brain — AI Employee Vault
"""

    filepath.write_text(content, encoding="utf-8")
    return filename


def run_scan():
    """Run a single scan cycle."""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{now}] Scanning for HIGH priority items...")

    # Step 1: Get high-priority items from CEO Briefing
    high_items = parse_briefing_priorities()
    print(f"  [SCAN] Found {len(high_items)} HIGH priority items in CEO Briefing")

    if not high_items:
        print("  [OK] No new high-priority items to process.")
        return 0

    # Step 2: Load email details for cross-referencing
    email_lookup = parse_email_files()
    print(f"  [SCAN] Loaded {len(email_lookup)} emails from Readings/")

    # Step 3: Create task files + plan files
    created_tasks = []
    created_plans = []
    for item in high_items:
        email_detail = None
        subject_lower = item["subject"].lower()
        for key, val in email_lookup.items():
            if subject_lower in key or key in subject_lower:
                email_detail = val
                break

        task_result = create_task_file(item, email_detail)
        if task_result:
            created_tasks.append(task_result)
            print(f"  [TASK]  {task_result}")

        plan_result = create_plan_file(item, email_detail)
        if plan_result:
            created_plans.append(plan_result)
            print(f"  [PLAN]  {plan_result}")

    total = len(created_tasks) + len(created_plans)
    if total == 0:
        print("  [OK] All tasks & plans already exist. Nothing new.")
    else:
        print(f"  [DONE] Tasks: {len(created_tasks)} | Plans: {len(created_plans)}")

    return total


def main():
    print("=" * 50)
    print("  Agent Brain — Autonomous Task Generator")
    print("=" * 50)
    print(f"  Vault:    {BASE_DIR}")
    print(f"  Tasks:    {TASKS_DIR}")
    print()

    # Single-run mode
    if "--once" in sys.argv:
        run_scan()
        print("\nDone (single run).")
        return

    # Continuous loop mode
    print(f"[LOOP] Scanning every {POLL_INTERVAL}s (5 min). Press Ctrl+C to stop.\n")
    while True:
        try:
            run_scan()
        except KeyboardInterrupt:
            print("\n[STOP] Stopped by user.")
            break
        except Exception as e:
            print(f"  [ERROR] {e} — retrying in {POLL_INTERVAL}s...")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
