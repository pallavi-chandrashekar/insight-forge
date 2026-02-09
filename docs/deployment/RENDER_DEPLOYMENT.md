# Deploy InsightForge to Render (Free Tier)

## Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free)
3. **Anthropic API Key** - Get one at [console.anthropic.com](https://console.anthropic.com)

## Deployment Steps

### Step 1: Push to GitHub

Make sure your code is pushed to GitHub:

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Deploy via Render Blueprint

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the `insight-forge` repository
5. Render will automatically detect the `render.yaml` file

### Step 3: Configure Environment Variables

After the Blueprint is created, you need to set the Anthropic API key:

1. Go to the **insightforge-api** service in Render dashboard
2. Click **"Environment"** tab
3. Find `API_KEY` and click **"Edit"**
4. Paste your Anthropic API key
5. Click **"Save Changes"**
6. The service will automatically redeploy

### Step 4: Wait for Deployment

- Database creation: ~2-3 minutes
- Backend deployment: ~3-5 minutes
- Frontend deployment: ~2-3 minutes

### Step 5: Access Your App

Once deployed, your app will be available at:
- **Frontend**: `https://insightforge.onrender.com`
- **Backend API**: `https://insightforge-api.onrender.com`
- **API Docs**: `https://insightforge-api.onrender.com/docs`

## Free Tier Limitations

### What's Free:
- ✅ PostgreSQL database (free for 90 days, then requires upgrade)
- ✅ Web services (backend + frontend)
- ✅ Automatic HTTPS/SSL
- ✅ Automatic deploys from GitHub

### Limitations:
- ⚠️ **Spin-down**: Free services spin down after 15 minutes of inactivity
- ⚠️ **Cold starts**: First request after spin-down takes 30-60 seconds
- ⚠️ **Database expiry**: Free PostgreSQL expires after 90 days
- ⚠️ **No Redis**: Free tier doesn't include Redis (caching disabled)

### To Keep Services Running:
1. Upgrade to paid plan ($7/month per service), OR
2. Use a free cron service (like cron-job.org) to ping your backend every 10 minutes

## Custom Domain (Optional)

To use your own domain:

1. Go to service settings → **"Custom Domains"**
2. Add your domain (e.g., `app.yourdomain.com`)
3. Update DNS with the provided CNAME record
4. Update `CORS_ORIGINS` in backend to include your domain

## Troubleshooting

### Database Connection Errors
- Check that DATABASE_URL is properly set (should auto-configure from Blueprint)
- Verify database is running in Render dashboard

### API Key Errors
- Ensure `API_KEY` is set in the backend environment variables
- Verify it's a valid Anthropic API key

### CORS Errors
- Update `CORS_ORIGINS` to match your frontend URL
- Redeploy backend after changes

### Build Failures
Check logs in Render dashboard:
1. Go to service → **"Logs"** tab
2. Look for error messages during build

## Upgrading from Free Tier

When ready to upgrade:

1. **Database**: Click "Upgrade" on your database ($7/month for Starter)
2. **Backend**: Change plan to "Starter" ($7/month) for always-on
3. **Frontend**: Static sites remain free

Total cost for always-on: ~$14-21/month

## Manual Deployment (Alternative)

If you prefer not to use Blueprint, deploy each service manually:

### 1. Create PostgreSQL Database
- New → PostgreSQL → Free tier
- Copy the "Internal Database URL"

### 2. Deploy Backend
- New → Web Service → Connect GitHub repo
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add environment variables manually

### 3. Deploy Frontend
- New → Static Site → Connect GitHub repo
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`
- Add `VITE_API_URL` environment variable
