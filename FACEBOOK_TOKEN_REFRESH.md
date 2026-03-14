# Facebook Token Refresh Guide

## Issue
Your Facebook Page Access Token has expired (expired on March 10, 2026).

## How to Get a New Token

### Option 1: Facebook Graph API Explorer (Quick - 1 hour token)

1. Go to: https://developers.facebook.com/tools/explorer/

2. Select your app (or create a new one)

3. Click "Get Token" → "Get Page Access Token"

4. Select your page

5. Copy the token

6. Update your `.env` file:
   ```
   META_ACCESS_TOKEN=your_new_token_here
   ```

### Option 2: Long-Lived Token (60 days)

1. Get a short-lived token from Graph API Explorer

2. Go to: https://developers.facebook.com/tools/debug/access_token/

3. Click "Debug" to see your token details

4. Click "Extend Access Token"

5. Copy the new long-lived token

6. Update your `.env` file

### Option 3: Get Page Token from User Token

1. Get a user token with these permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`

2. Make this API call:
   ```
   GET https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_USER_TOKEN
   ```

3. Copy the `access_token` from your page in the response

4. Update your `.env` file

## Required Permissions

Make sure your token has these permissions:
- ✅ `pages_show_list`
- ✅ `pages_read_engagement`
- ✅ `pages_manage_posts`

## After Updating .env

1. Restart your Streamlit app
2. Run the Facebook test again:
   ```bash
   python test_facebook_post.py
   ```

## Find Your Page ID

If you also need your Page ID:
- Go to: https://findmyfbid.in/
- Or look in your Facebook Page URL

## Current Configuration

Your current Page ID: `4449990781989754`
