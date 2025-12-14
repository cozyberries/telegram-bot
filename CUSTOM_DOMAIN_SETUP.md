# Custom Domain Setup for Telegram Bot

## Suggested Subdomains

Choose one of these subdomains for your Telegram bot:

1. **`bot.cozyberries.in`** ⭐ (Recommended - simple and clear)
2. **`telegram.cozyberries.in`** (Descriptive)
3. **`admin-bot.cozyberries.in`** (Specific to admin functionality)
4. **`api.cozyberries.in`** (Generic API endpoint)
5. **`webhook.cozyberries.in`** (Webhook-focused)

**Recommendation**: Use `bot.cozyberries.in` - it's short, memorable, and clearly indicates it's for the bot.

## Setup Instructions

### Step 1: Add Domain to Vercel Project

#### Option A: Via Vercel Dashboard (Easiest)

1. Go to: https://vercel.com/cozyberries-projects/telegram-bot/settings/domains

2. Click "Add Domain"

3. Enter your chosen subdomain: `bot.cozyberries.in`

4. Click "Add"

5. Vercel will show you the DNS configuration needed

#### Option B: Via Vercel CLI

```bash
cd /Users/abdul.azeez/Personal/cozyberries/telegram-bot

# Add the domain
vercel domains add bot.cozyberries.in telegram-bot
```

### Step 2: Configure DNS Records

Since `cozyberries.in` is already in Vercel, you need to add a CNAME record for the subdomain.

#### If using Vercel DNS (Domain registered with Vercel)

Vercel will automatically configure the DNS for you. No action needed!

#### If using External DNS Provider (e.g., GoDaddy, Cloudflare, Namecheap)

Add this DNS record to your domain provider:

```
Type:  CNAME
Name:  bot
Value: cname.vercel-dns.com.
TTL:   3600 (or Auto)
```

**Example configurations:**

**Cloudflare:**
```
Type: CNAME
Name: bot
Target: cname.vercel-dns.com
Proxy status: DNS only (gray cloud)
TTL: Auto
```

**GoDaddy:**
```
Type: CNAME
Host: bot
Points to: cname.vercel-dns.com
TTL: 1 Hour
```

**Namecheap:**
```
Type: CNAME Record
Host: bot
Value: cname.vercel-dns.com
TTL: Automatic
```

### Step 3: Verify Domain Configuration

```bash
# Check DNS propagation (may take 5-30 minutes)
dig bot.cozyberries.in

# Or use online tool
# https://www.whatsmydns.net/#CNAME/bot.cozyberries.in
```

Expected output:
```
bot.cozyberries.in.    300    IN    CNAME    cname.vercel-dns.com.
```

### Step 4: Wait for SSL Certificate

Vercel automatically provisions SSL certificates via Let's Encrypt. This takes 1-5 minutes after DNS propagation.

You'll see in Vercel Dashboard:
- 🟡 Pending (DNS not propagated yet)
- 🟢 Valid (Domain configured and SSL active)

### Step 5: Update Telegram Webhook

After domain is verified and SSL is active:

```bash
cd /Users/abdul.azeez/Personal/cozyberries/telegram-bot

# Set webhook with custom domain
python scripts/setup_webhook.py set --url https://bot.cozyberries.in/api/webhook

# Verify webhook
python scripts/setup_webhook.py info
```

Or manually:
```bash
# Get bot token
export TELEGRAM_BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d '=' -f2)

# Set webhook
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -d "url=https://bot.cozyberries.in/api/webhook"

# Verify
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

### Step 6: Update Supabase Webhook (if configured)

Update the Supabase webhook URL to use the custom domain:

1. Go to Supabase Dashboard → Database → Webhooks
2. Edit the `telegram-order-notification` webhook
3. Change URL to: `https://bot.cozyberries.in/api/notify-order`
4. Save

### Step 7: Test the Bot

```bash
# Test health endpoint
curl https://bot.cozyberries.in/api/health

# Expected response
{"status": "healthy", "service": "telegram-bot"}

# Test webhook endpoint (will return 200 if configured)
curl -X POST https://bot.cozyberries.in/api/webhook \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Quick Setup Commands

```bash
# 1. Add domain to Vercel
vercel domains add bot.cozyberries.in telegram-bot

# 2. Check domain status
vercel domains ls

# 3. After DNS propagation, update webhook
python scripts/setup_webhook.py set --url https://bot.cozyberries.in/api/webhook

# 4. Verify everything works
curl https://bot.cozyberries.in/api/health
```

## Troubleshooting

### Domain shows "Invalid Configuration"

**Check DNS:**
```bash
dig bot.cozyberries.in CNAME
nslookup bot.cozyberries.in
```

**Common issues:**
- DNS not propagated yet (wait 5-30 minutes)
- Wrong CNAME value (should be `cname.vercel-dns.com`)
- Proxy enabled on Cloudflare (disable for initial setup)

### SSL Certificate Pending

- Wait 5 minutes after DNS propagation
- Vercel automatically provisions Let's Encrypt certificate
- Check status in Vercel Dashboard → Domains

### Webhook Not Working

```bash
# Check webhook info
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"

# Should show:
# "url": "https://bot.cozyberries.in/api/webhook"
# "has_custom_certificate": false
# "pending_update_count": 0
```

If pending_update_count > 0:
- Bot might have errors processing updates
- Check Vercel logs: `vercel logs --follow`

### Domain Not Accessible

```bash
# Test with curl
curl -I https://bot.cozyberries.in/api/health

# Expected: HTTP/2 200
```

If getting errors:
- Check Vercel deployment status: `vercel ls`
- Verify domain in Vercel Dashboard
- Check DNS propagation

## Environment Variables Update

After setting custom domain, update environment variables if needed:

```bash
# If BOT_WEBHOOK_URL is used in code
vercel env add BOT_WEBHOOK_URL production
# Value: https://bot.cozyberries.in
```

## Benefits of Custom Domain

✅ Professional appearance: `bot.cozyberries.in` vs long Vercel URL
✅ Easier to remember and share
✅ Consistent branding with main domain
✅ Better for webhooks (cleaner URLs)
✅ Can change deployment without changing webhook

## Domain Management

### Check domain status
```bash
vercel domains ls
```

### Remove domain (if needed)
```bash
vercel domains rm bot.cozyberries.in
```

### Inspect domain configuration
```bash
vercel domains inspect bot.cozyberries.in
```

## Final Configuration

After setup is complete, your endpoints will be:

| Endpoint | URL |
|----------|-----|
| Health Check | https://bot.cozyberries.in/api/health |
| Telegram Webhook | https://bot.cozyberries.in/api/webhook |
| Order Notification | https://bot.cozyberries.in/api/notify-order |

---

**Estimated Setup Time**: 10-30 minutes (including DNS propagation)

**Status Checks**:
- DNS: https://www.whatsmydns.net/#CNAME/bot.cozyberries.in
- SSL: https://www.ssllabs.com/ssltest/analyze.html?d=bot.cozyberries.in
- Vercel: https://vercel.com/cozyberries-projects/telegram-bot/settings/domains
