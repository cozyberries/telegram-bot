"""Telegram bot initialization and setup"""

import logging
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from app.config import settings

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot manager"""
    
    def __init__(self):
        """Initialize the bot wrapper"""
        # We do not store self.application permanently effectively in serverless
        # because the loop changes. We will create it on demand.
        self._global_application = None 
    
    async def get_application(self) -> Application:
        """
        Create and initialize a fresh bot application for the current event loop.
        This is critical for Vercel/Serverless where asyncio.run() creates a new loop per request.
        """
        try:
            logger.info(f"Creating new bot application with token: {settings.telegram_bot_token[:10]}...")
            
            # Create application
            application = (
                Application.builder()
                .token(settings.telegram_bot_token)
                .build()
            )
            
            # Register handlers
            self._register_handlers(application)
            
            # Register error handler
            application.add_error_handler(self._error_handler)
            
            # Initialize the application (sets up http client on current loop)
            await application.initialize()
            logger.info("Bot application initialized successfully for current request")
            
            return application
            
        except Exception as e:
            logger.error(f"Failed to create and initialize bot application: {e}", exc_info=True)
            raise
    
    @property
    def _initialized(self):
        """Compatibility property for checking if a global app is initialized"""
        return self._global_application is not None

    def stop(self):
        """Stop the bot and cleanup resources"""
        try:
            if self._global_application:
                logger.info("Stopping global bot application...")
                # We can't really await here in sync method, but normally stop is called at shutdown
                # If we are in async context, we should await application.shutdown()
                # But since we store it in _global_application, strict cleanup might be needed if running persistently
                self._global_application = None
                logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    def _register_handlers(self, application: Application):
        """Register all command and callback handlers"""
        try:
            from app.bot.handlers import start, expenses, menu
            
            # Main menu and start commands
            application.add_handler(CommandHandler("start", start.start_command))
            application.add_handler(CommandHandler("menu", start.menu_command))
            
            # Expense handlers
            application.add_handler(CommandHandler("expenses", expenses.list_expenses_command))
            application.add_handler(CommandHandler("expense", expenses.get_expense_command))
            application.add_handler(expenses.add_expense_conversation())
            application.add_handler(CommandHandler("delete_expense", expenses.delete_expense_command))
            
            # Stats command for expenses
            from app.services import expense_service
            
            async def stats_command_wrapper(update, context):
                """Show expense statistics"""
                try:
                    stats = expense_service.get_expense_stats()
                    message = stats.to_telegram_message()
                    await update.message.reply_text(message, parse_mode="Markdown")
                except Exception as e:
                    await update.message.reply_text(f"Error fetching statistics: {str(e)}")
            
            application.add_handler(CommandHandler("stats", stats_command_wrapper))
            
            # Callback query handler for inline buttons
            application.add_handler(CallbackQueryHandler(self._handle_callback_query))
            
            logger.info("All command handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering handlers: {e}", exc_info=True)
            raise
    
    async def _handle_callback_query(self, update: Update, context):
        """Handle callback queries from inline buttons"""
        query = update.callback_query
        data = query.data
        
        # Route to appropriate handler based on callback data prefix
        try:
            # Answer callback query early to prevent timeout
            try:
                await query.answer()
            except Exception as e:
                logger.warning(f"Failed to answer callback query early: {e}")
            
            # Menu navigation
            if data.startswith("menu_"):
                from app.bot.handlers import menu
                await menu.handle_menu_callback(update, context)
            
            # Expenses  
            elif data.startswith("exp_"):
                from app.bot.handlers import expenses
                # Handle expense browser and menu
                if data.startswith("exp_page_") or data == "exp_close_browser":
                    await expenses.handle_expense_browser_callback(update, context)
                else:
                    # Handle expense conversation menu callbacks
                    pass  # Already answered above
            
            elif data.startswith("expenses_") or data == "start_add_expense":
                # Handle expenses interactive menu
                from app.bot.handlers.expenses_menu import handle_expenses_menu
                await handle_expenses_menu(update, context)
            
            # No-op (for pagination indicators)
            elif data == "noop":
                pass  # Already answered above
            
            # Unknown callback
            else:
                logger.warning(f"Unhandled callback data: {data}")
        
        except Exception as e:
            logger.error(f"Error handling callback query: {e}", exc_info=True)
            try:
                await query.answer(f"Error: {str(e)}", show_alert=True)
            except Exception:
                pass  # Ignore if we can't send error
    
    async def _error_handler(self, update: Update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}", exc_info=True)
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "⚠️ An error occurred while processing your request. "
                    "Please try again or contact support."
                )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    async def set_bot_commands(self):
        """Set bot commands for Telegram UI"""
        # This method should ideally be called once at deployment or startup,
        # not per request, as it sets global bot commands.
        # It will use a temporary application instance if self._global_application is not set.
        application = self._global_application
        if not application:
            # Create a temporary application just to set commands
            logger.info("Creating temporary application to set bot commands...")
            application = (
                Application.builder()
                .token(settings.telegram_bot_token)
                .build()
            )
            await application.initialize()
            self._global_application = application # Store for potential reuse if not serverless
            
        commands = [
            BotCommand("start", "Show all available commands"),
            BotCommand("products", "List all products"),
            BotCommand("product", "Get product details"),
            BotCommand("add_product", "Add a new product"),
            BotCommand("orders", "List recent orders"),
            BotCommand("order", "Get order details"),
            BotCommand("order_status", "Update order status"),
            BotCommand("expenses", "List expenses"),
            BotCommand("expense", "Get expense details"),
            BotCommand("add_expense", "Add a new expense"),
            BotCommand("stock", "View stock levels"),
            BotCommand("low_stock", "View low stock products"),
            BotCommand("stats", "View overall statistics"),
        ]
        
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")
        
        # If this was a temporary application, shut it down
        if not self._global_application: # If it wasn't stored, it was temporary
            await application.shutdown()
    
    async def process_update(self, update_data: dict):
        """
        Process an update from Telegram webhook
        
        Args:
            update_data: Update data from Telegram
        """
        try:
            # For each update, get a fresh application on the current loop
            application = await self.get_application()
            
            logger.info(f"Processing update: {update_data.get('update_id')}")
            
            # Create Update object from JSON
            update = Update.de_json(update_data, application.bot)
            
            # Process the update through the application
            await application.process_update(update)
            
            logger.info(f"Update {update_data.get('update_id')} processed successfully")
            
            # Cleanup
            await application.shutdown()
            
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            raise


# Global bot instance
bot = TelegramBot()
