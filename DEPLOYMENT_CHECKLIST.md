# Render Deployment Checklist

## Pre-Deployment

### 1. Code Preparation
- [x] Admin API key reads from environment variable
- [x] CORS configuration supports environment variable
- [x] Port reads from environment variable
- [x] Production config exists in config.py
- [x] .gitignore includes .env file
- [x] render.yaml created for easy deployment
- [x] requirements.txt is up to date

### 2. MongoDB Atlas Setup
- [ ] MongoDB Atlas cluster created
- [ ] Database user created with password
- [ ] Network access allows 0.0.0.0/0 (or Render IPs)
- [ ] Connection string copied (format: `mongodb+srv://user:password@cluster.mongodb.net/memofarm`)

### 3. Push to Git
```bash
cd backend
git init
git add .
git commit -m "Prepare for Render deployment"
git remote add origin <your-repo-url>
git push -u origin main
```

---

## Render Setup

### 1. Create Web Service
1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Connect your Git repository
4. Select your repo and branch

### 2. Configure Service
**Name:** `memofarm-api`
**Region:** Oregon (or closest to users)
**Branch:** `main`
**Root Directory:** `backend` (or blank if backend is root)
**Runtime:** `Python 3`
**Build Command:** `pip install -r requirements.txt`
**Start Command:** `gunicorn run:app`
**Instance Type:** Free or Starter

### 3. Environment Variables
Add these in Environment tab:

#### Required:
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/memofarm?retryWrites=true&w=majority
DB_NAME=memofarm
SECRET_KEY=<generate-with-command-below>
FLASK_ENV=production
API_PREFIX=/api
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Admin Panel:
```bash
ADMIN_API_KEY=<generate-with-command-below>
```

Generate ADMIN_API_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### CORS (Update with your domains):
```bash
CORS_ORIGINS=https://your-flutter-app.com,https://admin.your-app.com
```

#### Optional (if using Firebase):
```bash
FIREBASE_PROJECT_ID=your-firebase-project-id
```

### 4. Deploy
- Click **Create Web Service**
- Wait for build to complete (2-3 minutes)
- Check logs for any errors

---

## Post-Deployment

### 1. Test API
```bash
# Health check
curl https://your-app.onrender.com/health

# Get stats
curl https://your-app.onrender.com/api/italian-medicines/stats
```

### 2. Update Flutter App
**File:** `lib/core/constants/api_constants.dart`
```dart
static const String baseUrl = 'https://your-app.onrender.com/api';
```

### 3. Update Admin Panel
**File:** `src/services/adminApi.js`
```javascript
const API_BASE = 'https://your-app.onrender.com/api/admin';
const ADMIN_API_KEY = '<your-generated-admin-key>';
```

### 4. Test Admin Endpoints
```bash
curl -H "X-Admin-Key: <your-admin-key>" \
  https://your-app.onrender.com/api/admin/stats
```

---

## Troubleshooting

### Build Failed
- [ ] Check Python version compatibility
- [ ] Verify requirements.txt is valid
- [ ] Review build logs in Render dashboard

### App Crashed on Start
- [ ] Verify MONGODB_URI is correct
- [ ] Check all required env vars are set
- [ ] Review runtime logs
- [ ] Ensure gunicorn is in requirements.txt

### Database Connection Error
- [ ] MongoDB Atlas network access allows Render
- [ ] Connection string includes `?retryWrites=true&w=majority`
- [ ] Database user has correct permissions
- [ ] Database name matches DB_NAME env var

### CORS Errors
- [ ] CORS_ORIGINS includes your frontend domain
- [ ] Protocol (https://) is included
- [ ] No trailing slashes in domains
- [ ] Multiple domains separated by commas (no spaces)

---

## Monitoring

### Check Logs
- Render Dashboard → Your Service → Logs
- Filter by error level
- Download logs if needed

### Performance
- Monitor response times
- Check memory usage
- Watch for cold starts (Free tier)

---

## Upgrade Path (When Ready)

**Free Tier Limits:**
- Spins down after 15 minutes inactivity
- Cold start: 30-60 seconds
- 512MB RAM

**Starter Plan ($7/month):**
- Always on (no cold starts)
- 512MB RAM
- Better for production

**To Upgrade:**
- Render Dashboard → Your Service → Settings
- Change Instance Type to "Starter"
- Save changes

---

## Security Checklist

- [ ] SECRET_KEY is random and secure
- [ ] ADMIN_API_KEY is random and secure
- [ ] MongoDB credentials are secure
- [ ] .env file is gitignored
- [ ] CORS_ORIGINS limited to your domains (not *)
- [ ] Firebase credentials secured (if used)

---

## Success Indicators

✅ Build completes without errors
✅ Service status shows "Live"
✅ Health endpoint returns 200 OK
✅ Italian medicines stats returns count
✅ Flutter app can fetch data
✅ Admin panel can authenticate and fetch data

---

## Your Deployment URLs

**API URL:** `https://_____________________.onrender.com`
**Health Check:** `https://_____________________.onrender.com/health`
**Admin Stats:** `https://_____________________.onrender.com/api/admin/stats`

**Deployed on:** _______________
**Deployed by:** _______________

---

## Support Resources

- Render Docs: https://render.com/docs/web-services
- Python on Render: https://render.com/docs/deploy-flask
- MongoDB Atlas: https://docs.atlas.mongodb.com/
- API Documentation: See ADMIN_API_REFERENCE.md

---

**Status:** [ ] Not Started  [ ] In Progress  [ ] Deployed  [ ] Tested  [ ] Production Ready
