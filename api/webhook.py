"""Vercel serverless function for Telegram webhook"""

import json
import logging
import asyncio
from http.server import BaseHTTPRequestHandler
from telegram import Update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for Telegram webhook"""
    
    def do_POST(self):
        """Handle POST requests from Telegram"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            update_data = json.loads(body.decode('utf-8'))
            
            update_id = update_data.get('update_id')
            logger.info(f"Received update: {update_id}")
            
            # Process update
            asyncio.run(self.process_telegram_update(update_data))
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            
            # Log error to Logfire
            try:
                from app.logging_config import log_error
                log_error(e, {"endpoint": "webhook", "update_data": update_data})
            except:
                pass
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    async def process_telegram_update(self, update_data: dict):
        """Process Telegram update asynchronously"""
        try:
            # Import here to avoid issues with module loading
            from app.bot.bot import bot
            from app.config import settings
            
            # Initialize Logfire if not already done
            try:
                from app.logging_config import configure_logfire, log_bot_update
                configure_logfire()
                
                # Log update with context
                update_id = update_data.get('update_id')
                user_id = None
                command = None
                
                # Extract user and command info
                if 'message' in update_data:
                    msg = update_data['message']
                    user_id = msg.get('from', {}).get('id')
                    command = msg.get('text', '').split()[0] if msg.get('text') else None
                
                with log_bot_update(update_id, user_id, command):
                    # Initialize bot if not already initialized
                    if not bot._initialized:
                        await asyncio.to_thread(bot.initialize)
                    
                    # Create Update object from JSON data
                    update = Update.de_json(update_data, bot.application.bot)
                    
                    # Process the update
                    await bot.application.process_update(update)
                    
                    logger.info(f"Successfully processed update {update_id}")
                    
            except ImportError:
                # Logfire not configured, fall back to regular processing
                if not bot._initialized:
                    await asyncio.to_thread(bot.initialize)
                
                update = Update.de_json(update_data, bot.application.bot)
                await bot.application.process_update(update)
                
                logger.info(f"Successfully processed update {update_data.get('update_id')}")
            
        except Exception as e:
            logger.error(f"Error in process_telegram_update: {e}", exc_info=True)
            raise
    
    def do_GET(self):
        """Handle GET requests - return bot info"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "ok",
                "bot": "CozyBerries Admin Bot",
                "webhook": "active"
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_response(500)
            self.end_headers()
