"""Interactive menu system with nested inline keyboards"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.bot.middleware.auth import admin_required


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate main menu keyboard - Expenses only"""
    keyboard = [
        [InlineKeyboardButton("💰 Expense Management", callback_data="menu_expenses")],
        [InlineKeyboardButton("❓ Help", callback_data="menu_help")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_expenses_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate expenses submenu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📋 View All Expenses", callback_data="expenses_list_all")],
        [
            InlineKeyboardButton("➕ Add Expense", callback_data="expenses_create"),
            InlineKeyboardButton("📊 Statistics", callback_data="expenses_stats"),
        ],
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
        "💰 *CozyBerries Expense Manager*\n\n"
        "Manage all your business expenses with ease.\n"
        "Track spending, categorize expenses, and get insights."
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
    
    elif data == "menu_expenses":
        text = "💰 *Expense Management*\n\nSelect an action:"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_expenses_menu_keyboard()
        )
    
    elif data == "menu_help":
        help_text = (
            "❓ *Help & Commands*\n\n"
            "*How to use this bot:*\n"
            "1. Use the menu buttons to navigate\n"
            "2. Select actions from expense menu\n"
            "3. Follow prompts for data entry\n\n"
            "*Available Features:*\n"
            "• View all expenses\n"
            "• Add new expenses\n"
            "• Browse expenses with pagination\n"
            "• View expense details\n"
            "• Delete expenses\n"
            "• View expense statistics\n\n"
            "*Quick Commands:*\n"
            "/menu - Show main menu\n"
            "/expenses - List expenses\n"
            "/add_expense - Add new expense\n"
            "/stats - View expense statistics\n\n"
            "💡 *Tip:* All operations are accessible through interactive menus!"
        )
        keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]]
        await query.edit_message_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "noop":
        # No operation - for page indicator button
        pass
