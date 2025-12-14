# Deployment Checklist

## Pre-Deployment

- [ ] Get Telegram bot token from @BotFather
- [ ] Get your Telegram user ID from @userinfobot
- [ ] Have Supabase project URL and service role key
- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Login to Vercel: `vercel login`

## Configuration

- [ ] Copy `.env.example` to `.env`
- [ ] Set `TELEGRAM_BOT_TOKEN` in `.env`
- [ ] Set `ADMIN_TELEGRAM_USER_IDS` (comma-separated)
- [ ] Set `SUPABASE_URL`
- [ ] Set `SUPABASE_SERVICE_ROLE_KEY`
- [ ] Test locally: `python scripts/test_connection.py`

## Vercel Deployment

### Set Environment Variables in Vercel

```bash
vercel env add TELEGRAM_BOT_TOKEN
vercel env add ADMIN_TELEGRAM_USER_IDS
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_ROLE_KEY
```

### Deploy

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod
```

### After Deployment

- [ ] Note your Vercel deployment URL
- [ ] Set Telegram webhook:
  ```bash
  python scripts/setup_webhook.py set --url https://your-project.vercel.app/api/webhook
  ```
- [ ] Verify webhook: `python scripts/setup_webhook.py info`
- [ ] Test health endpoint: `curl https://your-project.vercel.app/api/health`

## Supabase Webhook Setup

For order notifications:

1. Go to Supabase Dashboard
2. Navigate to: Database → Webhooks
3. Click "Create a new hook"
4. Configure:
   - **Name**: Order Notifications
   - **Table**: orders
   - **Events**: INSERT
   - **Type**: HTTP Request
   - **Method**: POST
   - **URL**: `https://your-project.vercel.app/api/notify-order`
5. Save webhook

## Testing

- [ ] Send `/start` to your bot on Telegram
- [ ] Test `/help` command
- [ ] Test `/products` command
- [ ] Test `/stats` command
- [ ] Create a test order in Supabase (verify notification arrives)
- [ ] Check Vercel logs: `vercel logs`

## Troubleshooting

### Bot not responding
```bash
# Check webhook status
python scripts/setup_webhook.py info

# Check Vercel logs
vercel logs

# Test health endpoint
curl https://your-project.vercel.app/api/health
```

### Authentication issues
- Verify your user ID is in ADMIN_TELEGRAM_USER_IDS
- Check environment variables in Vercel dashboard
- No spaces in comma-separated user IDs

### Deployment errors
```bash
# Check Vercel deployment status
vercel ls

# View detailed logs
vercel logs --follow

# Redeploy
vercel --prod --force
```

## Post-Deployment

- [ ] Document bot commands for team
- [ ] Add monitoring (optional)
- [ ] Set up backup admin user IDs
- [ ] Test all major features
- [ ] Share bot username with team

## Maintenance

### Update bot code
```bash
git pull
vercel --prod
```

### View logs
```bash
vercel logs
vercel logs --follow  # Real-time logs
```

### Update environment variables
```bash
vercel env rm VARIABLE_NAME production
vercel env add VARIABLE_NAME production
vercel --prod  # Redeploy after env changes
```

## Support Resources

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **python-telegram-bot**: https://docs.python-telegram-bot.org/

## Quick Commands Reference

```bash
# Test connections
python scripts/test_connection.py

# Set webhook
python scripts/setup_webhook.py set --url https://your-url.vercel.app/api/webhook

# Check webhook
python scripts/setup_webhook.py info

# Deploy to Vercel
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls
```
