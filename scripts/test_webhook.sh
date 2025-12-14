#!/bin/bash
# Test webhook endpoint with sample Telegram update

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Telegram Webhook${NC}"
echo "================================"
echo ""

# Check if URL is provided
if [ -z "$1" ]; then
    URL="https://bot.cozyberries.in/webhook"
else
    URL="$1"
fi

echo -e "${YELLOW}Testing URL:${NC} $URL"
echo ""

# Sample Telegram update (simulating /start command)
SAMPLE_UPDATE='{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "Test",
      "username": "testuser"
    },
    "chat": {
      "id": 123456789,
      "first_name": "Test",
      "username": "testuser",
      "type": "private"
    },
    "date": 1234567890,
    "text": "/start"
  }
}'

echo -e "${YELLOW}Sending sample update...${NC}"
echo ""

# Send request
RESPONSE=$(curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "$SAMPLE_UPDATE" \
  -w "\nHTTP_CODE:%{http_code}" \
  -s)

# Extract HTTP code
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

echo -e "${YELLOW}Response:${NC}"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Success! HTTP 200${NC}"
else
    echo -e "${RED}❌ Failed! HTTP $HTTP_CODE${NC}"
fi

echo ""
echo -e "${YELLOW}Check Vercel logs:${NC}"
echo "vercel logs --follow"
echo ""
echo -e "${YELLOW}Check Telegram webhook status:${NC}"
echo 'curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"'
