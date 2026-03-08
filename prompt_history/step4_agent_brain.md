# Step 4 — Agent Brain: Autonomous Task Generator from High-Priority Emails

**Date:** February 18, 2026
**Author:** Sikandar Tahir
**Project:** GIAIC Hackathon 0 — Personal AI Employee

---

## Prompt Given

> Create a new script named `agent_brain.py`. This script should:
> 1. Read all markdown files in the `Readings/` folder.
> 2. Look for any email that has 'Status: High' or 'Priority: High'.
> 3. For every High priority email, automatically create a new file in the `Tasks/` folder named `AI_TASK_[Subject].md`.
> 4. Inside that file, write: 'AI has detected this as urgent. Suggested action: [One line action].'
> 5. Log this step in `prompt_history/step4_agent_brain.md`.

---

## What Was Built

### `agent_brain.py` — Autonomous Task Generator

A standalone Python script that cross-references two data sources to detect high-priority items and auto-generate actionable task files.

#### Data Flow

```
Readings/EMAIL_*.md  ──┐
                       ├──> agent_brain.py ──> Task/AI_TASK_*.md
CEO_Briefing_Feb_17.md ┘
```

#### How It Works

1. **Parse CEO Briefing:** Extracts the Inbox Intelligence table using regex, filters for rows where Priority = `**HIGH**`
2. **Parse Email Files:** Reads all `EMAIL_*.md` files in `Readings/`, builds a lookup dictionary keyed by subject
3. **Cross-Reference:** Matches each HIGH priority item from the briefing to its source email file via fuzzy subject matching
4. **Generate Tasks:** For each match, creates `AI_TASK_[Subject].md` in `Task/` with:
   - Priority, sender, detection timestamp, source email filename
   - AI-generated suggested action (keyword-based matching)
   - Original action text from the CEO Briefing
5. **Deduplication:** Skips task files that already exist (idempotent — safe to re-run)

#### Keyword-Based Action Hints

The script uses a keyword dictionary to generate contextual one-line suggested actions:

| Keyword | Suggested Action |
|---------|-----------------|
| `connect` | Accept or decline the connection request promptly |
| `cart` / `order` | Complete the purchase or dismiss the cart before it expires |
| `ramadan` | Review the time-sensitive event and decide on participation today |
| `hiring` | Review job listings and apply to relevant positions |
| (fallback) | Review this item immediately and take appropriate action |

---

## Execution Output

```
==================================================
  Agent Brain — Task Generator
==================================================

[SCAN] Found 3 HIGH priority items in CEO Briefing
[SCAN] Loaded 10 emails from Readings/

  [CREATED] AI_TASK_I_want_to_connect.md
  [CREATED] AI_TASK_Something_special_is_coming_this_Ramadan!.md
  [CREATED] AI_TASK_Your_cart's_rolling_away._Complete_your_order_today.md

[DONE] Created: 3 | Skipped: 0
```

---

## Files Created

### Task/AI_TASK_I_want_to_connect.md
- **Sender:** Hamza Naeem (LinkedIn)
- **Source:** EMAIL_19c68c55290eb40f.md
- **Action:** Accept or decline the connection request promptly

### Task/AI_TASK_Something_special_is_coming_this_Ramadan!.md
- **Sender:** Binance
- **Source:** EMAIL_19c675dde1fc8852.md
- **Action:** Review the time-sensitive event and decide on participation today

### Task/AI_TASK_Your_cart's_rolling_away._Complete_your_order_today.md
- **Sender:** GoDaddy
- **Source:** EMAIL_19c6873649a1bfef.md
- **Action:** Complete the purchase or dismiss the cart before it expires

---

## File Structure After This Step

```
AI_Employee_Vault/
├── agent_brain.py                    # NEW — autonomous task generator
├── app.py                            # Streamlit dashboard
├── CEO_Briefing_Feb_17.md
├── Readings/                         # 10 email markdown files
├── Task/
│   ├── Shopping_List.md              # Existing (from Bronze tier)
│   ├── AI_TASK_I_want_to_connect.md              # NEW
│   ├── AI_TASK_Something_special_is_coming_this_Ramadan!.md  # NEW
│   └── AI_TASK_Your_cart's_rolling_away._Complete_your_order_today.md  # NEW
├── watchers/
├── prompt_history/
│   ├── step0_bronze_tier.md
│   ├── step1_silver_tier_gmail.md
│   ├── step2_gold_tier_dashboard.md
│   └── step4_agent_brain.md          # NEW — this file
└── .streamlit/
```

---

## Architecture Significance

This step implements the **"Brain"** layer of the Digital FTE architecture. The agent now autonomously:

1. **Perceives** — reads email data from the vault (Senses layer already done)
2. **Reasons** — identifies which items are urgent via priority analysis
3. **Acts** — creates structured task files with suggested actions

This transforms the system from a passive data aggregator into a proactive task-generating agent.

---

## Technologies Used

- Python 3.13
- `pathlib` for robust cross-platform paths
- `re` (regex) for markdown table and metadata parsing
- Keyword-based action suggestion engine

---

## How to Run

```bash
cd "C:\Users\Sikandar Tahir\OneDrive\Desktop\AI_Employee_Vault"
python agent_brain.py
```

Safe to re-run — duplicates are automatically skipped.

---

## Status

Complete. 3 HIGH priority tasks auto-generated from 10 emails. The Agent Brain is operational.
