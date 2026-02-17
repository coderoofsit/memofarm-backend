# Memofarm Backend - Render Deployment Guide

## Quick Deploy to Render

### 1. Push to GitHub/GitLab
```bash
cd backend
git init
git add .
git commit -m "Initial backend commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your repository
4. Configure:

**Basic Settings:**
- **Name:** `memofarm-api`
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** `backend` (if backend is subfolder) or leave empty
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn run:app`

**Instance Type:**
- Free tier or Starter ($7/month)

### 3. Environment Variables

Add these in Render Dashboard → Environment tab:

```bash
# Required
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/memofarm?retryWrites=true&w=majority
DB_NAME=memofarm
SECRET_KEY=<generate-random-secret-key-here>
FLASK_ENV=production

# Firebase (Optional - for token verification)
FIREBASE_PROJECT_ID=your-firebase-project-id

# API Configuration
API_PREFIX=/api
PORT=10000

# CORS - Add your Flutter app and admin panel domains
CORS_ORIGINS=https://your-app.com,https://admin.your-app.com

# Optional: Google/Apple OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=com.coderoof.memofarm
APPLE_TEAM_ID=your-apple-team-id
APPLE_KEY_ID=your-apple-key-id
```

### 4. Deploy

Click **Create Web Service** - Render will automatically:
- Install dependencies
- Start the app with gunicorn
- Provide a URL like: `https://memofarm-api.onrender.com`

---

## Important: Update Flutter App

After deployment, update your Flutter app with the production URL:

**File:** `lib/core/constants/api_constants.dart`
```dart
class ApiConstants {
  static const String baseUrl = 'https://memofarm-api.onrender.com/api';
  // ...
}
```

---

## Important: Update Admin API Key

**File:** `backend/app/routes/admin.py` (line 8)

Change from:
```python
ADMIN_API_KEY = "memofarm_admin_2026_secure_key"
```

To a strong random key:
```python
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "fallback-key")
```

Then add to Render environment variables:
```
ADMIN_API_KEY=<generate-strong-random-key>
```

Generate key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Health Check

Test your deployment:
```bash
curl https://memofarm-api.onrender.com/health
# Should return: {"status": "ok", "message": "Memofarm API is running"}

curl https://memofarm-api.onrender.com/api/italian-medicines/stats
# Should return Italian medicines count
```

---

## Troubleshooting

### Build Failed
- Check Python version (Render uses Python 3.11 by default)
- Verify all dependencies in `requirements.txt`
- Check build logs in Render dashboard

### App Crashed
- Check logs in Render dashboard
- Verify MongoDB URI is correct
- Ensure PORT environment variable is set
- Check MONGODB_URI includes `?retryWrites=true&w=majority`

### CORS Errors
- Add your frontend domains to `CORS_ORIGINS`
- Include protocol: `https://your-domain.com`
- Separate multiple domains with commas (no spaces)

### MongoDB Connection Failed
- Verify MongoDB Atlas allows connections from anywhere (0.0.0.0/0)
- Or add Render's IP ranges to MongoDB whitelist
- Check connection string format

---

## Free Tier Limitations

Render Free Tier:
- ✅ 750+ hours/month
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold start takes 30-60 seconds
- 💡 Upgrade to Starter ($7/month) for always-on service

---

## Post-Deployment Checklist

- [ ] Update Flutter app with production API URL
- [ ] Change admin API key to secure random string
- [ ] Configure CORS_ORIGINS with your domains
- [ ] Test all API endpoints
- [ ] Monitor logs for errors
- [ ] Set up MongoDB backup (Atlas automated backups)
- [ ] Consider enabling Render persistent disk if needed

---

## Monitoring

Access logs:
- Render Dashboard → Your Service → Logs
- Real-time log streaming
- Search and filter capabilities

---

## Cost Estimate

**Free Tier:**
- Render: Free
- MongoDB Atlas: Free (512MB)
- Total: **$0/month**

**Production:**
- Render Starter: $7/month
- MongoDB Atlas M10: $57/month (1.5GB RAM, 10GB storage)
- Total: **~$64/month**

---

## Alternative: Deploy with render.yaml

Create `render.yaml` in backend folder:

```yaml
services:
  - type: web
    name: memofarm-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: MONGODB_URI
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: API_PREFIX
        value: /api
```

Then push and Render will auto-detect and deploy.

---

**Need Help?** Check Render documentation: https://render.com/docs/web-services
