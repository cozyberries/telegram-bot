#!/bin/bash
# Quick Deployment Script for Telegram Bot on Vercel

set -e

echo "🚀 Telegram Bot - Quick Deployment to Vercel"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file with required variables."
    echo "See .env.local.example for template."
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ TELEGRAM_BOT_TOKEN not set in .env${NC}"
    exit 1
fi

if [ -z "$ADMIN_TELEGRAM_USER_IDS" ]; then
    echo -e "${YELLOW}⚠️  ADMIN_TELEGRAM_USER_IDS not set${NC}"
fi

if [ -z "$SUPABASE_URL" ]; then
    echo -e "${YELLOW}⚠️  SUPABASE_URL not set${NC}"
fi

echo "✅ Environment variables loaded"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not found${NC}"
    echo "Install with: npm i -g vercel"
    exit 1
fi

echo "✅ Vercel CLI found"
echo ""

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

# Get deployment URL
DEPLOYMENT_URL=$(vercel --prod 2>&1 | grep -o 'https://[^[:space:]]*' | tail -1)
if [ -z "$DEPLOYMENT_URL" ]; then
    DEPLOYMENT_URL="https://telegram-aeyusvb61-cozyberries-projects.vercel.app"
fi

echo "🌐 Production URL: $DEPLOYMENT_URL"
echo ""

# Ask to set webhook
read -p "Do you want to set the Telegram webhook now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔗 Setting Telegram webhook..."
    WEBHOOK_URL="${DEPLOYMENT_URL}/api/webhook"
    
    RESPONSE=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}")
    
    if echo "$RESPONSE" | grep -q '"ok":true'; then
        echo -e "${GREEN}✅ Webhook set successfully!${NC}"
        echo "Webhook URL: $WEBHOOK_URL"
    else
        echo -e "${RED}❌ Failed to set webhook${NC}"
        echo "Response: $RESPONSE"
        echo ""
        echo "Set manually with:"
        echo "python scripts/setup_webhook.py set --url $WEBHOOK_URL"
    fi
else
    echo "⏭️  Skipping webhook setup"
    echo ""
    echo "Set webhook manually with:"
    echo "python scripts/setup_webhook.py set --url ${DEPLOYMENT_URL}/api/webhook"
fi

echo ""
echo "📊 Check deployment status:"
echo "   vercel ls"
echo ""
echo "📝 View logs:"
echo "   vercel logs --follow"
echo ""
echo "🔍 Test bot:"
echo "   Open Telegram and send /start to your bot"
echo ""
echo -e "${GREEN}✅ All done!${NC}"
