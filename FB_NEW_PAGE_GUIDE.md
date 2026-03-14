# Facebook Page Access Token - Quick Setup for New Pages

## Your Situation
You created a new Facebook Page but can't get Page Access Token.

## The Problem
New pages need special setup. Facebook doesn't give Page tokens unless:
1. Your Facebook App is **Live** (not in Development mode)
2. You're **admin** of both the App AND the Page
3. You have the right **permissions**

## Quick Solution (5 minutes)

### Step 1: Make Your App Live
1. Go to: https://developers.facebook.com/apps/
2. Select your app
3. Go to **Settings** → **Basic**
4. Find **"App Mode"** at the top
5. Click **"Switch to Live"** (if it says Development)
6. Click **"Confirm"**

### Step 2: Add Yourself as Admin
1. In your app, go to **Roles** → **Administrators** (left sidebar)
2. Click **"Add Facebook User"**
3. Select **your Facebook account**
4. Click **"Assign"**

### Step 3: Get Token
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select **your app** from the dropdown (top)
3. Click **"Get Token"** → **"Get Page Access Token"**
4. Your page should now appear in the list!
5. **Click on your page**
6. **Copy the token** that appears

### Step 4: Update .env
1. Open `.env` file in your project
2. Replace the `META_ACCESS_TOKEN=...` line with your new token
3. Save the file

### Step 5: Test
```bash
python test_facebook_post.py
```

---

## If Your Page Still Doesn't Appear

### Option A: Use User Token First
1. In Graph API Explorer, click "Get Token" → "Get User Access Token"
2. Select these permissions:
   - ✓ pages_show_list
   - ✓ pages_read_engagement  
   - ✓ pages_manage_posts
3. Click "Generate Token"
4. Copy the User Token
5. Run: `python facebook_new_page_setup.py`
6. Paste your User Token when prompted
7. It will extract the Page Token for you

### Option B: Direct API Call
1. Get a User Token with pages_* permissions (above)
2. Go to this URL (replace YOUR_USER_TOKEN):
```
https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_USER_TOKEN
```
3. You'll see your pages with their access tokens
4. Copy the `access_token` for your page

---

## Your Current Info
- **Page ID**: 4449990781989754
- **App ID**: 4449990781989754 (using Page as App)

**Note**: You're using your Page ID as App ID. You might need to create a separate Facebook App.
