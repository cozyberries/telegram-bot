"""Authentication middleware for admin verification"""

import functools
import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.config import settings

logger = logging.getLogger(__name__)


def admin_required(func):
    """
    Decorator to require admin authentication for command handlers
    
    Args:
        func: The command handler function to wrap
    
    Returns:
        Wrapped function that checks admin status before execution
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # Get user ID from update
        user_id = None
        if update.effective_user:
            user_id = update.effective_user.id
        
        # Check if user is admin
        if not user_id or user_id not in settings.admin_user_ids:
            username = update.effective_user.username if update.effective_user else "Unknown"
            logger.warning(
                f"Unauthorized access attempt by user_id={user_id}, username={username}"
            )
            
            await update.effective_message.reply_text(
                "🚫 *Access Denied*\n\n"
                "This bot is restricted to authorized administrators only.\n"
                "If you believe this is an error, please contact the system administrator.",
                parse_mode="Markdown"
            )
            return
        
        # Log authorized access
        username = update.effective_user.username if update.effective_user else "Unknown"
        logger.info(
            f"Admin access: user_id={user_id}, username={username}, "
            f"command={update.effective_message.text if update.effective_message else 'N/A'}"
        )
        
        # Execute the original function
        return await func(update, context, *args, **kwargs)
    
    return wrapper


async def is_admin(user_id: int) -> bool:
    """
    Check if a user ID is an admin
    
    Args:
        user_id: Telegram user ID to check
    
    Returns:
        bool: True if user is admin, False otherwise
    """
    return user_id in settings.admin_user_ids


def get_user_info(update: Update) -> dict:
    """
    Extract user information from update
    
    Args:
        update: Telegram update object
    
    Returns:
        dict: User information including ID, username, first_name, last_name
    """
    if not update.effective_user:
        return {}
    
    user = update.effective_user
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": user.id in settings.admin_user_ids,
    }
