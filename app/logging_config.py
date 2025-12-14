"""Logfire configuration for observability"""

import os
import logging
from typing import Optional
import logfire
from logfire import LogfireSpan

logger = logging.getLogger(__name__)


def configure_logfire() -> None:
    """
    Configure Logfire for application observability
    
    Environment variables:
    - LOGFIRE_TOKEN: Logfire API token (required for production)
    - LOGFIRE_PROJECT_NAME: Project name (optional, defaults to "telegram-bot")
    - LOGFIRE_ENVIRONMENT: Environment name (optional, defaults to "production")
    """
    try:
        # Get configuration from environment
        logfire_token = os.getenv("LOGFIRE_TOKEN")
        project_name = os.getenv("LOGFIRE_PROJECT_NAME", "cozyberries-telegram-bot")
        environment = os.getenv("LOGFIRE_ENVIRONMENT", "production")
        
        if not logfire_token:
            logger.warning("LOGFIRE_TOKEN not set - Logfire logging disabled")
            return
        
        # Configure Logfire
        logfire.configure(
            token=logfire_token,
            service_name=project_name,
            environment=environment,
            send_to_logfire=True,
            console=False,  # Don't duplicate to console
        )
        
        # Instrument libraries
        logfire.instrument_fastapi()  # If using FastAPI locally
        logfire.instrument_httpx()
        logfire.instrument_psycopg()  # For Supabase/Postgres
        
        logger.info(f"✅ Logfire configured: {project_name} ({environment})")
        
    except Exception as e:
        logger.error(f"Failed to configure Logfire: {e}", exc_info=True)


def log_bot_update(update_id: int, user_id: Optional[int] = None, command: Optional[str] = None) -> LogfireSpan:
    """
    Log a bot update with context
    
    Args:
        update_id: Telegram update ID
        user_id: User ID who sent the update
        command: Command being executed
        
    Returns:
        LogfireSpan: Span for additional logging
    """
    return logfire.span(
        "telegram_update",
        update_id=update_id,
        user_id=user_id,
        command=command,
    )


def log_api_request(endpoint: str, method: str = "POST") -> LogfireSpan:
    """
    Log an API request
    
    Args:
        endpoint: API endpoint being called
        method: HTTP method
        
    Returns:
        LogfireSpan: Span for additional logging
    """
    return logfire.span(
        "api_request",
        endpoint=endpoint,
        method=method,
    )


def log_database_operation(operation: str, table: str, record_id: Optional[str] = None) -> LogfireSpan:
    """
    Log a database operation
    
    Args:
        operation: Operation type (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        record_id: Record ID being operated on
        
    Returns:
        LogfireSpan: Span for additional logging
    """
    return logfire.span(
        "database_operation",
        operation=operation,
        table=table,
        record_id=record_id,
    )


def log_error(error: Exception, context: Optional[dict] = None) -> None:
    """
    Log an error with context
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    logfire.error(
        "error_occurred",
        error=str(error),
        error_type=type(error).__name__,
        context=context or {},
    )


def log_metric(name: str, value: float, tags: Optional[dict] = None) -> None:
    """
    Log a metric
    
    Args:
        name: Metric name
        value: Metric value
        tags: Additional tags
    """
    logfire.info(
        f"metric_{name}",
        value=value,
        **(tags or {}),
    )
