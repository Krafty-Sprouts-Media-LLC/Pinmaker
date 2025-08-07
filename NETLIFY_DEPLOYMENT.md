# Netlify Frontend Deployment Guide

This guide walks you through deploying the Pinterest Template Generator frontend to Netlify while keeping the FastAPI backend on your VPS.

## Prerequisites

- Netlify account (free tier is sufficient)
- GitHub repository access
- Backend API running on `https://pinmaker.kraftysprouts.com`

## Step 1: Prepare Your Repository

The repository has been updated with:
- ✅ `frontend/netlify.toml` - Netlify configuration
- ✅ `frontend/.env.example` - Environment variables template
- ✅ Updated API service to use environment variables
- ✅ Backend CORS updated to allow Netlify domains

## Step 2: Deploy to Netlify

### Option A: Netlify Dashboard (Recommended)

1. **Connect Repository**
   - Go to [Netlify Dashboard](https://app.netlify.com)
   - Click "New site from Git"
   - Connect your GitHub account
   - Select `Krafty-Sprouts-Media-LLC/Pinmaker` repository

2. **Configure Build Settings**
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
   - **Node version**: `18` (set in netlify.toml)

3. **Set Environment Variables**
   - Go to Site settings → Environment variables
   - Add these variables:
     ```
     VITE_API_BASE_URL=https://pinmaker.kraftysprouts.com
     VITE_APP_NAME=Pinterest Template Generator
     NODE_ENV=production
     ```

4. **Deploy**
   - Click "Deploy site"
   - Netlify will build and deploy automatically
   - You'll get a URL like `https://amazing-name-123456.netlify.app`

### Option B: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# From the frontend directory
cd frontend

# Initialize Netlify site
netlify init

# Set environment variables
netlify env:set VITE_API_BASE_URL https://pinmaker.kraftysprouts.com
netlify env:set VITE_APP_NAME "Pinterest Template Generator"

# Deploy
netlify deploy --prod
```

## Step 3: Update Backend CORS

Update your backend's CORS origins with your Netlify URL:

```python
# In main.py, update CORS_ORIGINS
CORS_ORIGINS = [
    "https://pinmaker.kraftysprouts.com",
    "http://localhost:3000",
    "https://*.netlify.app",  # Allows all Netlify subdomains
    "https://your-site-name.netlify.app",  # Your specific Netlify URL
]
```

## Step 4: Custom Domain (Optional)

1. **Add Custom Domain**
   - In Netlify Dashboard → Domain settings
   - Add your custom domain (e.g., `app.kraftysprouts.com`)
   - Follow DNS configuration instructions

2. **Update Backend CORS**
   - Add your custom domain to CORS_ORIGINS
   - Update nginx configuration if needed

## Step 5: Test the Deployment

1. **Frontend Tests**
   - Visit your Netlify URL
   - Check browser console for errors
   - Test image upload functionality
   - Verify API calls are working

2. **Backend Tests**
   - Check nginx logs: `sudo tail -f /var/log/nginx/access.log`
   - Monitor API responses
   - Verify CORS headers are present

## Benefits of This Setup

### ✅ Solved Problems
- **No more build failures** - Netlify handles all frontend builds
- **Faster deployments** - No VPS build process
- **Better performance** - Global CDN for frontend assets
- **Automatic HTTPS** - Free SSL certificates
- **Deploy previews** - Test changes before going live

### ✅ Improved Workflow
- **Git-based deployments** - Push to deploy
- **Rollback capability** - Instant rollbacks
- **Branch deployments** - Test features safely
- **Build logs** - Clear error messages

## Troubleshooting

### Build Failures
```bash
# Check build logs in Netlify dashboard
# Common issues:
# 1. Missing environment variables
# 2. Node version mismatch
# 3. Build command errors
```

### CORS Errors
```bash
# Check browser console
# Verify backend CORS_ORIGINS includes your Netlify URL
# Test API endpoint directly: https://pinmaker.kraftysprouts.com/api/health
```

### API Connection Issues
```bash
# Verify environment variables are set
# Check network tab in browser dev tools
# Ensure backend is running and accessible
```

## Next Steps

1. **Monitor Performance**
   - Use Netlify Analytics
   - Monitor Core Web Vitals
   - Track deployment frequency

2. **Optimize Further**
   - Enable Netlify Edge Functions if needed
   - Set up form handling for contact forms
   - Configure redirects for SEO

3. **Consider Gradio Migration**
   - With frontend successfully separated
   - Backend can be gradually migrated to Gradio
   - Maintain API compatibility during transition

## Support

If you encounter issues:
1. Check Netlify build logs
2. Verify environment variables
3. Test API endpoints directly
4. Check browser console for errors
5. Review nginx logs on VPS

---

**Status**: ✅ Ready for deployment
**Estimated Setup Time**: 15-30 minutes
**Downtime**: None (backend continues running)