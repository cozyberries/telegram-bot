"""Product CRUD command handlers"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from app.bot.middleware.auth import admin_required
from app.services import product_service
from app.database.models import ProductCreate
from app.utils.formatters import (
    format_product_summary,
    format_list_header,
    format_pagination_info,
    create_pagination_keyboard,
)
from app.utils.validators import (
    validate_amount,
    validate_quantity,
    validate_uuid,
    parse_command_args,
)

# Conversation states
PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESC, PRODUCT_STOCK, PRODUCT_CATEGORY = range(5)


@admin_required
async def list_products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /products command - list all products"""
    try:
        products = await product_service.get_products(limit=10)
        
        if not products:
            await update.message.reply_text("No products found.")
            return
        
        message = format_list_header("Products", len(products))
        
        for product in products:
            message += f"\n{format_product_summary(product)}\n---\n"
        
        # Add action buttons
        keyboard = [[
            InlineKeyboardButton("➕ Add Product", callback_data="product_add"),
            InlineKeyboardButton("🔄 Refresh", callback_data="product_refresh"),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching products: {str(e)}")


@admin_required
async def get_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /product <id> command - get product details"""
    is_valid, args, error = parse_command_args(update.message.text, 1)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /product <product_id>\n"
            "Example: /product 123e4567-e89b-12d3-a456-426614174000"
        )
        return
    
    product_id = args[0]
    
    try:
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            await update.message.reply_text("❌ Product not found")
            return
        
        message = format_product_summary(product)
        
        # Add action buttons
        keyboard = [
            [
                InlineKeyboardButton("📝 Update", callback_data=f"product_update_{product_id}"),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"product_delete_{product_id}"),
            ],
            [
                InlineKeyboardButton("📦 Update Stock", callback_data=f"product_stock_{product_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching product: {str(e)}")


@admin_required
async def update_product_stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /product_stock <id> <quantity> command"""
    is_valid, args, error = parse_command_args(update.message.text, 2)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /product_stock <product_id> <quantity>\n"
            "Example: /product_stock abc123 50"
        )
        return
    
    product_id, quantity_str = args
    
    # Validate quantity
    is_valid, quantity, error = validate_quantity(quantity_str)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    try:
        product = await product_service.update_product_stock(product_id, quantity)
        
        if not product:
            await update.message.reply_text("❌ Product not found")
            return
        
        await update.message.reply_text(
            f"✅ Stock updated successfully!\n\n"
            f"Product: {product.name}\n"
            f"New stock: {product.stock_quantity} units"
        )
    except Exception as e:
        await update.message.reply_text(f"Error updating stock: {str(e)}")


@admin_required
async def delete_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /delete_product <id> command"""
    is_valid, args, error = parse_command_args(update.message.text, 1)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /delete_product <product_id>\n"
            "Example: /delete_product abc123"
        )
        return
    
    product_id = args[0]
    
    try:
        # First check if product exists
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            await update.message.reply_text("❌ Product not found")
            return
        
        # Ask for confirmation
        keyboard = [[
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f"product_confirm_delete_{product_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="product_cancel_delete"),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ Are you sure you want to delete this product?\n\n"
            f"*{product.name}*\n"
            f"Price: ₹{product.price}\n"
            f"Stock: {product.stock_quantity}\n\n"
            f"This action cannot be undone.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


# Conversation handlers for adding product
@admin_required
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add product conversation"""
    await update.message.reply_text(
        "📦 *Add New Product*\n\n"
        "Please enter the product name:\n\n"
        "Send /cancel to stop.",
        parse_mode="Markdown"
    )
    return PRODUCT_NAME


async def add_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive product name"""
    context.user_data['product_name'] = update.message.text
    
    await update.message.reply_text(
        "✅ Product name saved.\n\n"
        "Now enter the product price (in ₹):"
    )
    return PRODUCT_PRICE


async def add_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive product price"""
    is_valid, price, error = validate_amount(update.message.text)
    
    if not is_valid:
        await update.message.reply_text(f"❌ {error}\n\nPlease enter a valid price:")
        return PRODUCT_PRICE
    
    context.user_data['product_price'] = price
    
    await update.message.reply_text(
        "✅ Price saved.\n\n"
        "Enter product description (or send /skip):"
    )
    return PRODUCT_DESC


async def add_product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive product description"""
    if update.message.text != "/skip":
        context.user_data['product_description'] = update.message.text
    
    await update.message.reply_text(
        "Enter initial stock quantity:"
    )
    return PRODUCT_STOCK


async def add_product_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive stock quantity and create product"""
    is_valid, stock, error = validate_quantity(update.message.text)
    
    if not is_valid:
        await update.message.reply_text(f"❌ {error}\n\nPlease enter a valid quantity:")
        return PRODUCT_STOCK
    
    context.user_data['product_stock'] = stock
    
    # Create product
    try:
        product_data = ProductCreate(
            name=context.user_data['product_name'],
            price=context.user_data['product_price'],
            description=context.user_data.get('product_description'),
            stock_quantity=stock,
            is_featured=False,
        )
        
        product = await product_service.create_product(product_data)
        
        await update.message.reply_text(
            f"✅ *Product created successfully!*\n\n"
            f"{format_product_summary(product)}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error creating product: {str(e)}")
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text("Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


def add_product_conversation():
    """Create conversation handler for adding products"""
    return ConversationHandler(
        entry_points=[CommandHandler("add_product", add_product_start)],
        states={
            PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name)],
            PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            PRODUCT_DESC: [
                CommandHandler("skip", add_product_description),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_description)
            ],
            PRODUCT_STOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_stock)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )


async def handle_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product-related callback queries"""
    query = update.callback_query
    data = query.data
    
    if data == "product_add":
        await query.message.reply_text("Use /add_product to add a new product")
    
    elif data == "product_refresh":
        # Re-run list products
        await list_products_command(update, context)
    
    elif data.startswith("product_confirm_delete_"):
        product_id = data.replace("product_confirm_delete_", "")
        try:
            success = await product_service.delete_product(product_id)
            if success:
                await query.edit_message_text("✅ Product deleted successfully")
            else:
                await query.edit_message_text("❌ Failed to delete product")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
    
    elif data == "product_cancel_delete":
        await query.edit_message_text("Deletion cancelled")


# Update product command (simplified version)
@admin_required
async def update_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /update_product <id> command"""
    await update.message.reply_text(
        "To update a product:\n"
        "1. Use /product <id> to view product details\n"
        "2. Click the 'Update' button\n"
        "3. Or use /product_stock <id> <quantity> to update stock only"
    )
