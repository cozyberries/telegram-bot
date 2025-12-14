#!/bin/bash
# Quick activation script for conda environment

source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate cozyberries-telegram-bot

echo "✅ Conda environment activated: cozyberries-telegram-bot"
echo "   Python: $(which python)"
echo "   Version: $(python --version)"
echo ""
echo "To deactivate: conda deactivate"
