# Step 2 — Gold Tier: Streamlit CEO Dashboard with Real-Time Refresh

**Date:** February 17–18, 2026
**Tier:** Gold
**Author:** Sikandar Tahir
**Project:** GIAIC Hackathon 0 — Personal AI Employee

---

## Objective

Build a premium, dark-themed Streamlit dashboard that visualizes all AI Employee Vault data — emails, tasks, priorities, and the CEO Briefing — in a professional, real-time interface branded as "Sikandar Tahir | AI Command Center."

---

## What Was Built

### 1. Dashboard Application (`app.py`)

A full-featured Streamlit application with the following sections:

#### Page Configuration
- Title: "Sikandar Tahir | AI Command Center"
- Layout: Wide mode with expanded sidebar
- Dark theme configured via `.streamlit/config.toml`

#### Custom CSS Theme
- Dark gradient backgrounds (`#0E1117` to `#161B22`)
- Purple accent palette (`#6C63FF`, `#A78BFA`)
- Glassmorphic metric cards with subtle box shadows
- Gradient sidebar with clean dividers
- Color-coded priority badges (RED/YELLOW/GREEN)

#### Sidebar (Minimalist)
- **Branding:** "Sikandar Tahir" with gradient text, "AI Command Center" subtitle
- **Report Date:** Dynamically shows current date
- **System Status:** Green "LIVE" badge
- **Refresh Timer:** Shows last auto-refresh timestamp

#### KPI Metrics Row (4 columns)
| Metric | Value | Source |
|--------|-------|--------|
| Total Emails | 10 | `Readings/` folder file count |
| Unread Emails | 10 | Parsed from email Status field |
| High Priority | 3 | Extracted from CEO Briefing table |
| Pending Tasks | 5 | Checkboxes from CEO Briefing |

#### Charts (Plotly)

**Email Distribution Pie Chart:**
- Donut chart (`hole=0.45`) showing email count per sender
- Purple color sequence, transparent background
- Source: Inbox Intelligence table from CEO Briefing

**Task Status Bar Chart:**
- Vertical bars: Pending (yellow `#D29922`) vs Done (green `#238636`)
- Source: Checkbox items parsed from CEO Briefing

**Priority Distribution Horizontal Bar:**
- HIGH (red), MEDIUM (yellow), LOW (green)
- Shows count of emails per priority level

#### Inbox Intelligence Table
- Interactive `st.dataframe` with color-coded Priority column
- Columns: Priority, Sender, Subject, Action Required
- Parsed from the CEO Briefing markdown table using regex

#### Email Details Table
- Full table of all 10 emails from `Readings/`
- Columns: Subject, From, Date, Status, Summary
- Each email parsed from individual markdown files

#### Desktop & Local Tasks
- Checklist display with status icons
- Hourglass for pending, checkmark for done

#### Full CEO Briefing
- Collapsible `st.expander` with the complete markdown content

#### AI Recommendation
- Extracted from the `## AI Recommendation` section
- Displayed in a `st.info` callout box

#### Footer
- "Sikandar Tahir | AI Command Center | AI Employee Vault"

### 2. Real-Time Auto-Refresh

```python
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=30000, key="datarefresh")
```

- Dashboard automatically refreshes every 30 seconds
- Picks up new emails added to `Readings/` by the Gmail Bridge
- Picks up any changes to `CEO_Briefing_Feb_17.md`

### 3. Streamlit Theme Configuration (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#6C63FF"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#161B22"
textColor = "#C9D1D9"
font = "sans serif"
```

### 4. Robust Path Handling

All file paths are dynamically resolved:
```python
BASE_DIR = Path(__file__).resolve().parent
READINGS_DIR = BASE_DIR / "Readings"
BRIEFING_FILE = BASE_DIR / "CEO_Briefing_Feb_17.md"
```

This ensures the dashboard works regardless of the working directory.

---

## Evolution Summary

The dashboard went through three iterations:

### Iteration 1 — Initial Build
- "Multicraft Agency" / "Lyvexa AI" branding
- Basic metrics + charts + tables
- Sidebar with data sources and priority filter

### Iteration 2 — Branding Cleanup
- Removed all "Multicraft Agency" / "Lyvexa AI" references
- Rebranded to "Sikandar Tahir | AI Command Center"
- Minimalist sidebar (removed filter clutter, data sources)
- Added `padding-top: 2rem` fix for header cut-off
- Added `streamlit-autorefresh` for 30s auto-reload
- Added LIVE status badge and refresh timestamp

---

## Dependencies Installed

```bash
pip install streamlit pandas plotly streamlit-autorefresh
```

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.48.0 | Dashboard framework |
| pandas | 2.3.1 | Data manipulation |
| plotly | 6.5.2 | Interactive charts |
| streamlit-autorefresh | 1.0.1 | Auto-refresh component |

---

## How to Run

```bash
cd "C:\Users\Sikandar Tahir\OneDrive\Desktop\AI_Employee_Vault"
streamlit run app.py
```

Opens at: `http://localhost:8501`

---

## File Structure After Gold Tier

```
AI_Employee_Vault/
├── .streamlit/
│   └── config.toml          # Dark theme configuration
├── app.py                    # Streamlit dashboard (main)
├── CEO_Briefing_Feb_17.md    # Auto-generated CEO briefing
├── Readings/                 # 10 email markdown files
├── Task/                     # Auto-sorted task files
├── watchers/                 # Python watcher scripts
├── Hackathon 0/              # Project documentation
└── prompt_history/           # This documentation folder
```

---

## Technologies Used

- Python 3.13
- Streamlit 1.48.0
- Plotly 6.5.2
- Pandas 2.3.1
- streamlit-autorefresh 1.0.1
- Custom CSS (gradient backgrounds, glassmorphism, color-coded badges)
- Regex-based markdown parsing

---

## Status

Complete. The Gold Tier dashboard is live at `localhost:8501` with real-time auto-refresh, full data visualization, and personal branding.
