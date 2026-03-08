# Step 8 — Platinum Tier: Social Media Agent (Facebook & Instagram)

**Date:** February 18, 2026
**Author:** Sikandar Tahir
**Project:** GIAIC Hackathon 0 — Personal AI Employee

---

## Prompt Given

> Create `social_media_agent.py` that simulates fetching messages/notifications from Facebook and Instagram using a mock `social_updates.json`.
> Generate a summary in `Readings/Social_Summary.md`.
> If any message is a business inquiry, auto-create a task in `Needs_Action/Social/`.
> Log as `step8_social_media_integration.md`.

---

## What Was Built

### 1. Mock Data File (`social_updates.json`)

A structured JSON file simulating social media activity across 2 platforms:

| Platform | Messages | Business Inquiries | Notifications |
|----------|----------|--------------------|---------------|
| Facebook | 4 | 2 | 2 |
| Instagram | 3 | 2 | 2 |
| **Total** | **7** | **4** | **4** |

#### Business Inquiries (auto-detected)

| Platform | From | Nature |
|----------|------|--------|
| Facebook | Ahmed Raza | E-commerce project for clothing brand, wants a call |
| Facebook | Sara Khan | Interested in Lyvexa AI dashboard for her startup |
| Instagram | Usman Tariq | Restaurant chain in Lahore, needs mobile app + website |
| Instagram | Tech Starter PK | SaaS company looking for AI automation partner |

#### Non-Business Messages

| Platform | From | Content |
|----------|------|---------|
| Facebook | Ali Hassan | Casual encouragement |
| Facebook | Fatima Zahra | Reaction/like on a post |
| Instagram | Zainab Malik | Asking about editing tools |

### 2. Social Media Agent (`social_media_agent.py`)

#### Features

- **Data loading:** Reads `social_updates.json` from vault root
- **Summary generation:** Creates `Readings/Social_Summary.md` with:
  - Overview stats table (total messages, inquiries, notifications)
  - Per-platform breakdown with message tables
  - Notification logs
- **Business inquiry detection:** Uses the `is_business_inquiry` flag from data
- **Smart response suggestions:** Keyword-based action hints:
  - "rate/price/cost" → Send pricing deck
  - "call/schedule/meeting" → Schedule via Calendly
  - "app/website/mobile" → Share portfolio and discuss scope
  - "partner/automation/ai" → Arrange Lyvexa AI consultation
  - (fallback) → Follow up to understand requirements
- **Task creation:** Business inquiries get task files in `Needs_Action/Social/`
- **Deduplication:** Skips tasks that already exist
- **Dual mode:** `--once` for single run, default for 5-minute loop

### 3. Generated Outputs

#### `Readings/Social_Summary.md`

Full social media intelligence report with tables for each platform, message previews, and notification activity.

#### `Needs_Action/Social/` — 4 Task Files

| File | Platform | From | AI Suggested Action |
|------|----------|------|---------------------|
| `SOCIAL_TASK_facebook_Ahmed_Raza.md` | Facebook | Ahmed Raza | Schedule a discovery call via Calendly |
| `SOCIAL_TASK_facebook_Sara_Khan.md` | Facebook | Sara Khan | Share portfolio and discuss project scope |
| `SOCIAL_TASK_instagram_Usman_Tariq.md` | Instagram | Usman Tariq | Share portfolio and discuss project scope |
| `SOCIAL_TASK_instagram_Tech_Starter_PK.md` | Instagram | Tech Starter PK | Schedule a discovery call via Calendly |

Each task file contains the original message, metadata, and an AI-suggested next step.

### 4. Execution Output

```
==================================================
  Social Media Agent — Platinum Tier
==================================================
  Vault:  AI_Employee_Vault
  Data:   social_updates.json
  Tasks:  Needs_Action/Social

[02:47:16] Scanning social media updates...
  [SCAN] Loaded 7 messages across 2 platforms
  [SUMMARY] Social_Summary.md (4 business inquiries)
  [TASK] SOCIAL_TASK_facebook_Ahmed_Raza.md
  [TASK] SOCIAL_TASK_facebook_Sara_Khan.md
  [TASK] SOCIAL_TASK_instagram_Usman_Tariq.md
  [TASK] SOCIAL_TASK_instagram_Tech_Starter_PK.md
  [DONE] Created 4 new social task(s).
```

---

## How to Run

```bash
python social_media_agent.py --once    # Single scan
python social_media_agent.py           # Continuous loop (every 5 min)
```

To add new social data, edit `social_updates.json` and re-run. When real APIs are connected (Platinum+), replace the JSON loader with Facebook Graph API and Instagram Basic Display API calls.

---

## File Structure After This Step

```
AI_Employee_Vault/
├── social_media_agent.py          # NEW — social media scanner
├── social_updates.json            # NEW — mock data (Facebook + Instagram)
├── Readings/
│   ├── Social_Summary.md          # NEW — generated social intelligence report
│   └── EMAIL_*.md                 # (10 email files)
├── Needs_Action/
│   ├── Social/                    # NEW — business inquiry tasks
│   │   ├── SOCIAL_TASK_facebook_Ahmed_Raza.md
│   │   ├── SOCIAL_TASK_facebook_Sara_Khan.md
│   │   ├── SOCIAL_TASK_instagram_Usman_Tariq.md
│   │   └── SOCIAL_TASK_instagram_Tech_Starter_PK.md
│   ├── Shopping_List.md
│   └── AI_TASK_*.md               # (3 email task files)
├── In_Progress/
├── Pending_Approval/
├── Done/
├── Plans/
├── Drafts/
├── watchers/
├── prompt_history/
│   ├── step0_bronze_tier.md
│   ├── step1_silver_tier_gmail.md
│   ├── step2_gold_tier_dashboard.md
│   ├── step4_agent_brain.md
│   ├── step6_silver_completion.md
│   ├── step7_platinum_vault_setup.md
│   └── step8_social_media_integration.md   # This file
├── agent_brain.py
├── app.py
├── linkedin_agent.py
└── CEO_Briefing_Feb_17.md
```

---

## Architecture Significance

The Social Media Agent adds a new "sense" to the AI Employee:

| Sense | Agent | Data Source |
|-------|-------|-------------|
| Email | Gmail Bridge | Gmail API → `Readings/EMAIL_*.md` |
| Desktop | Desktop Watcher | File system → `Desktop_Log.md` |
| Social Media | Social Media Agent | Facebook + Instagram → `Social_Summary.md` |

Business inquiries from social platforms now flow through the same Claim-by-Move pipeline as email tasks.

---

## Technologies Used

- Python 3.13
- JSON for mock data storage
- Keyword-based NLP for response suggestion
- `pathlib` for robust paths
- Markdown templating

---

## Status

Complete. Social Media Agent is operational. 4 business inquiries detected and routed to `Needs_Action/Social/`. Summary generated in `Readings/`.
