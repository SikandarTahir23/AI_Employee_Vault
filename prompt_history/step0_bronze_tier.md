# Step 0 — Bronze Tier: AI Employee Vault Setup & Desktop Watcher

**Date:** February 17, 2026
**Tier:** Bronze
**Author:** Sikandar Tahir
**Project:** GIAIC Hackathon 0 — Personal AI Employee

---

## Objective

Set up the foundational infrastructure for a local-first AI Employee system using Obsidian as the knowledge base and Python watchers as the "senses" of the agent.

---

## What Was Built

### 1. Obsidian Vault — `AI_Employee_Vault`

A new Obsidian vault was created on the Desktop with the following folder structure:

```
AI_Employee_Vault/
├── .obsidian/           # Obsidian config (appearance, plugins, workspace)
├── Readings/            # Auto-populated email summaries (Silver Tier)
├── Task/                # Auto-sorted task files (e.g., Shopping_List.md)
├── Hackathon 0/         # Project documentation and architecture blueprint
├── watchers/            # Python watcher scripts + credentials
│   ├── desktop_watcher.py
│   ├── watchers.md      # Smart sorter watcher
│   ├── gmail_bridge.py  # (Silver Tier)
│   ├── credentials.json # Google OAuth client secret
│   ├── token.json       # Cached OAuth token
│   └── Desktop_Log.md   # Log of detected desktop files
└── CEO_Briefing_Feb_17.md  # Auto-generated Monday briefing
```

### 2. Desktop Watcher (`desktop_watcher.py`)

A lightweight Python script that monitors the user's Desktop folder in a continuous loop (polling every 5 seconds). When a new file appears, it appends an entry to `Desktop_Log.md`.

**Key behavior:**
- Uses `os.listdir()` to snapshot the Desktop directory
- Compares before/after snapshots to detect added files
- Logs each detection with the filename and timestamp
- Runs as a persistent background process

### 3. Smart Sorter Watcher (`watchers.md`)

An enhanced version of the desktop watcher that reads the content of newly detected `.txt` files and auto-sorts them into the vault:

- Files containing "task" or "todo" keywords go to `Task/`
- All other files go to `Readings/`
- Each sorted file is wrapped in a Markdown template with metadata (source, category, timestamp)
- Includes retry logic (5 attempts) for locked files on Windows

### 4. Desktop Log Output

The watcher successfully detected and logged the following desktop activity:

| File | Timestamp |
|------|-----------|
| `New folder` | Wed Feb 11, 04:13 |
| `test folder` | Wed Feb 11, 04:13 |
| `python watchers.md` | Tue Feb 17, 02:19 |
| `agent_test.txt` | Tue Feb 17, 02:19 |
| `apple.txt` | Tue Feb 17, 02:24 |

The `apple.txt` file contained "I need to buy apples, this is a task" and was correctly routed to `Task/Shopping_List.md`.

---

## Architecture Context

This step implements the **"Senses"** layer of the Digital FTE architecture described in the Hackathon 0 documentation:

- **The Brain:** Claude Code (reasoning engine)
- **The Memory/GUI:** Obsidian (local Markdown vault)
- **The Senses:** Python watcher scripts (this step)
- **The Hands:** MCP servers (future steps)

---

## Technologies Used

- Python 3.13
- Obsidian v1.10.6+
- `os` and `time` standard libraries
- Windows filesystem monitoring via polling

---

## Status

Complete. The Bronze Tier foundation is operational with file detection, smart sorting, and local logging fully functional.
