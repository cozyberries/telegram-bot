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
        """Initialize the bot application"""
        self.application = None
        self._initialized = False
    
    def initialize(self) -> Application:
        """
        Initialize and configure the bot application
        
        Returns:
            Application: Configured bot application
        """
        if self._initialized and self.application:
            return self.application
        
        try:
            logger.info(f"Initializing bot with token: {settings.telegram_bot_token[:10]}...")
            
            # Create application
            self.application = (
                Application.builder()
                .token(settings.telegram_bot_token)
                .build()
            )
            
            # Initialize the application for webhook mode
            # This is required for processing updates without polling
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Check if event loop is already running
                if not loop.is_running():
                    # Initialize the application
                    loop.run_until_complete(self.application.initialize())
                    logger.info("Application initialized for webhook mode")
                else:
                    # For testing: create a new task to initialize
                    logger.info("Event loop already running, scheduling async initialization")
                    # We'll initialize later when processing first update
            except Exception as e:
                logger.warning(f"Could not initialize application with event loop: {e}")
                # Application will be initialized on first update
                pass
            
            # Register handlers
            self._register_handlers()
            
            # Register error handler
            self.application.add_error_handler(self._error_handler)
            
            self._initialized = True
            logger.info("Bot application initialized successfully")
            
            return self.application
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            raise
    
    def _register_handlers(self):
        """Register all command and callback handlers"""
        try:
            from app.bot.handlers import start, expenses, menu
            
            # Main menu and start commands
            self.application.add_handler(CommandHandler("start", start.start_command))
            self.application.add_handler(CommandHandler("menu", start.menu_command))
            
            # Expense handlers
            self.application.add_handler(CommandHandler("expenses", expenses.list_expenses_command))
            self.application.add_handler(CommandHandler("expense", expenses.get_expense_command))
            self.application.add_handler(expenses.add_expense_conversation())
            self.application.add_handler(CommandHandler("delete_expense", expenses.delete_expense_command))
            
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
            
            self.application.add_handler(CommandHandler("stats", stats_command_wrapper))
            
            # Callback query handler for inline buttons
            self.application.add_handler(CallbackQueryHandler(self._handle_callback_query))
            
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
            
            elif data.startswith("expenses_"):
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
        
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")
    
    async def process_update(self, update_data: dict):
        """
        Process an update from Telegram webhook
        
        Args:
            update_data: Update data from Telegram
        """
        try:
            if not self._initialized:
                self.initialize()
            
            # Ensure application is initialized for async context
            if not self.application._initialized:
                await self.application.initialize()
            
            logger.info(f"Processing update: {update_data.get('update_id')}")
            
            # Create Update object from JSON
            update = Update.de_json(update_data, self.application.bot)
            
            # Process the update through the application
            await self.application.process_update(update)
            
            logger.info(f"Update {update_data.get('update_id')} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            raise
    
    def stop(self):
        """Stop the bot and cleanup resources"""
        try:
            if self._initialized and self.application:
                logger.info("Stopping bot application...")
                # Don't call shutdown in Lambda - let the container handle it
                self._initialized = False
                logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")


# Global bot instance
bot = TelegramBot()
