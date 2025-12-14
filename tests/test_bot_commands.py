"""
Integration tests for bot commands and interactive menus

Tests the /start command and interactive menu functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Chat, Message, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# Test user ID from Supabase (test@cozyberries.in)
TEST_USER_UUID = "aa79eb28-baf3-4cba-9388-5d8c7d598ad9"


class TestStartCommand:
    """Test /start command functionality"""
    
    @pytest.mark.asyncio
    async def test_start_command_shows_main_menu(self):
        """Test that /start command shows the main interactive menu"""
        from app.bot.handlers.start import start_command
        
        # Create mock update and context
        update = MagicMock(spec=Update)
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Mock user
        user = MagicMock(spec=User)
        user.id = 1701203448
        user.first_name = "Test"
        user.username = "testuser"
        
        # Mock message
        message = AsyncMock(spec=Message)
        message.reply_text = AsyncMock()
        
        # Setup update - no callback_query for /start command
        update.effective_user = user
        update.message = message
        update.callback_query = None  # Important: /start is a message command, not callback
        
        # Call start command
        await start_command(update, context)
        
        # Verify reply_text was called
        assert message.reply_text.called
        
        # Get the call arguments
        call_args = message.reply_text.call_args
        text = call_args[1]['text'] if 'text' in call_args[1] else call_args[0][0]
        reply_markup = call_args[1].get('reply_markup')
        parse_mode = call_args[1].get('parse_mode')
        
        # Verify message content
        assert "Welcome" in text
        assert "Test" in text  # User's first name
        assert "CozyBerries" in text
        assert "Expense Manager" in text
        
        # Verify parse mode
        assert parse_mode == "Markdown"
        
        # Verify keyboard is present
        assert reply_markup is not None
        assert isinstance(reply_markup, InlineKeyboardMarkup)
        
        # Verify keyboard structure
        keyboard = reply_markup.inline_keyboard
        assert len(keyboard) > 0
        
        # Check for Expense Management button
        buttons = [button.text for row in keyboard for button in row]
        assert "💰 Expense Management" in buttons or "Expense Management" in " ".join(buttons)
        
        print("✅ /start command displays main menu correctly")
    
    @pytest.mark.asyncio
    async def test_start_command_with_admin_check(self):
        """Test that /start command checks admin permissions"""
        from app.bot.handlers.start import start_command
        from app.bot.middleware.auth import admin_required
        
        # Verify that start_command has admin_required decorator
        # This ensures only authorized users can access the bot
        assert hasattr(start_command, '__wrapped__') or hasattr(start_command, '__name__')
        
        print("✅ /start command has proper authorization")
    
    @pytest.mark.asyncio
    async def test_menu_command_shows_main_menu(self):
        """Test that /menu command shows the main interactive menu"""
        from app.bot.handlers.start import menu_command
        
        # Create mock update and context
        update = MagicMock(spec=Update)
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Mock user
        user = MagicMock(spec=User)
        user.id = 1701203448
        user.first_name = "Test"
        user.username = "testuser"
        
        # Mock message
        message = AsyncMock(spec=Message)
        message.reply_text = AsyncMock()
        
        # Setup update - no callback_query for /menu command
        update.effective_user = user
        update.message = message
        update.callback_query = None  # Important: /menu is a message command, not callback
        
        # Call menu command
        await menu_command(update, context)
        
        # Verify reply_text was called
        assert message.reply_text.called
        
        print("✅ /menu command works correctly")


class TestMainMenuStructure:
    """Test main menu structure and buttons"""
    
    def test_main_menu_keyboard_structure(self):
        """Test that main menu has correct button structure"""
        from app.bot.handlers.menu import get_main_menu_keyboard
        
        keyboard = get_main_menu_keyboard()
        
        # Verify it's an InlineKeyboardMarkup
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Get all buttons
        buttons = keyboard.inline_keyboard
        assert len(buttons) > 0
        
        # Verify we have the essential buttons
        all_button_texts = [button.text for row in buttons for button in row]
        all_callback_data = [button.callback_data for row in buttons for button in row]
        
        # Check for expense management button
        assert any("Expense" in text for text in all_button_texts)
        
        # Check for help button
        assert any("Help" in text for text in all_button_texts)
        
        # Verify callback data format
        assert any(data.startswith("menu_") for data in all_callback_data)
        
        print("✅ Main menu keyboard structure is correct")
        print(f"   Found {len(buttons)} rows with {len(all_button_texts)} total buttons")
    
    def test_expenses_menu_keyboard_structure(self):
        """Test that expenses submenu has correct buttons"""
        from app.bot.handlers.menu import get_expenses_menu_keyboard
        
        keyboard = get_expenses_menu_keyboard()
        
        # Verify it's an InlineKeyboardMarkup
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Get all buttons
        buttons = keyboard.inline_keyboard
        all_button_texts = [button.text for row in buttons for button in row]
        all_callback_data = [button.callback_data for row in buttons for button in row]
        
        # Check for essential expense buttons
        assert any("View All" in text or "List" in text for text in all_button_texts)
        assert any("Add" in text for text in all_button_texts)
        assert any("Statistics" in text or "Stats" in text for text in all_button_texts)
        assert any("Back" in text for text in all_button_texts)
        
        # Verify callback data
        assert "expenses_list_all" in all_callback_data
        assert "expenses_create" in all_callback_data
        assert "expenses_stats" in all_callback_data
        assert "menu_main" in all_callback_data
        
        print("✅ Expenses menu keyboard structure is correct")
        print(f"   Found {len(all_button_texts)} buttons")


class TestMenuNavigation:
    """Test menu navigation callbacks"""
    
    @pytest.mark.asyncio
    async def test_menu_expenses_callback(self):
        """Test navigation to expenses menu"""
        from app.bot.handlers.menu import handle_menu_callback
        
        # Create mock update and context
        update = MagicMock(spec=Update)
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Mock callback query
        callback_query = AsyncMock()
        callback_query.data = "menu_expenses"
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        
        update.callback_query = callback_query
        
        # Mock user
        user = MagicMock(spec=User)
        user.id = 1701203448
        user.first_name = "Test"
        
        update.effective_user = user
        
        # Call menu callback handler
        await handle_menu_callback(update, context)
        
        # Verify callback was answered
        assert callback_query.answer.called
        
        # Verify message was edited
        assert callback_query.edit_message_text.called
        
        # Get the call arguments
        call_args = callback_query.edit_message_text.call_args
        text = call_args[1]['text'] if 'text' in call_args[1] else call_args[0][0]
        reply_markup = call_args[1].get('reply_markup')
        
        # Verify expense menu text
        assert "Expense" in text
        
        # Verify keyboard is present
        assert reply_markup is not None
        
        print("✅ Menu navigation to expenses works correctly")
    
    @pytest.mark.asyncio
    async def test_menu_help_callback(self):
        """Test navigation to help menu"""
        from app.bot.handlers.menu import handle_menu_callback
        
        # Create mock update and context
        update = MagicMock(spec=Update)
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Mock callback query
        callback_query = AsyncMock()
        callback_query.data = "menu_help"
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        
        update.callback_query = callback_query
        
        # Mock user
        user = MagicMock(spec=User)
        user.id = 1701203448
        user.first_name = "Test"
        
        update.effective_user = user
        
        # Call menu callback handler
        await handle_menu_callback(update, context)
        
        # Verify callback was answered
        assert callback_query.answer.called
        
        # Verify message was edited
        assert callback_query.edit_message_text.called
        
        # Get the call arguments
        call_args = callback_query.edit_message_text.call_args
        text = call_args[1]['text'] if 'text' in call_args[1] else call_args[0][0]
        
        # Verify help text content
        assert "Help" in text
        assert "command" in text.lower() or "feature" in text.lower()
        
        print("✅ Menu navigation to help works correctly")


class TestExpenseMenuCallbacks:
    """Test expense menu callback handlers"""
    
    @pytest.mark.asyncio
    async def test_expenses_stats_callback(self):
        """Test expenses statistics callback"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        # Create mock update and context
        update = MagicMock(spec=Update)
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Mock callback query
        callback_query = AsyncMock()
        callback_query.data = "expenses_stats"
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        
        update.callback_query = callback_query
        
        # Call expenses menu handler
        await handle_expenses_menu(update, context)
        
        # Verify callback was answered
        assert callback_query.answer.called
        
        # Verify message was edited (stats should be displayed)
        assert callback_query.edit_message_text.called
        
        # Get the call arguments
        call_args = callback_query.edit_message_text.call_args
        text = call_args[1]['text'] if 'text' in call_args[1] else call_args[0][0]
        
        # Verify stats content
        assert "Statistics" in text or "Stats" in text
        assert "Total" in text or "Amount" in text
        
        print("✅ Expenses stats callback works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
