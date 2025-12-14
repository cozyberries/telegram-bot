"""Logfire configuration for observability"""

import os
import logging
from typing import Optional

# Set logging to WARNING to reduce console noise
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Global flag to track if Logfire is configured
_logfire_configured = False
_logfire_available = False

# Try to import logfire
try:
    import logfire
    from logfire import LogfireSpan
    _logfire_available = True
except ImportError:
    _logfire_available = False


def configure_logfire() -> bool:
    """
    Configure Logfire for application observability (silent operation)
    
    Returns:
        bool: True if configured successfully, False otherwise
    """
    global _logfire_configured
    
    if _logfire_configured:
        return True
    
    if not _logfire_available:
        return False
    
    try:
        # Get configuration from environment
        logfire_token = os.getenv("LOGFIRE_TOKEN")
        
        if not logfire_token:
            return False
        
        project_name = os.getenv("LOGFIRE_PROJECT_NAME", "cozyberries-telegram-bot")
        
        # Configure Logfire with minimal settings for serverless (SILENT)
        logfire.configure(
            token=logfire_token,
            service_name=project_name,
            send_to_logfire=True,
            console=False,  # Don't log to console
        )
        
        _logfire_configured = True
        
        return True
        
    except Exception as e:
        logger.error(f"Logfire config failed: {e}")
        return False


def is_logfire_enabled() -> bool:
    """Check if Logfire is configured and available"""
    return _logfire_available and _logfire_configured


def log_bot_update(update_id: int, user_id: Optional[int] = None, command: Optional[str] = None):
    """
    Log a bot update with context (silent)
    
    Args:
        update_id: Telegram update ID
        user_id: User ID who sent the update
        command: Command being executed
    """
    if not is_logfire_enabled():
        return None
    
    try:
        return logfire.span(
            "telegram_update",
            update_id=update_id,
            user_id=user_id,
            command=command,
        )
    except:
        return None


def log_api_request(endpoint: str, method: str = "POST"):
    """Log an API request (silent)"""
    if not is_logfire_enabled():
        return None
    
    try:
        return logfire.span(
            "api_request",
            endpoint=endpoint,
            method=method,
        )
    except:
        return None


def log_database_operation(operation: str, table: str, record_id: Optional[str] = None):
    """Log a database operation (silent)"""
    if not is_logfire_enabled():
        return None
    
    try:
        return logfire.span(
            "database_operation",
            operation=operation,
            table=table,
            record_id=record_id,
        )
    except:
        return None


def log_error(error: Exception, context: Optional[dict] = None) -> None:
    """Log an error with context"""
    if not is_logfire_enabled():
        return
    
    try:
        logfire.error(
            "error_occurred",
            error=str(error),
            error_type=type(error).__name__,
            context=context or {},
        )
    except:
        pass


def log_metric(name: str, value: float, tags: Optional[dict] = None) -> None:
    """Log a metric (silent)"""
    if not is_logfire_enabled():
        return
    
    try:
        logfire.info(
            f"metric_{name}",
            value=value,
            **(tags or {}),
        )
    except:
        pass


def log_event(event_name: str, **kwargs) -> None:
    """Log a custom event (silent)"""
    if not is_logfire_enabled():
        return
    
    try:
        logfire.info(event_name, **kwargs)
    except:
        pass
