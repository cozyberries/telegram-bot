#!/bin/bash
# Setup custom domain for Telegram Bot

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🌐 Custom Domain Setup for Telegram Bot${NC}"
echo "========================================"
echo ""

# Suggested subdomain
DOMAIN="bot.cozyberries.in"
echo -e "${YELLOW}Suggested subdomain: ${GREEN}${DOMAIN}${NC}"
echo ""

# Ask for confirmation
read -p "Use this domain? (y/n) or enter custom subdomain: " response
echo ""

if [[ ! $response =~ ^[Yy]$ ]]; then
    if [[ $response =~ \. ]]; then
        DOMAIN=$response
        echo -e "Using custom domain: ${GREEN}${DOMAIN}${NC}"
    else
        DOMAIN="${response}.cozyberries.in"
        echo -e "Using subdomain: ${GREEN}${DOMAIN}${NC}"
    fi
fi
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not found${NC}"
    echo "Install with: npm i -g vercel"
    exit 1
fi

echo "Step 1: Adding domain to Vercel..."
echo "-----------------------------------"
vercel domains add $DOMAIN telegram-bot || echo -e "${YELLOW}Note: Domain might already be added${NC}"
echo ""

echo "Step 2: Check domain status..."
echo "------------------------------"
vercel domains ls | grep $DOMAIN || echo -e "${YELLOW}Domain not found in list${NC}"
echo ""

echo -e "${GREEN}✅ Domain added to Vercel${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo ""
echo "1. Configure DNS (if not using Vercel DNS):"
echo "   ${BLUE}Add CNAME record:${NC}"
echo "   Type:  CNAME"
echo "   Name:  ${DOMAIN%%.*}  (the subdomain part)"
echo "   Value: cname.vercel-dns.com"
echo "   TTL:   Auto or 3600"
echo ""
echo "2. Wait for DNS propagation (5-30 minutes)"
echo "   Check: https://www.whatsmydns.net/#CNAME/$DOMAIN"
echo ""
echo "3. Verify domain in Vercel:"
echo "   https://vercel.com/cozyberries-projects/telegram-bot/settings/domains"
echo ""
echo "4. After domain shows '${GREEN}Valid${NC}' status, update webhook:"
echo "   ${BLUE}python scripts/setup_webhook.py set --url https://$DOMAIN/api/webhook${NC}"
echo ""
echo "5. Test the bot:"
echo "   ${BLUE}curl https://$DOMAIN/api/health${NC}"
echo ""
echo -e "${GREEN}📖 See CUSTOM_DOMAIN_SETUP.md for detailed instructions${NC}"
