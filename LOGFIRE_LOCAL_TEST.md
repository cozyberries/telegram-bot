# 🔥 Logfire Local Testing - Complete Guide

## Status
✅ **Logfire logging added to ALL routes**  
✅ **Local test scripts created**  
⚠️  **Needs LOGFIRE_TOKEN in .env.local to test**

---

## What Was Added

### 1. FastAPI App (`app/main.py`)

**Logfire initialization on startup:**
```python
from app.logging_config import configure_logfire
logfire_configured = configure_logfire()
```

**Logging added to ALL endpoints:**

| Endpoint | Method | Logging |
|----------|--------|---------|
| `/` | GET | ✅ `log_api_request("/", "GET")` |
| `/health` | GET | ✅ `log_api_request` + `log_metric("health_check")` |
| `/bot-info` | GET | ✅ `log_api_request("/bot-info", "GET")` |
| `/webhook` | GET | ✅ `log_api_request("/webhook", "GET")` |
| `/webhook` | POST | ✅ `log_bot_update(update_id, user_id, command)` |
| `/notify-order` | GET | ✅ `log_api_request("/notify-order", "GET")` |
| `/notify-order` | POST | ✅ `log_api_request` + `log_metric("order_notification")` |

**Global exception handler:**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    log_error(exc, {"endpoint": url, "method": method})
```

**Response includes Logfire status:**
```json
{
  "logfire_enabled": true
}
```

### 2. Test Scripts

**`TEST_LOGFIRE_LOCAL.sh`**
- Checks .env.local exists
- Validates LOGFIRE_TOKEN is set
- Installs dependencies
- Starts FastAPI server on port 8000

**`TEST_ENDPOINTS.sh`**
- Tests all GET endpoints
- Shows JSON responses
- Provides Logfire dashboard link

**`LOCAL_LOGFIRE_SETUP.md`**
- Step-by-step setup guide
- Troubleshooting tips
- Expected results

---

## How to Test Locally

### Prerequisites
```bash
cd /Users/abdul.azeez/Personal/cozyberries/telegram-bot
```

### Step 1: Get Logfire Token

1. Visit: https://logfire.pydantic.dev/
2. Sign up (free tier available)
3. Create project: `cozyberries-telegram-bot`
4. Settings → API Tokens → Create new token
5. Copy the token (starts with `lf_`)

### Step 2: Configure .env.local

```bash
# Open .env.local
nano .env.local
```

Add your token:
```env
LOGFIRE_TOKEN=lf_your_actual_token_here
LOGFIRE_PROJECT_NAME=cozyberries-telegram-bot
LOGFIRE_ENVIRONMENT=development
```

### Step 3: Start Server

**Terminal 1:**
```bash
./TEST_LOGFIRE_LOCAL.sh
```

You should see:
```
✅ Logfire configured for FastAPI
🔥 Logged app startup to Logfire
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Test Endpoints

**Terminal 2:**
```bash
# Test all endpoints at once
./TEST_ENDPOINTS.sh

# Or test individually
curl http://localhost:8000/health
curl http://localhost:8000/
curl http://localhost:8000/bot-info
```

### Step 5: Verify Logfire Dashboard

1. Open: https://logfire.pydantic.dev/
2. Select project: `cozyberries-telegram-bot`
3. Filter: `environment:development`
4. Time range: Last 15 minutes

**Expected entries:**

✅ **Events:**
- `app_startup` - Server initialization
- `api_request` - For each endpoint call

✅ **Metrics:**
- `health_check` - Count of health checks

✅ **Spans:**
- `api_request` with `endpoint`, `method`, `duration`

---

## What You'll See

### In Terminal (Server Logs)

```
INFO:app.main:Starting CozyBerries Telegram Bot...
INFO:app.logging_config:🔥 Configuring Logfire: cozyberries-telegram-bot (development)
INFO:app.logging_config:✅ Logfire configured successfully
INFO:app.main:✅ Logfire configured for FastAPI
INFO:app.main:🔥 Logged app startup to Logfire

# When accessing endpoints:
INFO:app.main:🔥 Health check - logged to Logfire
INFO:app.main:Health check endpoint accessed
```

### In API Responses

```json
{
  "status": "ok",
  "logfire_enabled": true,  // ← Shows Logfire is working
  ...
}
```

### In Logfire Dashboard

**Traces view:**
- Each request as a span
- Duration, status code
- Full request context

**Logs view:**
- Structured log events
- Searchable by endpoint, method
- Error logs with stack traces

**Metrics view:**
- Health check counts
- Request rates
- Error rates

---

## Verification Checklist

- [ ] Obtained Logfire token from dashboard
- [ ] Added token to .env.local
- [ ] Server starts without errors
- [ ] See "✅ Logfire configured" in terminal
- [ ] Access http://localhost:8000/health
- [ ] Response shows `"logfire_enabled": true`
- [ ] See "🔥 Health check - logged" in terminal
- [ ] Open Logfire dashboard
- [ ] See `app_startup` event
- [ ] See `api_request` spans
- [ ] Test all endpoints with script
- [ ] All endpoints log to Logfire

---

## Troubleshooting

### ⚠️ "LOGFIRE_TOKEN not set"

**Check:**
```bash
cat .env.local | grep LOGFIRE_TOKEN
```

**Should show:**
```
LOGFIRE_TOKEN=lf_xxxxxxxxxxxx...
```

**Not:**
```
LOGFIRE_TOKEN=
LOGFIRE_TOKEN=your-logfire-token
```

### ⚠️ "Logfire not configured"

**Reasons:**
1. Token not set in .env.local
2. Token is invalid/expired
3. `.env.local` not in same directory

**Fix:**
```bash
# Regenerate token in Logfire dashboard
# Update .env.local
nano .env.local

# Restart server
# Ctrl+C, then re-run
./TEST_LOGFIRE_LOCAL.sh
```

### ⚠️ No logs in Logfire dashboard

**Check:**
1. Project name: `cozyberries-telegram-bot`
2. Environment: `development`
3. Time range: Last 1 hour
4. Refresh dashboard

**Verify in terminal:**
```bash
# Should see these logs:
grep "🔥" server-logs.txt
```

### ⚠️ Server fails to start

**Check dependencies:**
```bash
pip install -r requirements.txt
```

**Check port 8000 is free:**
```bash
lsof -i :8000
# If occupied, kill it or use different port
```

---

## Quick Test Command

```bash
# One-line test
./TEST_LOGFIRE_LOCAL.sh &
sleep 5 && curl http://localhost:8000/health | jq '.logfire_enabled'
```

**Expected output:**
```json
true
```

---

## Production Deployment

Once local testing succeeds:

### 1. Push to GitHub
```bash
git add -A
git commit -m "Verified Logfire logging locally"
git push origin main
```

### 2. Deploy to Vercel
```bash
vercel --prod
```

### 3. Wait for deployment
```bash
# Wait 30-60 seconds
sleep 45
```

### 4. Test production
```bash
# Check health
curl https://bot.cozyberries.in/health | jq '.logfire_enabled'

# Should return: true
```

### 5. Send bot message
- Open Telegram
- Send `/start` to your bot

### 6. Check logs
```bash
vercel logs | grep "🔥"
```

**Expected:**
```
🔥 Configuring Logfire
✅ Logfire configured successfully
🔥 Telegram update XXX - logged to Logfire
```

### 7. Check Logfire dashboard
- Filter: `environment:production`
- Should see production logs

---

## Files Modified

| File | Changes |
|------|---------|
| `app/main.py` | ✅ Added Logfire to all routes |
| `api/webhook.py` | ✅ Already has Logfire |
| `api/health.py` | ℹ️ Static (no Logfire) |
| `app/logging_config.py` | ✅ Already configured |
| `TEST_LOGFIRE_LOCAL.sh` | ✅ Created |
| `TEST_ENDPOINTS.sh` | ✅ Created |
| `LOCAL_LOGFIRE_SETUP.md` | ✅ Created |

---

## Summary

✅ **What works:**
- Logfire configuration module
- Logging in all FastAPI routes
- Local test scripts
- Documentation

⚠️ **What's needed:**
- Your Logfire token in .env.local
- Run test scripts to verify

🎯 **Next step:**
```bash
# 1. Add token to .env.local
nano .env.local

# 2. Run test
./TEST_LOGFIRE_LOCAL.sh

# 3. Check dashboard
# https://logfire.pydantic.dev/
```

---

**Questions?** Check:
- `LOCAL_LOGFIRE_SETUP.md` - Detailed guide
- `LOGFIRE_SOLUTION.md` - Why no logs in production
- `LOGFIRE_TROUBLESHOOTING.md` - Common issues
