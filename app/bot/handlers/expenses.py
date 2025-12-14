"""Expense CRUD command handlers - Refactored with Pydantic models"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from pydantic import ValidationError
from decimal import Decimal, InvalidOperation

# ... (imports remain)
from app.bot.middleware.auth import admin_required, get_user_info
from app.services import expense_service
from app.schemas.expenses import ExpenseInput
from app.utils.parsers import ExpenseMessageParser, parse_command_args

# Conversation states
INPUT_AMOUNT = 2
INPUT_DESCRIPTION = 3
INPUT_DATE = 4


@admin_required
async def list_expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /expenses command - browser expenses one by one"""
    try:
        # Start at offset 0
        await show_expense_page(update, context, offset=0)
    except Exception as e:
        await update.message.reply_text(f"Error fetching expenses: {str(e)}")
@admin_required
async def get_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /expense <id> command - get expense details"""
    is_valid, args, error = parse_command_args(update.message.text, 1)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /expense <expense_id>\n"
            "Example: /expense 123e4567-e89b-12d3-a456-426614174000"
        )
        return
    
    expense_id = args[0]
    
    try:
        expense = expense_service.get_expense_by_id(expense_id)
        
        if not expense:
            await update.message.reply_text("❌ Expense not found")
            return
        
        # Use the response's built-in formatting
        message = expense.to_telegram_message()
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching expense: {str(e)}")

async def show_expense_page(update: Update, context: ContextTypes.DEFAULT_TYPE, offset: int):
    """Show a specific expense page"""
    try:
        # Get one expense at the specific offset
        response = expense_service.get_expenses(limit=1, offset=offset)
        
        if not response.expenses:
            text = "No expenses found."
            if update.callback_query:
                await update.callback_query.answer("No more expenses")
                return
            await update.message.reply_text(text)
            return

        expense = response.expenses[0]
        total_count = response.metadata.total
        
        # Format message
        text = (
            f"📋 *Expense {offset + 1} of {total_count}*\n\n"
            f"{expense.to_telegram_message()}"
        )
        
        # Build navigation keyboard
        keyboard = []
        nav_row = []
        
        if offset > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"exp_page_{offset - 1}"))
            
        if (offset + 1) < total_count:
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"exp_page_{offset + 1}"))
            
        if nav_row:
            keyboard.append(nav_row)
            
        keyboard.append([InlineKeyboardButton("❌ Close", callback_data="exp_close_browser")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or Edit
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            
    except Exception as e:
        error_text = f"Error showing expense: {str(e)}"
        if update.callback_query:
            await update.callback_query.message.reply_text(error_text)
        else:
            await update.message.reply_text(error_text)


async def handle_expense_browser_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle expense browser navigation"""
    query = update.callback_query
    data = query.data
    
    if data == "exp_close_browser":
        await query.delete_message()
        return

    if data.startswith("exp_page_"):
        try:
            offset = int(data.split("_")[2])
            await show_expense_page(update, context, offset)
        except (ValueError, IndexError):
            await query.answer("Invalid navigation")
    
    await query.answer()


def get_expense_keyboard(draft: dict) -> InlineKeyboardMarkup:
    """Generate simple action keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("💾 Save Expense", callback_data="exp_save"),
            InlineKeyboardButton("❌ Cancel", callback_data="exp_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_expense_summary_text(draft: dict) -> str:
    """Generate summary text for the draft expense"""
    amount = draft.get('amount', 'Not set')
    description = draft.get('description', 'Not set')
    date_val = draft.get('expense_date', 'Today')
    
    return (
        "📝 *Expense Summary*\n\n"
        f"💰 *Amount:* ₹{amount}\n"
        f"📄 *Description:* {description}\n"
        f"🗓 *Date:* {date_val}\n\n"
        "_Review and save or cancel_"
    )


@admin_required
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the add expense conversation - Step 1: Ask for amount"""
    # Initialize draft expense
    context.user_data['draft_expense'] = {}
    
    text = (
        "➕ *Add New Expense*\n\n"
        "💰 Step 1 of 3\n\n"
        "Please enter the *amount* (numbers only):\n\n"
        "_Example: 1500 or 1500.50_"
    )
    
    # Handle both message and callback query
    if update.callback_query:
        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown"
        )
    
    return INPUT_AMOUNT




async def input_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate amount input - Step 2: Ask for description"""
    try:
        amount = Decimal(update.message.text.strip())
        if amount <= 0:
            await update.message.reply_text(
                "❌ Amount must be positive. Please enter again:"
            )
            return INPUT_AMOUNT
        
        # Save amount
        context.user_data['draft_expense']['amount'] = float(amount)
        
        # Ask for description
        text = (
            f"✅ Amount: ₹{amount}\n\n"
            "📄 Step 2 of 3\n\n"
            "Please enter the *description*:\n\n"
            "_Example: Office supplies, Lunch with client, etc._"
        )
        
        await update.message.reply_text(text, parse_mode="Markdown")
        return INPUT_DESCRIPTION
        
    except (ValueError, InvalidOperation):
        await update.message.reply_text(
            "❌ Invalid amount. Please enter numbers only (e.g., 1500 or 1500.50):"
        )
        return INPUT_AMOUNT


async def input_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive description input - Step 3: Ask for date (optional)"""
    description = update.message.text.strip()
    
    if len(description) < 3:
        await update.message.reply_text(
            "❌ Description too short. Please enter at least 3 characters:"
        )
        return INPUT_DESCRIPTION
    
    # Save description
    context.user_data['draft_expense']['description'] = description
    
    # Ask for date (optional)
    keyboard = [[InlineKeyboardButton("📅 Use Today's Date", callback_data="exp_use_today")]]
    text = (
        f"✅ Description: {description}\n\n"
        "📅 Step 3 of 3 (Optional)\n\n"
        "Enter date in *YYYY-MM-DD* format\n"
        "Or tap the button to use today's date:\n\n"
        "_Example: 2025-12-14_"
    )
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return INPUT_DATE


async def input_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive date input and create expense"""
    date_text = update.message.text.strip().lower()
    
    # Try to parse date
    try:
        if date_text == 'today' or date_text == 'skip':
            expense_date = date.today()
        else:
            expense_date = date.fromisoformat(date_text)
        
        context.user_data['draft_expense']['expense_date'] = expense_date
        
        # Create the expense immediately
        return await save_expense(update, context)
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid date format. Please use YYYY-MM-DD or type 'today':"
        )
        return INPUT_DATE


async def handle_use_today_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Use Today's Date' button callback"""
    query = update.callback_query
    await query.answer()
    
    # Set today's date
    context.user_data['draft_expense']['expense_date'] = date.today()
    
    # Create the expense
    # Create a pseudo-update with message from callback
    update.message = query.message
    return await save_expense(update, context)


async def save_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the expense to database"""
    try:
        draft = context.user_data.get('draft_expense', {})
        
        # Validate required fields
        if not draft.get('amount') or not draft.get('description'):
            await update.message.reply_text(
                "❌ Missing required fields. Please start over with /add_expense"
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        # Get user info
        user_info = get_user_info(update)
        
        # Create expense input
        expense_input = ExpenseInput(
            user_id=user_info['user_id'],
            username=user_info['username'],
            amount=Decimal(str(draft['amount'])),
            description=draft['description'],
            expense_date=draft.get('expense_date', date.today())
        )
        
        # Save to database
        expense = expense_service.create_expense(expense_input)
        
        # Success message
        success_text = (
            "✅ *Expense Created Successfully!*\n\n"
            f"💰 *Amount:* ₹{expense.amount}\n"
            f"📄 *Description:* {expense.description}\n"
            f"🗓 *Date:* {expense.expense_date}\n"
            f"🆔 *ID:* `{expense.id}`\n\n"
            "_Use /expenses to view all expenses_"
        )
        
        await update.message.reply_text(
            success_text,
            parse_mode="Markdown"
        )
        
        context.user_data.clear()
        return ConversationHandler.END
        
    except Exception as e:
        error_text = f"❌ Error saving expense: {str(e)}"
        await update.message.reply_text(error_text)
        context.user_data.clear()
        return ConversationHandler.END


async def cancel_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the expense creation"""
    context.user_data.clear()
    
    # Handle both message and callback
    if update.callback_query:
        await update.callback_query.answer("Cancelled")
        await update.callback_query.edit_message_text("❌ Expense creation cancelled.")
    else:
        await update.message.reply_text("❌ Expense creation cancelled.")
    
    return ConversationHandler.END


def add_expense_conversation():
    """Create conversation handler for adding expenses with simple inline flow"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("add_expense", add_expense_start),
            MessageHandler(filters.Regex("^Add Expense$"), add_expense_start)
        ],
        states={
            INPUT_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_amount)
            ],
            INPUT_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_description)
            ],
            INPUT_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_date),
                CallbackQueryHandler(handle_use_today_callback, pattern="^exp_use_today$")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_expense),
            CallbackQueryHandler(cancel_expense, pattern="^exp_cancel$")
        ],
        per_message=True,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )


@admin_required
async def delete_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /delete_expense <id> command using Pydantic response"""
    is_valid, args, error = parse_command_args(update.message.text, 1)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /delete_expense <expense_id>\n"
            "Example: /delete_expense abc123"
        )
        return
    
    expense_id = args[0]
    
    try:
        # Delete expense and get response
        delete_response = expense_service.delete_expense(expense_id)
        
        if not delete_response:
            await update.message.reply_text("❌ Expense not found")
            return
        
        # Use the response's built-in formatting
        message = delete_response.to_telegram_message()
        
        await update.message.reply_text(message, parse_mode="Markdown")
            
    except Exception as e:
        await update.message.reply_text(f"Error deleting expense: {str(e)}")
