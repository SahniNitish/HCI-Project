# Deployment Guide

## Prerequisites
- Vercel account (sign up at https://vercel.com)
- MongoDB Atlas account (or another MongoDB hosting service)
- Vercel CLI installed globally

## Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

## Step 2: Deploy Backend First

### 2.1 Navigate to backend directory
```bash
cd backend
```

### 2.2 Deploy to Vercel
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? **Select your account**
- Link to existing project? **N**
- Project name? **expense-tracker-backend** (or your preferred name)
- Directory? **./backend**
- Want to override settings? **N**

### 2.3 Add Environment Variables
After deployment, add these environment variables in Vercel dashboard:
- `MONGO_URL`: Your MongoDB connection string
- `DB_NAME`: expense_tracker_db
- `JWT_SECRET`: Your secure JWT secret key
- `EMERGENT_LLM_KEY`: Your LLM API key (if using real AI features)
- `CORS_ORIGINS`: * (or your frontend domain)

Or use CLI:
```bash
vercel env add MONGO_URL
vercel env add DB_NAME
vercel env add JWT_SECRET
vercel env add EMERGENT_LLM_KEY
vercel env add CORS_ORIGINS
```

### 2.4 Redeploy with Environment Variables
```bash
vercel --prod
```

**Copy the backend deployment URL** - you'll need it for the frontend.

## Step 3: Deploy Frontend

### 3.1 Update Frontend Environment
Edit `frontend/.env.production` and replace the backend URL:
```
REACT_APP_BACKEND_URL=https://your-actual-backend-url.vercel.app
```

### 3.2 Navigate to frontend directory
```bash
cd ../frontend
```

### 3.3 Deploy to Vercel
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? **Select your account**
- Link to existing project? **N**
- Project name? **expense-tracker-frontend** (or your preferred name)
- Directory? **./frontend**
- Want to override settings? **N**

### 3.4 Deploy to Production
```bash
vercel --prod
```

## Step 4: Configure CORS
Update the backend's `CORS_ORIGINS` environment variable in Vercel dashboard to include your frontend domain:
```
https://your-frontend.vercel.app
```

Then redeploy the backend:
```bash
cd ../backend
vercel --prod
```

## MongoDB Setup (if using MongoDB Atlas)

1. Create a free cluster at https://www.mongodb.com/cloud/atlas
2. Create a database user
3. Whitelist all IP addresses (0.0.0.0/0) for Vercel
4. Get your connection string
5. Add it as `MONGO_URL` environment variable in Vercel

## Deployment URLs

After successful deployment, you'll have:
- **Frontend**: https://your-project.vercel.app
- **Backend**: https://your-backend.vercel.app

## Troubleshooting

### Backend Issues
- Check Vercel function logs in the dashboard
- Ensure all environment variables are set
- Verify MongoDB connection string is correct

### Frontend Issues
- Make sure `REACT_APP_BACKEND_URL` points to the correct backend
- Check browser console for CORS errors
- Verify build completed successfully in Vercel dashboard

### CORS Errors
- Update backend `CORS_ORIGINS` to include your frontend domain
- Redeploy backend after updating environment variables

## Quick Redeploy
To redeploy after making changes:
```bash
# Backend
cd backend
vercel --prod

# Frontend
cd frontend
vercel --prod
```

## Alternative: Deploy via GitHub Integration

You can also connect your GitHub repository to Vercel:
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Create two projects: one for frontend, one for backend
4. Set root directory for each project
5. Add environment variables
6. Vercel will auto-deploy on every push to main branch
