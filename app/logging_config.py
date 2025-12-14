"""Logfire configuration for observability"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global flag to track if Logfire is configured
_logfire_configured = False
_logfire_available = False

# Try to import logfire
try:
    import logfire
    from logfire import LogfireSpan
    _logfire_available = True
except ImportError:
    logger.warning("Logfire not installed - observability disabled")
    _logfire_available = False


def configure_logfire() -> bool:
    """
    Configure Logfire for application observability
    
    Returns:
        bool: True if configured successfully, False otherwise
    """
    global _logfire_configured
    
    if _logfire_configured:
        logger.info("Logfire already configured")
        return True
    
    if not _logfire_available:
        logger.warning("Logfire not available - skipping configuration")
        return False
    
    try:
        # Get configuration from environment
        logfire_token = os.getenv("LOGFIRE_TOKEN")
        
        if not logfire_token:
            logger.warning("⚠️ LOGFIRE_TOKEN not set - Logfire logging disabled")
            return False
        
        project_name = os.getenv("LOGFIRE_PROJECT_NAME", "cozyberries-telegram-bot")
        environment = os.getenv("LOGFIRE_ENVIRONMENT", "production")
        
        logger.info(f"🔥 Configuring Logfire: {project_name} ({environment})")
        logger.info(f"Token present: {logfire_token[:10]}...")
        
        # Configure Logfire with minimal settings for serverless
        logfire.configure(
            token=logfire_token,
            service_name=project_name,
            environment=environment,
            send_to_logfire=True,
            console=False,
        )
        
        # Test that it works
        logfire.info("logfire_initialized", message="Logfire configured successfully")
        
        _logfire_configured = True
        logger.info(f"✅ Logfire configured successfully: {project_name} ({environment})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to configure Logfire: {e}", exc_info=True)
        return False


def is_logfire_enabled() -> bool:
    """Check if Logfire is configured and available"""
    return _logfire_available and _logfire_configured


def log_bot_update(update_id: int, user_id: Optional[int] = None, command: Optional[str] = None):
    """
    Log a bot update with context
    
    Args:
        update_id: Telegram update ID
        user_id: User ID who sent the update
        command: Command being executed
    """
    if not is_logfire_enabled():
        logger.debug(f"Bot update (Logfire disabled): {update_id}, user={user_id}, cmd={command}")
        return None
    
    try:
        return logfire.span(
            "telegram_update",
            update_id=update_id,
            user_id=user_id,
            command=command,
        )
    except Exception as e:
        logger.error(f"Error logging bot update: {e}")
        return None


def log_api_request(endpoint: str, method: str = "POST"):
    """Log an API request"""
    if not is_logfire_enabled():
        return None
    
    try:
        return logfire.span(
            "api_request",
            endpoint=endpoint,
            method=method,
        )
    except Exception as e:
        logger.error(f"Error logging API request: {e}")
        return None


def log_database_operation(operation: str, table: str, record_id: Optional[str] = None):
    """Log a database operation"""
    if not is_logfire_enabled():
        return None
    
    try:
        return logfire.span(
            "database_operation",
            operation=operation,
            table=table,
            record_id=record_id,
        )
    except Exception as e:
        logger.error(f"Error logging database operation: {e}")
        return None


def log_error(error: Exception, context: Optional[dict] = None) -> None:
    """Log an error with context"""
    if not is_logfire_enabled():
        logger.error(f"Error (Logfire disabled): {error}", exc_info=True)
        return
    
    try:
        logfire.error(
            "error_occurred",
            error=str(error),
            error_type=type(error).__name__,
            context=context or {},
        )
    except Exception as e:
        logger.error(f"Error logging to Logfire: {e}")


def log_metric(name: str, value: float, tags: Optional[dict] = None) -> None:
    """Log a metric"""
    if not is_logfire_enabled():
        logger.info(f"Metric (Logfire disabled): {name}={value}")
        return
    
    try:
        logfire.info(
            f"metric_{name}",
            value=value,
            **(tags or {}),
        )
    except Exception as e:
        logger.error(f"Error logging metric: {e}")


def log_event(event_name: str, **kwargs) -> None:
    """Log a custom event"""
    if not is_logfire_enabled():
        logger.info(f"Event (Logfire disabled): {event_name} - {kwargs}")
        return
    
    try:
        logfire.info(event_name, **kwargs)
    except Exception as e:
        logger.error(f"Error logging event: {e}")
