"""Expense CRUD command handlers - Refactored with Pydantic models"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from pydantic import ValidationError
from decimal import Decimal

from app.bot.middleware.auth import admin_required, get_user_info
from app.services import expense_service
from app.schemas.expenses import ExpenseInput
from app.utils.parsers import ExpenseMessageParser, parse_command_args

# Conversation states
EXPENSE_INPUT = 0


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
    return EXPENSE_INPUT


async def add_expense_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parse and create expense using Pydantic validation"""
    message_text = update.message.text.strip()
    user_info = get_user_info(update)
    
    try:
        # Parse message using parser
        parsed_data = ExpenseMessageParser.parse(message_text)
        
        # Validate required fields first
        errors = ExpenseMessageParser.validate_required_fields(parsed_data)
        
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
            return EXPENSE_INPUT
        
        # Create Pydantic model with validation
        expense_input = ExpenseInput(
            user_id=str(user_info['id']),
            username=user_info.get('username'),
            amount=parsed_data['amount'],
            description=parsed_data['description'],
            transaction_date=parsed_data.get('transaction_date'),
            category=parsed_data.get('category')
        )
        
        # Create expense using validated input
        created_expense = expense_service.create_expense(expense_input)
        
        # Use the response's built-in formatting with success message
        success_msg = (
            "✅ *Expense Recorded Successfully!*\n\n"
            f"{created_expense.to_telegram_message()}"
        )
        
        await update.message.reply_text(success_msg, parse_mode="Markdown")
        
    except ValidationError as e:
        # Handle Pydantic validation errors
        error_messages = []
        for error in e.errors():
            field = error['loc'][0] if error['loc'] else 'field'
            msg = error['msg']
            error_messages.append(f"❌ {field}: {msg}")
        
        await update.message.reply_text(
            "\n".join(error_messages) + "\n\n"
            "Please check your input and try again.",
            parse_mode="Markdown"
        )
        return EXPENSE_INPUT
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to create expense: {str(e)}\n\n"
            "Please try again or contact support."
        )
        return EXPENSE_INPUT
    
    return ConversationHandler.END


async def cancel_expense_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


def add_expense_conversation():
    """Create conversation handler for adding expenses"""
    return ConversationHandler(
        entry_points=[CommandHandler("add_expense", add_expense_start)],
        states={
            EXPENSE_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_input),
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
