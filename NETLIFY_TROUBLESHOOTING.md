# Netlify Deployment Troubleshooting Guide

## 🚨 Known Issues and Solutions

### Issue #1: "vite: not found" Build Failure

**Date Encountered:** Current deployment  
**Error Code:** 127  
**Build Log:**
```
8:59:56 AM: $ npm run build
8:59:56 AM: > pinmaker-frontend@1.0.0 build
8:59:56 AM: > vite build
8:59:56 AM: sh: 1: vite: not found
8:59:56 AM: "build.command" failed
8:59:56 AM: Command failed with exit code 127: npm run build
```

**Root Cause Analysis:**
- Netlify was not installing `node_modules` dependencies before running the build command
- The `vite` binary was not available in the build environment
- Build command assumed dependencies were already installed

**Solution Applied:**
✅ **Fixed in `netlify.toml`:**
```toml
[build]
  base = "frontend"
  command = "npm ci && npm run build"  # Added npm ci
  publish = "frontend/dist"
```

✅ **Additional Fix in `package.json`:**
```json
"scripts": {
  "build": "npx vite build",  // Added npx prefix
  "dev": "npx vite",
  "start": "npx vite",
  "preview": "npx vite preview"
}
```

**Why This Works:**
- `npm ci` installs dependencies from `package-lock.json` (faster, more reliable for CI/CD)
- `npx` ensures the vite binary is found in `node_modules/.bin` even if PATH is not properly configured
- More deterministic than `npm install` in CI environments
- Resolves binary resolution issues in CI/CD environments

**Prevention:**
- Always include dependency installation in CI/CD build commands
- Use `npm ci` instead of `npm install` for production builds
- Test build process locally with clean `node_modules`

---

### Issue #2: PostCSS/Tailwind Configuration (Previously Resolved)

**Error:** Tailwind CSS PostCSS plugin compatibility  
**Solution Applied:**
- Updated `postcss.config.js` to use `@tailwindcss/postcss`
- Installed correct PostCSS plugin version
- Verified build works locally before deployment

---

## 🔍 Debugging Checklist

### Before Deployment
- [ ] Test build locally: `cd frontend && npm ci && npm run build`
- [ ] Verify `dist/` directory is created with all assets
- [ ] Check `package.json` scripts are correctly defined
- [ ] Ensure `netlify.toml` includes dependency installation
- [ ] Validate environment variables are set

### During Build Failure
1. **Check Netlify Build Logs**
   - Go to Netlify Dashboard → Site → Deploys → Failed Deploy
   - Look for specific error messages and exit codes

2. **Common Exit Codes**
   - `127`: Command not found (missing dependencies)
   - `1`: General build failure (check specific error)
   - `2`: Syntax or configuration error

3. **Verify Configuration**
   ```toml
   # netlify.toml should have:
   [build]
     base = "frontend"
     command = "npm ci && npm run build"
     publish = "frontend/dist"
   ```

### Environment Variables Checklist
- [ ] `VITE_API_BASE_URL` set to backend URL
- [ ] `NODE_ENV` set to "production"
- [ ] `NODE_VERSION` specified (18 or higher)
- [ ] No sensitive keys exposed in frontend

---

## 🛠️ Quick Fixes

### Fix #1: Dependency Installation
```bash
# Update netlify.toml build command
command = "npm ci && npm run build"
```

### Fix #2: Node Version Lock
```toml
# In netlify.toml
[build.environment]
  NODE_VERSION = "18"
```

### Fix #3: Clear Build Cache
```bash
# In Netlify Dashboard:
# Site Settings → Build & Deploy → Environment → Clear cache and retry deploy
```

### Fix #4: Manual Dependency Check
```bash
# Test locally
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📊 Build Performance Monitoring

### Expected Build Times
- **Dependency Installation**: 30-60 seconds
- **Vite Build**: 10-30 seconds
- **Total Build Time**: 1-2 minutes

### Build Size Expectations
```
dist/
├── index.html (~6KB)
├── assets/
│   ├── index-[hash].css (~0.5KB)
│   ├── vendor-[hash].js (~140KB)
│   ├── utils-[hash].js (~35KB)
│   └── index-[hash].js (~150KB)
└── static assets (images, fonts)
```

---

## 🔄 Rollback Procedures

### If Build Continues to Fail
1. **Revert to Previous Working Commit**
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Use Netlify Deploy Rollback**
   - Go to Netlify Dashboard → Deploys
   - Find last successful deploy
   - Click "Publish deploy"

3. **Emergency Static Hosting**
   - Build locally: `npm run build`
   - Manually upload `dist/` folder to Netlify
   - Configure redirects manually

---

## 📝 Change Log

### 2024-12-19 - "vite: not found" Issue Resolution (Final Fix)
- **Issue**: Build failing with "Cannot find package 'vite' imported" error
- **Root Cause**: Version mismatch (npx installing vite@6.3.5 vs package.json vite@5.4.0) and vite in devDependencies
- **Solution Applied**: Moved vite to dependencies to ensure availability during build, removed duplicate config file
- **Files Modified**: 
  - `frontend/netlify.toml`: Updated build command to `npm ci && npm run build`
  - `frontend/package.json`: Added `npx` prefix to vite commands in scripts, moved `vite` and `@vitejs/plugin-react` to dependencies
  - `frontend/vite.config.js`: Removed duplicate config file (keeping vite.config.ts)
  - `NETLIFY_DEPLOYMENT.md` (added troubleshooting section)
  - `NETLIFY_TROUBLESHOOTING.md` (comprehensive guide)
- **Status**: ✅ Ready for re-deployment (tested locally)

---

## 🆘 Emergency Contacts

### When to Escalate
- Build failures persist after applying documented fixes
- Performance degradation beyond expected ranges
- Security vulnerabilities detected in dependencies
- API connectivity issues between frontend and backend

### Escalation Steps
1. Document the exact error and steps taken
2. Check if backend API is responding: `https://pinmaker.kraftysprouts.com/api/health`
3. Verify DNS and SSL certificates are valid
4. Consider temporary rollback while investigating

---

**Last Updated**: 2024-12-19  
**Next Review**: After successful deployment  
**Maintainer**: Development Team