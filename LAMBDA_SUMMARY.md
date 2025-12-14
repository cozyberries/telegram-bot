# AWS Lambda Event Loop Fix - Summary

## Problem Identified

**Error:** `RuntimeError: Event loop is closed`

**Root Cause:**
- AWS Lambda reuses Python interpreter across invocations
- After first invocation, the event loop gets closed
- Telegram bot's HTTP client tries to use the closed loop on subsequent requests
- This causes all follow-up bot commands to fail

## Solution Implemented

### 1. Created Lambda-Specific Handler (`lambda_handler.py`)

**Key Features:**
- ✅ **Event Loop Management**: Creates new loop when closed
- ✅ **Resource Reuse**: Bot instance persists across Lambda warm starts
- ✅ **Proper Initialization**: Application initialized for webhook mode
- ✅ **No Cleanup**: Lets Lambda manage loop lifecycle
- ✅ **Error Handling**: Comprehensive error catching and logging

**Handler Function:**
```python
def lambda_handler(event, context):
    # Handles:
    - POST /webhook  (Telegram updates)
    - GET /webhook   (Info endpoint)
    - GET /health    (Health check)
    - GET /          (Root endpoint)
```

### 2. Updated Bot Class (`app/bot/bot.py`)

**Changes:**
- Added async `application.initialize()` call for webhook mode
- Added `stop()` method for cleanup
- Improved event loop detection and creation
- Better error handling and logging

**Key Code:**
```python
# Initialize application for webhook mode
loop.run_until_complete(self.application.initialize())
```

### 3. Created Test Suite (`test_lambda_handler.py`)

**Tests:**
- ✅ Health check endpoint
- ✅ Webhook info endpoint  
- ✅ Webhook POST processing
- ✅ Multiple invocations (event loop reuse)
- ✅ Invalid endpoint handling

**Test Results:**
```
All tests passing ✅
- Event loop properly managed
- Bot initialization working
- Multiple invocations successful
```

## How It Works

### Event Loop Lifecycle

**Before (Broken):**
```
Invocation 1: Create loop → Process → Close loop ✅
Invocation 2: Try to use closed loop → ERROR ❌
```

**After (Fixed):**
```
Invocation 1: Create/get loop → Process → Keep open ✅
Invocation 2: Reuse loop → Process → Keep open ✅
Invocation 3: Reuse loop → Process → Keep open ✅
```

### Code Flow

1. **Lambda receives event**
   ```python
   lambda_handler(event, context)
   ```

2. **Check/create event loop**
   ```python
   try:
       loop = asyncio.get_event_loop()
       if loop.is_closed():
           loop = asyncio.new_event_loop()
           asyncio.set_event_loop(loop)
   ```

3. **Get/create bot instance** (reused if warm start)
   ```python
   bot = get_or_create_bot()
   if not bot._initialized:
       bot.initialize()
   ```

4. **Initialize application for webhook**
   ```python
   if not bot.application.running:
       await bot.application.initialize()
   ```

5. **Process update**
   ```python
   await bot.process_update(update_data)
   ```

6. **Return response** (NO loop cleanup!)

## Deployment

### Update Lambda Configuration

```yaml
# serverless.yml
functions:
  telegram-bot:
    handler: lambda_handler.lambda_handler
    timeout: 30
    memorySize: 512
    environment:
      TELEGRAM_BOT_TOKEN: ${env:TELEGRAM_BOT_TOKEN}
      SUPABASE_URL: ${env:SUPABASE_URL}
      SUPABASE_KEY: ${env:SUPABASE_KEY}
      ADMIN_USER_IDS: ${env:ADMIN_USER_IDS}
```

### Or via AWS Console

1. Go to Lambda function configuration
2. Update **Handler**: `lambda_handler.lambda_handler`
3. Set **Timeout**: 30 seconds
4. Set **Memory**: 512 MB
5. Add environment variables

### Or via AWS CLI

```bash
aws lambda update-function-configuration \
  --function-name your-telegram-bot \
  --handler lambda_handler.lambda_handler \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{
    TELEGRAM_BOT_TOKEN=your_token,
    SUPABASE_URL=your_url,
    SUPABASE_KEY=your_key,
    ADMIN_USER_IDS=123,456,789
  }"
```

## Testing

### 1. Local Test
```bash
python test_lambda_handler.py
```

### 2. Lambda Test Console

Use this test event:
```json
{
  "httpMethod": "POST",
  "path": "/webhook",
  "body": "{\"update_id\":123456,\"message\":{\"message_id\":1,\"from\":{\"id\":123456789,\"first_name\":\"Test\"},\"chat\":{\"id\":123456789,\"type\":\"private\"},\"text\":\"/start\",\"date\":1234567890}}"
}
```

### 3. Real Telegram Test

After deployment, send a message to your bot:
```
/start
/add_expense
/expenses
```

Check CloudWatch logs for:
```
✅ Application initialized for webhook processing
📨 Processing update: 915251839
✅ Update 915251839 processed successfully
```

## Monitoring

### CloudWatch Logs to Watch

**Success indicators:**
```
🔄 Created new event loop for Lambda invocation
✅ Bot initialized successfully
✅ Application initialized for webhook processing
✅ Update X processed successfully
```

**Error indicators:**
```
❌ RuntimeError: Event loop is closed  (should NOT appear anymore)
❌ Bot not configured
❌ Error processing webhook
```

### Metrics to Track

- **Invocation count**: Should increase
- **Error rate**: Should decrease to near 0%
- **Duration**: Should be consistent (~500-1000ms)
- **Cold start**: First invocation may take 2-3s

## Files Modified/Created

1. **lambda_handler.py** (NEW) - Main Lambda handler
2. **test_lambda_handler.py** (NEW) - Test suite
3. **LAMBDA_FIX.md** (NEW) - Deployment guide
4. **app/bot/bot.py** (MODIFIED) - Added webhook initialization
5. **LAMBDA_SUMMARY.md** (NEW) - This file

## Verification Checklist

- [x] Event loop properly managed
- [x] Bot instance reused across warm starts
- [x] Application initialized for webhook mode
- [x] No loop cleanup (Lambda manages it)
- [x] Comprehensive error handling
- [x] Local tests passing
- [x] Documentation complete

## Expected Results

### Before Fix
```
Update 1: ✅ Success
Update 2: ❌ RuntimeError: Event loop is closed
Update 3: ❌ RuntimeError: Event loop is closed
```

### After Fix
```
Update 1: ✅ Success
Update 2: ✅ Success
Update 3: ✅ Success
Update 4: ✅ Success
...
```

## Support

If issues persist:

1. **Check CloudWatch logs** for detailed error messages
2. **Verify environment variables** are set correctly
3. **Test locally** with `python test_lambda_handler.py`
4. **Check Lambda timeout** (should be at least 30s)
5. **Check Lambda memory** (should be at least 512MB)

## Related Documentation

- `LAMBDA_FIX.md` - Detailed deployment guide
- `test_lambda_handler.py` - Local test suite
- `lambda_handler.py` - Main handler implementation

---

**Status:** ✅ Ready for Production Deployment
**Last Updated:** December 14, 2025
**Tested:** Local tests passing (5/5)
