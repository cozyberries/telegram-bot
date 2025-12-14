"""Start and help command handlers"""

from telegram import Update
from telegram.ext import ContextTypes
from app.bot.middleware.auth import admin_required


@admin_required
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome to *CozyBerries Admin Bot*, {user.first_name}!\n\n"
        "I'm here to help you manage your e-commerce operations:\n\n"
        "📦 *Orders* - View and update order status\n"
        "🛍️ *Products* - Manage product catalog\n"
        "💰 *Expenses* - Track and approve expenses\n"
        "📊 *Analytics* - View business statistics\n"
        "📦 *Stock* - Monitor inventory levels\n\n"
        "Use /help to see all available commands."
    )
    
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


@admin_required
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🤖 *CozyBerries Admin Bot - Command Reference*\n\n"
        
        "*📦 Orders*\n"
        "/orders - List recent orders\n"
        "/order `<id>` - Get order details\n"
        "/order\\_status `<id>` `<status>` - Update order status\n"
        "/add\\_order - Create new order\n\n"
        
        "*🛍️ Products*\n"
        "/products - List all products\n"
        "/product `<id>` - Get product details\n"
        "/add\\_product - Add new product\n"
        "/update\\_product `<id>` - Update product\n"
        "/delete\\_product `<id>` - Delete product\n"
        "/product\\_stock `<id>` `<qty>` - Update stock\n\n"
        
        "*💰 Expenses*\n"
        "/expenses - List expenses\n"
        "/expense `<id>` - Get expense details\n"
        "/add\\_expense - Add new expense\n"
        "/approve\\_expense `<id>` - Approve expense\n"
        "/reject\\_expense `<id>` `<reason>` - Reject expense\n\n"
        
        "*📦 Stock Management*\n"
        "/stock - View all stock levels\n"
        "/low\\_stock - View low stock products\n"
        "/update\\_stock `<id>` `<qty>` - Update stock\n\n"
        
        "*📊 Analytics*\n"
        "/stats - Overall statistics\n"
        "/stats\\_orders - Order statistics\n"
        "/stats\\_expenses - Expense statistics\n"
        "/stats\\_products - Product statistics\n\n"
        
        "*ℹ️ General*\n"
        "/start - Welcome message\n"
        "/help - This help message\n"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
