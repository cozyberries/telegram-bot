# 🔥 Logfire Quick Start (5 Minutes)

## What You Get

- Real-time logs for every bot message
- Performance tracking
- Error monitoring
- Database query tracing
- User behavior analytics

## Setup (3 Steps)

### 1. Get Logfire Token (2 min)

```bash
# Visit Logfire
open https://logfire.pydantic.dev/

# Sign up → Create project → Copy token
```

### 2. Add to Vercel (1 min)

```bash
# Go to environment variables
open https://vercel.com/cozyberries-projects/telegram-bot/settings/environment-variables

# Add:
LOGFIRE_TOKEN=your_token_here
```

### 3. Redeploy (2 min)

```bash
vercel --prod
```

## Done! 🎉

Now send a message to your bot and watch it appear in Logfire dashboard:

```bash
open https://logfire.pydantic.dev/
```

## What Gets Logged Automatically

✅ Every bot command
✅ User IDs and messages
✅ Database queries
✅ Response times
✅ Errors and stack traces
✅ Business metrics

## Example Log

```
[telegram_update]
├─ update_id: 123456789
├─ user_id: 123456789
├─ command: /start
├─ duration: 45ms
└─ status: ✅ success

[database_operation]
├─ operation: SELECT
├─ table: orders
├─ duration: 12ms
└─ rows: 5
```

## Benefits

📊 **See What's Happening**: Real-time view of all bot activity  
🐛 **Debug Faster**: See exact error context  
⚡ **Optimize Performance**: Find slow operations  
📈 **Track Growth**: Monitor command usage  

---

**Full guide**: See `LOGFIRE_SETUP.md`
