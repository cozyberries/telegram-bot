"""Vercel serverless function for Telegram webhook"""

import json
import logging
import asyncio
import os
from http.server import BaseHTTPRequestHandler
from telegram import Update

# Set logging to WARNING to reduce verbosity (only errors and warnings)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for Telegram webhook"""
    
    def do_POST(self):
        """Handle POST requests from Telegram"""
        update_data = {}
        
        try:
            # Initialize Logfire on first request (silent)
            self._ensure_logfire_configured()
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            update_data = json.loads(body.decode('utf-8'))
            
            # Log to Logfire (silent - Logfire handles it)
            self._log_to_logfire("webhook_request_received", update_id=update_data.get('update_id'))
            
            # Process update
            asyncio.run(self.process_telegram_update(update_data))
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
            
            # Log error to Logfire
            self._log_error_to_logfire(e, update_data)
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    def _ensure_logfire_configured(self):
        """Ensure Logfire is configured (silent)"""
        try:
            from app.logging_config import configure_logfire, is_logfire_enabled
            
            if not is_logfire_enabled():
                configure_logfire()  # Silent - no logging
        except Exception as e:
            logger.error(f"Logfire config failed: {e}")
    
    def _log_to_logfire(self, event: str, **kwargs):
        """Log an event to Logfire (silent)"""
        try:
            from app.logging_config import log_event, is_logfire_enabled
            
            if is_logfire_enabled():
                log_event(event, **kwargs)
        except:
            pass  # Silent failure
    
    def _log_error_to_logfire(self, error: Exception, context: dict):
        """Log an error to Logfire"""
        try:
            from app.logging_config import log_error
            log_error(error, {"endpoint": "webhook", "context": context})
        except:
            pass  # Silent failure
    
    async def process_telegram_update(self, update_data: dict):
        """Process Telegram update asynchronously"""
        span = None
        
        try:
            # Import here to avoid issues with module loading
            from app.bot.bot import bot
            
            # Extract update info for Logfire and logging
            update_id = update_data.get('update_id')
            user_id = None
            username = None
            command = None
            message_type = None
            
            if 'message' in update_data:
                msg = update_data['message']
                user_id = msg.get('from', {}).get('id')
                username = msg.get('from', {}).get('username', 'unknown')
                text = msg.get('text', '')
                command = text.split()[0] if text else None
                message_type = 'command' if command and command.startswith('/') else 'message'
            elif 'callback_query' in update_data:
                callback = update_data['callback_query']
                user_id = callback.get('from', {}).get('id')
                username = callback.get('from', {}).get('username', 'unknown')
                command = callback.get('data', 'callback')
                message_type = 'callback'
            
            # Log command execution
            if command:
                logger.warning(f"📨 Webhook [{message_type}]: {command} from @{username} (user_id: {user_id}, update: {update_id})")
            else:
                logger.warning(f"📨 Webhook [unknown]: update {update_id} from user {user_id}")
            
            # Start Logfire span (silent)
            try:
                from app.logging_config import log_bot_update, is_logfire_enabled
                
                if is_logfire_enabled():
                    span = log_bot_update(update_id, user_id, command)
                    if span:
                        span.__enter__()
            except:
                pass  # Silent failure
            
            # Process the update using the bot instance which manages the application lifecycle
            await bot.process_update(update_data)
            
            # Log success to Logfire (silent)
            try:
                from app.logging_config import log_event, is_logfire_enabled
                if is_logfire_enabled():
                    log_event("update_processed", update_id=update_id, status="success")
            except:
                pass
            
        except Exception as e:
            logger.error(f"❌ Update processing error: {e}")
            
            # Log error to Logfire
            try:
                from app.logging_config import log_event, is_logfire_enabled
                if is_logfire_enabled():
                    log_event("update_processed", update_id=update_id, status="error", error=str(e))
            except:
                pass
            
            raise
        finally:
            # Close Logfire span
            if span:
                try:
                    span.__exit__(None, None, None)
                except:
                    pass
    
    def do_GET(self):
        """Handle GET requests - return bot info"""
        try:
            # Check Logfire status
            logfire_status = "disabled"
            try:
                from app.logging_config import is_logfire_enabled
                logfire_status = "enabled" if is_logfire_enabled() else "disabled"
            except:
                pass
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "ok",
                "bot": "CozyBerries Assistant",
                "webhook": "active",
                "logfire": logfire_status,
                "env": {
                    "LOGFIRE_TOKEN": "set" if os.getenv("LOGFIRE_TOKEN") else "not set"
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"GET request error: {e}")
            self.send_response(500)
            self.end_headers()
