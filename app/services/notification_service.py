"""Notification service for sending Telegram messages"""

import logging
from typing import List
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from app.config import settings
from app.database.models import Order
from app.utils.formatters import format_order_summary

logger = logging.getLogger(__name__)


async def send_order_notification(order: Order):
    """
    Send notification about new order to all admin users
    
    Args:
        order: The order object to notify about
    """
    try:
        bot = Bot(token=settings.telegram_bot_token)
        
        message = (
            "🔔 *New Order Received!*\n\n"
            f"{format_order_summary(order)}"
        )
        
        # Add action buttons
        keyboard = [[
            InlineKeyboardButton("View Details", callback_data=f"order_view_{order.id}"),
            InlineKeyboardButton("Confirm Payment", callback_data=f"order_status_{order.id}_payment_confirmed"),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send to all admin users
        for admin_id in settings.admin_user_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
                logger.info(f"Order notification sent to admin {admin_id} for order {order.id}")
            except Exception as e:
                logger.error(f"Failed to send notification to admin {admin_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error sending order notification: {e}")


async def send_custom_notification(
    message: str,
    admin_ids: List[int] = None,
    parse_mode: str = "Markdown"
):
    """
    Send custom notification to admins
    
    Args:
        message: Message to send
        admin_ids: List of admin IDs (defaults to all admins)
        parse_mode: Telegram parse mode
    """
    try:
        bot = Bot(token=settings.telegram_bot_token)
        
        target_ids = admin_ids if admin_ids else settings.admin_user_ids
        
        for admin_id in target_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode=parse_mode
                )
                logger.info(f"Custom notification sent to admin {admin_id}")
            except Exception as e:
                logger.error(f"Failed to send notification to admin {admin_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error sending custom notification: {e}")
