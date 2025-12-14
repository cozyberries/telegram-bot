"""Vercel serverless function for Telegram webhook"""

import json
import logging
from http.server import BaseHTTPRequestHandler
from app.bot.bot import bot
from app.config import settings

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
            
            # Initialize bot if not already initialized
            if not bot._initialized:
                bot.initialize()
            
            # Process update asynchronously
            import asyncio
            asyncio.run(bot.process_update(update_data))
            
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
