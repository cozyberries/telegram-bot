# Conda Environment Setup

## Environment Details

**Name:** `cozyberries-telegram-bot`  
**Python Version:** 3.13.11  
**Location:** `/opt/homebrew/Caskroom/miniconda/base/envs/cozyberries-telegram-bot`

## Quick Start

### Activate Environment
```bash
conda activate cozyberries-telegram-bot
```

### Verify Activation
```bash
which python
# Should output: /opt/homebrew/Caskroom/miniconda/base/envs/cozyberries-telegram-bot/bin/python

python --version
# Should output: Python 3.13.11
```

### Deactivate Environment
```bash
conda deactivate
```

## Installation

### Fresh Install (If environment doesn't exist)
```bash
# Method 1: From environment.yml
conda env create -f environment.yml

# Method 2: Manual creation
conda create -n cozyberries-telegram-bot python=3.13 -y
conda activate cozyberries-telegram-bot
pip install -r requirements.txt
```

### Update Existing Environment
```bash
conda activate cozyberries-telegram-bot
pip install -r requirements.txt --upgrade
```

## Installed Packages

All packages from `requirements.txt`:
- python-telegram-bot==20.7
- supabase==2.3.4
- pydantic==2.9.2
- pydantic-settings==2.6.1
- httpx==0.25.2
- python-dotenv==1.0.1
- python-dateutil==2.9.0
- fastapi==0.115.5
- uvicorn[standard]==0.34.0
- logfire==0.54.0

## Usage

### Run FastAPI Server
```bash
conda activate cozyberries-telegram-bot
uvicorn app.main:app --reload
```

Or use the test script:
```bash
conda activate cozyberries-telegram-bot
./TEST_LOGFIRE_LOCAL.sh
```

### Run Python Scripts
```bash
conda activate cozyberries-telegram-bot
python scripts/test_connection.py
```

### Run Tests
```bash
conda activate cozyberries-telegram-bot
pytest tests/
```

## Package Management

### Install New Package
```bash
conda activate cozyberries-telegram-bot
pip install package-name

# Add to requirements.txt
echo "package-name==version" >> requirements.txt
```

### Update environment.yml
After installing new packages:
```bash
conda activate cozyberries-telegram-bot
conda env export > environment.yml
```

Or manually add to the pip section in `environment.yml`.

## Environment Management

### List All Environments
```bash
conda env list
```

### Remove Environment
```bash
conda env remove -n cozyberries-telegram-bot
```

### Clone Environment
```bash
conda create --name cozyberries-telegram-bot-backup --clone cozyberries-telegram-bot
```

### Export Environment
```bash
conda activate cozyberries-telegram-bot
conda env export > environment-backup.yml
```

## Troubleshooting

### Environment Not Found
```bash
# List environments
conda env list

# If not listed, create it
conda env create -f environment.yml
```

### Wrong Python Version
```bash
# Check version
python --version

# If wrong, recreate environment
conda deactivate
conda env remove -n cozyberries-telegram-bot
conda env create -f environment.yml
```

### Package Not Found
```bash
# Make sure environment is activated
conda activate cozyberries-telegram-bot

# Install missing package
pip install package-name
```

### Permission Errors
```bash
# Make sure you own the conda directory
# If using system conda, you might need sudo (not recommended)
# Better: Use conda in your home directory
```

## Cursor Integration

The `.cursor/rules` file ensures Cursor always uses this conda environment.

### Manual Activation in Cursor Terminal
```bash
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate cozyberries-telegram-bot
```

### Verify in Cursor
```bash
which python
# Should show conda environment path

echo $CONDA_DEFAULT_ENV
# Should show: cozyberries-telegram-bot
```

## Best Practices

1. **Always activate** the environment before running Python code
2. **Verify activation** with `which python` before important operations
3. **Update requirements.txt** when installing new packages
4. **Don't mix** conda and pip installations (prefer pip in conda env)
5. **Test locally** in conda environment before deploying
6. **Keep environment.yml** in sync with requirements.txt

## Auto-Activation (Optional)

### For Terminal
Add to `~/.zshrc` or `~/.bashrc`:
```bash
# Auto-activate conda environment for telegram-bot project
if [[ "$PWD" == *"telegram-bot"* ]]; then
    if [[ "$CONDA_DEFAULT_ENV" != "cozyberries-telegram-bot" ]]; then
        conda activate cozyberries-telegram-bot 2>/dev/null
    fi
fi
```

### For VS Code / Cursor
Add to `.vscode/settings.json` or `.cursor/settings.json`:
```json
{
  "python.defaultInterpreterPath": "/opt/homebrew/Caskroom/miniconda/base/envs/cozyberries-telegram-bot/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.condaPath": "/opt/homebrew/Caskroom/miniconda/base/bin/conda"
}
```

## Common Commands Reference

```bash
# Activate
conda activate cozyberries-telegram-bot

# Deactivate
conda deactivate

# List packages
conda list

# Install package
pip install package-name

# Update package
pip install --upgrade package-name

# Freeze requirements
pip freeze > requirements.txt

# Run server
uvicorn app.main:app --reload

# Run script
python script.py

# Check environment
echo $CONDA_DEFAULT_ENV

# Python path
which python
```

## Environment Information

To get full environment info:
```bash
conda activate cozyberries-telegram-bot
conda info
conda list
```

## Useful Aliases (Optional)

Add to `~/.zshrc`:
```bash
alias cond-tb='conda activate cozyberries-telegram-bot'
alias cond-d='conda deactivate'
alias run-tb='conda activate cozyberries-telegram-bot && uvicorn app.main:app --reload'
```

Then use:
```bash
cond-tb     # Activate environment
run-tb      # Run FastAPI server
cond-d      # Deactivate
```
