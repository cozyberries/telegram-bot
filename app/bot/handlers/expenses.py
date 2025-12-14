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
    """Handle /expenses command - list expenses using Pydantic models"""
    try:
        # Get expenses with metadata
        response = expense_service.get_expenses(limit=20)
        
        # Use the response's built-in formatting
        message = response.to_telegram_message()
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown"
        )
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


def get_expense_keyboard(draft: dict) -> InlineKeyboardMarkup:
    """Generate the interactive form keyboard"""
    
    # Status indicators
    amt_status = "✅" if draft.get('amount') else "❌"
    desc_status = "✅" if draft.get('description') else "❌"
    date_status = f"🗓 {draft.get('transaction_date', 'Today')}"
    cat_status = f"📂 {draft.get('category') or 'None'}"
    
    keyboard = [
        [
            InlineKeyboardButton(f"{amt_status} Set Amount", callback_data="set_amount"),
            InlineKeyboardButton(f"{desc_status} Set Desc", callback_data="set_desc")
        ],
        [
            InlineKeyboardButton(date_status, callback_data="set_date"),
            InlineKeyboardButton(cat_status, callback_data="set_cat")
        ],
        [
            InlineKeyboardButton("💾 Save Expense", callback_data="save"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_expense_summary_text(draft: dict) -> str:
    """Generate summary text for the form"""
    amount = f"₹{draft.get('amount'):,.2f}" if draft.get('amount') else "Not set"
    desc = draft.get('description') or "Not set"
    date_val = str(draft.get('transaction_date') or "Today")
    category = draft.get('category') or "Uncategorized"
    
    return (
        "💰 *New Expense Entry*\n\n"
        f"*Amount:* {amount}\n"
        f"*Description:* {desc}\n"
        f"*Date:* {date_val}\n"
        f"*Category:* {category}\n\n"
        "👇 Select a field to edit:"
    )


@admin_required
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the interactive expense wizard"""
    # Initialize draft
    context.user_data['draft_expense'] = {
        'amount': None,
        'description': None,
        'transaction_date': None,
        'category': None
    }
    
    text = get_expense_summary_text(context.user_data['draft_expense'])
    reply_markup = get_expense_keyboard(context.user_data['draft_expense'])
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return EXPENSE_MENU


async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle interactions with the expense menu"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    draft = context.user_data.get('draft_expense', {})
    
    if action == "set_amount":
        await query.edit_message_text(
            f"💰 Current Amount: {draft.get('amount') or 'Not set'}\n\n"
            "Please enter the new amount (e.g., 1500):"
        )
        return INPUT_AMOUNT
        
    elif action == "set_desc":
        await query.edit_message_text(
            f"📝 Current Description: {draft.get('description') or 'Not set'}\n\n"
            "Please enter the description:"
        )
        return INPUT_DESCRIPTION
        
    elif action == "set_date":
        await query.edit_message_text(
            f"🗓 Current Date: {draft.get('transaction_date') or 'Today'}\n\n"
            "Enter date (YYYY-MM-DD) or 'today':"
        )
        return INPUT_DATE
        
    elif action == "set_cat":
        await query.edit_message_text(
            f"📂 Current Category: {draft.get('category') or 'None'}\n\n"
            "Enter category name:"
        )
        return INPUT_CATEGORY
        
    elif action == "save":
        # Validate before saving
        if not draft.get('amount') or not draft.get('description'):
            await query.edit_message_text(
                get_expense_summary_text(draft) + "\n\n⚠️ Amount and Description are required!",
                reply_markup=get_expense_keyboard(draft),
                parse_mode="Markdown"
            )
            return EXPENSE_MENU
            
        return await save_expense(update, context)
        
    elif action == "cancel":
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
