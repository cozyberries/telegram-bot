#!/bin/bash

echo "🧪 Testing Logfire Integration Locally"
echo "======================================"
echo ""

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "❌ .env.local not found!"
    echo "Creating from example..."
    cp .env.local.example .env.local 2>/dev/null || echo "No .env.local.example found"
    echo ""
    echo "⚠️  Please edit .env.local and add your LOGFIRE_TOKEN"
    echo "Get token from: https://logfire.pydantic.dev/"
    exit 1
fi

# Check if LOGFIRE_TOKEN is set
if ! grep -q "LOGFIRE_TOKEN=" .env.local || grep -q "LOGFIRE_TOKEN=your-logfire-token" .env.local || grep -q "LOGFIRE_TOKEN=$" .env.local; then
    echo "⚠️  LOGFIRE_TOKEN not configured in .env.local"
    echo "Please add your Logfire token:"
    echo "  LOGFIRE_TOKEN=lf_xxxxxxxxxx"
    echo ""
    echo "Get token from: https://logfire.pydantic.dev/"
    echo ""
    echo "Continuing anyway for testing..."
fi

echo "✅ Environment file found"
echo ""

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "❌ conda not found!"
    echo "Please install conda or use system Python"
    exit 1
fi

echo "🔧 Activating conda environment: cozyberries-telegram-bot"
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate cozyberries-telegram-bot

echo "✅ Environment activated"
echo "   Python: $(which python)"
echo "   Version: $(python --version)"
echo ""

# Load environment variables
export $(grep -v '^#' .env.local | xargs 2>/dev/null || true)

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
