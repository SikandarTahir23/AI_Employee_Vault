# 📘 Meta (Facebook & Instagram) Automation Setup Guide

**Sikandar Tahir | AI Agency Dashboard**

---

## 🎯 Overview

The Social Media Commander enables you to post to **Facebook Pages** and **Instagram Business accounts** directly from the AI Employee Vault dashboard. Every post is automatically logged to your Obsidian vault for knowledge graph tracking.

---

## 📋 Prerequisites

1. **Meta Developer Account** - Free to create at [developers.facebook.com](https://developers.facebook.com)
2. **Facebook Business Page** - You must admin a Facebook Page
3. **Instagram Business Account** - Connected to your Facebook Page
4. **Meta App** - Created in Meta Developer Dashboard

---

## 🔧 Step-by-Step Setup

### Step 1: Create Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/apps)
2. Click **Create App**
3. Select **Business** as app type
4. Fill in:
   - **App Name**: `Sikandar Tahir Agency Dashboard`
   - **App Contact Email**: Your email
5. Click **Create App**

### Step 2: Add Products

1. In your app dashboard, find **Instagram Graph API** and click **Set Up**
2. Also add **Facebook Login** product
3. Configure Facebook Login:
   - Set **Valid OAuth Redirect URIs** to: `https://localhost`
   - Enable **Embedded Browser OAuth**

### Step 3: Generate Access Token

1. Go to **Tools > Graph API Explorer**
2. Select your app from dropdown
3. Click **Generate Access Token**
4. Grant these permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
   - `publish_to_groups`

5. Copy the generated token (starts with `EAAG...`)

### Step 4: Get Your IDs

#### Facebook Page ID:
- Visit [findmyfbid.in](https://findmyfbid.in/)
- Or go to your Page > About section
- Copy the Page ID (numeric string)

#### Instagram Business Account ID:
1. In Graph API Explorer, run:
   ```
   GET /me/accounts?fields=instagram_business_account
   ```
2. Find your page in results
3. Copy the `instagram_business_account.id` value

### Step 5: Configure in Dashboard

1. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

2. Navigate to **Social Media Commander** section

3. Click **Configure Meta API Credentials**

4. Enter:
   - **Meta Access Token**: Token from Step 3
   - **Facebook Page ID**: From Step 4
   - **Instagram Business Account ID**: From Step 4

5. Click **Save Configuration**

---

## ✅ Verify Setup

Run the test command:

```bash
python meta_automation.py
```

You should see:
```
============================================================
  META AUTOMATION TEST
  Sikandar Tahir | AI Agency Dashboard
============================================================

[1] Validating credentials...
    Result: Facebook: ✓ | Instagram: ✓

[OK] Credentials validated!

[2] Fetching account info...

    Facebook Page:
      - Name: Sikandar Tahir Agency
      - Username: @sikandartahir
      - Followers: 1234

    Instagram Account:
      - Username: @sikandartahir_agency
      - Followers: 5678
      - Posts: 42
```

---

## 🚀 Using the Social Media Commander

### Create a Post

1. Go to **Social Media Commander** in dashboard
2. Select platform: Facebook, Instagram, or Both
3. Write your caption in the text area
4. (Optional) Upload an image (required for Instagram)
5. Click **Preview Post** to see how it looks
6. Click **Publish Now** to post live

### Post Types Supported

| Platform | Text Only | With Image | With Link |
|----------|-----------|------------|-----------|
| Facebook | ✅ | ✅ | ✅ |
| Instagram | ❌ | ✅ | ❌ |

**Note:** Instagram requires an image for all posts. Links in captions are not clickable.

---

## 📚 Obsidian Vault Integration

Every successful post creates a markdown log file in:

```
AI_EMPLOYEE_VAULT/Social_Posts/YYYY-MM-DD/Meta_<platform>_<timestamp>.md
```

Each log includes:
- Post URL
- Timestamp
- Full content
- Platform (Facebook/Instagram)
- Post ID

Example log:

```markdown
---
type: social_post
platform: facebook
status: published
date: 2026-03-10
time: 14:30:00
tags:
  - social_media
  - meta
  - facebook
  - sikandar_tahir_agency
---

# Social Media Post Log

## Platform
**Facebook**

## Timestamp
📅 **Date:** 2026-03-10  
⏰ **Time:** 14:30:00

## Post URL
🔗 [View Post](https://www.facebook.com/...)

## Post ID
`123456789012345_678901234567890`

## Content
```
Excited to announce our new AI dashboard service!
```

## Metadata
- **Success:** true
- **API Version:** v18.0
- **Logged by:** AI Employee Vault
```

---

## 🔒 Security Best Practices

1. **Never commit .env file** - It's gitignored by default
2. **Use long-lived tokens** - Valid for 60 days
3. **Rotate tokens regularly** - Generate new ones monthly
4. **Limit permissions** - Only grant necessary API permissions
5. **Monitor API usage** - Check Meta Developer Dashboard

---

## 🐛 Troubleshooting

### "Credentials not configured" error
- Run `python meta_automation.py` to test
- Re-enter credentials in dashboard
- Ensure token hasn't expired

### Instagram posting fails
- Verify Instagram is a **Business** account (not Creator)
- Ensure Instagram is connected to Facebook Page
- Image must be publicly accessible URL (local files need upload)

### Facebook posting fails
- Verify you're admin of the Page
- Check token has `pages_manage_posts` permission
- Ensure Page ID is correct

### Token expired
- Generate new token in Graph API Explorer
- Update in dashboard configuration
- Tokens expire after 60 days

---

## 📞 Support

For issues or questions:
1. Check Meta Developer Documentation: [developers.facebook.com/docs](https://developers.facebook.com/docs)
2. Review API error messages in dashboard console
3. Check Obsidian logs for post history

---

**Built for Sikandar Tahir | AI Agency Dashboard**  
*Part of the AI Employee Vault ecosystem*
