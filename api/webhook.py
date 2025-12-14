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
            
            logger.info(f"Received update: {update_data.get('update_id')}")
            logger.info(f"Update data: {json.dumps(update_data)}")
            
            # Process update
            asyncio.run(self.process_telegram_update(update_data))
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            
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
            
            # Initialize bot if not already initialized
            if not bot._initialized:
                await asyncio.to_thread(bot.initialize)
            
            # Create Update object from JSON data
            update = Update.de_json(update_data, bot.application.bot)
            
            # Process the update
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
