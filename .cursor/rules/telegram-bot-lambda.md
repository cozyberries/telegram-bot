# Telegram Bot Lambda Deployment Rules

## 🚨 Critical: Lambda Event Loop Management

### Rule: Always Answer Callback Queries Early
**Problem:** Lambda aggressively closes event loops, causing `RuntimeError: Event loop is closed`

**Solution:**
```python
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # ✅ ALWAYS answer FIRST, before any processing
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Failed to answer callback: {e}")
        pass  # Continue processing even if answer fails
    
    # Then do your processing
    try:
        await query.edit_message_text(...)
    except Exception as e:
        logger.error(f"Failed to edit: {e}")
        # Fallback handling
```

**Why:** Prevents Telegram timeout (30s) and reduces race conditions with Lambda's event loop closure.

**Never:**
- ❌ Answer callback query at the end of processing
- ❌ Ignore answer failures without logging
- ❌ Block on callback answer

---

## 🚨 Critical: ConversationHandler Entry Points

### Rule: Never Call Entry Point Functions Directly from Callbacks
**Problem:** ConversationHandler state machine doesn't initialize if entry point is called directly

**Solution:**
```python
# ✅ CORRECT: Use registered entry points
ConversationHandler(
    entry_points=[
        CommandHandler("add_expense", add_expense_start),  # ✅ Entry point
        CallbackQueryHandler(start_handler, pattern="^start_")  # ✅ Entry point
    ],
    states={...}
)

# ❌ WRONG: Calling entry point function directly
async def handle_button(update, context):
    return await add_expense_start(update, context)  # ❌ Won't initialize conversation
```

**Alternative for Callbacks:**
```python
# ✅ CORRECT: Show instruction message
async def handle_start_button(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Please use the /add_expense command to start."
    )
```

**Why:** ConversationHandlers require proper entry point registration to initialize state machine.

**Always:**
- ✅ Register entry points in ConversationHandler definition
- ✅ Use CommandHandler or CallbackQueryHandler as entry points
- ✅ Direct users to commands if needed

**Never:**
- ❌ Call entry point functions directly from callbacks
- ❌ Bypass ConversationHandler registration
- ❌ Mix callback and command entry points incorrectly

---

## 🚨 Critical: Message vs CallbackQuery Handling

### Rule: Always Handle Both Message and CallbackQuery
**Problem:** Functions expecting `update.message` fail when called from callbacks

**Solution:**
```python
async def handler_that_needs_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ✅ ALWAYS check both
    if update.callback_query:
        message = update.callback_query.message
        await message.reply_text(...)
    else:
        await update.message.reply_text(...)
```

**Common Pattern:**
```python
# ✅ For functions that send messages
if update.callback_query:
    await update.callback_query.message.reply_text(text)
else:
    await update.message.reply_text(text)

# ✅ For functions that edit messages
if update.callback_query:
    await update.callback_query.edit_message_text(text)
else:
    await update.message.reply_text(text)
```

**Why:** Callbacks don't have `update.message`, only `update.callback_query.message`.

**Always:**
- ✅ Check `update.callback_query` first
- ✅ Use `callback_query.message` for callbacks
- ✅ Use `update.message` for direct messages

**Never:**
- ❌ Assume `update.message` always exists
- ❌ Access `update.message` without checking callback_query first

---

## ⚠️ Important: Markdown Parsing

### Rule: Use MarkdownV2 with Proper Escaping
**Problem:** Special characters cause parsing errors: `Can't parse entities`

**Solution:**
```python
# ✅ CORRECT: MarkdownV2 with escaped special chars
text = "Use the `/add_expense` command\\.\n\nOr tap the button:"
await message.reply_text(text, parse_mode="MarkdownV2")

# ❌ WRONG: Unescaped special chars
text = "Use the /add_expense command."
await message.reply_text(text, parse_mode="Markdown")  # May fail
```

**Special Characters to Escape in MarkdownV2:**
- `_` → `\_`
- `*` → `\*`
- `[` → `\[`
- `]` → `\]`
- `(` → `\(`
- `)` → `\)`
- `~` → `\~`
- `` ` `` → `` \` ``
- `>` → `\>`
- `#` → `\#`
- `+` → `\+`
- `-` → `\-`
- `=` → `\=`
- `|` → `\|`
- `{` → `\{`
- `}` → `\}`
- `.` → `\.`
- `!` → `\!`

**Fallback Pattern:**
```python
try:
    await message.reply_text(text, parse_mode="MarkdownV2")
except Exception as e:
    logger.warning(f"Markdown failed: {e}")
    # Fallback to plain text
    await message.reply_text(plain_text)
```

**Why:** Prevents user-facing errors and improves reliability.

---

## ⚠️ Important: Callback Routing

### Rule: Route All Callbacks Explicitly
**Problem:** Unhandled callbacks show warnings and don't work

**Solution:**
```python
async def _handle_callback_query(self, update: Update, context):
    query = update.callback_query
    data = query.data
    
    # ✅ Answer early
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Failed to answer: {e}")
    
    # ✅ Route explicitly by prefix
    if data.startswith("menu_"):
        await menu.handle_menu_callback(update, context)
    elif data.startswith("expenses_") or data == "start_add_expense":
        await expenses_menu.handle_expenses_menu(update, context)
    elif data.startswith("exp_"):
        await expenses.handle_expense_browser_callback(update, context)
    elif data == "noop":
        pass  # Intentional no-op
    else:
        logger.warning(f"Unhandled callback: {data}")  # ✅ Log unhandled
```

**Why:** Prevents silent failures and makes debugging easier.

**Always:**
- ✅ Route by prefix patterns
- ✅ Log unhandled callbacks
- ✅ Group related callbacks together

**Never:**
- ❌ Ignore unhandled callbacks silently
- ❌ Use generic catch-all handlers
- ❌ Mix callback routing logic

---

## ⚠️ Important: ConversationHandler Configuration

### Rule: Set per_message=True When Using CallbackQueryHandler
**Problem:** PTB warning: `If 'per_message=False', 'CallbackQueryHandler' will not be tracked`

**Solution:**
```python
ConversationHandler(
    entry_points=[...],
    states={
        STATE: [
            CallbackQueryHandler(handler),  # ✅ Needs per_message=True
            MessageHandler(filters.TEXT, handler)
        ]
    },
    per_message=True,   # ✅ Required for CallbackQueryHandler
    per_chat=True,      # ✅ Track per chat
    per_user=True,      # ✅ Track per user
    allow_reentry=True  # ✅ Better UX
)
```

**Why:** Ensures proper tracking of callback queries in conversation states.

---

## ✅ Best Practices: Error Handling

### Rule: Wrap All Async Operations in Try-Except
**Pattern:**
```python
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Main logic
        await some_operation()
    except SpecificError as e:
        logger.error(f"Specific error: {e}", exc_info=True)
        await handle_specific_error(update, e)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await handle_generic_error(update)
```

**Why:** Lambda errors can be cryptic; proper logging helps debugging.

---

## ✅ Best Practices: Logging

### Rule: Log All Important Operations
**Pattern:**
```python
logger.info(f"Processing callback: {data} from user {user_id}")
logger.warning(f"Non-critical issue: {issue}")
logger.error(f"Error occurred: {error}", exc_info=True)  # ✅ Include traceback
```

**Why:** Production debugging requires comprehensive logs.

---

## ✅ Best Practices: Testing

### Rule: Test Both Message and CallbackQuery Paths
**Pattern:**
```python
def create_mock_callback_update(callback_data: str):
    """Create mock for callback queries"""
    update = MagicMock(spec=Update)
    update.callback_query = AsyncMock()
    update.callback_query.data = callback_data
    update.message = None  # ✅ Important: callbacks don't have message
    return update

def create_mock_message_update():
    """Create mock for message commands"""
    update = MagicMock(spec=Update)
    update.message = AsyncMock()
    update.callback_query = None  # ✅ Important: messages don't have callback_query
    return update
```

**Why:** Ensures both interaction types work correctly.

---

## 📋 Checklist for New Handlers

Before committing any handler code, verify:

- [ ] Callback queries are answered early (before processing)
- [ ] Both `update.message` and `update.callback_query` are handled
- [ ] ConversationHandler entry points are properly registered
- [ ] Markdown text is properly escaped (if using MarkdownV2)
- [ ] All callbacks are routed explicitly
- [ ] Error handling wraps async operations
- [ ] Logging includes context (user_id, callback_data, etc.)
- [ ] Tests cover both message and callback paths
- [ ] `per_message=True` if using CallbackQueryHandler in ConversationHandler

---

## 🎯 Quick Reference

### Callback Query Handler Template
```python
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # 1. Answer early
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Failed to answer: {e}")
    
    # 2. Process
    try:
        # Your logic here
        await query.edit_message_text(...)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        # Fallback
```

### Message Handler Template
```python
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both message and callback_query
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message
    
    try:
        await message.reply_text(...)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
```

### ConversationHandler Template
```python
def create_conversation():
    return ConversationHandler(
        entry_points=[
            CommandHandler("command", start_handler),
            # ✅ Can add CallbackQueryHandler here too
        ],
        states={
            STATE: [
                MessageHandler(filters.TEXT, handler),
                CallbackQueryHandler(callback_handler, pattern="^pattern$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
        per_message=True,  # ✅ Required for CallbackQueryHandler
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
```

---

## 📚 Related Documentation

- `LAMBDA_FIXES_SUMMARY.md` - Complete technical details
- `VERCEL_DEPLOYMENT_FIXES.md` - Production issue analysis
- `EXPENSE_FORM_FLOW.md` - UX flow improvements

---

**Last Updated:** 2025-12-14
**Based on:** All Lambda deployment fixes and production issues resolved
