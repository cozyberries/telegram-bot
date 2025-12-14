"""Vercel serverless function for Telegram webhook"""

import json
import logging
import asyncio
import os
from http.server import BaseHTTPRequestHandler
from telegram import Update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for Telegram webhook"""
    
    def do_POST(self):
        """Handle POST requests from Telegram"""
        update_data = {}
        
        try:
            # Initialize Logfire on first request
            self._ensure_logfire_configured()
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            update_data = json.loads(body.decode('utf-8'))
            
            update_id = update_data.get('update_id')
            logger.info(f"📨 Received update: {update_id}")
            
            # Log to Logfire
            self._log_to_logfire("webhook_request_received", update_id=update_id)
            
            # Process update
            asyncio.run(self.process_telegram_update(update_data))
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            
            logger.info(f"✅ Successfully processed update {update_id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
            
            # Log error to Logfire
            self._log_error_to_logfire(e, update_data)
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    def _ensure_logfire_configured(self):
        """Ensure Logfire is configured (called on first request)"""
        try:
            from app.logging_config import configure_logfire, is_logfire_enabled
            
            if not is_logfire_enabled():
                result = configure_logfire()
                if result:
                    logger.info("✅ Logfire configured successfully")
                else:
                    logger.warning("⚠️ Logfire not configured (token missing?)")
        except Exception as e:
            logger.error(f"Failed to configure Logfire: {e}")
    
    def _log_to_logfire(self, event: str, **kwargs):
        """Log an event to Logfire"""
        try:
            from app.logging_config import log_event, is_logfire_enabled
            
            if is_logfire_enabled():
                log_event(event, **kwargs)
                logger.info(f"🔥 Logged to Logfire: {event}")
            else:
                logger.debug(f"Logfire disabled: {event}")
        except Exception as e:
            logger.error(f"Failed to log to Logfire: {e}")
    
    def _log_error_to_logfire(self, error: Exception, context: dict):
        """Log an error to Logfire"""
        try:
            from app.logging_config import log_error
            log_error(error, {"endpoint": "webhook", "context": context})
        except Exception as e:
            logger.error(f"Failed to log error to Logfire: {e}")
    
    async def process_telegram_update(self, update_data: dict):
        """Process Telegram update asynchronously"""
        span = None
        
        try:
            # Import here to avoid issues with module loading
            from app.bot.bot import bot
            from app.config import settings
            
            # Extract update info
            update_id = update_data.get('update_id')
            user_id = None
            command = None
            
            if 'message' in update_data:
                msg = update_data['message']
                user_id = msg.get('from', {}).get('id')
                command = msg.get('text', '').split()[0] if msg.get('text') else None
            
            logger.info(f"Processing update {update_id}: user={user_id}, command={command}")
            
            # Start Logfire span
            try:
                from app.logging_config import log_bot_update, is_logfire_enabled
                
                if is_logfire_enabled():
                    span = log_bot_update(update_id, user_id, command)
                    if span:
                        span.__enter__()
                        logger.info(f"🔥 Started Logfire span for update {update_id}")
            except Exception as e:
                logger.error(f"Failed to start Logfire span: {e}")
            
            # Initialize bot if not already initialized
            if not bot._initialized:
                logger.info("Initializing bot...")
                await asyncio.to_thread(bot.initialize)
                logger.info("Bot initialized")
            
            # CRITICAL: Initialize the Application for python-telegram-bot 21.9+
            if not bot.application._initialized:
                logger.info("Initializing Application...")
                await bot.application.initialize()
                logger.info("Application initialized")
            
            # Create Update object from JSON data
            update = Update.de_json(update_data, bot.application.bot)
            
            # Process the update
            await bot.application.process_update(update)
            
            logger.info(f"✅ Successfully processed update {update_id}")
            
            # Log success to Logfire
            try:
                from app.logging_config import log_event, is_logfire_enabled
                if is_logfire_enabled():
                    log_event("update_processed", update_id=update_id, status="success")
            except:
                pass
            
        except Exception as e:
            logger.error(f"❌ Error in process_telegram_update: {e}", exc_info=True)
            
            # Log error
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
                "bot": "CozyBerries Admin Bot",
                "webhook": "active",
                "logfire": logfire_status,
                "env": {
                    "LOGFIRE_TOKEN": "set" if os.getenv("LOGFIRE_TOKEN") else "not set"
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_response(500)
            self.end_headers()
