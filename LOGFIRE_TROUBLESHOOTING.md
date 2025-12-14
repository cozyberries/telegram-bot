# 🔥 Logfire Troubleshooting Guide

## Issue: No logs appearing in Logfire dashboard

### Quick Checks

#### 1. Verify Environment Variables Are Set
```bash
vercel env ls | grep LOGFIRE
```

Should show:
```
✅ LOGFIRE_TOKEN                    Encrypted
✅ LOGFIRE_PROJECT_NAME             Encrypted  
✅ LOGFIRE_ENVIRONMENT              Encrypted
```

#### 2. Check Webhook Status
```bash
curl https://bot.cozyberries.in/webhook
```

Should show:
```json
{
  "status": "ok",
  "logfire": "enabled",  // ← Should say "enabled"
  "env": {
    "LOGFIRE_TOKEN": "set"  // ← Should say "set"
  }
}
```

#### 3. Check Vercel Logs
```bash
vercel logs --follow
```

Look for:
- `🔥 Configuring Logfire` - Logfire initialization
- `✅ Logfire configured successfully` - Success message
- `⚠️ LOGFIRE_TOKEN not set` - Token missing (problem)
- `❌ Failed to configure Logfire` - Configuration error

#### 4. Send Test Message
```bash
# Send /start to your bot on Telegram
# Check Vercel logs immediately after
vercel logs | tail -20
```

### Common Issues

#### Issue 1: Environment Variables Not Applied

**Problem**: Variables set but not taking effect

**Solution**:
```bash
# After setting environment variables, MUST redeploy
vercel --prod

# Wait 30 seconds, then test
sleep 30
curl https://bot.cozyberries.in/webhook
```

#### Issue 2: Wrong Logfire Project

**Problem**: Logs going to wrong project or not visible

**Solution**:
1. Check project name in Logfire dashboard matches env var
2. Verify: `vercel env ls | grep LOGFIRE_PROJECT_NAME`
3. Should be: `cozyberries-telegram-bot`

#### Issue 3: Logfire Token Invalid

**Problem**: Token expired or incorrect

**Solution**:
1. Generate new token in Logfire dashboard
2. Update in Vercel:
   ```bash
   # Remove old token
   vercel env rm LOGFIRE_TOKEN production
   
   # Add new token
   vercel env add LOGFIRE_TOKEN production
   # Paste new token when prompted
   
   # Redeploy
   vercel --prod
   ```

#### Issue 4: Import Errors

**Problem**: Logfire module not installed

**Check Vercel build logs**:
```bash
vercel logs deployment-url | grep -i "import\|error"
```

**Solution**: Ensure `logfire==0.54.0` in requirements.txt

#### Issue 5: Cold Start Issues

**Problem**: First request after deployment doesn't log

**This is normal**: Logfire initializes on first request
- First message may not be logged
- Subsequent messages will be logged
- Send 2-3 test messages

### Debugging Steps

#### Step 1: Test Webhook Endpoint
```bash
curl https://bot.cozyberries.in/webhook
```

Expected response:
```json
{
  "status": "ok",
  "bot": "CozyBerries Admin Bot",
  "webhook": "active",
  "logfire": "enabled",  // ← Key indicator
  "env": {
    "LOGFIRE_TOKEN": "set"
  }
}
```

If `"logfire": "disabled"`:
- Token not set OR
- Token is empty string OR
- Logfire not initializing

#### Step 2: Check Vercel Deployment Logs
```bash
# Get latest deployment
vercel ls | grep telegram | head -1

# View logs for that deployment
vercel logs [deployment-url]
```

Look for Logfire-related messages

#### Step 3: Trigger Manual Log
Send this request to test Logfire directly:
```bash
curl -X POST https://bot.cozyberries.in/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 999999999,
    "message": {
      "message_id": 1,
      "from": {"id": 123, "is_bot": false, "first_name": "Test"},
      "chat": {"id": 123, "type": "private"},
      "date": 1234567890,
      "text": "/start"
    }
  }'
```

Then check:
1. Vercel logs: `vercel logs | tail -30`
2. Logfire dashboard: https://logfire.pydantic.dev/

#### Step 4: Verify Logfire Dashboard

1. Go to: https://logfire.pydantic.dev/
2. Select correct project: `cozyberries-telegram-bot`
3. Check environment filter: `production`
4. Time range: Last 15 minutes

### Manual Test Script

```bash
#!/bin/bash
# test_logfire.sh

echo "🔍 Testing Logfire Integration"
echo ""

# 1. Check environment variables
echo "1️⃣ Checking environment variables..."
vercel env ls | grep LOGFIRE
echo ""

# 2. Test webhook endpoint
echo "2️⃣ Testing webhook endpoint..."
curl -s https://bot.cozyberries.in/webhook | jq '.'
echo ""

# 3. Send test update
echo "3️⃣ Sending test update..."
curl -X POST https://bot.cozyberries.in/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 999999999,
    "message": {
      "message_id": 1,
      "from": {"id": 123, "is_bot": false, "first_name": "Test"},
      "chat": {"id": 123, "type": "private"},
      "date": 1234567890,
      "text": "/start"
    }
  }' | jq '.'
echo ""

# 4. Check logs
echo "4️⃣ Checking recent logs..."
echo "Run: vercel logs | tail -50"
echo ""

echo "5️⃣ Check Logfire dashboard:"
echo "https://logfire.pydantic.dev/"
```

### Expected Log Flow

```
[Vercel Logs]
📨 Received update: 999999999
🔥 Configuring Logfire: cozyberries-telegram-bot (production)
Token present: lf_abc123...
✅ Logfire configured successfully
🔥 Logged to Logfire: webhook_request_received
🔥 Started Logfire span for update 999999999
✅ Successfully processed update 999999999
```

### Logfire Dashboard

If everything works, you should see in Logfire:

**Traces**:
- `telegram_update` spans with update_id, user_id, command
- Duration and status

**Logs**:
- `logfire_initialized` - Initial config
- `webhook_request_received` - Each webhook call
- `update_processed` - Processing results

**Filters to try**:
```
update_id:999999999
event_name:webhook_request_received
environment:production
```

### Still Not Working?

#### Checklist:
- [ ] Environment variables set in Vercel dashboard
- [ ] Redeployed after setting variables
- [ ] Waited 30+ seconds after deployment
- [ ] Sent test message to bot
- [ ] Checked Vercel logs for Logfire messages
- [ ] Verified correct Logfire project selected
- [ ] Tried different time range in Logfire
- [ ] Token is valid (not expired)

#### Get Help:
1. Run test script above
2. Collect output
3. Check Vercel logs: `vercel logs > logs.txt`
4. Check webhook status: `curl https://bot.cozyberries.in/webhook > status.json`

### Alternative: Test Locally

```bash
# 1. Set environment variables
export LOGFIRE_TOKEN=your_token_here
export LOGFIRE_PROJECT_NAME=cozyberries-telegram-bot
export LOGFIRE_ENVIRONMENT=development

# 2. Run locally
uvicorn app.main:app --reload

# 3. Use ngrok
ngrok http 8000

# 4. Set webhook
python scripts/setup_webhook.py set --url https://your-ngrok.ngrok.io/webhook

# 5. Send message to bot
# 6. Check terminal logs AND Logfire dashboard
```

### Quick Fix Commands

```bash
# Reset environment variables
vercel env rm LOGFIRE_TOKEN production
vercel env rm LOGFIRE_PROJECT_NAME production
vercel env rm LOGFIRE_ENVIRONMENT production

# Re-add them
vercel env add LOGFIRE_TOKEN production
vercel env add LOGFIRE_PROJECT_NAME production
vercel env add LOGFIRE_ENVIRONMENT production

# Redeploy
vercel --prod

# Wait and test
sleep 30
curl https://bot.cozyberries.in/webhook
```

---

**Most Common Solution**: Redeploy after setting environment variables!
```bash
vercel --prod
```
