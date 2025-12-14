"""Stock management command handlers"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.bot.middleware.auth import admin_required
from app.services import stock_service
from app.utils.formatters import format_product_summary, format_list_header
from app.utils.validators import parse_command_args, validate_quantity


@admin_required
async def list_stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stock command - list all products with stock levels"""
    try:
        products = await stock_service.get_products(limit=20)
        
        if not products:
            await update.message.reply_text("No products found.")
            return
        
        message = format_list_header("Stock Levels", len(products))
        
        for product in products:
            stock_status = "✅" if (product.stock_quantity or 0) > 10 else "⚠️" if (product.stock_quantity or 0) > 0 else "❌"
            message += (
                f"\n{stock_status} *{product.name}*\n"
                f"Stock: {product.stock_quantity or 0} units\n"
                f"Price: ₹{product.price}\n"
                f"ID: `{product.id}`\n"
                f"---\n"
            )
        
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error fetching stock: {str(e)}")


@admin_required
async def low_stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /low_stock command - list products with low stock"""
    try:
        products = await stock_service.get_low_stock_products(threshold=10)
        
        if not products:
            await update.message.reply_text("✅ No low stock products. All inventory levels are good!")
            return
        
        message = "⚠️ *Low Stock Alert*\n\n"
        message += f"_Found {len(products)} products with low stock_\n\n"
        
        for product in products:
            stock_emoji = "❌" if (product.stock_quantity or 0) == 0 else "⚠️"
            message += (
                f"{stock_emoji} *{product.name}*\n"
                f"Stock: {product.stock_quantity or 0} units\n"
                f"Price: ₹{product.price}\n"
                f"ID: `{product.id}`\n"
                f"---\n"
            )
        
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error fetching low stock: {str(e)}")


@admin_required
async def update_stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /update_stock <product_id> <quantity> command"""
    is_valid, args, error = parse_command_args(update.message.text, 2)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /update_stock <product_id> <quantity>\n"
            "Example: /update_stock abc123 50"
        )
        return
    
    product_id, quantity_str = args
    
    # Validate quantity
    is_valid, quantity, error = validate_quantity(quantity_str)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    try:
        product = await stock_service.update_product_stock(product_id, quantity)
        
        if not product:
            await update.message.reply_text("❌ Product not found")
            return
        
        stock_emoji = "✅" if quantity > 10 else "⚠️" if quantity > 0 else "❌"
        
        await update.message.reply_text(
            f"{stock_emoji} *Stock Updated Successfully!*\n\n"
            f"Product: {product.name}\n"
            f"New Stock: {product.stock_quantity} units\n"
            f"Price: ₹{product.price}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error updating stock: {str(e)}")


async def handle_stock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stock-related callback queries"""
    query = update.callback_query
    await query.answer("Stock callback handled")
