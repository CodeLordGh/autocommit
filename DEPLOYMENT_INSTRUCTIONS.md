# Deployment Instructions for Auto Commit App

## Issue: GitHub Authentication Redirect Problem

When users click "Sign in with GitHub" in the login form and are redirected to the GitHub authentication page, after successful authentication, they encounter a 404 error. This happens because the backend is hardcoded to redirect to `http://localhost:5173/dashboard` after authentication, which doesn't exist in production.

## Solution

### 1. Update Render Backend Environment Variables

Add or update the following environment variables in your Render backend service:

```
FRONTEND_URL=https://autocommit-rac3.vercel.app
```

### 2. Update the Backend Code

Since we can't directly edit the deployed code on Render, you'll need to update your local code and redeploy:

1. Open `server/app.py`
2. Find line 120 (the GitHub callback function)
3. Replace:
   ```python
   return redirect("http://localhost:5173/dashboard")
   ```
   
   With:
   ```python
   frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
   return redirect(f"{frontend_url}/dashboard")
   ```

4. Commit and push these changes
5. Redeploy your backend to Render

### 3. Update GitHub OAuth Settings

Make sure your GitHub OAuth app settings have the correct callback URL:

1. Go to your GitHub Developer Settings
2. Select the OAuth App you're using for this project
3. Update the "Authorization callback URL" to:
   ```
   https://autocommit-2d1m.onrender.com/api/github/callback
   ```

### 4. Verify CORS Settings

Ensure your backend has the correct CORS settings to allow requests from your Vercel frontend:

1. Make sure the `ALLOWED_ORIGINS` environment variable on Render includes your Vercel domain:
   ```
   ALLOWED_ORIGINS=http://localhost:5173,https://autocommit-rac3.vercel.app
   ```

## Testing the Fix

After implementing these changes:

1. Visit your Vercel frontend: https://autocommit-rac3.vercel.app
2. Click "Sign in with GitHub"
3. Complete the GitHub authentication
4. You should be redirected back to your dashboard page without any 404 errors

## Troubleshooting

If you still encounter issues:

1. Check the browser console for any errors
2. Verify that all environment variables are set correctly
3. Ensure your GitHub OAuth app settings are correct
4. Check the Render logs for any backend errors during the authentication process