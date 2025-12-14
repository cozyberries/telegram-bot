# AWS Lambda Deployment Fix - Event Loop Issue

## Problem

The error `RuntimeError('Event loop is closed')` occurs in AWS Lambda because:

1. Lambda containers reuse Python interpreters across invocations
2. The event loop gets closed after the first invocation
3. The Telegram bot's HTTP client tries to use the closed loop
4. This causes all subsequent requests to fail

## Solution

I've created a Lambda-specific handler that properly manages the event loop lifecycle.

## Files Created/Updated

### 1. **lambda_handler.py** (NEW)

Main Lambda handler with proper event loop management:

```python
# Key features:
- Creates fresh event loop when needed
- Reuses bot instance across invocations (warm starts)
- Handles all Lambda event formats
- Proper error handling and logging
```

**Location:** `/telegram-bot/app/lambda_handler.py`

### 2. **app/bot/bot.py** (UPDATED)

Added `stop()` method for cleanup:

```python
def stop(self):
    """Stop the bot and cleanup resources"""
    # Minimal cleanup - let Lambda handle the rest
```

## Deployment Instructions

### Option 1: Update Lambda Handler Configuration

1. **Update Lambda function configuration:**
   ```bash
   # In AWS Lambda Console or via AWS CLI
   Handler: app.lambda_handler.lambda_handler
   ```

2. **Or in your deployment config (serverless.yml, SAM template, etc.):**
   ```yaml
   # serverless.yml example
   functions:
     telegram-bot:
       handler: app.lambda_handler.lambda_handler
       events:
         - http:
             path: /webhook
             method: post
   ```

3. **Or in AWS CDK:**
   ```python
   lambda_function = lambda_.Function(
       self, "TelegramBot",
       handler="app.lambda_handler.lambda_handler",
       # ... other config
   )
   ```

### Option 2: Update Existing Handler

If you want to keep your current handler name, copy the event loop management logic:

```python
# In your existing handler:
try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        raise RuntimeError("Loop is closed")
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.info("Created new event loop")

# Run your async code
result = loop.run_until_complete(your_async_function())

# DON'T close the loop - let Lambda manage it
```

## Environment Variables

Make sure these are set in Lambda:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key  # or SUPABASE_SERVICE_ROLE_KEY
ADMIN_USER_IDS=comma,separated,user,ids
```

## Testing

### 1. Test Locally

```bash
# Run the test at the bottom of lambda_handler.py
python -m pytest tests/test_lambda_handler.py
```

### 2. Test in Lambda

Use the Lambda Test console with this event:

```json
{
  "httpMethod": "POST",
  "path": "/webhook",
  "body": "{\"update_id\":123456,\"message\":{\"message_id\":1,\"from\":{\"id\":123456789,\"first_name\":\"Test\"},\"chat\":{\"id\":123456789,\"type\":\"private\"},\"text\":\"/start\",\"date\":1234567890}}"
}
```

### 3. Test via API Gateway

```bash
curl -X POST https://your-api-gateway-url/webhook \
  -H "Content-Type: application/json" \
  -d '{"update_id":123456,"message":{"message_id":1,"from":{"id":123456789,"first_name":"Test"},"chat":{"id":123456789,"type":"private"},"text":"/start","date":1234567890}}'
```

## Key Changes Explained

### 1. Event Loop Management

**Before (Causes Error):**
```python
# Event loop gets closed after first invocation
# Subsequent calls fail with "Event loop is closed"
```

**After (Fixed):**
```python
# Check if loop exists and is open
try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        raise RuntimeError("Loop is closed")
except RuntimeError:
    # Create new loop if needed
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
```

### 2. Resource Reuse

**Global instances for warm starts:**
```python
# Reused across Lambda invocations
_bot_instance = None  

def get_or_create_bot():
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TelegramBot()
        _bot_instance.initialize()
    return _bot_instance
```

### 3. No Loop Cleanup

**Important:** Don't close the event loop in Lambda:
```python
# ❌ DON'T DO THIS in Lambda:
finally:
    loop.close()  # This causes the error!

# ✅ DO THIS instead:
finally:
    pass  # Let Lambda manage the loop
```

## Monitoring

Add CloudWatch logging to monitor:

```python
logger.info("🔄 Created new event loop for Lambda invocation")
logger.info("✅ Bot initialized successfully")
logger.info(f"📨 Processing update: {update_id}")
```

## Troubleshooting

### Error Still Occurs

1. **Check handler name:**
   ```bash
   # Should be: app.lambda_handler.lambda_handler
   aws lambda get-function-configuration --function-name your-function-name
   ```

2. **Check Python version:**
   ```bash
   # Should be Python 3.11 or 3.12
   ```

3. **Check dependencies:**
   ```bash
   # Make sure python-telegram-bot is in your deployment package
   pip freeze | grep python-telegram-bot
   ```

### Cold Start Issues

If bot takes too long to initialize:

1. **Increase Lambda timeout:**
   ```yaml
   timeout: 30  # seconds
   ```

2. **Increase memory:**
   ```yaml
   memory: 512  # MB
   ```

3. **Use provisioned concurrency:**
   ```bash
   aws lambda put-provisioned-concurrency-config \
     --function-name your-function \
     --provisioned-concurrent-executions 1
   ```

## Deployment Checklist

- [ ] `app/lambda_handler.py` added to deployment package
- [ ] Lambda handler updated to `app.lambda_handler.lambda_handler`
- [ ] Environment variables configured
- [ ] Timeout set to at least 30 seconds
- [ ] Memory set to at least 512 MB
- [ ] All dependencies included in package
- [ ] API Gateway configured correctly
- [ ] Telegram webhook set to Lambda URL
- [ ] CloudWatch logs enabled
- [ ] Test invocation successful

## Additional Resources

- [AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [python-telegram-bot Webhook Guide](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks)
- [Async in AWS Lambda](https://aws.amazon.com/blogs/compute/using-python-asyncio-in-aws-lambda/)

## Support

If you continue to experience issues:

1. Check CloudWatch logs for detailed error messages
2. Verify environment variables are set correctly
3. Test locally first using `python -m pytest tests/test_lambda_handler.py`
4. Ensure Telegram webhook is pointed to the correct URL

---

**Status:** ✅ Ready for deployment
**Last Updated:** December 14, 2025
