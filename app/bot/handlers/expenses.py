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


# Conversation handlers for adding expense
@admin_required
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add expense conversation"""
    await update.message.reply_text(
        "💰 *Add New Expense*\n\n"
        "Please enter the expense title:\n\n"
        "Send /cancel to stop.",
        parse_mode="Markdown"
    )
    return EXPENSE_TITLE


async def add_expense_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive expense title"""
    context.user_data['expense_title'] = update.message.text
    
    await update.message.reply_text(
        "✅ Title saved.\n\n"
        "Now enter the amount (in ₹):"
    )
    return EXPENSE_AMOUNT


async def add_expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive expense amount"""
    is_valid, amount, error = validate_amount(update.message.text)
    
    if not is_valid:
        await update.message.reply_text(f"❌ {error}\n\nPlease enter a valid amount:")
        return EXPENSE_AMOUNT
    
    context.user_data['expense_amount'] = amount
    
    await update.message.reply_text(
        "✅ Amount saved.\n\n"
        "Select category:\n"
        "1. Office Supplies\n"
        "2. Travel\n"
        "3. Marketing\n"
        "4. Software\n"
        "5. Equipment\n"
        "6. Utilities\n"
        "7. Professional Services\n"
        "8. Training\n"
        "9. Maintenance\n"
        "10. Other\n\n"
        "Reply with the number or name:"
    )
    return EXPENSE_CATEGORY


async def add_expense_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive expense category"""
    category_map = {
        "1": "office_supplies",
        "2": "travel",
        "3": "marketing",
        "4": "software",
        "5": "equipment",
        "6": "utilities",
        "7": "professional_services",
        "8": "training",
        "9": "maintenance",
        "10": "other",
    }
    
    text = update.message.text.lower()
    category = category_map.get(text, text.replace(" ", "_"))
    
    valid_categories = list(category_map.values())
    if category not in valid_categories:
        await update.message.reply_text("❌ Invalid category. Please select a valid option:")
        return EXPENSE_CATEGORY
    
    context.user_data['expense_category'] = category
    
    await update.message.reply_text(
        "✅ Category saved.\n\n"
        "Enter expense date (YYYY-MM-DD):"
    )
    return EXPENSE_DATE


async def add_expense_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive expense date"""
    is_valid, date, error = validate_date(update.message.text)
    
    if not is_valid:
        await update.message.reply_text(f"❌ {error}\n\nPlease enter a valid date:")
        return EXPENSE_DATE
    
    context.user_data['expense_date'] = date
    
    await update.message.reply_text(
        "✅ Date saved.\n\n"
        "Enter vendor name (or send /skip):"
    )
    return EXPENSE_VENDOR


async def add_expense_vendor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive vendor and create expense"""
    if update.message.text != "/skip":
        context.user_data['expense_vendor'] = update.message.text
    
    user_info = get_user_info(update)
    
    # Create expense
    try:
        expense_data = ExpenseCreate(
            title=context.user_data['expense_title'],
            amount=context.user_data['expense_amount'],
            category=context.user_data['expense_category'],
            expense_date=context.user_data['expense_date'],
            vendor=context.user_data.get('expense_vendor'),
            priority="medium",
            payment_method="company_card",
        )
        
        # Call synchronous function
        expense = expense_service.create_expense(expense_data, str(user_info["id"]))
        
        await update.message.reply_text(
            f"✅ *Expense created successfully!*\n\n"
            f"{format_expense_summary(expense)}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error creating expense: {str(e)}")
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_expense_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text("Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


def add_expense_conversation():
    """Create conversation handler for adding expenses"""
    return ConversationHandler(
        entry_points=[CommandHandler("add_expense", add_expense_start)],
        states={
            EXPENSE_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_title)],
            EXPENSE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_amount)],
            EXPENSE_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_category)],
            EXPENSE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_date)],
            EXPENSE_VENDOR: [
                CommandHandler("skip", add_expense_vendor),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_vendor)
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
