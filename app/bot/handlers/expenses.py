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
EXPENSE_MENU = 1
INPUT_AMOUNT = 2
INPUT_DESCRIPTION = 3
INPUT_DATE = 4
INPUT_CATEGORY = 5


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
    """Generate the interactive form keyboard"""
    
    # Status indicators
    amt_status = "✅" if draft.get('amount') else "❌"
    desc_status = "✅" if draft.get('description') else "❌"
    date_status = f"🗓 {draft.get('transaction_date', 'Today')}"
    cat_status = f"📂 {draft.get('category') or 'None'}"
    
    keyboard = [
        [
            InlineKeyboardButton(f"{amt_status} Set Amount", callback_data="exp_set_amount"),
            InlineKeyboardButton(f"{desc_status} Set Desc", callback_data="exp_set_desc")
        ],
        [
            InlineKeyboardButton(date_status, callback_data="exp_set_date"),
            InlineKeyboardButton(cat_status, callback_data="exp_set_cat")
        ],
        [
            InlineKeyboardButton("💾 Save Expense", callback_data="exp_save"),
            InlineKeyboardButton("❌ Cancel", callback_data="exp_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_expense_summary_text(draft: dict) -> str:
    """Generate summary text for the draft expense"""
    return (
        "📝 *New Expense Draft*\n\n"
        f"💰 *Amount:* {draft.get('amount') or '_Not set_'}\n"
        f"📄 *Description:* {draft.get('description') or '_Not set_'}\n"
        f"🗓 *Date:* {draft.get('transaction_date') or 'Today'}\n"
        f"📂 *Category:* {draft.get('category') or 'None'}\n\n"
        "_Use the buttons below to update fields_"
    )


@admin_required
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the add expense conversation with interactive form"""
    # Initialize draft expense
    context.user_data['draft_expense'] = {}
    
    text = get_expense_summary_text({})
    reply_markup = get_expense_keyboard({})
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return EXPENSE_MENU


async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle interactions with the expense menu"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    draft = context.user_data.get('draft_expense', {})
    
    if action == "exp_set_amount":
        await query.edit_message_text(
            f"💰 Current Amount: {draft.get('amount') or 'Not set'}\n\n"
            "Please enter the new amount (e.g., 1500):"
        )
        return INPUT_AMOUNT
        
    elif action == "exp_set_desc":
        await query.edit_message_text(
            f"📝 Current Description: {draft.get('description') or 'Not set'}\n\n"
            "Please enter the description:"
        )
        return INPUT_DESCRIPTION
        
    elif action == "exp_set_date":
        await query.edit_message_text(
            f"🗓 Current Date: {draft.get('transaction_date') or 'Today'}\n\n"
            "Enter date (YYYY-MM-DD) or 'today':"
        )
        return INPUT_DATE
        
    elif action == "exp_set_cat":
        await query.edit_message_text(
            f"📂 Current Category: {draft.get('category') or 'None'}\n\n"
            "Enter category name:"
        )
        return INPUT_CATEGORY
        
    elif action == "exp_save":
        # Validate before saving
        if not draft.get('amount') or not draft.get('description'):
            await query.edit_message_text(
                get_expense_summary_text(draft) + "\n\n⚠️ Amount and Description are required!",
                reply_markup=get_expense_keyboard(draft),
                parse_mode="Markdown"
            )
            return EXPENSE_MENU
            
        return await save_expense(update, context)
        
    elif action == "exp_cancel":
        await query.edit_message_text("❌ Expense creation cancelled.")
        context.user_data.clear()
        return ConversationHandler.END
        
    return EXPENSE_MENU


async def return_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper to return to the main menu after input"""
    draft = context.user_data.get('draft_expense', {})
    text = get_expense_summary_text(draft)
    reply_markup = get_expense_keyboard(draft)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return EXPENSE_MENU


async def input_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle amount input"""
    text = update.message.text.strip()
    try:
        amount = ExpenseMessageParser.parse_amount(text)
        if not amount or amount <= 0:
            raise ValueError("Invalid amount")
            
        context.user_data['draft_expense']['amount'] = amount
        return await return_to_menu(update, context)
        
    except Exception:
        await update.message.reply_text("❌ Invalid amount. Please enter a positive number (e.g. 1500):")
        return INPUT_AMOUNT


async def input_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle description input"""
    text = update.message.text.strip()
    if len(text) < 3:
        await update.message.reply_text("❌ Description too short. Please enter at least 3 characters:")
        return INPUT_DESCRIPTION
        
    context.user_data['draft_expense']['description'] = text
    return await return_to_menu(update, context)


async def input_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date input"""
    text = update.message.text.strip().lower()
    if text == 'today':
        context.user_data['draft_expense']['transaction_date'] = None # Defaults to today in backend
    else:
        date_obj = ExpenseMessageParser.parse_date(text)
        if not date_obj:
            await update.message.reply_text("❌ Invalid date. Use YYYY-MM-DD or 'today':")
            return INPUT_DATE
        context.user_data['draft_expense']['transaction_date'] = date_obj.date()
        
    return await return_to_menu(update, context)


async def input_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category input"""
    text = update.message.text.strip()
    context.user_data['draft_expense']['category'] = text
    return await return_to_menu(update, context)


async def save_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finalize and save the expense"""
    try:
        draft = context.user_data['draft_expense']
        user_info = get_user_info(update)
        
        expense_input = ExpenseInput(
            user_id=str(user_info['id']),
            username=user_info.get('username'),
            amount=draft['amount'],
            description=draft['description'],
            transaction_date=draft.get('transaction_date'),
            category=draft.get('category')
        )
        
        created_expense = expense_service.create_expense(expense_input)
        
        # Determine where to send the final message (msg or callback)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "✅ *Expense Saved!*\n\n" + created_expense.to_telegram_message(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "✅ *Expense Saved!*\n\n" + created_expense.to_telegram_message(),
                parse_mode="Markdown"
            )
            
        context.user_data.clear()
        return ConversationHandler.END
        
    except Exception as e:
        error_text = f"❌ Error saving expense: {str(e)}"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)
        return ConversationHandler.END


async def cancel_expense_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


def add_expense_conversation():
    """Create conversation handler for adding expenses"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("add_expense", add_expense_start),
            MessageHandler(filters.Regex("^Add Expense$"), add_expense_start)
        ],
        states={
            EXPENSE_MENU: [
                CallbackQueryHandler(handle_menu_callback)
            ],
            INPUT_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_amount)
            ],
            INPUT_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_description)
            ],
            INPUT_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_date)
            ],
            INPUT_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_category)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_expense_conversation)],
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
