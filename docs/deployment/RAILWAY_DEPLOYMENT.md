# Deploy InsightForge to Railway

Railway offers $5 free credit per month - enough for hobby projects.

## Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Railway Account** - Sign up at [railway.app](https://railway.app) (use GitHub login)

## Quick Deploy (5 minutes)

### Step 1: Create Railway Project

1. Go to [railway.app/new](https://railway.app/new)
2. Click **"Deploy from GitHub repo"**
3. Select your `insight-forge` repository
4. Railway will auto-detect the monorepo structure

### Step 2: Add PostgreSQL Database

1. In your project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway automatically creates and connects it

### Step 3: Deploy Backend

1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repo and set **Root Directory**: `backend`
3. Add environment variables (click on the service → Variables):

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<click Generate to create one>
API_KEY=
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://your-frontend.up.railway.app
```

4. Railway will auto-deploy using `backend/railway.toml`

### Step 4: Deploy Frontend

1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repo and set **Root Directory**: `frontend`
3. Add environment variable:

```
VITE_API_URL=https://your-backend.up.railway.app/api
```

4. Railway will build and serve the static site

### Step 5: Update CORS

After both services are deployed:
1. Copy the frontend URL (e.g., `https://insightforge-frontend.up.railway.app`)
2. Go to backend service → Variables
3. Update `CORS_ORIGINS` with the frontend URL

## Environment Variables Reference

### Backend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `${{Postgres.DATABASE_URL}}` |
| `SECRET_KEY` | JWT signing key | Generate random string |
| `API_KEY` | Leave empty | Users provide their own |
| `ENVIRONMENT` | Environment name | `production` |
| `DEBUG` | Debug mode | `False` |
| `CORS_ORIGINS` | Allowed origins | Frontend URL |

### Frontend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://xxx.up.railway.app/api` |

## Custom Domain (Optional)

1. Go to service → **Settings** → **Domains**
2. Click **"+ Custom Domain"**
3. Add your domain (e.g., `app.yourdomain.com`)
4. Update DNS with the provided CNAME
5. Update `CORS_ORIGINS` on backend

## Pricing

| Resource | Free Tier |
|----------|-----------|
| Compute | $5/month credit |
| PostgreSQL | Included |
| Bandwidth | 100GB/month |
| Build minutes | Unlimited |

**Typical usage:** $2-4/month for light usage (stays within free tier)

## Monitoring

- **Logs:** Click on any service → View Logs
- **Metrics:** Service → Metrics tab
- **Deployments:** Service → Deployments tab

## Troubleshooting

### Build Fails
- Check logs in Deployments tab
- Ensure `requirements.txt` / `package.json` are correct
- Verify root directory is set correctly

### Database Connection Error
- Ensure `DATABASE_URL` uses `${{Postgres.DATABASE_URL}}` reference
- Check PostgreSQL service is running

### CORS Errors
- Update `CORS_ORIGINS` to match your frontend URL exactly
- Include `https://` prefix
- Redeploy backend after changing

### Frontend Can't Reach Backend
- Verify `VITE_API_URL` is set correctly
- Check backend is running (health check: `/health`)
- Ensure backend URL ends with `/api`

## Manual CLI Deployment (Alternative)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing project
railway link

# Deploy backend
cd backend
railway up

# Deploy frontend
cd ../frontend
railway up
```

## Updating Your App

Railway auto-deploys on every push to `main`:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway automatically deploys!
```

To disable auto-deploy:
- Service → Settings → Disable "Auto Deploy"
