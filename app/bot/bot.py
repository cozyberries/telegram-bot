"""Telegram bot initialization and setup"""

import logging
from telegram import Update, BotCommand
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
                
                # Initialize the application
                loop.run_until_complete(self.application.initialize())
                logger.info("Application initialized for webhook mode")
            except Exception as e:
                logger.warning(f"Could not initialize application with event loop: {e}")
                # Try sync initialization as fallback
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
            from app.bot.handlers import start, products, orders, expenses, stock, analytics
            
            # Start command (merged with help)
            self.application.add_handler(CommandHandler("start", start.start_command))
            
            # Product handlers
            self.application.add_handler(CommandHandler("products", products.list_products_command))
            self.application.add_handler(CommandHandler("product", products.get_product_command))
            self.application.add_handler(products.add_product_conversation())
            self.application.add_handler(CommandHandler("update_product", products.update_product_command))
            self.application.add_handler(CommandHandler("delete_product", products.delete_product_command))
            self.application.add_handler(CommandHandler("product_stock", products.update_product_stock_command))
            
            # Order handlers
            self.application.add_handler(CommandHandler("orders", orders.list_orders_command))
            self.application.add_handler(CommandHandler("order", orders.get_order_command))
            self.application.add_handler(CommandHandler("order_status", orders.update_order_status_command))
            self.application.add_handler(orders.add_order_conversation())
            
            # Expense handlers
            self.application.add_handler(CommandHandler("expenses", expenses.list_expenses_command))
            self.application.add_handler(CommandHandler("expense", expenses.get_expense_command))
            self.application.add_handler(expenses.add_expense_conversation())
            self.application.add_handler(CommandHandler("delete_expense", expenses.delete_expense_command))
            
            # Stock handlers
            self.application.add_handler(CommandHandler("stock", stock.list_stock_command))
            self.application.add_handler(CommandHandler("low_stock", stock.low_stock_command))
            self.application.add_handler(CommandHandler("update_stock", stock.update_stock_command))
            
            # Analytics handlers
            self.application.add_handler(CommandHandler("stats", analytics.stats_command))
            self.application.add_handler(CommandHandler("stats_orders", analytics.stats_orders_command))
            self.application.add_handler(CommandHandler("stats_expenses", analytics.stats_expenses_command))
            self.application.add_handler(CommandHandler("stats_products", analytics.stats_products_command))
            
            # Callback query handler for inline buttons
            self.application.add_handler(CallbackQueryHandler(self._handle_callback_query))
            
            logger.info("All command handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering handlers: {e}", exc_info=True)
            raise
    
    async def _handle_callback_query(self, update: Update, context):
        """Handle callback queries from inline buttons"""
        query = update.callback_query
        await query.answer()
        
        # Route to appropriate handler based on callback data
        data = query.data
        
        if data.startswith("product_"):
            from app.bot.handlers import products
            await products.handle_product_callback(update, context)
        elif data.startswith("order_"):
            from app.bot.handlers import orders
            await orders.handle_order_callback(update, context)
        elif data.startswith("stock_"):
            from app.bot.handlers import stock
            await stock.handle_stock_callback(update, context)
        elif data.startswith("exp_page_") or data == "exp_close_browser":
            from app.bot.handlers import expenses
            await expenses.handle_expense_browser_callback(update, context)
        elif data.startswith("exp_"):
            # If we get here and it's not a browser command, 
            # implies the conversation state is lost/expired.
            await query.edit_message_text(
                "⚠️ This session has expired. Please start a new expense entry with /add_expense"
            )
        else:
            await query.edit_message_text("Unknown action")
    
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
