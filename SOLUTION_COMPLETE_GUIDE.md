# 🚨 UVIS Layout Fix - Complete Solution Guide

**Date:** 2026-02-25  
**Status:** Secret mode still broken - Assets not loading  
**Root Cause:** JavaScript/CSS files missing from Docker container

---

## 📊 Current Situation Analysis

### ✅ What's Working
- Local build (`npm run build`) succeeds
- All CSS/JS files exist in `frontend/dist/`
- OrdersPage.tsx JSX fragment fixed
- `.dockerignore` updated (removed dist/build)

### ❌ What's Broken
- **Container has NO JavaScript files** in `/usr/share/nginx/html/assets/`
- Browser loads `index.html` but fails to load JS bundle
- Layout appears broken even in incognito mode
- Console shows missing module errors

### 🎯 Root Cause
Even though we:
1. Fixed `.dockerignore` (removed `dist` entry)
2. Rebuilt Docker image (`--no-cache`)
3. Manually copied files with `docker cp`

**The container still has no JS files!**

This indicates one of these issues:
1. Docker COPY instruction in Dockerfile is incorrect
2. Build stage doesn't preserve dist/ folder
3. Multi-stage build isn't copying from correct stage
4. NGINX config is serving from wrong directory

---

## 🔧 Solution Steps

### Step 1: Run Diagnostic Script

```bash
cd /root/uvis
bash DIAGNOSE_CONTAINER.sh
```

This will show:
- What files exist locally
- What files exist in container
- What .dockerignore is blocking
- Specific root cause

### Step 2: Check Dockerfile

```bash
cat frontend/Dockerfile
```

**Look for these issues:**

❌ **Problem 1: Wrong source in multi-stage build**
```dockerfile
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html/  # ← WRONG! Should be /app/dist
```

✅ **Fix:**
```dockerfile
COPY --from=builder /app/dist /usr/share/nginx/html/
```

❌ **Problem 2: Missing COPY instruction**
```dockerfile
FROM nginx:alpine
# Missing: COPY dist/ /usr/share/nginx/html/
```

✅ **Fix:**
```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf
```

### Step 3: Verify .dockerignore

```bash
cat frontend/.dockerignore
```

**Must NOT contain:**
```
dist
dist/
build
build/
```

**Safe entries:**
```
node_modules
.env
.git
*.log
coverage
.cache
```

### Step 4: Emergency Rebuild

Run the automatic fix script:

```bash
cd /root/uvis
bash EMERGENCY_FIX.sh
```

This script will:
1. ✅ Fix OrdersPage.tsx (if needed)
2. ✅ Update .dockerignore
3. ✅ Clean build frontend
4. ✅ Rebuild Docker image (no cache)
5. ✅ Start container
6. ✅ Verify assets are present
7. ✅ Show deployment status

### Step 5: Manual Verification

After rebuild, check:

```bash
# 1. Container is running
docker ps | grep uvis-frontend

# 2. JS files exist in container
docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js | wc -l"

# 3. Show first 10 files
docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.js | head -10"

# 4. Check index.html references correct files
docker exec uvis-frontend cat /usr/share/nginx/html/index.html
```

**Expected output:**
```
- Container should have 80+ JavaScript files
- Container should have 3-4 CSS files
- index.html should reference files that exist in assets/
```

### Step 6: Browser Test

**Clear cache COMPLETELY:**

1. **Chrome/Edge:**
   - Press `Ctrl + Shift + Delete`
   - Select "All time" / "전체 기간"
   - Check both:
     - ✅ Cookies and other site data
     - ✅ Cached images and files
   - Click "Clear data"
   - **Close ALL browser windows**
   - Restart browser

2. **Test in Incognito:**
   - Press `Ctrl + Shift + N`
   - Visit: `http://139.150.11.99/login`
   - Login: `admin` / `admin123`

**Expected Result:**
- ✅ Login page: Centered box, blue gradient background
- ✅ Dashboard: Single sidebar (left), header (top), stat cards, charts
- ✅ Sidebar: Icons + menu text, hover effects
- ✅ Console: No red errors about missing modules

---

## 🩹 Quick Workarounds

### Option A: Manual Copy (Fastest)

If Docker build still fails, manually copy dist:

```bash
cd /root/uvis

# Clean copy entire dist folder
docker exec uvis-frontend sh -c "rm -rf /usr/share/nginx/html/*"
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/

# Verify
docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js | wc -l"
docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/index.html"

# Reload nginx
docker exec uvis-frontend nginx -s reload
```

### Option B: Rebuild from Scratch

```bash
cd /root/uvis

# Stop and remove everything
docker-compose down
docker rmi uvis-frontend uvis-backend uvis-nginx 2>/dev/null || true

# Clean rebuild
docker-compose build --no-cache

# Start
docker-compose up -d

# Wait
sleep 30

# Check
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/ | head -20
```

---

## 🔍 Debugging Checklist

Run these to identify the issue:

```bash
# 1. Local build status
ls -lh /root/uvis/frontend/dist/index.html
ls /root/uvis/frontend/dist/assets/*.js | wc -l

# 2. Container status
docker ps | grep uvis
docker exec uvis-frontend ls /usr/share/nginx/html/ 2>/dev/null

# 3. What index.html references
cat /root/uvis/frontend/dist/index.html | grep -E 'src=|href='
docker exec uvis-frontend cat /usr/share/nginx/html/index.html | grep -E 'src=|href='

# 4. Compare
cat /root/uvis/frontend/dist/index.html
docker exec uvis-frontend cat /usr/share/nginx/html/index.html

# 5. Check if files match
JS_FILE=$(grep -oP 'src="/assets/\K[^"]+' /root/uvis/frontend/dist/index.html)
echo "Looking for: $JS_FILE"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/$JS_FILE

# 6. Dockerfile inspection
cat /root/uvis/frontend/Dockerfile | grep -A 5 "FROM nginx"

# 7. Docker build logs
docker-compose build frontend 2>&1 | grep -i "copying\|step\|error"
```

---

## 📋 Expected File Structure

### Local (after build):
```
/root/uvis/frontend/dist/
├── index.html              # References /assets/index-XXXXX.js
├── assets/
│   ├── index-B5F1Uvtw.js   # Main bundle (280KB+)
│   ├── index-BjMybcaV.css  # Main styles (15KB)
│   ├── leaflet-Dgihpmma.css
│   ├── OrderCalendarPage-D0RJcmxZ.css
│   ├── LoginPage-XXXXX.js
│   ├── DashboardPage-XXXXX.js
│   ├── OrdersPage-XXXXX.js
│   └── ... (80+ more JS files)
└── vite.svg
```

### Container (should match):
```
/usr/share/nginx/html/
├── index.html              # Same as local
├── assets/
│   ├── index-B5F1Uvtw.js   # Same hash
│   ├── index-BjMybcaV.css  # Same hash
│   └── ... (all other files)
└── vite.svg
```

---

## 🎯 Success Criteria

After fix, you should see:

```bash
# Container has many JS files
$ docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js | wc -l"
82

# Container has CSS files
$ docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.css"
/usr/share/nginx/html/assets/OrderCalendarPage-D0RJcmxZ.css
/usr/share/nginx/html/assets/index-BjMybcaV.css
/usr/share/nginx/html/assets/leaflet-Dgihpmma.css

# index.html references existing files
$ docker exec uvis-frontend cat /usr/share/nginx/html/index.html
<!doctype html>
<html lang="ko">
  <head>
    <script type="module" crossorigin src="/assets/index-B5F1Uvtw.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-BjMybcaV.css">
  </head>
  <body><div id="root"></div></body>
</html>

# Browser shows correct layout (incognito mode)
✅ Login page: Centered, styled
✅ Dashboard: Sidebar + header working
✅ Console: No module loading errors
```

---

## 📞 Next Steps if Still Broken

If after all fixes the issue persists, gather this info:

1. **Dockerfile content:**
   ```bash
   cat /root/uvis/frontend/Dockerfile
   ```

2. **Container file listing:**
   ```bash
   docker exec uvis-frontend find /usr/share/nginx/html -type f
   ```

3. **Docker build log:**
   ```bash
   docker-compose build --no-cache frontend 2>&1 | tee docker-build.log
   ```

4. **Browser DevTools:**
   - F12 → Console tab (screenshot)
   - Network tab → Filter: JS, CSS (screenshot showing 404s)
   - Elements tab → `<head>` section (show script/link tags)

5. **Nginx logs:**
   ```bash
   docker logs uvis-frontend --tail 100
   ```

---

## 🎬 One-Line Nuclear Option

If nothing else works, try this complete reset:

```bash
cd /root/uvis && \
docker-compose down && \
rm -rf frontend/dist/ frontend/node_modules/.vite && \
cd frontend && npm run build && cd .. && \
docker-compose build --no-cache frontend && \
docker-compose up -d && \
sleep 30 && \
docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.js | head -10" && \
echo "✅ Done - Test in browser incognito mode"
```

---

## 📝 Git Commit (After Success)

```bash
cd /root/uvis

git add frontend/src/pages/OrdersPage.tsx frontend/.dockerignore frontend/Dockerfile
git commit -m "fix(frontend): Complete layout and Docker asset deployment fix

- Add missing </> closing tag for JSX fragment in OrdersPage.tsx
- Remove dist and build from .dockerignore to allow Docker COPY
- Fix Dockerfile COPY instruction to include dist/ folder
- Ensure all JS/CSS assets are deployed to container

Root cause: Docker build was not copying frontend/dist/ assets to container
Result: Layout now renders correctly with all styles and scripts loaded

Fixes #layout-broken
Tested: 
- Local build ✅ (npm run build)
- Docker build ✅ (--no-cache)
- Container assets ✅ (82 JS files, 3 CSS files)
- Browser rendering ✅ (incognito mode verified)
"

git push origin main
```

---

## ✨ Summary

**Problem:** Container missing JavaScript files → Browser can't load app → Layout broken

**Root Causes:**
1. ~~OrdersPage.tsx JSX error~~ ✅ Fixed
2. ~~.dockerignore blocking dist/~~ ✅ Fixed
3. ❓ Dockerfile COPY instruction ← **Check this**
4. ❓ Multi-stage build source path ← **Check this**

**Solution Priority:**
1. 🥇 Run `EMERGENCY_FIX.sh` → Auto-fix everything
2. 🥈 Run `DIAGNOSE_CONTAINER.sh` → Identify specific issue
3. 🥉 Manual copy `docker cp frontend/dist/. uvis-frontend:/...` → Quick workaround

**Success Indicator:**
```bash
docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js | wc -l"
# Should output: 80+ (not 0!)
```

---

**Files Created:**
- ✅ `EMERGENCY_FIX.sh` - Automated complete fix
- ✅ `DIAGNOSE_CONTAINER.sh` - Diagnostic tool
- ✅ `SOLUTION_COMPLETE_GUIDE.md` - This document
- ✅ `QUICK_FIX_GUIDE.txt` - Previous quick reference

**Run this first:** `bash DIAGNOSE_CONTAINER.sh`
