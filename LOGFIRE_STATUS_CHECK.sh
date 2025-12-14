#!/bin/bash
# Quick Logfire status check script

echo "🔥 Logfire Status Check"
echo "======================="
echo ""

echo "1️⃣ Environment Variables:"
vercel env ls 2>&1 | grep LOGFIRE || echo "❌ No Logfire env vars found"
echo ""

echo "2️⃣ Webhook Status:"
curl -s https://bot.cozyberries.in/webhook | jq '.' 2>/dev/null || curl -s https://bot.cozyberries.in/webhook
echo ""

echo "3️⃣ Recent Deployment:"
vercel ls | grep telegram | head -3
echo ""

echo "4️⃣ Test by sending message to bot, then check:"
echo "   - Vercel logs: vercel logs | tail -50"
echo "   - Logfire: https://logfire.pydantic.dev/"
echo ""

echo "Expected in webhook status:"
echo '  "logfire": "enabled"  ✅'
echo '  "LOGFIRE_TOKEN": "set"  ✅'
