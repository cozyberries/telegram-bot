#!/bin/bash

echo "🔍 Verifying Conda Environment Setup"
echo "====================================="
echo ""

# Check conda installation
echo "1️⃣ Checking conda installation..."
if command -v conda &> /dev/null; then
    echo "   ✅ conda found: $(which conda)"
    conda --version
else
    echo "   ❌ conda not found"
    exit 1
fi
echo ""

# Check environment exists
echo "2️⃣ Checking environment exists..."
if conda env list | grep -q "cozyberries-telegram-bot"; then
    echo "   ✅ Environment exists: cozyberries-telegram-bot"
else
    echo "   ❌ Environment not found"
    echo "   Create with: conda env create -f environment.yml"
    exit 1
fi
echo ""

# Activate and check Python version
echo "3️⃣ Checking Python version..."
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate cozyberries-telegram-bot
PYTHON_PATH=$(which python)
PYTHON_VERSION=$(python --version)
echo "   ✅ Python: $PYTHON_PATH"
echo "   ✅ Version: $PYTHON_VERSION"
echo ""

# Check key packages
echo "4️⃣ Checking installed packages..."
PACKAGES=("fastapi" "uvicorn" "logfire" "python-telegram-bot" "supabase" "pydantic")
for pkg in "${PACKAGES[@]}"; do
    if pip show "$pkg" &> /dev/null; then
        VERSION=$(pip show "$pkg" | grep Version | cut -d ' ' -f 2)
        echo "   ✅ $pkg: $VERSION"
    else
        echo "   ❌ $pkg: NOT INSTALLED"
    fi
done
echo ""

# Check Cursor files
echo "5️⃣ Checking Cursor integration..."
if [ -f ".cursorrules" ]; then
    echo "   ✅ .cursorrules exists"
else
    echo "   ⚠️  .cursorrules not found"
fi

if [ -f ".cursor/rules" ]; then
    echo "   ✅ .cursor/rules exists"
else
    echo "   ⚠️  .cursor/rules not found"
fi
echo ""

# Check documentation
echo "6️⃣ Checking documentation..."
if [ -f "CONDA_SETUP.md" ]; then
    echo "   ✅ CONDA_SETUP.md exists"
else
    echo "   ⚠️  CONDA_SETUP.md not found"
fi

if [ -f "environment.yml" ]; then
    echo "   ✅ environment.yml exists"
else
    echo "   ⚠️  environment.yml not found"
fi
echo ""

# Summary
echo "✅ Conda Environment Verification Complete!"
echo ""
echo "📋 Quick Commands:"
echo "   Activate: conda activate cozyberries-telegram-bot"
echo "   Or use:   source activate.sh"
echo "   Test:     ./TEST_LOGFIRE_LOCAL.sh"
echo ""
echo "📚 Documentation: CONDA_SETUP.md"
