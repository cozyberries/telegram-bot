"""Expense CRUD command handlers"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from app.bot.middleware.auth import admin_required, get_user_info
from app.services import expense_service
from app.database.models import ExpenseCreate
from app.utils.formatters import format_expense_summary, format_list_header
from app.utils.validators import parse_command_args, validate_amount, validate_date

# Conversation states
EXPENSE_TITLE, EXPENSE_AMOUNT, EXPENSE_CATEGORY, EXPENSE_DATE, EXPENSE_VENDOR = range(5)


@admin_required
async def list_expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /expenses command - list expenses"""
    try:
        # Call synchronous function
        expenses = expense_service.get_expenses(limit=10)
        
        if not expenses:
            await update.message.reply_text("No expenses found.")
            return
        
        message = format_list_header("Expenses", len(expenses))
        
        for expense in expenses:
            message += f"\n{format_expense_summary(expense)}\n---\n"
        
        # Add filter buttons
        keyboard = [
            [
                InlineKeyboardButton("⏳ Pending", callback_data="expense_filter_pending"),
                InlineKeyboardButton("✅ Approved", callback_data="expense_filter_approved"),
            ],
            [
                InlineKeyboardButton("❌ Rejected", callback_data="expense_filter_rejected"),
                InlineKeyboardButton("🔄 All", callback_data="expense_filter_all"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
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
        
        # Add action buttons based on status
        keyboard = []
        if expense.status == "pending":
            keyboard.append([
                InlineKeyboardButton("✅ Approve", callback_data=f"expense_approve_{expense_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"expense_reject_{expense_id}"),
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching expense: {str(e)}")


@admin_required
async def approve_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve_expense <id> command"""
    is_valid, args, error = parse_command_args(update.message.text, 1)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /approve_expense <expense_id>\n"
            "Example: /approve_expense abc123"
        )
        return
    
    expense_id = args[0]
    user_info = get_user_info(update)
    
    try:
        # Call synchronous function
        expense = expense_service.approve_expense(expense_id, str(user_info["id"]))
        
        if not expense:
            await update.message.reply_text("❌ Expense not found")
            return
        
        await update.message.reply_text(
            f"✅ Expense approved!\n\n"
            f"{format_expense_summary(expense)}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error approving expense: {str(e)}")


@admin_required
async def reject_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reject_expense <id> <reason> command"""
    is_valid, args, error = parse_command_args(update.message.text, 2)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /reject_expense <expense_id> <reason>\n"
            "Example: /reject_expense abc123 Missing receipt"
        )
        return
    
    expense_id, reason = args
    
    try:
        # Call synchronous function
        expense = expense_service.reject_expense(expense_id, reason)
        
        if not expense:
            await update.message.reply_text("❌ Expense not found")
            return
        
        await update.message.reply_text(
            f"❌ Expense rejected\n\n"
            f"Reason: {reason}\n\n"
            f"{format_expense_summary(expense)}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error rejecting expense: {str(e)}")


# Single-message expense creation
@admin_required
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add expense - single message format"""
    help_text = (
        "💰 *Add New Expense*\n\n"
        "Please send all details in one message using this format:\n\n"
        "```\n"
        "Amount: 1500\n"
        "Detail: Office supplies purchase\n"
        "Date: 2025-12-14\n"
        "Notes: Pens, paper, and notebooks\n"
        "```\n\n"
        "📋 *Format Guide:*\n"
        "• `Amount:` Required - expense amount (₹)\n"
        "• `Detail:` Required - what was purchased\n"
        "• `Date:` Optional - transaction date (YYYY-MM-DD)\n"
        "• `Notes:` Optional - additional information\n\n"
        "💡 *Example:*\n"
        "```\n"
        "Amount: 2500\n"
        "Detail: Client lunch meeting\n"
        "Date: 2025-12-14\n"
        "Notes: 3 people at Taj restaurant\n"
        "```\n\n"
        "Send your expense details now, or /cancel to stop."
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
    return EXPENSE_TITLE  # Reuse state for single message


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
            elif key in ['detail', 'details', 'description', 'desc', 'title']:
                expense_data['detail'] = value
            elif key in ['date', 'transaction date', 'expense date']:
                expense_data['date'] = value
            elif key in ['notes', 'note', 'additional notes', 'comments']:
                expense_data['notes'] = value
    
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
    
    if 'detail' not in expense_data:
        errors.append("❌ Detail/Description is required")
    
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
            "```\n"
            "Amount: 1500\n"
            "Detail: Office supplies\n"
            "Date: 2025-12-14\n"
            "Notes: Optional notes\n"
            "```",
            parse_mode="Markdown"
        )
        return EXPENSE_TITLE
    
    # Create the expense
    try:
        expense = ExpenseCreate(
            title=expense_data['detail'][:50],  # Use first 50 chars as title
            description=expense_data['detail'],
            amount=expense_data['amount'],
            category="other",  # Default category
            priority="medium",  # Default priority
            expense_date=expense_data['date'],
            payment_method="cash",  # Default payment method
            notes=expense_data.get('notes'),
            vendor=None
        )
        
        created_expense = expense_service.create_expense(expense, user_info['id'])
        
        # Format success message
        success_msg = (
            "✅ *Expense Created Successfully!*\n\n"
            f"💰 *Amount:* ₹{created_expense.amount:,.2f}\n"
            f"📝 *Detail:* {created_expense.description}\n"
            f"📅 *Date:* {created_expense.expense_date}\n"
        )
        
        if created_expense.notes:
            success_msg += f"📌 *Notes:* {created_expense.notes}\n"
        
        success_msg += (
            f"\n🆔 *ID:* `{created_expense.id}`\n"
            f"⏳ *Status:* {created_expense.status.upper()}\n"
        )
        
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


async def handle_expense_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle expense-related callback queries"""
    query = update.callback_query
    data = query.data
    
    if data.startswith("expense_approve_"):
        expense_id = data.replace("expense_approve_", "")
        user_info = get_user_info(update)
        
        try:
            # Call synchronous function
            expense = expense_service.approve_expense(expense_id, str(user_info["id"]))
            if expense:
                await query.edit_message_text(
                    f"✅ Expense approved!\n\n{format_expense_summary(expense)}",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text("❌ Expense not found")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
    
    elif data.startswith("expense_reject_"):
        expense_id = data.replace("expense_reject_", "")
        await query.edit_message_text(
            f"To reject this expense, use:\n"
            f"/reject_expense {expense_id} <reason>"
        )
    
    elif data.startswith("expense_filter_"):
        status_filter = data.replace("expense_filter_", "")
        
        try:
            # Call synchronous function
            if status_filter == "all":
                expenses = expense_service.get_expenses(limit=10)
            else:
                expenses = expense_service.get_expenses(status=status_filter)
            
            if not expenses:
                await query.edit_message_text(f"No expenses found with status: {status_filter}")
                return
            
            message = format_list_header(f"Expenses - {status_filter.title()}", len(expenses))
            
            for expense in expenses[:10]:
                message += f"\n{format_expense_summary(expense)}\n---\n"
            
            await query.edit_message_text(message, parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")


@admin_required
async def update_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /update_expense command"""
    await update.message.reply_text(
        "To update an expense, use /expense <id> to view it first."
    )
