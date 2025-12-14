"""Order CRUD command handlers"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from app.bot.middleware.auth import admin_required
from app.services import order_service
from app.utils.formatters import (
    format_order_summary,
    format_order_details,
    format_list_header,
)
from app.utils.validators import parse_command_args


@admin_required
async def list_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /orders command - list recent orders"""
    try:
        orders = await order_service.get_orders(limit=10)
        
        if not orders:
            await update.message.reply_text("No orders found.")
            return
        
        message = format_list_header("Recent Orders", len(orders))
        
        for order in orders:
            message += f"\n{format_order_summary(order)}\n---\n"
        
        # Add filter buttons
        keyboard = [
            [
                InlineKeyboardButton("⏳ Pending", callback_data="order_filter_payment_pending"),
                InlineKeyboardButton("✅ Confirmed", callback_data="order_filter_payment_confirmed"),
            ],
            [
                InlineKeyboardButton("📦 Shipped", callback_data="order_filter_shipped"),
                InlineKeyboardButton("🔄 All", callback_data="order_filter_all"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching orders: {str(e)}")


@admin_required
async def get_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /order <id> command - get order details"""
    is_valid, args, error = parse_command_args(update.message.text, 1)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /order <order_id>\n"
            "Example: /order 123e4567-e89b-12d3-a456-426614174000"
        )
        return
    
    order_id = args[0]
    
    try:
        order = await order_service.get_order_by_id(order_id)
        
        if not order:
            await update.message.reply_text("❌ Order not found")
            return
        
        message = format_order_details(order)
        
        # Add status update buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Payment", callback_data=f"order_status_{order_id}_payment_confirmed"),
                InlineKeyboardButton("🔄 Processing", callback_data=f"order_status_{order_id}_processing"),
            ],
            [
                InlineKeyboardButton("📦 Shipped", callback_data=f"order_status_{order_id}_shipped"),
                InlineKeyboardButton("✅ Delivered", callback_data=f"order_status_{order_id}_delivered"),
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data=f"order_status_{order_id}_cancelled"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching order: {str(e)}")


@admin_required
async def update_order_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /order_status <id> <status> command"""
    is_valid, args, error = parse_command_args(update.message.text, 2)
    
    if not is_valid:
        await update.message.reply_text(
            "Usage: /order_status <order_id> <status>\n"
            "Status options: payment_pending, payment_confirmed, processing, shipped, delivered, cancelled\n"
            "Example: /order_status abc123 shipped"
        )
        return
    
    order_id, status = args
    
    # Validate status
    valid_statuses = [
        "payment_pending", "payment_confirmed", "processing",
        "shipped", "delivered", "cancelled", "refunded"
    ]
    
    if status not in valid_statuses:
        await update.message.reply_text(
            f"❌ Invalid status. Valid options:\n" + "\n".join(valid_statuses)
        )
        return
    
    try:
        order = await order_service.update_order_status(order_id, status)
        
        if not order:
            await update.message.reply_text("❌ Order not found")
            return
        
        await update.message.reply_text(
            f"✅ Order status updated!\n\n"
            f"Order: #{order.order_number}\n"
            f"New status: {status.replace('_', ' ').title()}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error updating order: {str(e)}")


# Simplified add order conversation
@admin_required
async def add_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add order conversation"""
    await update.message.reply_text(
        "ℹ️ Creating orders through the bot is complex.\n\n"
        "For now, please use the admin dashboard to create orders.\n\n"
        "You can use this bot to:\n"
        "• View orders with /orders\n"
        "• Check order details with /order <id>\n"
        "• Update order status with /order_status <id> <status>"
    )
    return ConversationHandler.END


def add_order_conversation():
    """Create conversation handler for adding orders"""
    return ConversationHandler(
        entry_points=[CommandHandler("add_order", add_order_start)],
        states={},
        fallbacks=[],
    )


async def handle_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle order-related callback queries"""
    query = update.callback_query
    data = query.data
    
    if data.startswith("order_status_"):
        # Extract order_id and status from callback data
        parts = data.replace("order_status_", "").rsplit("_", 1)
        if len(parts) == 2:
            order_id, status = parts
            
            try:
                order = await order_service.update_order_status(order_id, status)
                
                if order:
                    await query.edit_message_text(
                        f"✅ Status updated to: {status.replace('_', ' ').title()}\n\n"
                        f"{format_order_summary(order)}",
                        parse_mode="Markdown"
                    )
                else:
                    await query.edit_message_text("❌ Order not found")
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {str(e)}")
    
    elif data.startswith("order_filter_"):
        status_filter = data.replace("order_filter_", "")
        
        try:
            if status_filter == "all":
                orders = await order_service.get_orders(limit=10)
            else:
                orders = await order_service.get_orders_by_status(status_filter)
            
            if not orders:
                await query.edit_message_text(f"No orders found with status: {status_filter}")
                return
            
            message = format_list_header(f"Orders - {status_filter.replace('_', ' ').title()}", len(orders))
            
            for order in orders[:10]:  # Limit to 10 for message size
                message += f"\n{format_order_summary(order)}\n---\n"
            
            await query.edit_message_text(message, parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
