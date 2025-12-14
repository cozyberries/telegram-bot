"""AWS Lambda handler for the Telegram bot

This handler is specifically designed for AWS Lambda/serverless environments
where the event loop lifecycle needs to be carefully managed.
"""

import json
import asyncio
import logging
from typing import Dict, Any
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global application instance (reused across invocations)
_app = None
_bot_instance = None


def get_or_create_app():
    """Get or create the FastAPI application instance"""
    global _app
    if _app is None:
        from app.main import app
        _app = app
        logger.info("✅ Created new FastAPI app instance")
    return _app


def get_or_create_bot():
    """Get or create the bot instance with proper initialization"""
    global _bot_instance
    
    if _bot_instance is None:
        from app.bot.bot import TelegramBot
        _bot_instance = TelegramBot()
        
        # Initialize bot if we have a token
        if os.getenv("TELEGRAM_BOT_TOKEN"):
            try:
                _bot_instance.initialize()
                logger.info("✅ Bot initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize bot: {e}")
                # Don't raise - we'll try again on next invocation
        else:
            logger.warning("⚠️  TELEGRAM_BOT_TOKEN not set")
    
    return _bot_instance


async def process_telegram_webhook_async(update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Telegram webhook update asynchronously
    
    Args:
        update_data: Update data from Telegram
        
    Returns:
        Response dict
    """
    try:
        bot = get_or_create_bot()
        
        # Ensure bot is initialized
        if not bot._initialized:
            if not os.getenv("TELEGRAM_BOT_TOKEN"):
                return {
                    'statusCode': 503,
                    'body': json.dumps({
                        'ok': False,
                        'error': 'Bot not configured - TELEGRAM_BOT_TOKEN missing'
                    })
                }
            bot.initialize()
        
        # Ensure the application is initialized for webhook mode
        if bot.application and not bot.application.running:
            try:
                await bot.application.initialize()
                logger.info("✅ Application initialized for webhook processing")
            except Exception as e:
                logger.warning(f"Application already initialized or initialization not needed: {e}")
        
        update_id = update_data.get('update_id', 'unknown')
        logger.info(f"📨 Processing update: {update_id}")
        
        # Process the update
        await bot.process_update(update_data)
        
        logger.info(f"✅ Update {update_id} processed successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'ok': True,
                'update_id': update_id
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'ok': False,
                'error': str(e),
                'type': type(e).__name__
            })
        }


def process_telegram_webhook(update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Telegram webhook with proper event loop management for Lambda
    
    This function creates a fresh event loop for each invocation to avoid
    'Event loop is closed' errors in AWS Lambda.
    
    Args:
        update_data: Update data from Telegram
        
    Returns:
        Response dict
    """
    try:
        # Get the current event loop or create a new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Loop is closed")
        except RuntimeError:
            # Create a new event loop if the current one is closed
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info("🔄 Created new event loop for Lambda invocation")
        
        # Run the async function
        result = loop.run_until_complete(process_telegram_webhook_async(update_data))
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Fatal error in webhook processing: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'ok': False,
                'error': f'Fatal error: {str(e)}',
                'type': type(e).__name__
            })
        }
    finally:
        # DON'T close the loop - let Lambda manage it
        # This prevents the "Event loop is closed" error
        pass


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event data
        context: Lambda context
        
    Returns:
        API Gateway response dict
    """
    try:
        logger.info(f"🚀 Lambda invocation - request ID: {context.request_id if context else 'unknown'}")
        logger.info(f"📋 Event: {json.dumps(event)[:200]}...")
        
        # Extract the HTTP method and path
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'POST'))
        path = event.get('path', event.get('rawPath', '/'))
        
        logger.info(f"🔍 Method: {http_method}, Path: {path}")
        
        # Handle different endpoints
        if path == '/webhook' and http_method == 'POST':
            # Parse the body
            try:
                if isinstance(event.get('body'), str):
                    body = json.loads(event['body'])
                else:
                    body = event.get('body', {})
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in body: {e}")
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'ok': False,
                        'error': 'Invalid JSON in request body'
                    })
                }
            
            # Process Telegram webhook
            return process_telegram_webhook(body)
        
        elif path == '/webhook' and http_method == 'GET':
            # Webhook info
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'active',
                    'endpoint': '/webhook',
                    'bot': 'CozyBerries Admin Bot',
                    'configured': bool(os.getenv('TELEGRAM_BOT_TOKEN'))
                })
            }
        
        elif path == '/health' or path == '/':
            # Health check
            bot_initialized = False
            if _bot_instance:
                bot_initialized = _bot_instance._initialized
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'ok',
                    'service': 'CozyBerries Telegram Bot',
                    'bot_initialized': bot_initialized,
                    'env_configured': bool(os.getenv('TELEGRAM_BOT_TOKEN'))
                })
            }
        
        else:
            # Unknown endpoint
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'ok': False,
                    'error': f'Endpoint not found: {http_method} {path}'
                })
            }
    
    except Exception as e:
        logger.error(f"❌ Lambda handler error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'ok': False,
                'error': str(e),
                'type': type(e).__name__
            })
        }


# For local testing
if __name__ == '__main__':
    # Test event
    test_event = {
        'httpMethod': 'POST',
        'path': '/webhook',
        'body': json.dumps({
            'update_id': 123456,
            'message': {
                'message_id': 1,
                'from': {'id': 123456789, 'first_name': 'Test'},
                'chat': {'id': 123456789, 'type': 'private'},
                'text': '/start',
                'date': 1234567890
            }
        })
    }
    
    class MockContext:
        request_id = 'test-request-id'
    
    result = lambda_handler(test_event, MockContext())
    print(f"Result: {json.dumps(result, indent=2)}")
