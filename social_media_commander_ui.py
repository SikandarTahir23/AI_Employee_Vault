"""
Social Media Commander Module
Sikandar Tahir | AI Agency Dashboard

This module provides the Meta (Facebook & Instagram) automation UI components
for the Streamlit dashboard.
"""

import streamlit as st
import os
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
    """Check if an environment variable is set."""
    value = os.getenv(var_name, "")
    return bool(value) and value != f"your_{var_name.lower()}_here"


def get_env_var(var_name: str) -> str:
    """Get an environment variable value."""
    return os.getenv(var_name, "")


def save_env_vars(vars_dict: dict) -> bool:
    """
    Save environment variables to .env file.
    
    Args:
        vars_dict: Dictionary of {var_name: value}
        
    Returns:
        True if successful
    """
    env_file = BASE_DIR / ".env"
    
    # Read existing content
    existing_content = ""
    if env_file.exists():
        existing_content = env_file.read_text(encoding="utf-8")
    
    # Update or add variables
    lines = existing_content.split("\n")
    updated_lines = []
    updated_keys = set()
    
    for line in lines:
        # Check if this line defines a variable we're updating
        key_match = line.split("=")[0].strip() if "=" in line else ""
        if key_match in vars_dict:
            updated_lines.append(f"{key_match}={vars_dict[key_match]}")
            updated_keys.add(key_match)
        else:
            updated_lines.append(line)
    
    # Add any new variables not in existing file
    for key, value in vars_dict.items():
        if key not in updated_keys:
            updated_lines.append(f"{key}={value}")
    
    # Write back
    env_file.write_text("\n".join(updated_lines), encoding="utf-8")
    return True


def render_meta_config_section():
    """
    Render the Meta API Configuration section.
    
    Returns:
        dict with configuration status
    """
    st.markdown('<div class="section-header">Meta API Configuration</div>', unsafe_allow_html=True)
    
    # Check current configuration status
    meta_token_set = validate_env_var("META_ACCESS_TOKEN")
    fb_page_set = validate_env_var("FB_PAGE_ID")
    ig_account_set = validate_env_var("IG_BUSINESS_ACCOUNT_ID")
    
    config_status = {
        "meta_token": meta_token_set,
        "fb_page": fb_page_set,
        "ig_account": ig_account_set,
        "fully_configured": meta_token_set and fb_page_set and ig_account_set,
    }
    
    # Configuration status card
    status_cols = st.columns(4)
    
    with status_cols[0]:
        status_icon = "✅" if meta_token_set else "⚠️"
        status_text = "Configured" if meta_token_set else "Missing"
        st.markdown(
            f'<div class="card">'
            f'<div class="card-title">{status_icon} Meta Token</div>'
            f'<div class="card-meta">{status_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    
    with status_cols[1]:
        status_icon = "✅" if fb_page_set else "⚠️"
        status_text = "Configured" if fb_page_set else "Missing"
        st.markdown(
            f'<div class="card">'
            f'<div class="card-title">{status_icon} Facebook Page</div>'
            f'<div class="card-meta">{status_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    
    with status_cols[2]:
        status_icon = "✅" if ig_account_set else "⚠️"
        status_text = "Configured" if ig_account_set else "Missing"
        st.markdown(
            f'<div class="card">'
            f'<div class="card-title">{status_icon} Instagram Account</div>'
            f'<div class="card-meta">{status_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    
    with status_cols[3]:
        overall_status = "✅ Ready" if config_status["fully_configured"] else "⚠️ Setup Required"
        overall_class = "channel-status-ready" if config_status["fully_configured"] else "channel-status-idle"
        st.markdown(
            f'<div class="card">'
            f'<div class="card-title">Overall Status</div>'
            f'<div class="card-meta"><span class="channel-status {overall_class}">{overall_status}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    
    # Configuration form
    with st.expander("🔧 Configure Meta API Credentials", expanded=not config_status["fully_configured"]):
        st.markdown("""
        **Get your credentials from Meta:**
        1. Go to [Meta for Developers](https://developers.facebook.com/apps)
        2. Create or select your app
        3. Add Facebook and Instagram products
        4. Generate a long-lived access token
        5. Find your Page ID and Instagram Business Account ID
        """)
        
        with st.form("meta_config_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_meta_token = st.text_input(
                    "Meta Access Token",
                    value=get_env_var("META_ACCESS_TOKEN") if meta_token_set else "",
                    type="password",
                    placeholder="EAAG...",
                    help="Long-lived Page Access Token from Meta Developer Tools"
                )
                
                new_fb_page = st.text_input(
                    "Facebook Page ID",
                    value=get_env_var("FB_PAGE_ID") if fb_page_set else "",
                    placeholder="1234567890",
                    help="Your Facebook Page ID (find at findmyfbid.in)"
                )
            
            with col2:
                new_ig_account = st.text_input(
                    "Instagram Business Account ID",
                    value=get_env_var("IG_BUSINESS_ACCOUNT_ID") if ig_account_set else "",
                    placeholder="17841400000000000",
                    help="Instagram Business Account ID from Graph API"
                )
                
                new_app_id = st.text_input(
                    "Meta App ID (Optional)",
                    value=get_env_var("META_APP_ID") if validate_env_var("META_APP_ID") else "",
                    placeholder="123456789012345"
                )
            
            submitted = st.form_submit_button("💾 Save Configuration", use_container_width=True)
            
            if submitted:
                vars_to_save = {}
                if new_meta_token.strip():
                    vars_to_save["META_ACCESS_TOKEN"] = new_meta_token.strip()
                if new_fb_page.strip():
                    vars_to_save["FB_PAGE_ID"] = new_fb_page.strip()
                if new_ig_account.strip():
                    vars_to_save["IG_BUSINESS_ACCOUNT_ID"] = new_ig_account.strip()
                if new_app_id.strip():
                    vars_to_save["META_APP_ID"] = new_app_id.strip()
                
                if vars_to_save:
                    if save_env_vars(vars_to_save):
                        st.success("✅ Configuration saved! Please refresh the page.")
                        st.balloons()
                    else:
                        st.error("❌ Failed to save configuration")
    
    return config_status


def render_post_creator(config_status: dict):
    """
    Render the Meta Post Creator section.
    
    Args:
        config_status: Dict from render_meta_config_section
    """
    st.markdown('<div class="section-header">Meta Post Creator</div>', unsafe_allow_html=True)
    
    if not config_status["fully_configured"]:
        st.warning("⚠️ Please configure your Meta API credentials above before creating posts.")
        return
    
    # Post type selection
    post_type = st.radio(
        "Select Platform",
        options=["facebook_only", "instagram_only", "both"],
        format_func=lambda x: {"facebook_only": "📘 Facebook Only", 
                               "instagram_only": "📷 Instagram Only", 
                               "both": "📘📷 Both Platforms"}[x],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Content input
    st.markdown("### Post Content")
    
    content_col1, content_col2 = st.columns([2, 1])
    
    with content_col1:
        post_caption = st.text_area(
            "Caption / Message",
            placeholder="Write your post content here...",
            height=150,
            key="meta_post_caption",
            label_visibility="collapsed"
        )
    
    with content_col2:
        st.markdown("**Preview**")
        if post_caption.strip():
            st.markdown(
                f'<div class="ai-preview-box">{post_caption[:500]}{"..." if len(post_caption) > 500 else ""}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="ai-preview-box" style="color:#6a6a6a;">Preview will appear here...</div>',
                unsafe_allow_html=True
            )
    
    # Image upload
    st.markdown("### Media (Optional)")
    uploaded_image = st.file_uploader(
        "Upload Image",
        type=["jpg", "jpeg", "png"],
        key="meta_post_image",
        help="Instagram requires an image. Facebook posts can be text-only."
    )
    
    # Save uploaded image temporarily
    image_path = None
    if uploaded_image:
        temp_dir = BASE_DIR / "temp_uploads"
        temp_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = temp_dir / f"meta_upload_{timestamp}.jpg"
        image_path.write_bytes(uploaded_image.getvalue())
        st.success(f"✅ Image uploaded: {uploaded_image.name}")
    
    # Additional options
    with st.expander("Advanced Options"):
        fb_link = st.text_input(
            "Facebook Link (Optional)",
            placeholder="https://...",
            help="Link to share on Facebook (Instagram doesn't support links in posts)"
        )
        
        ig_caption_different = st.checkbox("Use different caption for Instagram")
        ig_caption = None
        if ig_caption_different:
            ig_caption = st.text_area(
                "Instagram Caption",
                placeholder="Write a different caption for Instagram...",
                height=100,
                key="meta_ig_caption"
            )
    
    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 1])
    
    with btn_col1:
        preview_clicked = st.button(
            "👁️ Preview Post",
            key="meta_preview_btn",
            use_container_width=True,
        )
    
    with btn_col2:
        publish_clicked = st.button(
            "🚀 Publish Now",
            key="meta_publish_btn",
            use_container_width=True,
            type="primary",
            disabled=not post_caption.strip()
        )
    
    with btn_col3:
        if st.button("Clear", key="meta_clear_btn", use_container_width=True):
            for key in ["meta_post_caption", "meta_post_image", "meta_ig_caption"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Preview section
    if preview_clicked:
        st.markdown("### Post Preview")
        
        preview_cols = st.columns(2 if post_type != "instagram_only" else 1)
        
        if post_type in ["facebook_only", "both"]:
            with preview_cols[0]:
                st.markdown("**Facebook Preview**")
                st.markdown(
                    f'<div style="background:#1a1a1a;border:1px solid #39FF14;border-radius:8px;'
                    f'padding:16px;font-size:0.85rem;">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">'
                    f'<div style="width:32px;height:32px;border-radius:50%;background:#39FF14;"></div>'
                    f'<div><strong style="color:#39FF14;">Sikandar Tahir Agency</strong>'
                    f'<div style="color:#6a6a6a;font-size:0.75rem;">Just now</div></div></div>'
                    f'<div style="color:#C9D1C9;line-height:1.5;">{post_caption[:300]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if uploaded_image:
                    st.image(str(image_path), caption="Attached Image", use_container_width=True)
                if fb_link:
                    st.caption(f"🔗 Link: {fb_link}")
        
        if post_type in ["instagram_only", "both"] and uploaded_image:
            with preview_cols[-1]:
                st.markdown("**Instagram Preview**")
                st.image(str(image_path), caption="Post Image", use_container_width=True)
                ig_text = ig_caption if ig_caption_different and ig_caption else post_caption
                st.markdown(
                    f'<div style="background:#1a1a1a;border:1px solid #39FF14;border-radius:8px;'
                    f'padding:16px;font-size:0.85rem;">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">'
                    f'<div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);"></div>'
                    f'<div><strong style="color:#39FF14;">@sikandartahir_agency</strong></div></div>'
                    f'<div style="color:#C9D1C9;line-height:1.5;">{ig_text[:300]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    
    # Publish action
    if publish_clicked:
        if not post_caption.strip():
            st.error("Please enter a caption")
        elif post_type == "instagram_only" and not uploaded_image:
            st.error("Instagram posts require an image")
        else:
            # Import and use the Meta automation module
            try:
                from meta_automation import MetaAutomation, MetaAutomationError
                
                meta = MetaAutomation()
                
                with st.status("Publishing to Meta platforms...", expanded=True) as status:
                    results = {"success": 0, "errors": []}
                    
                    # Post to Facebook
                    if post_type in ["facebook_only", "both"]:
                        st.write("📘 Posting to Facebook...")
                        try:
                            fb_result = meta.post_to_facebook(
                                message=post_caption,
                                image_path=str(image_path) if image_path else None,
                                link=fb_link if post_type == "facebook_only" else None
                            )
                            st.success(f"✅ Facebook post published!")
                            st.caption(f"Post ID: {fb_result.get('post_id')}")
                            results["success"] += 1
                        except MetaAutomationError as e:
                            st.error(f"❌ Facebook error: {e}")
                            results["errors"].append(f"Facebook: {str(e)}")
                    
                    # Post to Instagram
                    if post_type in ["instagram_only", "both"] and uploaded_image:
                        st.write("📷 Posting to Instagram...")
                        try:
                            ig_caption_text = ig_caption if ig_caption_different and ig_caption else post_caption
                            ig_result = meta.post_to_instagram(
                                caption=ig_caption_text,
                                image_path=str(image_path)
                            )
                            st.success(f"✅ Instagram post published!")
                            st.caption(f"Post ID: {ig_result.get('post_id')}")
                            results["success"] += 1
                        except MetaAutomationError as e:
                            st.error(f"❌ Instagram error: {e}")
                            results["errors"].append(f"Instagram: {str(e)}")
                    
                    # Final status
                    if results["success"] > 0:
                        status.update(label=f"✅ Published to {results['success']} platform(s)!", state="complete")
                        st.toast(f"🎉 Successfully published to {results['success']} platform(s)!")
                        
                        # Clean up temp image
                        if image_path and image_path.exists():
                            image_path.unlink()
                    else:
                        status.update(label="❌ Publishing failed", state="error")
                        st.error("No posts were published successfully")
                
            except ImportError as e:
                st.error(f"❌ Meta automation module not found: {e}")
            except Exception as e:
                st.error(f"❌ Publishing failed: {e}")


def render_recent_posts_log():
    """Render the recent posts log from Obsidian vault."""
    st.markdown('<div class="section-header">Recent Posts Log</div>', unsafe_allow_html=True)
    
    social_posts_dir = VAULT_DIR / "Social_Posts"
    
    if not social_posts_dir.exists():
        st.info("📝 No posts logged yet. Your published posts will appear here.")
        return
    
    # Get recent post logs
    post_files = []
    for date_dir in sorted(social_posts_dir.iterdir(), reverse=True)[:7]:  # Last 7 days
        if date_dir.is_dir():
            post_files.extend(sorted(date_dir.glob("*.md"), reverse=True)[:3])  # 3 per day
    
    post_files = sorted(post_files, reverse=True)[:10]  # Last 10 posts
    
    if not post_files:
        st.info("📝 No posts logged yet.")
        return
    
    for post_file in post_files:
        content = post_file.read_text(encoding="utf-8")
        
        # Parse frontmatter
        platform = "Unknown"
        post_url = "#"
        timestamp = ""
        
        if "---" in content:
            frontmatter = content.split("---")[1]
            if "platform:" in frontmatter:
                platform = frontmatter.split("platform:")[1].split("\n")[0].strip()
            if "post_url:" in frontmatter:
                post_url = frontmatter.split("post_url:")[1].split("\n")[0].strip()
            if "time:" in frontmatter:
                timestamp = frontmatter.split("time:")[1].split("\n")[0].strip()
        
        # Get post content
        post_content = content.split("---")[-1] if "---" in content else content
        post_content = post_content[:200].replace("\n", " ") + "..." if len(post_content) > 200 else post_content
        
        platform_icon = {"facebook": "📘", "instagram": "📷"}.get(platform.lower(), "📱")
        
        st.markdown(
            f'<div class="card">'
            f'<div class="card-title">{platform_icon} {platform.title()} Post</div>'
            f'<div class="card-meta">📅 {timestamp} | 🔗 <a href="{post_url}" target="_blank" style="color:#39FF14;">View Post</a></div>'
            f'<div class="card-body">{post_content}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_social_media_commander():
    """
    Main function to render the complete Social Media Commander section.
    Call this from app.py to add the Meta automation UI.
    """
    st.markdown('<div class="section-header">Social Media Commander</div>', unsafe_allow_html=True)
    
    # Configuration section
    config_status = render_meta_config_section()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Post creator section
    render_post_creator(config_status)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent posts log
    render_recent_posts_log()


# For testing standalone
if __name__ == "__main__":
    st.set_page_config(page_title="Social Media Commander Test", layout="wide")
    render_social_media_commander()
