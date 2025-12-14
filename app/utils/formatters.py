"""Message formatting utilities for Telegram bot"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database.models import Order, Product, Expense, OrderStatus


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format amount as currency string"""
    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_datetime(dt_str: str) -> str:
    """Format ISO datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%d %b %Y, %I:%M %p")
    except:
        return dt_str


def format_date(dt_str: str) -> str:
    """Format ISO datetime string to date only"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%d %b %Y")
    except:
        return dt_str


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def escape_markdown(text: str) -> str:
    """Escape special characters for Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def format_order_status(status: OrderStatus) -> str:
    """Format order status with emoji"""
    status_emoji = {
        "payment_pending": "⏳",
        "payment_confirmed": "✅",
        "processing": "🔄",
        "shipped": "📦",
        "delivered": "✅",
        "cancelled": "❌",
        "refunded": "💰"
    }
    emoji = status_emoji.get(status, "")
    formatted = status.replace('_', ' ').title()
    return f"{emoji} {formatted}"


def format_order_summary(order: Order) -> str:
    """Format order as summary message"""
    message = (
        f"📦 *Order #{order.order_number}*\n\n"
        f"*Status:* {format_order_status(order.status)}\n"
        f"*Customer:* {escape_markdown(order.customer_email)}\n"
        f"*Total:* {format_currency(order.total_amount, order.currency)}\n"
        f"*Items:* {len(order.items)}\n"
        f"*Date:* {format_datetime(order.created_at)}\n"
    )
    
    if order.tracking_number:
        message += f"*Tracking:* `{order.tracking_number}`\n"
    
    return message


def format_order_details(order: Order) -> str:
    """Format order with full details"""
    message = format_order_summary(order)
    
    message += "\n*Items:*\n"
    for item in order.items:
        message += f"• {escape_markdown(item.name)} × {item.quantity} - {format_currency(item.price)}\n"
    
    message += (
        f"\n*Amounts:*\n"
        f"Subtotal: {format_currency(order.subtotal)}\n"
        f"Delivery: {format_currency(order.delivery_charge)}\n"
        f"Tax: {format_currency(order.tax_amount)}\n"
        f"*Total: {format_currency(order.total_amount)}*\n"
    )
    
    message += (
        f"\n*Shipping Address:*\n"
        f"{escape_markdown(order.shipping_address.full_name)}\n"
        f"{escape_markdown(order.shipping_address.address_line_1)}\n"
    )
    
    if order.shipping_address.address_line_2:
        message += f"{escape_markdown(order.shipping_address.address_line_2)}\n"
    
    message += (
        f"{escape_markdown(order.shipping_address.city)}, "
        f"{escape_markdown(order.shipping_address.state)} "
        f"{escape_markdown(order.shipping_address.postal_code)}\n"
    )
    
    if order.notes:
        message += f"\n*Notes:* {escape_markdown(order.notes)}\n"
    
    return message


def format_product_summary(product: Product) -> str:
    """Format product as summary message"""
    stock_emoji = "✅" if (product.stock_quantity or 0) > 10 else "⚠️" if (product.stock_quantity or 0) > 0 else "❌"
    featured = "⭐ " if product.is_featured else ""
    
    message = (
        f"{featured}*{escape_markdown(product.name)}*\n\n"
        f"*Price:* {format_currency(product.price)}\n"
        f"*Stock:* {stock_emoji} {product.stock_quantity or 0} units\n"
        f"*ID:* `{product.id}`\n"
    )
    
    if product.category:
        message += f"*Category:* {escape_markdown(product.category)}\n"
    
    if product.description:
        desc = truncate_text(product.description, 150)
        message += f"\n{escape_markdown(desc)}\n"
    
    return message


def format_expense_summary(expense: Expense) -> str:
    """Format expense as summary message"""
    message = (
        f"💳 *{escape_markdown(expense.title)}*\n\n"
        f"*Amount:* {format_currency(expense.amount)}\n"
        f"*Date:* {format_date(expense.transaction_date)}\n"
    )
    
    if expense.category:
        message += f"*Category:* {escape_markdown(expense.category)}\n"
    
    if expense.description and expense.description != expense.title:
        desc = truncate_text(expense.description, 100)
        message += f"\n{escape_markdown(desc)}\n"
    
    message += f"\n*ID:* `{expense.id}`\n"
    
    return message


def format_pagination_info(current_page: int, total_pages: int, total_items: int) -> str:
    """Format pagination information"""
    return f"Page {current_page}/{total_pages} • Total: {total_items} items"


def format_list_header(title: str, count: int) -> str:
    """Format list header with count"""
    return f"📋 *{title}*\n\n_Found {count} items_\n"


def format_stats_summary(stats: Dict[str, Any]) -> str:
    """Format statistics summary"""
    message = "📊 *Statistics Summary*\n\n"
    
    for key, value in stats.items():
        formatted_key = key.replace('_', ' ').title()
        
        if isinstance(value, (int, float)):
            if 'amount' in key.lower() or 'revenue' in key.lower() or 'value' in key.lower():
                formatted_value = format_currency(value)
            else:
                formatted_value = f"{value:,}"
        else:
            formatted_value = str(value)
        
        message += f"• *{formatted_key}:* {formatted_value}\n"
    
    return message


def create_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str
) -> List[List[Dict[str, str]]]:
    """Create inline keyboard for pagination"""
    keyboard = []
    buttons = []
    
    # Previous button
    if current_page > 1:
        buttons.append({
            "text": "⬅️ Previous",
            "callback_data": f"{callback_prefix}_page_{current_page - 1}"
        })
    
    # Page info
    buttons.append({
        "text": f"{current_page}/{total_pages}",
        "callback_data": "noop"
    })
    
    # Next button
    if current_page < total_pages:
        buttons.append({
            "text": "Next ➡️",
            "callback_data": f"{callback_prefix}_page_{current_page + 1}"
        })
    
    if buttons:
        keyboard.append(buttons)
    
    return keyboard
