"""Start command handler"""

from telegram import Update
from telegram.ext import ContextTypes
from app.bot.middleware.auth import admin_required


@admin_required
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - shows all available commands"""
    user = update.effective_user
    
    help_text = (
        f"👋 Welcome *{user.first_name}* to *CozyBerries Assistant*!\n\n"
        "I'll help you manage your e-commerce operations. Here are all available commands:\n\n"
        
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
        "/start - Show this help message\n"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
