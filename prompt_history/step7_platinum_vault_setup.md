# Step 7 — Platinum Tier: Claim-by-Move Vault Structure

**Date:** February 18, 2026
**Author:** Sikandar Tahir
**Project:** GIAIC Hackathon 0 — Personal AI Employee

---

## Prompt Given

> Prepare the vault for Platinum Tier's 'Claim-by-move' rule.
> Create directories: `/Needs_Action`, `/In_Progress`, `/Done`, `/Pending_Approval`.
> Move existing tasks from `Task/` into `/Needs_Action`.
> Update `agent_brain.py` so new tasks go directly into `/Needs_Action`.
> Log this as `step7_platinum_vault_setup.md`.

---

## What Was Done

### 1. Workflow Directories Created

Four new directories representing the Platinum Tier task lifecycle:

```
AI_Employee_Vault/
├── Needs_Action/        # Tasks awaiting pickup (entry point)
├── In_Progress/         # Tasks actively being worked on
├── Pending_Approval/    # Tasks completed but awaiting review
└── Done/                # Archived completed tasks
```

**Claim-by-Move Rule:** To "claim" a task, move it from `Needs_Action/` to `In_Progress/`. When finished, move to `Pending_Approval/`. Once reviewed, move to `Done/`. This creates a visual Kanban workflow inside the file system.

```
Needs_Action/ ──> In_Progress/ ──> Pending_Approval/ ──> Done/
```

### 2. Tasks Migrated

All 4 files from `Task/` were moved to `Needs_Action/`:

| File | Origin |
|------|--------|
| `Shopping_List.md` | Bronze Tier (smart sorter) |
| `AI_TASK_I_want_to_connect.md` | Agent Brain (Step 4) |
| `AI_TASK_Something_special_is_coming_this_Ramadan!.md` | Agent Brain (Step 4) |
| `AI_TASK_Your_cart's_rolling_away._Complete_your_order_today.md` | Agent Brain (Step 4) |

The `Task/` folder is now empty.

### 3. `agent_brain.py` Updated

- `TASKS_DIR` changed from `BASE_DIR / "Task"` to `BASE_DIR / "Needs_Action"`
- Docstring updated to reflect new target directory
- All new AI-generated tasks will land directly in `Needs_Action/`

### 4. `app.py` Updated

- `TASKS_DIR` changed to `BASE_DIR / "Needs_Action"`
- AI task loader now reads from `Needs_Action/AI_TASK_*.md`
- Dashboard will display tasks from the new location

---

## Task Lifecycle (Platinum Tier)

```
1. Gmail Bridge detects new email    ──> Readings/EMAIL_*.md
2. CEO Briefing is generated         ──> CEO_Briefing_Feb_17.md
3. Agent Brain scans for HIGH items  ──> Needs_Action/AI_TASK_*.md + Plans/PLAN_*.md
4. Human (or agent) claims task      ──> Move to In_Progress/
5. Work is done                      ──> Move to Pending_Approval/
6. Review & sign-off                 ──> Move to Done/
```

---

## Files Changed

| File | Change |
|------|--------|
| `agent_brain.py` | `TASKS_DIR` now points to `Needs_Action/` |
| `app.py` | `TASKS_DIR` now points to `Needs_Action/` |
| `Task/` | All files moved out (now empty) |
| `Needs_Action/` | Received all 4 task files |
| `In_Progress/` | Created (empty, ready for use) |
| `Pending_Approval/` | Created (empty, ready for use) |
| `Done/` | Created (empty, ready for use) |

---

## Vault Structure After This Step

```
AI_Employee_Vault/
├── .streamlit/
├── Needs_Action/          # NEW — 4 task files moved here
│   ├── Shopping_List.md
│   ├── AI_TASK_I_want_to_connect.md
│   ├── AI_TASK_Something_special_is_coming_this_Ramadan!.md
│   └── AI_TASK_Your_cart's_rolling_away._Complete_your_order_today.md
├── In_Progress/           # NEW — empty, ready for claimed tasks
├── Pending_Approval/      # NEW — empty, ready for review
├── Done/                  # NEW — empty, archive for completed
├── Plans/                 # Execution plans
├── Drafts/                # LinkedIn post drafts
├── Readings/              # Email summaries
├── Task/                  # Now empty (legacy)
├── watchers/
├── prompt_history/
│   ├── step0_bronze_tier.md
│   ├── step1_silver_tier_gmail.md
│   ├── step2_gold_tier_dashboard.md
│   ├── step4_agent_brain.md
│   ├── step6_silver_completion.md
│   └── step7_platinum_vault_setup.md   # This file
├── agent_brain.py         # UPDATED — targets Needs_Action/
├── app.py                 # UPDATED — reads from Needs_Action/
├── linkedin_agent.py
└── CEO_Briefing_Feb_17.md
```

---

## Status

Complete. Platinum Tier vault structure is in place. The claim-by-move workflow is operational.
