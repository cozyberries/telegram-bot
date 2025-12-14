"""
Expenses menu callback handlers for interactive navigation
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_expenses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle expenses menu callbacks"""
    query = update.callback_query
    data = query.data
    
    # Answer callback query first if not already done
    try:
        await query.answer()
    except Exception as e:
        pass  # Ignore if already answered
    
    if data == "expenses_list_all":
        from app.bot.handlers import expenses
        # Redirect to list expenses
        try:
            await expenses.list_expenses_command(update, context)
        except Exception as e:
            logger.error(f"Failed to list expenses: {e}")
    
    elif data == "expenses_create":
        from app.bot.handlers import expenses
        # Start the add expense conversation
        text = (
            "➕ *Add New Expense*\n\n"
            "Please use the /add_expense command to start adding a new expense.\n\n"
            "Or tap the button below:"
        )
        keyboard = [
            [InlineKeyboardButton("Start Adding Expense", callback_data="start_add_expense")],
            [InlineKeyboardButton("« Back", callback_data="menu_expenses")]
        ]
        try:
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
    
    elif data == "start_add_expense":
        from app.bot.handlers import expenses
        # Trigger add_expense_start
        try:
            await expenses.add_expense_start(update, context)
        except Exception as e:
            logger.error(f"Failed to start add expense: {e}")
    
    elif data == "expenses_stats":
        from app.services import expense_service
        try:
            stats = expense_service.get_expense_stats()
            message = "📊 *Expense Statistics*\n\n" + stats.to_telegram_message()
            
            keyboard = [[InlineKeyboardButton("« Back to Expenses", callback_data="menu_expenses")]]
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Failed to show stats: {e}")
            try:
                await query.answer(f"Error: {str(e)}", show_alert=True)
            except Exception:
                pass
