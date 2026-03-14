"""
Facebook Page Integration Page for Streamlit Dashboard
"""

import streamlit as st
from facebook_integration import (
    FacebookPageClient,
    validate_facebook_credentials,
    post_to_facebook_page,
    META_ACCESS_TOKEN,
    FB_PAGE_ID,
    META_APP_ID,
    META_APP_SECRET
)


def facebook_page():
    """Render the Facebook integration page"""
    st.title("📘 Facebook Page Automation")
    
    # Initialize session state
    if 'fb_client' not in st.session_state:
        st.session_state.fb_client = None
    if 'fb_validated' not in st.session_state:
        st.session_state.fb_validated = False
    if 'fb_page_info' not in st.session_state:
        st.session_state.fb_page_info = None
    
    # Check credentials
    st.sidebar.header("Credentials Status")
    
    creds_ok = True
    if not META_ACCESS_TOKEN:
        st.sidebar.error("❌ META_ACCESS_TOKEN missing")
        creds_ok = False
    else:
        st.sidebar.success("✅ META_ACCESS_TOKEN set")
    
    if not FB_PAGE_ID:
        st.sidebar.error("❌ FB_PAGE_ID missing")
        creds_ok = False
    else:
        st.sidebar.success("✅ FB_PAGE_ID set")
    
    if not META_APP_ID:
        st.sidebar.warning("⚠️ META_APP_ID missing (needed for token debug)")
    else:
        st.sidebar.success("✅ META_APP_ID set")
    
    if not META_APP_SECRET:
        st.sidebar.warning("⚠️ META_APP_SECRET missing (needed for token debug)")
    else:
        st.sidebar.success("✅ META_APP_SECRET set")
    
    if not creds_ok:
        st.error("⚠️ Missing required credentials. Please check your `.env` file.")
        st.markdown("""
        ### Required Environment Variables:
        ```env
        META_ACCESS_TOKEN=your_page_access_token
        FB_PAGE_ID=your_facebook_page_id
        META_APP_ID=your_app_id
        META_APP_SECRET=your_app_secret
        ```
        """)
        return
    
    # Validate button
    if not st.session_state.fb_validated:
        if st.sidebar.button("🔐 Validate Credentials", use_container_width=True):
            with st.spinner("Validating..."):
                is_valid, msg = validate_facebook_credentials()
                if is_valid:
                    st.session_state.fb_validated = True
                    st.session_state.fb_client = FacebookPageClient()
                    
                    # Get page info
                    st.session_state.fb_page_info = st.session_state.fb_client.get_page_info()
                    
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    else:
        st.sidebar.success("✅ Credentials Validated")
        
        if st.session_state.fb_page_info:
            st.sidebar.info(f"""
            **Page:** {st.session_state.fb_page_info.get('name', 'Unknown')}
            
            **Category:** {st.session_state.fb_page_info.get('category', 'Unknown')}
            
            **Followers:** {st.session_state.fb_page_info.get('followers_count', 'N/A')}
            """)
        
        if st.sidebar.button("🔄 Refresh Page Info", use_container_width=True):
            st.session_state.fb_page_info = st.session_state.fb_client.get_page_info()
            st.rerun()
    
    # Main content
    if not st.session_state.fb_validated:
        st.info("👈 Click 'Validate Credentials' in the sidebar to get started")
        
        st.markdown("""
        ### Setup Instructions:
        
        1. **Create a Meta App:**
           - Go to [Meta for Developers](https://developers.facebook.com/)
           - Create a new app
           - Add "Facebook Login" product
        
        2. **Get Page Access Token:**
           - Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
           - Select your app
           - Get User Token with permissions: `pages_manage_posts`, `pages_read_engagement`
           - Exchange for Page Access Token
        
        3. **Get Page ID:**
           - Your Page ID is in the Graph API Explorer
           - Or find it in your Page's About section
        
        4. **Add to `.env` file:**
           ```env
           META_ACCESS_TOKEN=EAAG...
           FB_PAGE_ID=123456789
           META_APP_ID=your_app_id
           META_APP_SECRET=your_app_secret
           ```
        """)
        return
    
    # Create Post Section
    st.subheader("📝 Create Post")
    
    with st.form("facebook_post_form"):
        message = st.text_area(
            "Post Message",
            placeholder="What's on your mind?",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            link = st.text_input("Link (optional)", placeholder="https://...")
        with col2:
            photo_url = st.text_input("Photo URL (optional)", placeholder="https://...")
        
        submitted = st.form_submit_button("🚀 Post to Facebook", use_container_width=True)
        
        if submitted:
            if not message:
                st.error("Please enter a message")
            else:
                with st.spinner("Posting to Facebook..."):
                    try:
                        client = st.session_state.fb_client
                        success, result = client.post_to_page(
                            message=message,
                            link=link if link else None,
                            photo_url=photo_url if photo_url else None
                        )
                        
                        if success:
                            st.success(f"✅ {result}")
                            st.balloons()
                        else:
                            st.error(f"❌ {result}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # Recent Posts Section
    st.divider()
    st.subheader("📋 Recent Posts")
    
    if st.button("🔄 Load Recent Posts", use_container_width=True):
        with st.spinner("Loading posts..."):
            posts = st.session_state.fb_client.get_recent_posts(limit=10)
            if posts:
                st.session_state.fb_recent_posts = posts
            else:
                st.warning("Could not load posts")
    
    if 'fb_recent_posts' in st.session_state:
        for post in st.session_state.fb_recent_posts:
            with st.expander(f"📌 {post.get('message', 'No text')[:100]}..."):
                st.write(f"**Created:** {post.get('created_time', 'Unknown')}")
                st.write(f"**Post ID:** {post.get('id', 'Unknown')}")
                
                if 'permalink_url' in post:
                    st.link_button("View Post", post['permalink_url'])
                
                # Engagement
                likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                st.write(f"👍 {likes} likes | 💬 {comments} comments")
    
    # API Reference
    with st.expander("📚 API Reference"):
        st.markdown("""
        ### Python Usage:
        
        ```python
        from facebook_integration import post_to_facebook_page
        
        # Simple text post
        success, msg = post_to_facebook_page("Hello World!")
        
        # Post with link
        success, msg = post_to_facebook_page(
            "Check this out!",
            link="https://example.com"
        )
        
        # Post with photo
        success, msg = post_to_facebook_page(
            "Beautiful sunset!",
            photo_url="https://example.com/image.jpg"
        )
        ```
        
        ### Required Permissions:
        - `pages_manage_posts` - Create posts
        - `pages_read_engagement` - Read page data
        - `pages_show_list` - List pages
        
        ### Graph API Endpoint:
        ```
        POST /v21.0/{page-id}/feed
        Params: message, link, url (photo)
        ```
        """)
    
    # Debug section
    with st.expander("🐛 Debug Info"):
        st.write("**Environment Variables:**")
        st.code(f"""
META_ACCESS_TOKEN: {'Set' if META_ACCESS_TOKEN else 'Missing'}
FB_PAGE_ID: {FB_PAGE_ID or 'Missing'}
META_APP_ID: {META_APP_ID or 'Missing'}
META_APP_SECRET: {'Set' if META_APP_SECRET else 'Missing'}
        """)


if __name__ == '__main__':
    facebook_page()