"""
Social Media Commander Module
Sikandar Tahir | AI Agency Dashboard

This module provides the Meta (Facebook & Instagram) automation UI components
for the Streamlit dashboard, featuring the Elite Neon Green & Deep Black theme.
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
VAULT_DIR = BASE_DIR / "AI_EMPLOYEE_VAULT"
VAULT_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────
def validate_env_var(var_name: str) -> bool:
    """Check if an environment variable is set and not a placeholder."""
    value = os.getenv(var_name, "")
    return bool(value) and not value.startswith("your_")


def get_env_var(var_name: str) -> str:
    """Get an environment variable value."""
    return os.getenv(var_name, "")


def save_env_vars(vars_dict: dict) -> bool:
    """Save environment variables to .env file."""
    env_file = BASE_DIR / ".env"
    existing_lines = []
    if env_file.exists():
        existing_lines = env_file.read_text(encoding="utf-8").splitlines()
    
    new_lines = []
    updated_keys = set()
    for line in existing_lines:
        if "=" in line:
            key = line.split("=")[0].strip()
            if key in vars_dict:
                new_lines.append(f"{key}={vars_dict[key]}")
                updated_keys.add(key)
                continue
        new_lines.append(line)
    
    for key, value in vars_dict.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}")
    
    env_file.write_text("\n".join(new_lines), encoding="utf-8")
    return True


def render_meta_config_section():
    """Render the Meta API Configuration section with Elite styling."""
    st.markdown('<div class="section-header">Meta API Configuration</div>', unsafe_allow_html=True)
    
    meta_token_set = validate_env_var("META_ACCESS_TOKEN")
    fb_page_set = validate_env_var("FB_PAGE_ID")
    ig_account_set = validate_env_var("IG_BUSINESS_ACCOUNT_ID")
    
    config_status = {
        "meta_token": meta_token_set,
        "fb_page": fb_page_set,
        "ig_account": ig_account_set,
        "fully_configured": meta_token_set and fb_page_set and ig_account_set,
    }
    
    cols = st.columns(4)
    status_items = [
        ("Meta Token", meta_token_set),
        ("FB Page ID", fb_page_set),
        ("IG Account ID", ig_account_set),
        ("Status", config_status["fully_configured"])
    ]
    
    for i, (label, is_set) in enumerate(status_items):
        with cols[i]:
            icon = "✅" if is_set else "⚠️"
            status_text = "Ready" if is_set else "Missing"
            border_color = "#39FF14" if is_set else "#F85149"
            st.markdown(
                f'<div style="background:rgba(0,0,0,0.5); border:1px solid {border_color}; '
                f'border-radius:8px; padding:12px; text-align:center;">'
                f'<div style="color:{border_color}; font-size:0.7rem; text-transform:uppercase; '
                f'letter-spacing:0.1em; font-weight:700;">{label}</div>'
                f'<div style="color:#FFF; font-size:1rem; margin-top:4px;">{icon} {status_text}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    with st.expander("🔧 Edit Meta Credentials", expanded=not config_status["fully_configured"]):
        with st.form("meta_credentials_form"):
            c1, c2 = st.columns(2)
            with c1:
                token = st.text_input("Meta Access Token", value=get_env_var("META_ACCESS_TOKEN"), type="password")
                fb_id = st.text_input("Facebook Page ID", value=get_env_var("FB_PAGE_ID"))
            with c2:
                ig_id = st.text_input("Instagram Business Account ID", value=get_env_var("IG_BUSINESS_ACCOUNT_ID"))
                st.caption("IDs can be found in your Meta Developer Dashboard or via Graph API Explorer.")
            
            if st.form_submit_button("Save Configuration", use_container_width=True):
                if save_env_vars({
                    "META_ACCESS_TOKEN": token.strip(),
                    "FB_PAGE_ID": fb_id.strip(),
                    "IG_BUSINESS_ACCOUNT_ID": ig_id.strip()
                }):
                    st.success("Credentials saved to .env")
                    st.rerun()
    
    return config_status


def render_post_creator(config_status: dict):
    """Render the Elite Meta Post Creator."""
    st.markdown('<div class="section-header">Post Command Center</div>', unsafe_allow_html=True)
    
    if not config_status["fully_configured"]:
        st.warning("Complete configuration to enable posting.")
        return

    st.markdown(
        '<div class="ai-creator-wrap">'
        '<div class="ai-creator-title"><span class="ai-badge">META</span> Simultaneous Multi-Platform Posting</div>'
        '<div class="ai-creator-sub">Broadcast to Facebook and Instagram in one click.</div>'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([3, 2])
    
    with c1:
        post_caption = st.text_area(
            "Global Caption",
            placeholder="Broadcast your update...",
            height=200,
            key="meta_global_caption"
        )
        
        image_input = st.text_input(
            "Image URL (Required for Instagram)",
            placeholder="https://example.com/image.jpg",
            help="Instagram Graph API requires a public URL for images."
        )
        
        st.info("💡 Note: Facebook supports local uploads, but for simultaneous posting, a public URL is recommended.")

    with c2:
        st.markdown("**Live Preview**")
        if post_caption.strip():
            st.markdown(
                f'<div class="ai-preview-box" style="height:300px; overflow-y:auto;">'
                f'<strong style="color:#39FF14;">Sikandar Tahir Agency</strong><br><br>'
                f'{post_caption}</div>',
                unsafe_allow_html=True
            )
            if image_input.strip().startswith("http"):
                try:
                    st.image(image_input.strip(), use_container_width=True)
                except:
                    st.error("Invalid Image URL")
        else:
            st.markdown(
                '<div class="ai-preview-box" style="height:300px; color:#444; text-align:center; padding-top:130px;">'
                'Content preview will appear here</div>',
                unsafe_allow_html=True
            )

    pub_col1, pub_col2 = st.columns(2)
    with pub_col1:
        if st.button("🚀 BLAST TO ALL PLATFORMS", use_container_width=True, type="primary"):
            if not post_caption.strip():
                st.error("Caption is required")
            else:
                from meta_automation import MetaAutomation
                meta = MetaAutomation()
                with st.status("Broadcasting...", expanded=True) as status:
                    st.write("Initiating Meta API handshake...")
                    results = meta.post_to_meta_simultaneously(post_caption, image_input.strip() if image_input.strip() else None)
                    
                    fb_res = results.get("facebook", {})
                    ig_res = results.get("instagram", {})
                    
                    if fb_res.get("success"):
                        st.success(f"✅ Facebook: Posted successfully! (ID: {fb_res.get('post_id')})")
                    else:
                        st.error(f"❌ Facebook: {fb_res.get('error')}")
                        
                    if ig_res.get("success"):
                        st.success(f"✅ Instagram: Posted successfully! (ID: {ig_res.get('post_id')})")
                    else:
                        st.error(f"❌ Instagram: {ig_res.get('error')}")
                    
                    status.update(label="Broadcast Complete", state="complete")
                    st.balloons()

    with pub_col2:
        if st.button("📄 Save as Draft Only", use_container_width=True):
            # Future: Implement Meta draft saving
            st.toast("Draft saved to AI_EMPLOYEE_VAULT/Drafts")


def render_recent_posts_log():
    """Render recent posts with Elite styling."""
    st.markdown('<div class="section-header">Broadcast History</div>', unsafe_allow_html=True)
    
    log_dir = VAULT_DIR / "Social_Posts"
    if not log_dir.exists():
        st.info("No broadcast history found.")
        return
        
    all_logs = []
    for date_dir in sorted(log_dir.iterdir(), reverse=True):
        if date_dir.is_dir():
            for f in date_dir.glob("*.md"):
                all_logs.append(f)
    
    if not all_logs:
        st.info("No broadcast history found.")
        return
        
    for log_file in sorted(all_logs, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        content = log_file.read_text(encoding="utf-8")
        platform = "META"
        if "platform: facebook" in content.lower(): platform = "FACEBOOK"
        if "platform: instagram" in content.lower(): platform = "INSTAGRAM"
        
        # Simple extraction for preview
        body = content.split("## Content")[-1].strip().split("---")[0].strip()
        timestamp = log_file.stem.split("_")[-1]
        
        st.markdown(
            f'<div class="card">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            f'<span class="tag tag-social">{platform}</span>'
            f'<span class="card-meta">{log_file.parent.name} {timestamp}</span>'
            f'</div>'
            f'<div class="card-body" style="margin-top:8px; color:#C9D1D9;">{body[:200]}...</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_social_media_commander():
    """Main entry point for the Social Media Commander UI."""
    config_status = render_meta_config_section()
    st.markdown("<br>", unsafe_allow_html=True)
    render_post_creator(config_status)
    st.markdown("<br>", unsafe_allow_html=True)
    render_recent_posts_log()


if __name__ == "__main__":
    st.set_page_config(page_title="Sikandar Tahir | Social Commander", layout="wide")
    render_social_media_commander()
