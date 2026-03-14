# 🤖 AI Employee Vault

> **A fully autonomous AI-powered business operations system** — built for Sikandar Tahir, CEO of Sikandar Tahir Agency.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b?style=flat-square)](https://playwright.dev)
[![Meta Graph API](https://img.shields.io/badge/Meta-Graph_API-1877F2?style=flat-square&logo=facebook)](https://developers.facebook.com/docs/graph-api)
[![License](https://img.shields.io/badge/License-Private-red?style=flat-square)]()

---

## 🏆 System Score: 10 / 10 — Production Ready

The AI Employee Vault is a personal AI operations platform that replaces manual business workflows with autonomous agents. It reads emails, generates LinkedIn content, sends WhatsApp messages, tracks accounting, posts to Facebook & Instagram, and gives the CEO full control — all from a single dark-themed dashboard.

---

## ✨ Features

### 🖥️ CEO Command Dashboard (`app.py`)
- **Real-time financial metrics** — net profit, collected, expenses, bank balance (PKR)
- **Odoo accounting bridge** — live JSON + inline mock fallback (always shows data)
- **Kanban task board** — Needs Action / In Progress / Done
- **Agent console** — live tail of `logs/agent_activity.log`
- **Auto-refresh** every 30 seconds

### 📱 Social Media Commander (NEW)
- **Meta Graph API Integration** — Post to Facebook Pages & Instagram Business accounts
- **Unified Post Creator** — Write once, publish to both platforms simultaneously
- **Live Post Preview** — See exactly how your post will look before publishing
- **Obsidian Vault Logging** — Every post auto-logged with URL, timestamp, and content
- **Secure Credential Management** — API tokens stored in `.env` file

### 📝 AI Post Creator
- Type a 1-line prompt → instant professional LinkedIn post
- Brand: **Sikandar Tahir Agency**
- Live preview & edit in dashboard (`st.text_area`)
- **Publish Now** button — saves, approves, and triggers poster in one click
- Fully isolated subprocess (never freezes the dashboard)

### 📱 Communication Hub
| Channel | Features |
|---|---|
| 📧 Email Inbox | Priority-tagged cards (HIGH / MEDIUM / LOW) |
| 💬 WhatsApp | Task scanner, AI Quick Reply composer, Run Sender button |
| 📊 Social | Activity overview from social_media_agent |
| 💼 LinkedIn | Channel status card, approved post count, Run Poster button |
| 📘 Facebook | Post to Facebook Pages with images and links |
| 📷 Instagram | Post to Instagram Business accounts |

### 📁 Draft Management
- Lists all drafts with brand, date, and status badges
- **Edit** → in-dashboard text editor
- **Save & Approve** → moves file from `Drafts/` to `Approved/`
- **Cancel** → non-destructive exit
- Approved drafts summary expander

### ⚙️ Background Watchers (Sidebar)
Start/Stop individual agents directly from the dashboard:
- Gmail Bridge
- Desktop Watcher
- Agent Brain
- Social Media Agent
- Odoo Bridge

### 🚀 Quick Actions (Sidebar)
- **Execute All Approved** — LinkedIn + WhatsApp in one click
- **Run Full Audit** — Odoo bridge with live `st.status` steps
- **System Health Check** — scripts, watchers, git status
- **Sync Vault** — git push via `vault_sync.py`
- **Autopilot Toggle** — autonomous 24h LinkedIn posting (single thread, no spam)

---

## 🗂️ Vault Architecture

```
AI_Employee_Vault/
│
├── app.py                    # CEO Dashboard (Streamlit)
├── agent_brain.py            # AI task dispatcher
├── linkedin_agent.py         # LinkedIn post generator
├── linkedin_poster.py        # Playwright browser automation
├── whatsapp_sender.py        # WhatsApp Web automation
├── social_media_agent.py     # Social monitoring
├── odoo_mcp_bridge.py        # Accounting / Odoo bridge
├── vault_sync.py             # Git-based cloud sync (with safety guard)
│
├── watchers/
│   ├── gmail_bridge.py       # Gmail IMAP reader
│   └── desktop_watcher.py    # Local file watcher
│
├── Needs_Action/             # 📥 Incoming tasks
├── In_Progress/              # 🔄 Active work
├── Approved/                 # ✅ CEO-approved, ready to execute
├── Done/                     # 📦 Completed & archived
├── Drafts/                   # 📝 AI-generated content drafts
├── Readings/                 # 📧 Parsed emails & social summaries
├── Plans/                    # 🧠 AI execution plans
├── Commands/                 # 💬 CEO Odoo commands
├── logs/                     # 📋 Agent activity log
├── AI_EMPLOYEE_VAULT/        # 📚 Obsidian vault (auto-logged posts)
│   └── Social_Posts/         # 📱 Meta post logs (by date)
└── prompt_history/           # 🗒️ Development changelog
```

---

## 🔄 Automation Pipelines

### LinkedIn Pipeline
```
linkedin_agent.py → Drafts/ → [CEO reviews in Dashboard] → Approved/ → linkedin_poster.py → Done/
```

### WhatsApp Pipeline
```
CEO types reply in Dashboard → Approved/WA_Reply_*.md → whatsapp_sender.py → Done/
```

### Email Pipeline
```
Gmail → watchers/gmail_bridge.py → Readings/EMAIL_*.md → agent_brain.py → Needs_Action/
```

### Accounting Pipeline
```
accounting_status.json → odoo_mcp_bridge.py → Readings/Accounting_Audit.md → Dashboard
```

### Meta Social Pipeline (NEW)
```
Dashboard Post Creator → meta_automation.py → Facebook/Instagram → AI_EMPLOYEE_VAULT/Social_Posts/
```

---

## 📘 Meta (Facebook & Instagram) Setup

### 1. Get Meta Developer Credentials

1. Go to [Meta for Developers](https://developers.facebook.com/apps)
2. Create a new app or select existing
3. Add **Facebook Login** and **Instagram Graph API** products
4. Generate a **Long-Lived Page Access Token**

### 2. Find Your IDs

- **Facebook Page ID**: Visit [findmyfbid.in](https://findmyfbid.in/) or check Page settings
- **Instagram Business Account ID**: Use Graph API Explorer: `GET /me/accounts?fields=instagram_business_account`

### 3. Configure in Dashboard

1. Open the AI Employee Vault dashboard
2. Navigate to **Social Media Commander** section
3. Click **Configure Meta API Credentials**
4. Enter your credentials and save

### 4. Test Posting

```bash
python meta_automation.py
```

This will validate your credentials and show account info.

---

## 🛡️ Stability Features

| Feature | Description |
|---|---|
| `CREATE_NEW_CONSOLE` | Child processes isolated — crashes never propagate to dashboard |
| `PROTECTED_FILES` | `vault_sync.py` never overwrites `app.py` or runtime scripts |
| Mock Odoo fallback | Financial metrics always render, even without live JSON |
| Single autopilot thread | Toggle-on spawns exactly one background thread, 24h delay |
| `close_fds=True` | No file handle inheritance between parent and child processes |

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install streamlit streamlit-autorefresh plotly pandas playwright python-dotenv requests
playwright install chromium
```

### 2. Run the dashboard
```bash
streamlit run app.py
```

Open **http://localhost:8501**

### 3. First-time LinkedIn login
```bash
python linkedin_poster.py --login
```

### 4. Configure Meta Social Media (Optional)
- Edit `.env` file with your Meta API credentials
- Or configure directly in the dashboard under **Social Media Commander**

### 5. Configure Gmail (optional)
Add credentials to `watchers/credentials.json` and `watchers/token.json`.

---

## 📊 Live Financial Snapshot

| Metric | Value |
|---|---|
| Net Profit | PKR 435,500 |
| Collected | PKR 570,000 |
| Total Expenses | PKR 134,500 |
| Bank Balance | PKR 612,000 |
| Overdue Invoices | 1 |

---

## 🏗️ Built With

- **[Streamlit](https://streamlit.io)** — Dashboard UI
- **[Playwright](https://playwright.dev/python/)** — Browser automation (LinkedIn, WhatsApp Web)
- **[Meta Graph API](https://developers.facebook.com/docs/graph-api)** — Facebook & Instagram posting
- **[Plotly](https://plotly.com/python/)** — Financial charts
- **[Claude AI](https://anthropic.com)** — AI content generation backbone
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — Environment variable management
- **[Requests](https://requests.readthedocs.io/)** — HTTP client for Meta API
- **Python 3.11+** — Core runtime

---

## 👤 Author

**Sikandar Tahir**
CEO — Sikandar Tahir Agency
GIAIC Hackathon 0

---

*Built with the AI Employee Vault framework — where every agent is a digital FTE.*
