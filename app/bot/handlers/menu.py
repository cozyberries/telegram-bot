"""Interactive menu system with nested inline keyboards"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.bot.middleware.auth import admin_required


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📦 Orders", callback_data="menu_orders"),
            InlineKeyboardButton("🛍️ Products", callback_data="menu_products"),
        ],
        [
            InlineKeyboardButton("💰 Expenses", callback_data="menu_expenses"),
            InlineKeyboardButton("📊 Stock", callback_data="menu_stock"),
        ],
        [
            InlineKeyboardButton("📈 Analytics", callback_data="menu_analytics"),
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
        ],
        [InlineKeyboardButton("❓ Help", callback_data="menu_help")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_orders_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate orders submenu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📋 View All Orders", callback_data="orders_list_all")],
        [
            InlineKeyboardButton("⏳ Pending", callback_data="orders_filter_pending"),
            InlineKeyboardButton("✅ Confirmed", callback_data="orders_filter_confirmed"),
        ],
        [
            InlineKeyboardButton("📦 Shipped", callback_data="orders_filter_shipped"),
            InlineKeyboardButton("✅ Delivered", callback_data="orders_filter_delivered"),
        ],
        [InlineKeyboardButton("➕ Create New Order", callback_data="orders_create")],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_products_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate products submenu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📋 View All Products", callback_data="products_list_all")],
        [
            InlineKeyboardButton("🔍 Search", callback_data="products_search"),
            InlineKeyboardButton("📊 By Category", callback_data="products_by_category"),
        ],
        [InlineKeyboardButton("➕ Add New Product", callback_data="products_create")],
        [
            InlineKeyboardButton("✏️ Update Product", callback_data="products_update"),
            InlineKeyboardButton("🗑️ Delete Product", callback_data="products_delete"),
        ],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_expenses_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate expenses submenu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📋 View All Expenses", callback_data="expenses_list_all")],
        [
            InlineKeyboardButton("⏳ Pending", callback_data="expenses_filter_pending"),
            InlineKeyboardButton("✅ Approved", callback_data="expenses_filter_approved"),
        ],
        [InlineKeyboardButton("➕ Add New Expense", callback_data="expenses_create")],
        [
            InlineKeyboardButton("✅ Approve", callback_data="expenses_approve"),
            InlineKeyboardButton("❌ Reject", callback_data="expenses_reject"),
        ],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_stock_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate stock submenu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📊 View All Stock", callback_data="stock_list_all")],
        [
            InlineKeyboardButton("⚠️ Low Stock", callback_data="stock_low"),
            InlineKeyboardButton("❌ Out of Stock", callback_data="stock_out"),
        ],
        [InlineKeyboardButton("📝 Update Stock", callback_data="stock_update")],
        [InlineKeyboardButton("📈 Stock Report", callback_data="stock_report")],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_analytics_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate analytics submenu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📊 Overall Stats", callback_data="analytics_overall")],
        [
            InlineKeyboardButton("📦 Order Stats", callback_data="analytics_orders"),
            InlineKeyboardButton("💰 Expense Stats", callback_data="analytics_expenses"),
        ],
        [
            InlineKeyboardButton("🛍️ Product Stats", callback_data="analytics_products"),
            InlineKeyboardButton("📈 Revenue Stats", callback_data="analytics_revenue"),
        ],
        [InlineKeyboardButton("📅 Date Range Report", callback_data="analytics_date_range")],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str, extra_buttons: list = None) -> InlineKeyboardMarkup:
    """Generate pagination keyboard with optional extra buttons"""
    keyboard = []
    
    # Navigation buttons
    nav_row = []
    if current_page > 0:
        nav_row.append(InlineKeyboardButton("« Previous", callback_data=f"{prefix}_page_{current_page - 1}"))
    
    nav_row.append(InlineKeyboardButton(f"{current_page + 1}/{total_pages}", callback_data="noop"))
    
    if current_page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next »", callback_data=f"{prefix}_page_{current_page + 1}"))
    
    if nav_row:
        keyboard.append(nav_row)
    
    # Extra buttons if provided
    if extra_buttons:
        for button_row in extra_buttons:
            keyboard.append(button_row)
    
    return InlineKeyboardMarkup(keyboard)


def get_item_action_keyboard(item_type: str, item_id: str, back_callback: str = None) -> InlineKeyboardMarkup:
    """Generate action keyboard for a specific item (order, product, expense)"""
    keyboard = []
    
    if item_type == "order":
        keyboard = [
            [
                InlineKeyboardButton("✏️ Update Status", callback_data=f"order_update_status_{item_id}"),
                InlineKeyboardButton("👁️ View Details", callback_data=f"order_details_{item_id}"),
            ],
            [
                InlineKeyboardButton("📧 Notify Customer", callback_data=f"order_notify_{item_id}"),
                InlineKeyboardButton("🗑️ Cancel Order", callback_data=f"order_cancel_{item_id}"),
            ]
        ]
    elif item_type == "product":
        keyboard = [
            [
                InlineKeyboardButton("✏️ Edit", callback_data=f"product_edit_{item_id}"),
                InlineKeyboardButton("👁️ View Details", callback_data=f"product_details_{item_id}"),
            ],
            [
                InlineKeyboardButton("📦 Update Stock", callback_data=f"product_stock_{item_id}"),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"product_delete_{item_id}"),
            ]
        ]
    elif item_type == "expense":
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"expense_approve_{item_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"expense_reject_{item_id}"),
            ],
            [
                InlineKeyboardButton("👁️ View Details", callback_data=f"expense_details_{item_id}"),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"expense_delete_{item_id}"),
            ]
        ]
    
    # Add back button if callback provided
    if back_callback:
        keyboard.append([InlineKeyboardButton("« Back", callback_data=back_callback)])
    
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(action: str, item_id: str, back_callback: str) -> InlineKeyboardMarkup:
    """Generate confirmation keyboard for destructive actions"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Confirm", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=back_callback),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


@admin_required
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main interactive menu"""
    user = update.effective_user
    
    text = (
        f"👋 Welcome *{user.first_name}*!\n\n"
        "🏪 *CozyBerries Admin Panel*\n\n"
        "Choose a category to manage:"
    )
    
    keyboard = get_main_menu_keyboard()
    
    # Handle both message and callback query
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )


async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    # Main menu navigation
    if data == "menu_main":
        await show_main_menu(update, context)
    
    elif data == "menu_orders":
        text = "📦 *Orders Management*\n\nSelect an action:"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_orders_menu_keyboard()
        )
    
    elif data == "menu_products":
        text = "🛍️ *Products Management*\n\nSelect an action:"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_products_menu_keyboard()
        )
    
    elif data == "menu_expenses":
        text = "💰 *Expenses Management*\n\nSelect an action:"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_expenses_menu_keyboard()
        )
    
    elif data == "menu_stock":
        text = "📊 *Stock Management*\n\nSelect an action:"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_stock_menu_keyboard()
        )
    
    elif data == "menu_analytics":
        text = "📈 *Analytics Dashboard*\n\nSelect a report:"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_analytics_menu_keyboard()
        )
    
    elif data == "menu_help":
        help_text = (
            "❓ *Help & Commands*\n\n"
            "*How to use this bot:*\n"
            "1. Use the menu buttons to navigate\n"
            "2. Select actions from submenus\n"
            "3. Follow prompts for data entry\n\n"
            "*Quick Commands:*\n"
            "/menu - Show main menu\n"
            "/orders - Orders management\n"
            "/products - Products management\n"
            "/expenses - Expenses management\n"
            "/stock - Stock management\n"
            "/stats - View analytics\n\n"
            "💡 *Tip:* All operations are now accessible through interactive menus!"
        )
        keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]]
        await query.edit_message_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "menu_settings":
        text = (
            "⚙️ *Settings*\n\n"
            "_Settings panel coming soon..._\n\n"
            "Configure:\n"
            "• Notification preferences\n"
            "• Low stock thresholds\n"
            "• Currency settings\n"
            "• Export options"
        )
        keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]]
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "noop":
        # No operation - for page indicator button
        pass
