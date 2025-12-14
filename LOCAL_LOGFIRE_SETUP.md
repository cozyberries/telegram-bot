# Local Logfire Testing Guide

## Quick Setup (5 minutes)

### Step 1: Get Logfire Token
1. Go to https://logfire.pydantic.dev/
2. Sign up / Log in (free tier available)
3. Create project: cozyberries-telegram-bot
4. Settings → API Tokens → Create token

### Step 2: Configure Environment
```bash
cp .env.local.example .env.local
nano .env.local
```

Add:
```env
LOGFIRE_TOKEN=lf_your_token_here
LOGFIRE_PROJECT_NAME=cozyberries-telegram-bot
LOGFIRE_ENVIRONMENT=development
```

### Step 3: Run Tests
```bash
./TEST_LOGFIRE_LOCAL.sh
```

In another terminal:
```bash
./TEST_ENDPOINTS.sh
```

### Step 4: Check Dashboard
https://logfire.pydantic.dev/

## Expected Results

### Terminal Logs:
```
✅ Logfire configured for FastAPI
🔥 Health check - logged to Logfire
```

### Logfire Dashboard:
- Events: app_startup, api_request
- Spans: api_request with endpoints
- Metrics: health_check count
