# Deployment Guide - Whiskey Sensory Training App

**Last Updated**: January 29, 2026
**Status**: Production Ready
**Version**: 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Architecture](#deployment-architecture)
4. [Backend Deployment (Railway)](#backend-deployment-railway)
5. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
6. [Database Setup](#database-setup)
7. [Environment Configuration](#environment-configuration)
8. [Custom Domain Setup](#custom-domain-setup)
9. [SSL/HTTPS Configuration](#sslhttps-configuration)
10. [Monitoring & Analytics](#monitoring--analytics)
11. [Post-Deployment Verification](#post-deployment-verification)
12. [Troubleshooting](#troubleshooting)
13. [Cost Estimates](#cost-estimates)
14. [Security Best Practices](#security-best-practices)
15. [Rollback Plan](#rollback-plan)

---

## Overview

This guide covers deploying the Whiskey Sensory Training App to production. The recommended architecture uses:

- **Backend**: Railway (Flask API + SQLite)
- **Frontend**: Vercel (React SPA)
- **DNS**: Cloudflare (optional, for caching and DDoS protection)
- **Analytics**: Plausible or Simple Analytics (privacy-focused)
- **Monitoring**: Sentry (error tracking)

### Why This Stack?

- **Railway**: Excellent for Python apps, built-in SQLite support, automatic HTTPS
- **Vercel**: Best-in-class React deployment, automatic builds from Git, global CDN
- **SQLite**: No external database needed (16MB production database is well within limits)
- **Free Tier Friendly**: Both Railway and Vercel have generous free tiers

---

## Prerequisites

### Required Accounts

1. **GitHub Account** (to host code repository)
2. **Railway Account** (backend hosting)
   - Sign up at [railway.app](https://railway.app)
   - Free tier: $5/month credits (sufficient for MVP)
3. **Vercel Account** (frontend hosting)
   - Sign up at [vercel.com](https://vercel.com)
   - Free tier: Unlimited bandwidth for personal projects
4. **Domain Registrar** (optional, for custom domain)
   - Namecheap, Cloudflare, Google Domains, etc.

### Development Tools

- Git (for version control)
- GitHub CLI (optional, for easier deployment)
- Node.js 18+ (for local frontend testing)
- Python 3.8+ (for local backend testing)

---

## Deployment Architecture

```
┌─────────────────┐
│   Cloudflare    │ (Optional: CDN, caching, DDoS protection)
│   DNS + Proxy   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Vercel │ │Railway│
│React  │ │Flask  │
│SPA    │ │API    │
└───────┘ └───┬───┘
              │
         ┌────▼────┐
         │ SQLite  │
         │Database │
         └─────────┘
```

### Traffic Flow

1. User visits `yourapp.com` (Vercel-hosted frontend)
2. Frontend makes API calls to `api.yourapp.com` (Railway-hosted backend)
3. Backend queries SQLite database (stored on Railway's persistent volume)
4. Response flows back through the chain

---

## Backend Deployment (Railway)

### Step 1: Prepare Repository

1. **Create GitHub Repository**
   ```bash
   # If not already a git repo
   cd /path/to/whiskey-scraper
   git init
   git add .
   git commit -m "Initial commit - production ready"

   # Create GitHub repo (using gh CLI)
   gh repo create whiskey-training-app --public --source=. --remote=origin --push
   ```

2. **Add `.gitignore`**
   Create `.gitignore` if not present:
   ```
   # Python
   __pycache__/
   *.py[cod]
   venv/
   env/

   # Environment variables
   .env
   .env.local

   # Database backups (keep production db)
   backups/
   archive/

   # Node
   node_modules/
   frontend/dist/
   frontend/node_modules/

   # IDE
   .vscode/
   .idea/
   *.swp

   # OS
   .DS_Store
   Thumbs.db
   ```

### Step 2: Create Railway Project

1. **Connect GitHub to Railway**
   - Go to [railway.app/new](https://railway.app/new)
   - Click "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub
   - Select `whiskey-training-app` repository

2. **Configure Build Settings**
   Railway auto-detects Python, but verify:

   **Build Command**: (automatically detected from `requirements.txt`)
   ```
   pip install -r requirements.txt
   ```

   **Start Command**:
   ```
   gunicorn app:app
   ```

3. **Add `gunicorn` to requirements**
   Update `/requirements.txt`:
   ```
   Flask==2.3.2
   Flask-CORS==4.0.0
   gunicorn==21.2.0
   ```

4. **Create Procfile** (optional, Railway auto-detects)
   Create `/Procfile`:
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT
   ```

### Step 3: Configure Environment Variables

In Railway dashboard:

```bash
# Flask configuration
FLASK_ENV=production
FLASK_APP=app.py

# Database path (Railway provides persistent disk)
DB_PATH=/app/databases/whiskey_production.db

# Port (Railway provides this automatically)
PORT=5000
```

### Step 4: Setup Persistent Storage

1. **Add Volume** in Railway:
   - Go to your service settings
   - Click "Variables" → "Add Volume"
   - Mount Path: `/app/databases`
   - Size: 1GB (sufficient for 16MB database)

2. **Upload Production Database**

   **Option A: Using Railway CLI**
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli

   # Login and link project
   railway login
   railway link

   # Upload database
   railway run python3 -c "import shutil; shutil.copy('databases/whiskey_production.db', '/app/databases/whiskey_production.db')"
   ```

   **Option B: Include in Repository** (simpler)
   - Commit the database to Git (it's only 16MB)
   - Railway will automatically copy it during deployment
   - Update `.gitignore` to ensure databases aren't ignored:
     ```
     # Don't ignore production database
     !databases/whiskey_production.db
     !databases/whiskey_reviews.db
     ```

### Step 5: Deploy

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Railway Auto-Deploys**
   - Railway watches your `main` branch
   - Automatic deployment on every push
   - Check deployment logs in Railway dashboard

3. **Get Backend URL**
   - Railway provides: `https://your-app.up.railway.app`
   - Note this URL for frontend configuration

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

1. **Update API URL**

   Edit `/frontend/src/config.js` (create if doesn't exist):
   ```javascript
   // config.js
   const config = {
     API_URL: import.meta.env.VITE_API_URL || 'http://localhost:5001'
   };

   export default config;
   ```

2. **Update API Calls**

   Edit `/frontend/src/services/api.js` (create if doesn't exist):
   ```javascript
   import config from '../config';

   const API_BASE_URL = config.API_URL;

   export const searchWhiskeys = async (query) => {
     const response = await fetch(
       `${API_BASE_URL}/api/whiskeys/search?q=${encodeURIComponent(query)}`
     );
     return response.json();
   };

   export const getQuiz = async (whiskeyId) => {
     const response = await fetch(`${API_BASE_URL}/api/quiz/${whiskeyId}`);
     return response.json();
   };
   ```

3. **Update Components**

   Replace hardcoded `localhost:5001` URLs in:
   - `/frontend/src/pages/HomePage.jsx`
   - `/frontend/src/pages/QuizPage.jsx`
   - `/frontend/src/pages/ResultsPage.jsx`

   With:
   ```javascript
   import { searchWhiskeys, getQuiz } from '../services/api';
   ```

### Step 2: Deploy to Vercel

1. **Install Vercel CLI** (optional)
   ```bash
   npm i -g vercel
   ```

2. **Deploy via Vercel Dashboard** (recommended)
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Framework Preset: **Vite**
   - Root Directory: **frontend**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Add Environment Variables** in Vercel

   In Vercel project settings → Environment Variables:
   ```
   VITE_API_URL=https://your-app.up.railway.app
   ```

   **Important**: Add this to all environments (Production, Preview, Development)

4. **Deploy**
   - Click "Deploy"
   - Vercel builds and deploys automatically
   - Get frontend URL: `https://your-app.vercel.app`

### Step 3: Configure CORS

Update `/app.py` backend to allow your Vercel frontend:

```python
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS for production
CORS(app, origins=[
    "http://localhost:3000",  # Local development
    "https://your-app.vercel.app",  # Production frontend
    "https://yourapp.com"  # Custom domain (if applicable)
])
```

Redeploy backend after updating CORS.

---

## Database Setup

### Production Database Checklist

- [x] **Database File**: `/databases/whiskey_production.db` (16MB)
- [x] **Whiskeys**: 2,125 total, 2,109 quiz-ready (99.2%)
- [x] **Reviews**: 2,164 reviews processed
- [x] **Descriptors**: 81 active descriptors
- [x] **Extractions**: 30,808 descriptor tags

### Database Backup Strategy

1. **Automated Backups** (Railway)
   - Railway doesn't auto-backup volumes
   - Set up GitHub Actions for scheduled backups

2. **Manual Backup Script**
   Create `/scripts/backup_db.sh`:
   ```bash
   #!/bin/bash
   # Backup production database

   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="backups"
   DB_FILE="databases/whiskey_production.db"

   mkdir -p $BACKUP_DIR
   cp $DB_FILE $BACKUP_DIR/whiskey_production_$DATE.db

   echo "✓ Backup created: $BACKUP_DIR/whiskey_production_$DATE.db"

   # Keep only last 7 backups
   ls -t $BACKUP_DIR/whiskey_production_*.db | tail -n +8 | xargs rm -f
   ```

3. **GitHub Actions Backup** (recommended)
   Create `/.github/workflows/backup-db.yml`:
   ```yaml
   name: Backup Database

   on:
     schedule:
       - cron: '0 2 * * *'  # Daily at 2 AM UTC
     workflow_dispatch:  # Manual trigger

   jobs:
     backup:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Download database from Railway
           run: |
             # Use Railway CLI to download database
             railway run python3 scripts/download_db.py

         - name: Commit backup
           run: |
             git config user.name "GitHub Actions"
             git config user.email "actions@github.com"
             git add backups/
             git commit -m "Automated database backup $(date +%Y-%m-%d)"
             git push
   ```

---

## Environment Configuration

### Backend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `FLASK_APP` | `app.py` | Flask entry point |
| `PORT` | `5000` | Server port (Railway provides) |
| `DB_PATH` | `/app/databases/whiskey_production.db` | Database location |
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Allowed frontend origins |

### Frontend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://your-app.up.railway.app` | Backend API URL |

---

## Custom Domain Setup

### Option 1: Use Railway + Vercel Domains

**Backend**: `api.yourapp.com` (pointed to Railway)
**Frontend**: `yourapp.com` (pointed to Vercel)

1. **Add Custom Domain to Railway**
   - Railway Settings → Domains
   - Add `api.yourapp.com`
   - Copy the CNAME record provided

2. **Add Custom Domain to Vercel**
   - Vercel Settings → Domains
   - Add `yourapp.com` and `www.yourapp.com`
   - Copy the DNS records provided

3. **Configure DNS** (at your registrar)
   ```
   Type    Name    Value
   CNAME   api     your-app.up.railway.app
   CNAME   www     cname.vercel-dns.com
   A       @       76.76.21.21  (Vercel IP)
   ```

4. **Update Environment Variables**
   - Vercel: `VITE_API_URL=https://api.yourapp.com`
   - Railway CORS: Add `https://yourapp.com`

### Option 2: Use Cloudflare (Recommended)

**Benefits**: Free CDN, caching, DDoS protection, analytics

1. **Add Site to Cloudflare**
   - Sign up at cloudflare.com
   - Add your domain
   - Update nameservers at registrar

2. **Configure DNS Records**
   ```
   Type    Name    Value               Proxy
   CNAME   api     your-app.up.railway.app   ☁️ Proxied
   CNAME   www     cname.vercel-dns.com      ☁️ Proxied
   A       @       76.76.21.21               ☁️ Proxied
   ```

3. **Enable Settings**
   - SSL/TLS: Full (strict)
   - Caching: Standard
   - Auto Minify: JS, CSS, HTML
   - Brotli compression: On

---

## SSL/HTTPS Configuration

### Automatic HTTPS

Both Railway and Vercel provide automatic HTTPS certificates:

- **Railway**: Free Let's Encrypt SSL (auto-renews)
- **Vercel**: Free SSL certificates (auto-renews)

### Verification

1. **Check Backend**
   ```bash
   curl https://api.yourapp.com/api/health
   ```
   Should return: `{"status": "healthy", "whiskeys": 2125, ...}`

2. **Check Frontend**
   Visit `https://yourapp.com` in browser
   - Look for 🔒 padlock in address bar
   - No mixed content warnings

### Force HTTPS

Add to `/frontend/public/_redirects` (Vercel):
```
# Force HTTPS
http://yourapp.com/* https://yourapp.com/:splat 301!
http://www.yourapp.com/* https://yourapp.com/:splat 301!
```

---

## Monitoring & Analytics

### Error Monitoring (Sentry)

1. **Sign up** at [sentry.io](https://sentry.io)

2. **Install Sentry** (Backend)
   ```bash
   pip install sentry-sdk[flask]
   ```

   Update `/app.py`:
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.flask import FlaskIntegration

   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[FlaskIntegration()],
       traces_sample_rate=1.0,
       environment="production"
   )
   ```

3. **Install Sentry** (Frontend)
   ```bash
   cd frontend
   npm install @sentry/react @sentry/tracing
   ```

   Update `/frontend/src/main.jsx`:
   ```javascript
   import * as Sentry from "@sentry/react";

   Sentry.init({
     dsn: "your-sentry-dsn",
     integrations: [new Sentry.BrowserTracing()],
     tracesSampleRate: 1.0,
     environment: "production"
   });
   ```

### Analytics (Plausible)

**Why Plausible?**
- Privacy-focused (GDPR compliant)
- No cookies, no tracking
- Lightweight script (< 1KB)
- Clean, simple dashboard

1. **Sign up** at [plausible.io](https://plausible.io) ($9/month)

2. **Add Script** to `/frontend/index.html`:
   ```html
   <head>
     <!-- Plausible Analytics -->
     <script defer data-domain="yourapp.com"
             src="https://plausible.io/js/script.js"></script>
   </head>
   ```

3. **Track Custom Events** (optional)
   ```javascript
   // Track quiz completion
   window.plausible('Quiz Completed', {
     props: { whiskey: whiskeyName, score: accuracy }
   });
   ```

### Alternative: Simple Analytics

Free and open-source alternative:
- [simpleanalytics.com](https://simpleanalytics.com)
- Self-hosted option available
- Similar privacy-focused approach

---

## Post-Deployment Verification

### Deployment Checklist

Run through this checklist after deployment:

#### Backend Health Check

- [ ] API health endpoint responds: `https://api.yourapp.com/api/health`
- [ ] Returns correct whiskey count (2,125)
- [ ] Response time < 500ms

#### Frontend Functionality

- [ ] Homepage loads without errors
- [ ] Search functionality works
- [ ] Can search for "Eagle Rare" and find results
- [ ] Can click a whiskey and start quiz
- [ ] Quiz displays 9 descriptors per section
- [ ] Can select multiple descriptors
- [ ] Can progress through Nose → Palate → Finish
- [ ] Results page displays accuracy
- [ ] Source review links work

#### Mobile Testing

- [ ] Test on iPhone (Safari)
- [ ] Test on Android (Chrome)
- [ ] Touch targets are adequate (44x44px minimum)
- [ ] No horizontal scrolling
- [ ] Text is readable without zooming

#### Performance

- [ ] Lighthouse score > 90 (Performance)
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] No console errors

#### Security

- [ ] HTTPS enabled on both domains
- [ ] No mixed content warnings
- [ ] CORS configured correctly
- [ ] No API keys exposed in frontend

### Testing Script

Create `/scripts/verify_deployment.sh`:
```bash
#!/bin/bash

API_URL="https://api.yourapp.com"
FRONTEND_URL="https://yourapp.com"

echo "🧪 Testing Deployment..."
echo

# Test backend health
echo "1. Backend Health Check..."
HEALTH=$(curl -s "$API_URL/api/health")
echo "$HEALTH" | jq .

# Test search endpoint
echo
echo "2. Search Endpoint..."
SEARCH=$(curl -s "$API_URL/api/whiskeys/search?q=eagle")
echo "$SEARCH" | jq '.results | length'

# Test quiz endpoint
echo
echo "3. Quiz Generation..."
QUIZ=$(curl -s "$API_URL/api/quiz/1")
echo "$QUIZ" | jq '.quiz | length'

# Test frontend
echo
echo "4. Frontend Status..."
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
echo "HTTP Status: $FRONTEND"

echo
echo "✓ Deployment verification complete!"
```

---

## Troubleshooting

### Common Issues

#### Issue: "Failed to fetch" in Frontend

**Cause**: CORS not configured or API URL incorrect

**Solution**:
1. Check `VITE_API_URL` in Vercel environment variables
2. Verify CORS origins in `/app.py` include your Vercel domain
3. Redeploy backend after CORS changes

#### Issue: Database Not Found

**Cause**: Database path incorrect or volume not mounted

**Solution**:
1. Verify Railway volume is mounted at `/app/databases`
2. Check `DB_PATH` environment variable
3. Ensure database is committed to Git or uploaded to volume

#### Issue: 502 Bad Gateway

**Cause**: Backend crashed or not responding

**Solution**:
1. Check Railway logs: `railway logs`
2. Verify `gunicorn` is in `requirements.txt`
3. Check `Procfile` or start command is correct

#### Issue: Slow API Response

**Cause**: Database queries not optimized or cold start

**Solution**:
1. Railway free tier has cold starts (~30s)
2. Upgrade to Railway Pro for always-on instances
3. Add database indexes if needed

#### Issue: Build Failed on Vercel

**Cause**: Node modules or build errors

**Solution**:
1. Check Vercel build logs
2. Verify `package.json` has correct scripts
3. Ensure build command is `npm run build`
4. Check root directory is set to `frontend`

---

## Cost Estimates

### Monthly Costs (Conservative)

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| **Railway** | Starter | $5/month | Includes $5 credits |
| **Vercel** | Free | $0 | Personal projects |
| **Cloudflare** | Free | $0 | Optional |
| **Plausible** | Starter | $9/month | Optional (can use free alternatives) |
| **Sentry** | Developer | $0 | Up to 5K errors/month |
| **Domain** | Varies | $10-15/year | One-time annual cost |

**Total Monthly**: **$5-14/month**

### Cost Optimization

**Free Tier Strategy** ($0/month for first 3 months):
- Use Railway's $5 free credits monthly
- Use Vercel free tier
- Skip Plausible (use Cloudflare analytics instead)
- Use free Sentry tier

**Production Strategy** ($14/month):
- Railway Starter ($5)
- Plausible Analytics ($9)
- Domain ($1.25/month amortized)

---

## Security Best Practices

### API Security

1. **Rate Limiting**

   Add to `/app.py`:
   ```python
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address

   limiter = Limiter(
       app=app,
       key_func=get_remote_address,
       default_limits=["200 per day", "50 per hour"]
   )

   @app.route('/api/quiz/<int:whiskey_id>')
   @limiter.limit("30 per minute")
   def get_quiz(whiskey_id):
       # ...
   ```

2. **SQL Injection Protection**
   - Already using parameterized queries ✓
   - Never use string concatenation for SQL

3. **Input Validation**

   Add validation to search:
   ```python
   import re

   @app.route('/api/whiskeys/search')
   def search_whiskeys():
       query = request.args.get('q', '')

       # Sanitize input
       query = re.sub(r'[^\w\s-]', '', query)
       query = query[:100]  # Limit length

       # ...
   ```

### Frontend Security

1. **Content Security Policy**

   Add to `/frontend/index.html`:
   ```html
   <meta http-equiv="Content-Security-Policy"
         content="default-src 'self';
                  script-src 'self' 'unsafe-inline' https://plausible.io;
                  style-src 'self' 'unsafe-inline';
                  img-src 'self' data:;
                  connect-src 'self' https://api.yourapp.com">
   ```

2. **Prevent Clickjacking**

   Add to backend `/app.py`:
   ```python
   @app.after_request
   def set_security_headers(response):
       response.headers['X-Frame-Options'] = 'DENY'
       response.headers['X-Content-Type-Options'] = 'nosniff'
       response.headers['X-XSS-Protection'] = '1; mode=block'
       return response
   ```

### Database Security

1. **Read-Only Access**
   - Quiz generation only reads database
   - No user input modifies database
   - No DELETE or UPDATE endpoints

2. **Backup Encryption**
   - Encrypt backups if storing sensitive data
   - Use GitHub's encrypted secrets for credentials

---

## Rollback Plan

### If Deployment Fails

1. **Frontend Rollback** (Vercel)
   - Vercel keeps deployment history
   - Go to Deployments → Select previous version → Promote to Production
   - Instant rollback (<1 minute)

2. **Backend Rollback** (Railway)
   - Railway keeps deployment history
   - Go to Deployments → Redeploy previous version
   - Or: Revert Git commit and push
   ```bash
   git revert HEAD
   git push origin main
   ```

3. **Database Rollback**
   ```bash
   # Restore from backup
   railway run python3 -c "import shutil; shutil.copy('backups/whiskey_production_20260128.db', 'databases/whiskey_production.db')"
   ```

### Zero-Downtime Deployment

1. **Use Preview Deployments** (Vercel)
   - Every PR gets preview URL
   - Test before merging to main

2. **Canary Deployment** (Railway)
   - Deploy to staging environment first
   - Test thoroughly
   - Promote to production

---

## Next Steps After Deployment

1. **Beta Testing**
   - Share with 10-20 whiskey enthusiasts
   - Collect feedback via Google Form or Typeform
   - Monitor Sentry for errors

2. **SEO Optimization**
   - Add meta tags to `index.html`
   - Create `robots.txt` and `sitemap.xml`
   - Submit to Google Search Console

3. **Feature Additions**
   - User accounts (Auth0 or Supabase)
   - Quiz history tracking
   - Leaderboard
   - Social sharing

4. **Marketing**
   - Write blog post about the project
   - Share on Reddit (r/bourbon, r/whiskey)
   - Post on LinkedIn
   - Submit to Product Hunt

---

## Support & Resources

### Documentation Links

- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [React Deployment](https://create-react-app.dev/docs/deployment/)

### Community Support

- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Vercel Discord: [vercel.com/discord](https://vercel.com/discord)
- Flask Community: [discord.gg/pallets](https://discord.gg/pallets)

### Project Maintainer

- **Email**: angoliam@gmail.com
- **GitHub**: Link to repository

---

## Deployment Timeline

**Estimated Time**: 2-4 hours total

| Phase | Task | Time |
|-------|------|------|
| 1 | Prepare repository, add deployment configs | 30 min |
| 2 | Deploy backend to Railway | 45 min |
| 3 | Deploy frontend to Vercel | 30 min |
| 4 | Configure custom domains | 30 min |
| 5 | Setup monitoring and analytics | 30 min |
| 6 | Testing and verification | 45 min |

**Total**: ~3 hours 30 minutes

---

**Document Status**: ✅ Ready for Review
**Last Updated**: January 29, 2026
**Next Review**: Before deployment

---

*This deployment guide is part of the Whiskey Sensory Training App documentation. For other guides, see [README.md](README.md).*
