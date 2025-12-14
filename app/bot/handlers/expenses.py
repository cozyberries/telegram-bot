"""Expense CRUD command handlers"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from app.bot.middleware.auth import admin_required, get_user_info
from app.services import expense_service
from app.database.models import ExpenseCreate
from app.utils.formatters import format_expense_summary, format_list_header
from app.utils.validators import parse_command_args, validate_amount, validate_date

# Conversation states
EXPENSE_TITLE = 0


@admin_required
async def list_expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /expenses command - list expenses"""
    try:
        # Call synchronous function
        expenses = expense_service.get_expenses(limit=20)
        
        if not expenses:
            await update.message.reply_text("No expenses found.")
            return
        
        message = format_list_header("Recent Expenses", len(expenses))
        
        for expense in expenses:
            message += f"\n{format_expense_summary(expense)}\n---\n"
        
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
        # Call synchronous function
        expense = expense_service.get_expense_by_id(expense_id)
        
        if not expense:
            await update.message.reply_text("❌ Expense not found")
            return
        
        message = format_expense_summary(expense)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching expense: {str(e)}")


# Single-message expense creation with improved form
@admin_required
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add expense - improved form response"""
    help_text = (
        "💰 *Add New Expense*\n\n"
        "Please provide your expense details in the following format:\n\n"
        "*Required Fields:*\n"
        "┣ Amount: _expense amount in ₹_\n"
        "┗ Description: _what was purchased/paid for_\n\n"
        "*Optional Fields:*\n"
        "┣ Date: _transaction date (YYYY-MM-DD)_\n"
        "┗ Category: _expense category_\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Example Message:*\n\n"
        "`Amount: 2500`\n"
        "`Description: Client lunch meeting at Taj`\n"
        "`Date: 2025-12-14`\n"
        "`Category: Marketing`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 *Quick Tips:*\n"
        "• Each field on a new line\n"
        "• Date defaults to today if not provided\n"
        "• Amount can be written as: 1500 or 1,500 or 1500.50\n\n"
        "Send your expense details now 👇\n"
        "Or use /cancel to stop"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
    return EXPENSE_TITLE


async def add_expense_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parse and create expense from single message"""
    message_text = update.message.text.strip()
    user_info = get_user_info(update)
    
    # Parse the message
    lines = message_text.split('\n')
    expense_data = {}
    
    for line in lines:
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key in ['amount', 'amt', 'price', 'cost']:
                expense_data['amount'] = value
            elif key in ['description', 'desc', 'detail', 'details', 'title']:
                expense_data['description'] = value
            elif key in ['date', 'transaction date', 'expense date']:
                expense_data['date'] = value
            elif key in ['category', 'cat', 'type']:
                expense_data['category'] = value
    
    # Validate required fields
    errors = []
    
    if 'amount' not in expense_data:
        errors.append("❌ Amount is required")
    else:
        is_valid, amount, error = validate_amount(expense_data['amount'])
        if not is_valid:
            errors.append(f"❌ Invalid amount: {error}")
        else:
            expense_data['amount'] = amount
    
    if 'description' not in expense_data:
        errors.append("❌ Description is required")
    
    # Validate optional date
    if 'date' in expense_data:
        is_valid, date, error = validate_date(expense_data['date'])
        if not is_valid:
            errors.append(f"❌ Invalid date: {error}")
        else:
            expense_data['date'] = date
    else:
        # Use today's date if not provided
        from datetime import datetime
        expense_data['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # If there are errors, show them
    if errors:
        error_msg = "\n".join(errors)
        await update.message.reply_text(
            f"{error_msg}\n\n"
            "Please try again with the correct format:\n\n"
            "`Amount: 1500`\n"
            "`Description: Office supplies`\n"
            "`Date: 2025-12-14`\n"
            "`Category: Office`",
            parse_mode="Markdown"
        )
        return EXPENSE_TITLE
    
    # Create the expense
    try:
        expense = ExpenseCreate(
            title=expense_data['description'][:100],  # Use first 100 chars as title
            description=expense_data['description'],
            amount=expense_data['amount'],
            transaction_date=expense_data['date'],
            category=expense_data.get('category')
        )
        
        created_expense = expense_service.create_expense(expense, user_info['id'])
        
        # Format success message
        success_msg = (
            "✅ *Expense Recorded Successfully!*\n\n"
            f"💰 *Amount:* ₹{created_expense.amount:,.2f}\n"
            f"📝 *Description:* {created_expense.description}\n"
            f"📅 *Date:* {created_expense.transaction_date}\n"
        )
        
        if created_expense.category:
            success_msg += f"🏷️ *Category:* {created_expense.category}\n"
        
        success_msg += f"\n🆔 *ID:* `{created_expense.id}`\n"
        
        await update.message.reply_text(success_msg, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to create expense: {str(e)}\n\n"
            "Please try again or contact support."
        )
    
    return ConversationHandler.END


async def cancel_expense_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


def add_expense_conversation():
    """Create conversation handler for adding expenses - single message format"""
    return ConversationHandler(
        entry_points=[CommandHandler("add_expense", add_expense_start)],
        states={
            EXPENSE_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_title),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_expense_conversation)],
    )


@admin_required
async def delete_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /delete_expense <id> command"""
    is_valid, args, error = parse_command_args(update.message.text, 1)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /delete_expense <expense_id>\n"
            "Example: /delete_expense abc123"
        )
        return
    
    expense_id = args[0]
    
    try:
        # Get expense first to show what's being deleted
        expense = expense_service.get_expense_by_id(expense_id)
        
        if not expense:
            await update.message.reply_text("❌ Expense not found")
            return
        
        # Delete the expense
        deleted = expense_service.delete_expense(expense_id)
        
        if deleted:
            await update.message.reply_text(
                f"✅ Expense deleted successfully!\n\n"
                f"Deleted: {expense.title}\n"
                f"Amount: ₹{expense.amount:,.2f}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Failed to delete expense")
            
    except Exception as e:
        await update.message.reply_text(f"Error deleting expense: {str(e)}")
