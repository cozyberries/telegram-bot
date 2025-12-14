# Quick Start Guide

Get your CozyBerries Telegram Bot up and running in 10 minutes!

## Step 1: Get Telegram Bot Token (2 min)

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## Step 2: Get Your Telegram User ID (1 min)

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your User ID (a number like: `123456789`)

## Step 3: Get Supabase Credentials (1 min)

1. Go to your Supabase project dashboard
2. Go to Settings → API
3. Copy:
   - Project URL (e.g., `https://abc123.supabase.co`)
   - Service Role Key (starts with `eyJ...`)

## Step 4: Deploy to Vercel (3 min)

```bash
# Navigate to bot directory
cd telegram-bot

# Login to Vercel (if not already logged in)
vercel login

# Set environment variables
vercel env add TELEGRAM_BOT_TOKEN
# Paste your bot token when prompted

vercel env add ADMIN_TELEGRAM_USER_IDS
# Paste your user ID (can add multiple: 123,456,789)

vercel env add SUPABASE_URL
# Paste your Supabase project URL

vercel env add SUPABASE_SERVICE_ROLE_KEY
# Paste your Supabase service role key

# Deploy!
vercel --prod
```

## Step 5: Set Telegram Webhook (1 min)

After deployment, Vercel will show your URL (e.g., `https://your-bot.vercel.app`)

```bash
# Replace YOUR_BOT_TOKEN and YOUR_VERCEL_URL
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://YOUR_VERCEL_URL/api/webhook"}'
```

Or use the script:
```bash
python scripts/setup_webhook.py set --url https://your-bot.vercel.app/api/webhook
```

## Step 6: Test Your Bot! (1 min)

1. Open Telegram
2. Search for your bot (@your_bot_name)
3. Send `/start`
4. You should see a welcome message!
5. Try `/help` to see all commands

## Step 7: (Optional) Setup Order Notifications (1 min)

1. Go to Supabase Dashboard → Database → Webhooks
2. Create new webhook:
   - **Table**: orders
   - **Events**: INSERT
   - **Type**: HTTP Request
   - **URL**: `https://your-bot.vercel.app/api/notify-order`
3. Save

## Verify Everything Works

```bash
# Test health endpoint
curl https://your-bot.vercel.app/api/health

# Should return: {"status": "ok", ...}
```

## Common Commands to Try

```
/start       - Welcome message
/help        - Show all commands
/products    - List products
/orders      - View orders
/stats       - Business statistics
```

## Troubleshooting

### Bot not responding?
```bash
# Check webhook status
curl https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo
```

### Access denied?
- Make sure your Telegram user ID is in `ADMIN_TELEGRAM_USER_IDS`
- Check you entered it correctly (no spaces between IDs)

### Need help?
1. Check `README.md` for detailed documentation
2. Check `DEPLOYMENT.md` for troubleshooting steps
3. View Vercel logs: `vercel logs`

## Next Steps

- Read full documentation in `README.md`
- Set up additional admin users
- Configure Supabase webhooks
- Test all features
- Share bot with team

---

**Time to complete**: ~10 minutes
**Difficulty**: Easy
**Prerequisites**: Telegram account, Supabase project, Vercel account
