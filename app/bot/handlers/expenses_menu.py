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
        from app.bot.handlers.expenses import show_expense_page
        from app.services import expense_service
        
        try:
            # Show expense browser starting at offset 0
            await show_expense_page(update, context, offset=0)
        except Exception as e:
            logger.error(f"Failed to list expenses: {e}", exc_info=True)
            text = f"❌ Error loading expenses: {str(e)}"
            keyboard = [[InlineKeyboardButton("« Back to Expenses", callback_data="menu_expenses")]]
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                pass
    
    elif data == "expenses_create":
        from app.bot.handlers import expenses
        # Start the add expense conversation
        text = (
            "➕ *Add New Expense*\n\n"
            "Please use the `/add_expense` command to start adding a new expense\\.\n\n"
            "Or tap the button below:"
        )
        keyboard = [
            [InlineKeyboardButton("Start Adding Expense", callback_data="start_add_expense")],
            [InlineKeyboardButton("« Back", callback_data="menu_expenses")]
        ]
        try:
            await query.edit_message_text(
                text,
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
            # Fallback to plain text
            text_plain = "➕ Add New Expense\n\nPlease use the /add_expense command to start adding a new expense.\n\nOr tap the button below:"
            try:
                await query.edit_message_text(
                    text_plain,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                pass
    
    elif data == "start_add_expense":
        from app.bot.handlers import expenses
        # Trigger add_expense_start - now properly handles callback_query
        try:
            return await expenses.add_expense_start(update, context)
        except Exception as e:
            logger.error(f"Failed to start add expense: {e}", exc_info=True)
            try:
                await query.message.reply_text(
                    "❌ Error starting expense creation. Please use /add_expense command instead."
                )
            except Exception:
                pass
    
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
            logger.error(f"Failed to show stats: {e}", exc_info=True)
            text = f"❌ Error loading statistics: {str(e)}"
            keyboard = [[InlineKeyboardButton("« Back to Expenses", callback_data="menu_expenses")]]
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                pass
