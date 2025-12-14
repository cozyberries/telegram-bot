"""Interactive product management handlers with nested menus"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.bot.middleware.auth import admin_required
from app.services import product_service
from app.utils.formatters import format_product_summary
from app.bot.handlers.menu import get_products_menu_keyboard, get_pagination_keyboard, get_item_action_keyboard


@admin_required
async def handle_products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle products menu selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "products_list_all":
        await show_products_list(update, context, page=0)
    
    elif data.startswith("products_page_"):
        page = int(data.split("_")[-1])
        await show_products_list(update, context, page=page)
    
    elif data == "products_search":
        text = (
            "🔍 *Search Products*\n\n"
            "Send me the product name or ID to search.\n\n"
            "💡 *Tip:* You can search by partial name"
        )
        keyboard = [[InlineKeyboardButton("« Back", callback_data="menu_products")]]
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['awaiting_product_search'] = True
    
    elif data == "products_by_category":
        await show_products_by_category(update, context)
    
    elif data == "products_create":
        await start_product_creation(update, context)
    
    elif data.startswith("product_details_"):
        product_id = data.replace("product_details_", "")
        await show_product_details(update, context, product_id)
    
    elif data.startswith("product_edit_"):
        product_id = data.replace("product_edit_", "")
        await start_product_edit(update, context, product_id)
    
    elif data.startswith("product_stock_"):
        product_id = data.replace("product_stock_", "")
        await start_stock_update(update, context, product_id)
    
    elif data.startswith("product_delete_"):
        product_id = data.replace("product_delete_", "")
        await confirm_product_deletion(update, context, product_id)


async def show_products_list(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, filter_category: str = None):
    """Show paginated product list"""
    query = update.callback_query
    items_per_page = 5
    offset = page * items_per_page
    
    try:
        products = await product_service.get_products(limit=items_per_page, offset=offset)
        total_count = await product_service.get_product_count()
        
        if not products:
            text = "📦 No products found."
            keyboard = [[InlineKeyboardButton("« Back to Products Menu", callback_data="menu_products")]]
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        total_pages = (total_count + items_per_page - 1) // items_per_page
        
        text = f"🛍️ *Products List* (Page {page + 1}/{total_pages})\n\n"
        text += f"_Showing {len(products)} of {total_count} products_\n\n"
        
        # Create inline keyboard with products
        keyboard = []
        for product in products:
            stock_emoji = "✅" if (product.stock_quantity or 0) > 10 else "⚠️" if (product.stock_quantity or 0) > 0 else "❌"
            button_text = f"{stock_emoji} {product.name} - ₹{product.price}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"product_details_{product.id}")])
        
        # Add pagination
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("« Prev", callback_data=f"products_page_{page - 1}"))
        nav_row.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("Next »", callback_data=f"products_page_{page + 1}"))
        
        if nav_row:
            keyboard.append(nav_row)
        
        # Add action buttons
        keyboard.append([
            InlineKeyboardButton("➕ Add Product", callback_data="products_create"),
            InlineKeyboardButton("🔄 Refresh", callback_data="products_list_all")
        ])
        keyboard.append([InlineKeyboardButton("« Back to Products Menu", callback_data="menu_products")])
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await query.edit_message_text(f"Error loading products: {str(e)}")


async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    """Show detailed product information with action buttons"""
    query = update.callback_query
    
    try:
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            await query.answer("Product not found", show_alert=True)
            return
        
        # Format detailed product info
        stock_status = "In Stock ✅" if (product.stock_quantity or 0) > 10 else \
                      "Low Stock ⚠️" if (product.stock_quantity or 0) > 0 else \
                      "Out of Stock ❌"
        
        text = (
            f"🛍️ *Product Details*\n\n"
            f"*Name:* {product.name}\n"
            f"*Price:* ₹{product.price:,.2f}\n"
            f"*Stock:* {product.stock_quantity or 0} units\n"
            f"*Status:* {stock_status}\n"
        )
        
        if product.description:
            text += f"*Description:* {product.description}\n"
        
        if product.category:
            text += f"*Category:* {product.category}\n"
        
        text += f"\n*ID:* `{product.id}`\n"
        
        # Action buttons
        keyboard = [
            [
                InlineKeyboardButton("✏️ Edit", callback_data=f"product_edit_{product_id}"),
                InlineKeyboardButton("📦 Update Stock", callback_data=f"product_stock_{product_id}"),
            ],
            [
                InlineKeyboardButton("🗑️ Delete", callback_data=f"product_delete_{product_id}"),
            ],
            [
                InlineKeyboardButton("« Back to List", callback_data="products_list_all"),
                InlineKeyboardButton("« Main Menu", callback_data="menu_main"),
            ]
        ]
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


async def show_products_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show products grouped by category"""
    query = update.callback_query
    
    try:
        # Get all products
        products = await product_service.get_products(limit=100)
        
        # Group by category
        categories = {}
        for product in products:
            category = product.category or "Uncategorized"
            if category not in categories:
                categories[category] = []
            categories[category].append(product)
        
        text = "📂 *Products by Category*\n\n"
        
        keyboard = []
        for category, items in sorted(categories.items()):
            button_text = f"{category} ({len(items)})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"products_cat_{category}")])
        
        keyboard.append([InlineKeyboardButton("« Back to Products Menu", callback_data="menu_products")])
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


async def start_product_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start product creation flow"""
    query = update.callback_query
    
    text = (
        "➕ *Create New Product*\n\n"
        "Send me the product details in this format:\n\n"
        "`Name: Product name`\n"
        "`Price: 999.99`\n"
        "`Stock: 50`\n"
        "`Description: Product description`\n"
        "`Category: Category name`\n\n"
        "💡 *Example:*\n"
        "`Name: Chocolate Cake`\n"
        "`Price: 599`\n"
        "`Stock: 20`\n"
        "`Description: Delicious chocolate cake`\n"
        "`Category: Cakes`"
    )
    
    keyboard = [[InlineKeyboardButton("« Cancel", callback_data="menu_products")]]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    context.user_data['awaiting_product_data'] = True


async def start_stock_update(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    """Start stock update flow"""
    query = update.callback_query
    
    try:
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            await query.answer("Product not found", show_alert=True)
            return
        
        text = (
            f"📦 *Update Stock*\n\n"
            f"*Product:* {product.name}\n"
            f"*Current Stock:* {product.stock_quantity or 0} units\n\n"
            "Send me the new stock quantity:\n\n"
            "💡 *Example:* `50`"
        )
        
        keyboard = [[InlineKeyboardButton("« Cancel", callback_data=f"product_details_{product_id}")]]
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        context.user_data['awaiting_stock_update'] = product_id
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


async def confirm_product_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    """Show confirmation dialog for product deletion"""
    query = update.callback_query
    
    try:
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            await query.answer("Product not found", show_alert=True)
            return
        
        text = (
            f"🗑️ *Delete Product*\n\n"
            f"Are you sure you want to delete:\n\n"
            f"*{product.name}*\n"
            f"Price: ₹{product.price}\n"
            f"Stock: {product.stock_quantity or 0} units\n\n"
            "⚠️ *Warning:* This action cannot be undone!"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_product_{product_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"product_details_{product_id}"),
            ]
        ]
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


async def start_product_edit(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    """Start product editing flow"""
    query = update.callback_query
    
    try:
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            await query.answer("Product not found", show_alert=True)
            return
        
        text = (
            f"✏️ *Edit Product*\n\n"
            f"*Current Details:*\n"
            f"Name: {product.name}\n"
            f"Price: ₹{product.price}\n"
            f"Stock: {product.stock_quantity or 0}\n"
            f"Category: {product.category or 'None'}\n\n"
            "Send me the updated details in this format:\n\n"
            "`Name: New product name`\n"
            "`Price: 999.99`\n"
            "`Stock: 50`\n"
            "`Description: New description`\n"
            "`Category: New category`\n\n"
            "💡 Only include fields you want to change"
        )
        
        keyboard = [[InlineKeyboardButton("« Cancel", callback_data=f"product_details_{product_id}")]]
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        context.user_data['awaiting_product_edit'] = product_id
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)
