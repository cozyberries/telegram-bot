#!/bin/bash

echo "🧪 Testing Logfire Integration Locally"
echo "======================================"
echo ""

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "❌ .env.local not found!"
    echo "Creating from example..."
    cp .env.local.example .env.local
    echo ""
    echo "⚠️  Please edit .env.local and add your LOGFIRE_TOKEN"
    echo "Get token from: https://logfire.pydantic.dev/"
    exit 1
fi

# Check if LOGFIRE_TOKEN is set
if ! grep -q "LOGFIRE_TOKEN=" .env.local || grep -q "LOGFIRE_TOKEN=your-logfire-token" .env.local; then
    echo "⚠️  LOGFIRE_TOKEN not configured in .env.local"
    echo "Please add your Logfire token:"
    echo "  LOGFIRE_TOKEN=lf_xxxxxxxxxx"
    echo ""
    echo "Get token from: https://logfire.pydantic.dev/"
    exit 1
fi

echo "✅ Environment file found"
echo ""

# Load environment variables
export $(grep -v '^#' .env.local | xargs)

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "🚀 Starting FastAPI server..."
echo "Server will start on http://localhost:8000"
echo ""
echo "📊 Testing Endpoints:"
echo "  - Health: http://localhost:8000/health"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Root: http://localhost:8000/"
echo ""
echo "🔥 Logfire Dashboard:"
echo "  https://logfire.pydantic.dev/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================="
echo ""

# Start uvicorn
uvicorn app.main:app --reload --port 8000
