"""FastAPI application for CozyBerries Telegram Bot"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
from typing import Dict, Any

from app.config import settings
from app.bot.bot import bot
from app.services.notification_service import send_order_notification
from app.database.models import Order

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CozyBerries Telegram Admin Bot",
    description="""
    Telegram bot for managing CozyBerries admin operations.
    
    ## Features
    
    * **Products Management**: CRUD operations for products
    * **Orders Management**: View and update orders
    * **Expenses Management**: Track and approve expenses
    * **Stock Management**: Monitor and update inventory
    * **Analytics**: Business statistics and reports
    * **Notifications**: Real-time order notifications
    
    ## Authentication
    
    Admin-only access via Telegram user ID verification.
    
    ## Endpoints
    
    * `/webhook` - Telegram webhook for bot updates
    * `/notify-order` - Supabase webhook for order notifications
    * `/health` - Health check endpoint
    * `/bot-info` - Bot configuration and status
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "CozyBerries",
        "url": "https://cozyberries.in",
    },
    license_info={
        "name": "MIT",
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize bot on startup"""
    try:
        logger.info("Starting CozyBerries Telegram Bot...")
        if not bot._initialized:
            await bot.initialize()
        logger.info("Bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down CozyBerries Telegram Bot...")
    try:
        await bot.stop()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get(
    "/",
    tags=["General"],
    summary="Root endpoint",
    description="Returns basic API information"
)
async def root():
    """Root endpoint"""
    return {
        "message": "CozyBerries Telegram Admin Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the service is running and healthy",
    response_description="Health status information"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "CozyBerries Telegram Bot",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "bot_initialized": bot._initialized
    }


@app.get(
    "/bot-info",
    tags=["Bot"],
    summary="Get bot information",
    description="Returns bot configuration and status (sensitive data masked)"
)
async def bot_info():
    """Get bot information"""
    return {
        "status": "active",
        "bot_name": "CozyBerries Admin Bot",
        "webhook": "configured",
        "initialized": bot._initialized,
        "admin_users_count": len(settings.admin_user_ids),
        "features": [
            "Products Management",
            "Orders Management",
            "Expenses Management",
            "Stock Management",
            "Analytics",
            "Notifications"
        ]
    }


@app.post(
    "/webhook",
    tags=["Telegram"],
    summary="Telegram webhook",
    description="Receives updates from Telegram Bot API",
    response_description="Processing status"
)
async def telegram_webhook(request: Request):
    """
    Process Telegram webhook updates.
    
    This endpoint receives updates from Telegram when users interact with the bot.
    Updates include messages, commands, callback queries, etc.
    """
    try:
        # Parse update data
        update_data = await request.json()
        update_id = update_data.get('update_id', 'unknown')
        
        logger.info(f"Received Telegram update: {update_id}")
        
        # Initialize bot if needed
        if not bot._initialized:
            await bot.initialize()
        
        # Process update
        await bot.process_update(update_data)
        
        return {"ok": True, "update_id": update_id}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process update: {str(e)}"
        )


@app.get(
    "/webhook",
    tags=["Telegram"],
    summary="Webhook info",
    description="Get webhook endpoint information"
)
async def webhook_info():
    """Get webhook information"""
    return {
        "status": "active",
        "endpoint": "/webhook",
        "bot": "CozyBerries Admin Bot",
        "description": "Telegram webhook for receiving bot updates"
    }


@app.post(
    "/notify-order",
    tags=["Notifications"],
    summary="Order notification webhook",
    description="Receives order notifications from Supabase webhook",
    response_description="Notification status"
)
async def notify_order(request: Request):
    """
    Process order notification from Supabase webhook.
    
    This endpoint receives new order data from Supabase and sends
    notifications to admin users via Telegram.
    
    **Expected payload formats:**
    - `{"record": {...}}` - Supabase webhook format
    - `{"data": {...}}` - Alternative format
    - Direct order object
    """
    try:
        # Parse request data
        data = await request.json()
        
        logger.info("Received order notification request")
        
        # Extract order data (support multiple formats)
        order_data = data.get('record') or data.get('data') or data
        
        if not order_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No order data found in request"
            )
        
        # Validate and create Order object
        try:
            order = Order(**order_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid order data: {str(e)}"
            )
        
        # Send notification
        await send_order_notification(order)
        
        return {
            "ok": True,
            "message": "Notification sent successfully",
            "order_id": order.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending notification: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )


@app.get(
    "/notify-order",
    tags=["Notifications"],
    summary="Notification endpoint info",
    description="Get notification endpoint information"
)
async def notify_order_info():
    """Get notification endpoint information"""
    return {
        "status": "active",
        "endpoint": "/notify-order",
        "description": "Receives order notifications from Supabase webhook",
        "method": "POST",
        "expected_payload": {
            "record": "Order data object",
            "or": "Direct order object"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.log_level.upper() == "DEBUG" else "An error occurred"
        }
    )


# For Vercel serverless compatibility
handler = app
