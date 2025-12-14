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
            from app.bot.handlers import start, products, orders, expenses, stock, analytics, menu
            from app.bot.handlers import products_interactive
            
            # Main menu and start commands
            self.application.add_handler(CommandHandler("start", start.start_command))
            self.application.add_handler(CommandHandler("menu", start.menu_command))
            
            # Product handlers (keep original commands for backward compatibility)
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
        data = query.data
        
        # Route to appropriate handler based on callback data prefix
        try:
            # Menu navigation
            if data.startswith("menu_"):
                from app.bot.handlers import menu
                await menu.handle_menu_callback(update, context)
            
            # Products
            elif data.startswith("products_") or data.startswith("product_"):
                from app.bot.handlers import products_interactive
                await products_interactive.handle_products_menu(update, context)
            
            # Orders
            elif data.startswith("order"):
                from app.bot.handlers import orders
                if hasattr(orders, 'handle_order_callback'):
                    await orders.handle_order_callback(update, context)
                else:
                    await query.answer("Orders interactive menu coming soon!")
            
            # Expenses  
            elif data.startswith("exp_"):
                from app.bot.handlers import expenses
                # Handle expense browser and menu
                if data.startswith("exp_page_") or data == "exp_close_browser":
                    await expenses.handle_expense_browser_callback(update, context)
                else:
                    await query.answer("Expense menu action processed")
            
            elif data.startswith("expense"):
                await query.answer("Expenses interactive menu coming soon!")
            
            # Stock
            elif data.startswith("stock"):
                from app.bot.handlers import stock
                if hasattr(stock, 'handle_stock_callback'):
                    await stock.handle_stock_callback(update, context)
                else:
                    await query.answer("Stock interactive menu coming soon!")
            
            # Analytics
            elif data.startswith("analytics_"):
                from app.bot.handlers import analytics
                # Direct call to analytics commands based on callback
                if data == "analytics_overall":
                    await analytics.stats_command(update, context)
                elif data == "analytics_orders":
                    await analytics.stats_orders_command(update, context)
                elif data == "analytics_expenses":
                    await analytics.stats_expenses_command(update, context)
                elif data == "analytics_products":
                    await analytics.stats_products_command(update, context)
                else:
                    await query.answer("Analytics menu action")
            
            # No-op (for pagination indicators)
            elif data == "noop":
                pass
            
            # Unknown callback
            else:
                await query.answer("Unknown action")
                logger.warning(f"Unhandled callback data: {data}")
        
        except Exception as e:
            logger.error(f"Error handling callback query: {e}", exc_info=True)
            await query.answer(f"Error: {str(e)}", show_alert=True)
    
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
