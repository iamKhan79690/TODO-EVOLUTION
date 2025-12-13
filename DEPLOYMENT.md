# Deployment Guide - Todo Evolution

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │────▶│   Database      │
│   (Vercel)      │     │   (Render)      │     │ (Neon Postgres) │
│   Next.js 16    │◀────│   FastAPI       │◀────│   Already setup │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Step 1: Prepare Your Code

### 1.1 Ensure requirements.txt is updated
```bash
cd backend
pip freeze > requirements.txt
```

### 1.2 Add Procfile for Render (already created)
File: `backend/Procfile`

### 1.3 Commit all changes
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

---

## Step 2: Deploy Backend to Render

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### 2.2 Create New Web Service
1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `todo-evolution-api` |
| **Region** | Choose nearest to you |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### 2.3 Add Environment Variables
In Render dashboard → Environment tab, add:

```
DATABASE_URL=postgresql://neondb_owner:npg_6XJMDV8OidrG@ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
DATABASE_URL_ASYNC=postgresql+asyncpg://neondb_owner:npg_6XJMDV8OidrG@ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech/neondb?ssl=require
BETTER_AUTH_SECRET=your-production-secret-change-this
JWT_SECRET=your-jwt-secret-change-this
CORS_ORIGINS=https://your-frontend.vercel.app
REDIS_ENABLED=False
ENVIRONMENT=production
```

> ⚠️ **Important**: Generate new secrets for production! Use: `openssl rand -base64 32`

### 2.4 Deploy
Click **Create Web Service**. Render will build and deploy automatically.

Your backend URL will be: `https://todo-evolution-api.onrender.com`

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### 3.2 Import Project
1. Click **Add New** → **Project**
2. Import your GitHub repository

### 3.3 Configure Build
| Setting | Value |
|---------|-------|
| **Framework Preset** | Next.js |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |

### 3.4 Add Environment Variables
```
NEXT_PUBLIC_FASTAPI_URL=https://todo-evolution-api.onrender.com
```

### 3.5 Deploy
Click **Deploy**. Vercel will build and deploy automatically.

Your frontend URL will be: `https://todo-evolution.vercel.app`

---

## Step 4: Update CORS Origins

After deploying frontend, update your **Render backend** environment:

```
CORS_ORIGINS=https://your-app.vercel.app,https://todo-evolution.vercel.app
```

---

## Step 5: Verify Deployment

1. Visit your Vercel URL
2. Sign up with a new account
3. Create a task
4. Verify it persists after refresh

---

## Troubleshooting

### Backend not starting
- Check Render logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is complete

### CORS errors
- Add your frontend URL to `CORS_ORIGINS`
- Include both `https://` and raw domain

### Database connection fails
- Verify Neon connection string includes `sslmode=require`
- For async: use `ssl=require` (not `sslmode`)

### Free tier cold starts
- Render free tier sleeps after 15 min of inactivity
- First request after sleep takes ~30 seconds
- Consider upgrading for always-on

---

## Production Checklist

- [ ] Generate new secrets for BETTER_AUTH_SECRET and JWT_SECRET
- [ ] Update CORS_ORIGINS with your actual frontend URL
- [ ] Remove debug print statements from `backend/src/dependencies/auth.py`
- [ ] Set ENVIRONMENT=production
- [ ] Test full auth flow on production

---

## Cost Summary

| Service | Free Tier |
|---------|-----------|
| **Neon** | 3GB storage, always free |
| **Render** | Free (sleeps after 15min idle) |
| **Vercel** | 100GB bandwidth, free forever |

**Total: $0/month** for hobby use! 🎉
