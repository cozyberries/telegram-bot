# 🔧 Troubleshooting Guide - Telegram Bot Not Responding

## Issue: Bot receives messages but doesn't respond

### Quick Diagnostics

#### 1. Check Webhook Status
```bash
export TELEGRAM_BOT_TOKEN="your-token-here"
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

**Good Response:**
```json
{
  "ok": true,
  "result": {
    "url": "https://bot.cozyberries.in/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": 0,
    "max_connections": 40
  }
}
```

**Problem Signs:**
- `pending_update_count > 0` - Updates are queuing up (bot not processing them)
- `last_error_date` present - Bot returning errors
- `last_error_message` - Shows what error occurred

#### 2. Check Environment Variables in Vercel
```bash
vercel env ls
```

Required variables:
- ✅ `TELEGRAM_BOT_TOKEN`
- ✅ `ADMIN_TELEGRAM_USER_IDS`
- ✅ `SUPABASE_URL`
- ✅ `SUPABASE_SERVICE_ROLE_KEY`

#### 3. Test Webhook Endpoint
```bash
bash scripts/test_webhook.sh
```

Or manually:
```bash
curl -X POST https://bot.cozyberries.in/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {"id": 123456789, "is_bot": false, "first_name": "Test"},
      "chat": {"id": 123456789, "type": "private"},
      "date": 1234567890,
      "text": "/start"
    }
  }'
```

#### 4. Check Vercel Logs
```bash
# Get latest deployment URL
vercel ls | grep telegram | head -1

# View logs (replace with your deployment URL)
vercel logs https://telegram-xxxxx-cozyberries-projects.vercel.app

# Or follow live logs
vercel logs --follow
```

---

## Common Issues & Solutions

### Issue 1: "pending_update_count" is growing

**Problem**: Bot receives updates but doesn't process them

**Solution**:
1. Check if environment variables are set in Vercel
2. Redeploy after setting env vars:
   ```bash
   vercel --prod
   ```
3. Clear pending updates:
   ```bash
   curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates?offset=-1"
   ```

### Issue 2: Bot responds locally but not in production

**Problem**: Works with `uvicorn` locally but not on Vercel

**Checklist**:
- ✅ Environment variables set in Vercel dashboard
- ✅ Webhook URL points to production domain
- ✅ Latest code deployed to Vercel
- ✅ No errors in Vercel logs

**Fix**:
```bash
# 1. Set webhook to production
python scripts/setup_webhook.py set --url https://bot.cozyberries.in/webhook

# 2. Verify
python scripts/setup_webhook.py info

# 3. Test with actual Telegram message
# Send /start to your bot on Telegram
```

### Issue 3: "Admin only" message appears

**Problem**: Bot responds with "Admin only" to all users

**Solution**:
1. Get your Telegram user ID:
   - Message @userinfobot on Telegram
   - Or send /start to your bot and check logs

2. Add your user ID to Vercel env vars:
   ```
   ADMIN_TELEGRAM_USER_IDS=123456789,987654321
   ```

3. Redeploy:
   ```bash
   vercel --prod
   ```

### Issue 4: Import errors or module not found

**Problem**: Vercel logs show import errors

**Solution**:
1. Check `requirements.txt` has all dependencies:
   ```bash
   cat requirements.txt
   ```

2. Ensure dependency versions are compatible:
   ```
   python-telegram-bot==20.7
   httpx==0.25.2
   supabase==2.3.4
   ```

3. Redeploy:
   ```bash
   vercel --prod
   ```

### Issue 5: Timeout or slow responses

**Problem**: Bot takes too long to respond or times out

**Solution**:
1. Vercel has 10-second timeout for serverless functions
2. For long operations, acknowledge immediately then process:
   ```python
   # Send "Processing..." immediately
   await update.message.reply_text("Processing...")
   
   # Do long operation
   result = await long_operation()
   
   # Send result
   await update.message.reply_text(f"Result: {result}")
   ```

---

## Debugging Steps

### Step 1: Test Webhook Locally

```bash
# 1. Start local server
uvicorn app.main:app --reload --port 8000

# 2. Use ngrok to expose
ngrok http 8000

# 3. Set webhook to ngrok URL
python scripts/setup_webhook.py set --url https://your-ngrok-url.ngrok.io/webhook

# 4. Test bot on Telegram
# Send /start and check terminal logs
```

### Step 2: Check Bot Token

```bash
# Verify bot token is valid
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# Should return bot information:
{
  "ok": true,
  "result": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "YourBot",
    "username": "your_bot"
  }
}
```

### Step 3: Test Without Admin Middleware

Temporarily remove `@admin_required` decorator to test if authentication is the issue:

```python
# In app/bot/handlers/start.py
# Comment out @admin_required
# @admin_required  # <-- Comment this
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is working!")
```

### Step 4: Check Supabase Connection

```bash
# Test Supabase connection
python scripts/test_connection.py
```

---

## Production Checklist

Before expecting bot to work in production:

- [ ] Environment variables set in Vercel dashboard
- [ ] `TELEGRAM_BOT_TOKEN` is correct
- [ ] `ADMIN_TELEGRAM_USER_IDS` includes your Telegram user ID
- [ ] `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
- [ ] Latest code deployed: `vercel --prod`
- [ ] Webhook URL set correctly: `https://bot.cozyberries.in/webhook`
- [ ] Webhook status shows `pending_update_count: 0`
- [ ] No errors in Vercel logs: `vercel logs`
- [ ] Bot responds to test message on Telegram

---

## Getting Help

### Collect Information

```bash
# 1. Webhook status
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo" > webhook_status.json

# 2. Vercel logs
vercel logs > vercel_logs.txt

# 3. Environment variables (without values)
vercel env ls > env_vars.txt

# 4. Test webhook
bash scripts/test_webhook.sh > webhook_test.txt
```

### Check Logs for Common Errors

```bash
# Search for errors in logs
vercel logs | grep -i "error"
vercel logs | grep -i "exception"
vercel logs | grep -i "failed"
```

---

## Quick Fixes

### Reset Everything

```bash
# 1. Clear pending updates
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates?offset=-1"

# 2. Delete webhook
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook"

# 3. Redeploy
vercel --prod

# 4. Set webhook again
python scripts/setup_webhook.py set --url https://bot.cozyberries.in/webhook

# 5. Test
# Send /start to bot on Telegram
```

### Force Redeploy

```bash
# Commit a small change
git commit --allow-empty -m "Force redeploy"
git push origin main

# Or redeploy directly
vercel --prod --force
```

---

## Still Not Working?

1. **Check this file**: `vercel logs` for any Python errors
2. **Verify webhook**: Use @userinfobot to get your Telegram user ID
3. **Test locally**: Run `uvicorn app.main:app --reload` and use ngrok
4. **Check versions**: Ensure Python 3.13 and correct package versions

**Last resort**: Delete and recreate the webhook:
```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook"
sleep 5
python scripts/setup_webhook.py set --url https://bot.cozyberries.in/webhook
```

---

**Pro Tip**: Add verbose logging by setting `LOG_LEVEL=DEBUG` in Vercel environment variables.
