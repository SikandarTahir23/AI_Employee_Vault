# Step 6 — Silver Tier Completion: LinkedIn Agent & Execution Plans

**Date:** February 18, 2026
**Author:** Sikandar Tahir
**Project:** GIAIC Hackathon 0 — Personal AI Employee

---

## Prompt Given

> Create a script `linkedin_agent.py` that drafts a professional LinkedIn post about Sikandar Tahir Agency or Lyvexa AI services, saving the draft to `Drafts/LinkedIn_Post.md`.
>
> Update `agent_brain.py` so that when it detects a HIGH priority task, it also creates a `Plan.md` file in the `/Plans` folder, detailing how to solve that task.
>
> Log this as `step6_silver_completion.md` in `prompt_history`.

---

## What Was Built

### 1. LinkedIn Agent (`linkedin_agent.py`)

A post-draft generator that creates professional LinkedIn content for two brands.

#### Features
- **Two brand profiles:** Sikandar Tahir Agency and Lyvexa AI, each with their own tagline, service catalog, and call-to-action
- **CLI flags:**
  - Default: generates a Sikandar Tahir Agency post
  - `--lyvexa`: generates a Lyvexa AI post
  - `--both`: generates drafts for both brands
  - Custom topic: `python linkedin_agent.py "Our new AI dashboard"`
- **Output:** Timestamped markdown files in `Drafts/`
- **Post structure:** Hook line, service list, CTA, hashtags, review reminder

#### Generated Files
```
Drafts/
├── LinkedIn_Post_sikandartahir_agency_20260218_021858.md
└── LinkedIn_Post_lyvexa_ai_20260218_021858.md
```

#### Sample Output (Lyvexa AI)
```markdown
In 2026, automation isn't optional — it's the competitive edge.

At Lyvexa AI, we specialize in turning complex challenges into elegant solutions:
  - AI Employee Agents (Digital FTEs)
  - Autonomous Email & Task Management
  - Real-Time Business Intelligence Dashboards
  - Custom LLM Integration & Fine-Tuning
  - Workflow Automation with Human-in-the-Loop

Ready to hire your first AI employee?
```

---

### 2. Agent Brain Update — Execution Plans

`agent_brain.py` now generates both a Task file AND a Plan file for every HIGH priority item.

#### New: `Plans/` Folder

Each plan file contains:
- **Objective:** One-line goal derived from the action hint
- **Context:** Original briefing action + email summary
- **Step-by-Step Plan:** 4-5 actionable steps tailored to the specific task type
- **Success Criteria:** Checkboxes for completion tracking

#### Plan Templates (keyword-matched)

| Keyword | Plan Focus |
|---------|-----------|
| `connect` | LinkedIn invitation review, profile assessment, accept/decline workflow |
| `cart` | E-commerce cart evaluation, purchase/abandon decision |
| `ramadan` | Time-sensitive event assessment, participation decision |
| `order` | Order review, payment/cancellation workflow |
| (fallback) | Generic 5-step review-decide-execute plan |

#### Generated Plan Files
```
Plans/
├── PLAN_I_want_to_connect.md
├── PLAN_Something_special_is_coming_this_Ramadan!.md
└── PLAN_Your_cart's_rolling_away._Complete_your_order_today.md
```

#### Execution Output
```
[02:19:42] Scanning for HIGH priority items...
  [SCAN] Found 3 HIGH priority items in CEO Briefing
  [SCAN] Loaded 10 emails from Readings/
  [PLAN]  PLAN_I_want_to_connect.md
  [PLAN]  PLAN_Something_special_is_coming_this_Ramadan!.md
  [PLAN]  PLAN_Your_cart's_rolling_away._Complete_your_order_today.md
  [DONE] Tasks: 0 | Plans: 3
```

(Tasks showed 0 because they were already created in Step 4. Plans were new.)

---

## File Structure After This Step

```
AI_Employee_Vault/
├── agent_brain.py          # UPDATED — now generates Plans/ alongside Tasks/
├── linkedin_agent.py       # NEW — LinkedIn post draft generator
├── app.py                  # Streamlit dashboard
├── CEO_Briefing_Feb_17.md
├── Readings/               # 10 email markdown files
├── Task/                   # AI-generated task files
│   ├── Shopping_List.md
│   ├── AI_TASK_I_want_to_connect.md
│   ├── AI_TASK_Something_special_is_coming_this_Ramadan!.md
│   └── AI_TASK_Your_cart's_rolling_away._Complete_your_order_today.md
├── Plans/                  # NEW — execution plans for HIGH priority items
│   ├── PLAN_I_want_to_connect.md
│   ├── PLAN_Something_special_is_coming_this_Ramadan!.md
│   └── PLAN_Your_cart's_rolling_away._Complete_your_order_today.md
├── Drafts/                 # NEW — LinkedIn post drafts
│   ├── LinkedIn_Post_sikandartahir_agency_*.md
│   └── LinkedIn_Post_lyvexa_ai_*.md
├── watchers/
├── prompt_history/
│   ├── step0_bronze_tier.md
│   ├── step1_silver_tier_gmail.md
│   ├── step2_gold_tier_dashboard.md
│   ├── step4_agent_brain.md
│   └── step6_silver_completion.md   # NEW — this file
└── .streamlit/
```

---

## How to Run

```bash
# LinkedIn Agent
python linkedin_agent.py              # Sikandar Tahir Agency draft
python linkedin_agent.py --lyvexa     # Lyvexa AI draft
python linkedin_agent.py --both       # Both brands

# Agent Brain (now creates Tasks + Plans)
python agent_brain.py --once          # Single scan
python agent_brain.py                 # Continuous loop (every 5 min)
```

---

## Architecture Significance

With this step, the AI Employee now has three autonomous capabilities:

1. **Perceive** — Gmail Bridge + Desktop Watcher (senses)
2. **Reason & Plan** — Agent Brain detects priorities AND generates execution plans
3. **Draft & Communicate** — LinkedIn Agent creates professional content

This completes the Silver Tier requirements and sets the foundation for the Platinum Tier.

---

## Technologies Used

- Python 3.13
- `pathlib` for cross-platform paths
- `re` (regex) for markdown parsing
- Keyword-based template engine for plans and action hints
- CLI argument parsing via `sys.argv`

---

## Status

Complete. Silver Tier requirements fulfilled. LinkedIn drafts generated. Execution plans auto-created for all 3 HIGH priority items.
