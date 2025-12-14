# Cursor Rules for Telegram Bot

This directory contains cursor rules to prevent common errors and enforce best practices.

## 📁 Files

### `project-config.md`
**Purpose:** Project-specific configuration and execution rules

**Covers:**
- ✅ Conda environment setup
- ✅ Execution rules (always use conda)
- ✅ Code style guidelines
- ✅ Project structure
- ✅ Testing approach
- ✅ Key commands

**When to Reference:**
- Running Python commands
- Setting up development environment
- Understanding project structure
- Installing dependencies

### `python-fastapi.md`
**Purpose:** Python and FastAPI best practices

**Covers:**
- ✅ Python coding standards
- ✅ FastAPI patterns
- ✅ Error handling
- ✅ Performance optimization
- ✅ Pydantic usage

**When to Reference:**
- Writing API endpoints
- Creating Pydantic models
- Error handling patterns
- Performance optimization

### `telegram-bot-lambda.md`
**Purpose:** Prevent Lambda deployment errors and Telegram bot issues

**Covers:**
- ✅ Lambda event loop management
- ✅ ConversationHandler entry points
- ✅ Message vs CallbackQuery handling
- ✅ Markdown parsing
- ✅ Callback routing
- ✅ Error handling patterns
- ✅ Testing patterns

**When to Reference:**
- Creating new Telegram bot handlers
- Working with ConversationHandlers
- Handling callback queries
- Deploying to Lambda/Vercel
- Debugging production issues

## 🎯 How to Use

Cursor will automatically reference these rules when:
- Writing new handler code
- Creating ConversationHandlers
- Handling callbacks
- Working with async operations
- Deploying to Lambda

## 📋 Quick Checklist

Before committing handler code:
- [ ] Read `telegram-bot-lambda.md` relevant sections
- [ ] Verify callback queries answered early
- [ ] Check both message and callback_query paths
- [ ] Ensure ConversationHandler entry points registered
- [ ] Test both interaction types

## 🔄 Updating Rules

When new issues are discovered and fixed:
1. Add the pattern to appropriate rule file
2. Include before/after examples
3. Explain why the rule exists
4. Add to checklist
5. Update this README if needed

---

**Maintained by:** Development team
**Last Updated:** 2025-12-14
