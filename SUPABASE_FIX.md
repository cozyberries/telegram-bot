# Supabase Service Fix

## Issue
Expense commands (and all Supabase-related commands) were not working because:

1. **Async/Sync Mismatch**: Service functions were defined as `async def` but the Supabase Python client is **synchronous**
2. **Incorrect await usage**: Handlers were using `await` on synchronous functions

## Root Cause

The `supabase-py` client is **not async**. All database operations are synchronous:

```python
# WRONG (was in code before)
async def get_expenses():
    response = supabase.table("expenses").select("*").execute()
    return response.data

# RIGHT (fixed now)
def get_expenses():
    response = supabase.table("expenses").select("*").execute()
    return response.data
```

## Files Fixed

### 1. `app/services/expense_service.py`
- ✅ Removed `async` from all function definitions
- ✅ All functions are now synchronous
- ✅ Direct Supabase client calls (no await)

### 2. `app/bot/handlers/expenses.py`
- ✅ Removed `await` when calling service functions
- ✅ Handlers remain `async` (for Telegram)
- ✅ Service calls are synchronous inside async handlers

## Example Fix

```python
# BEFORE (BROKEN)
@admin_required
async def list_expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expenses = await expense_service.get_expenses(limit=10)  # WRONG!
    
# AFTER (WORKING)
@admin_required
async def list_expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expenses = expense_service.get_expenses(limit=10)  # CORRECT!
```

## How It Works Now

1. **Handler (async)**: Telegram bot handlers must be async
2. **Service call (sync)**: Supabase operations are synchronous
3. **Mixed execution**: Async handler calls sync service

```python
async def handler():           # Async for Telegram
    data = service.get_data()  # Sync Supabase call
    await update.reply_text()  # Async Telegram API
```

## Testing

To test expense commands:

```bash
# Send to bot on Telegram
/expenses                    # List all expenses
/expense <id>               # Get expense details
/add_expense                # Start conversation to add
/approve_expense <id>       # Approve pending expense
/reject_expense <id> reason # Reject with reason
```

## Note for Other Services

All other service files need the same fix:
- `app/services/order_service.py` - Remove async
- `app/services/product_service.py` - Remove async  
- `app/services/stock_service.py` - Remove async
- `app/services/analytics_service.py` - Remove async

These will be fixed when testing their respective commands.

