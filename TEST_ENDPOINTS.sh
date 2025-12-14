#!/bin/bash

echo "🧪 Testing All Endpoints with Logfire Logging"
echo "=============================================="
echo ""
echo "Make sure the FastAPI server is running:"
echo "  ./TEST_LOGFIRE_LOCAL.sh"
echo ""
echo "Press Enter to continue..."
read

BASE_URL="http://localhost:8000"

echo "1️⃣ Testing Root Endpoint (GET /)"
echo "-----------------------------------"
curl -s $BASE_URL/ | jq '.'
echo ""
echo ""

echo "2️⃣ Testing Health Check (GET /health)"
echo "--------------------------------------"
curl -s $BASE_URL/health | jq '.'
echo ""
echo ""

echo "3️⃣ Testing Bot Info (GET /bot-info)"
echo "------------------------------------"
curl -s $BASE_URL/bot-info | jq '.'
echo ""
echo ""

echo "4️⃣ Testing Webhook Info (GET /webhook)"
echo "---------------------------------------"
curl -s $BASE_URL/webhook | jq '.'
echo ""
echo ""

echo "5️⃣ Testing Notify Order Info (GET /notify-order)"
echo "-------------------------------------------------"
curl -s $BASE_URL/notify-order | jq '.'
echo ""
echo ""

echo "✅ All GET endpoints tested!"
echo ""
echo "🔥 Check Logfire Dashboard:"
echo "   https://logfire.pydantic.dev/"
echo ""
echo "Expected logs in Logfire:"
echo "  ✅ api_request spans for each endpoint"
echo "  ✅ health_check metric"
echo "  ✅ All with proper context and timing"
echo ""
echo "Filters to try in Logfire:"
echo "  - service_name:telegram-bot"
echo "  - environment:local"
echo "  - endpoint:/health"
