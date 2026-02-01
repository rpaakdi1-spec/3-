# Production Deployment Guide - AI Cost Monitoring Dashboard

## Current Status Summary
- **Fixed Issue**: `ai_usage.py` import error (app.database → app.core.database) - Commit 1cac117
- **Server IP**: 139.150.11.99
- **Project Path**: `/root/uvis`
- **Problem**: uvis-backend container is unhealthy due to ModuleNotFoundError

## Deployment Steps (Execute on Production Server)

### Step 1: Navigate to Project Directory
```bash
cd /root/uvis
```

**Troubleshooting**: If you see "too many arguments" error:
- There might be hidden special characters in your terminal
- Try typing the command manually character by character
- Or try: `cd /root && cd uvis`

### Step 2: Pull Latest Code from GitHub
```bash
git fetch origin genspark_ai_developer
git pull origin genspark_ai_developer
```

**What to verify**: Look for "ai_usage.py" in the file changes list.

### Step 3: Stop All Containers
```bash
docker-compose -f docker-compose.prod.yml down
```

### Step 4: Rebuild Backend Container
```bash
docker-compose -f docker-compose.prod.yml build backend
```

**Expected output**: Should show steps building the backend image successfully.

### Step 5: Start All Services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Step 6: Verify Backend Health
Wait 30 seconds, then check:
```bash
docker ps
```

**What to check**: 
- `uvis-backend` should show status as "healthy" (not "unhealthy")
- All other containers (nginx, frontend, db, redis) should be "Up"

### Step 7: Check Backend Logs
```bash
docker logs uvis-backend --tail 100
```

**Success indicators to look for**:
- ✅ "Application startup complete"
- ✅ "Uvicorn running on http://0.0.0.0:8000"
- ✅ No "ModuleNotFoundError" messages
- ✅ No "ImportError" messages

**Error indicators**:
- ❌ "ModuleNotFoundError: No module named 'app.database'"
- ❌ "ImportError"
- ❌ "Exception in ASGI application"

### Step 8: Test AI Usage API Endpoints

Once backend is healthy, test the new endpoints:

```bash
# Test 1: Get AI usage statistics
curl -X GET "http://localhost:8000/api/v1/ai-usage/stats" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test 2: Get AI usage logs
curl -X GET "http://localhost:8000/api/v1/ai-usage/logs?limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test 3: Get cost summary
curl -X GET "http://localhost:8000/api/v1/ai-usage/cost-summary?period=7d" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Alternative Access Methods (If PuTTY SSH Fails)

### Option 1: Gabia Web Console
1. Login to Gabia control panel
2. Navigate to server management
3. Use web-based terminal/console

### Option 2: Alternative SSH Client
Try these instead of PuTTY:
- **Windows**: 
  - Windows Terminal + OpenSSH: `ssh root@139.150.11.99`
  - MobaXterm
  - WSL2 with ssh command
- **Web-based**: 
  - Check if Gabia provides web SSH interface

### Option 3: Verify SSH Configuration
If SSH is blocked:
```bash
# Check SSH service status
systemctl status sshd

# Check firewall rules
ufw status

# Check SSH key permissions
ls -la /root/.ssh/
```

## Troubleshooting Common Issues

### Issue 1: "cd /root/uvis" shows "too many arguments"
**Solution**: 
- Copy-paste might include hidden characters
- Type the command manually
- Or use: `cd /root && cd uvis`

### Issue 2: Git pull fails with merge conflicts
**Solution**:
```bash
# Stash any local changes
git stash

# Pull latest code
git pull origin genspark_ai_developer

# If needed, apply stashed changes
git stash pop
```

### Issue 3: Docker build fails
**Solution**:
```bash
# Clean up docker cache
docker system prune -a

# Rebuild without cache
docker-compose -f docker-compose.prod.yml build --no-cache backend
```

### Issue 4: Backend still unhealthy after rebuild
**Solution**:
```bash
# Check detailed logs
docker logs uvis-backend --tail 200

# Check if database migration is needed
docker exec uvis-backend alembic upgrade head

# Restart just the backend
docker-compose -f docker-compose.prod.yml restart backend
```

## Post-Deployment Verification

### 1. Check Container Status
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

All containers should be "Up" and backend should be "healthy".

### 2. Check API Response
```bash
# Health check
curl http://localhost:8000/health

# API docs (should be accessible)
curl http://localhost:8000/docs
```

### 3. Check Frontend Access
Access the application at: `http://139.150.11.99`

### 4. Monitor Logs for Errors
```bash
# Follow backend logs in real-time
docker logs -f uvis-backend

# Check for any errors in last 100 lines
docker logs uvis-backend --tail 100 | grep -i error
```

## Expected Results After Successful Deployment

1. ✅ Backend container is healthy
2. ✅ No ModuleNotFoundError in logs
3. ✅ AI usage API endpoints respond correctly
4. ✅ Frontend can access new AI cost monitoring dashboard
5. ✅ Data is being logged to database (AIUsageLog table)

## Next Steps After Deployment

1. **Test AI Chat Functionality**: Verify that AI chat messages are being logged
2. **Verify Cost Tracking**: Check that costs are calculated correctly
3. **Test Dashboard UI**: Access the AI cost monitoring dashboard in frontend
4. **Monitor Performance**: Watch logs and metrics for any issues

## Emergency Rollback (If Deployment Fails)

```bash
# Stop containers
docker-compose -f docker-compose.prod.yml down

# Checkout previous stable commit
git checkout b1b59ea  # Previous commit before ai_usage fix

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d
```

## Support Information

**GitHub Repository**: https://github.com/rpaakdi1-spec/3-.git  
**Branch**: genspark_ai_developer  
**Latest Commit**: 1cac117 (fix: ai_usage.py의 잘못된 database import 경로 수정)

---

## 🎯 Quick Commands Checklist

Copy and execute these commands in order on the production server:

```bash
# 1. Navigate to project
cd /root/uvis

# 2. Pull latest code
git pull origin genspark_ai_developer

# 3. Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d

# 4. Wait 30 seconds, then check status
sleep 30
docker ps

# 5. Check backend logs
docker logs uvis-backend --tail 50
```

**Please execute these commands on the server and share the output!**
