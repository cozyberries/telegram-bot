# Conda Quick Reference

## 🚀 Quick Start

```bash
# Activate environment
conda activate cozyberries-telegram-bot

# Or use shortcut
source activate.sh

# Verify
./verify_conda.sh
```

## 📋 Essential Commands

| Action | Command |
|--------|---------|
| **Activate** | `conda activate cozyberries-telegram-bot` |
| **Deactivate** | `conda deactivate` |
| **Check Python** | `which python` |
| **Check Version** | `python --version` |
| **List Packages** | `conda list` or `pip list` |
| **Install Package** | `pip install package-name` |
| **Run Server** | `uvicorn app.main:app --reload` |
| **Run Tests** | `./TEST_LOGFIRE_LOCAL.sh` |

## 🔍 Verification

```bash
# Quick verify
./verify_conda.sh

# Manual verify
which python
# Should show: .../cozyberries-telegram-bot/bin/python

python --version
# Should show: Python 3.13.11
```

## 🎯 Cursor Integration

**Automatic:** Cursor uses conda environment automatically via:
- `.cursorrules`
- `.cursor/rules`

**Manual (if needed):**
```bash
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate cozyberries-telegram-bot
```

## 📦 Package Management

```bash
# Install
conda activate cozyberries-telegram-bot
pip install package-name

# Add to requirements.txt
echo "package-name==version" >> requirements.txt

# Update all
pip install -r requirements.txt --upgrade
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Environment not found | `conda env create -f environment.yml` |
| Wrong Python | Deactivate and reactivate |
| Package missing | `conda activate ... && pip install package` |
| Cursor not using conda | Check `.cursorrules` file exists |

## 📚 Documentation

- **Full Guide:** `CONDA_SETUP.md`
- **Verification:** `./verify_conda.sh`
- **Activation:** `source activate.sh`

## 🔗 Important Paths

```
Environment: /opt/homebrew/Caskroom/miniconda/base/envs/cozyberries-telegram-bot
Python: .../cozyberries-telegram-bot/bin/python
Config: environment.yml
Rules: .cursorrules, .cursor/rules
```

## ⚡ One-Liners

```bash
# Activate and run server
conda activate cozyberries-telegram-bot && uvicorn app.main:app --reload

# Activate and test
conda activate cozyberries-telegram-bot && ./TEST_LOGFIRE_LOCAL.sh

# Activate and install
conda activate cozyberries-telegram-bot && pip install package-name

# Verify everything
./verify_conda.sh
```

---

**Quick Help:** `cat CONDA_QUICK_REFERENCE.md`  
**Full Docs:** `cat CONDA_SETUP.md`  
**Verify:** `./verify_conda.sh`
