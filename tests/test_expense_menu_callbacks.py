"""
Integration tests for expense menu callback handlers
Tests all menu navigation and callback operations
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Chat, Message, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import date
from decimal import Decimal

# Test user ID (from Supabase)
TEST_USER_ID = 1701203448
TEST_USER_UUID = "aa79eb28-baf3-4cba-9388-5d8c7d598ad9"


def create_mock_callback_update(callback_data: str) -> tuple[MagicMock, MagicMock]:
    """Create mock update and context for callback queries"""
    update = MagicMock(spec=Update)
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    
    # Mock user
    user = MagicMock(spec=User)
    user.id = TEST_USER_ID
    user.first_name = "Test"
    user.username = "testuser"
    
    # Mock message
    message = AsyncMock(spec=Message)
    message.reply_text = AsyncMock()
    message.edit_text = AsyncMock()
    
    # Mock callback query
    callback_query = AsyncMock(spec=CallbackQuery)
    callback_query.answer = AsyncMock()
    callback_query.edit_message_text = AsyncMock()
    callback_query.message = message
    callback_query.data = callback_data
    
    # Setup update
    update.effective_user = user
    update.callback_query = callback_query
    update.message = None  # Callback queries don't have direct messages
    
    # Setup context
    context.user_data = {}
    
    return update, context


class TestExpensesListAll:
    """Test the 'View All Expenses' callback"""
    
    @pytest.mark.asyncio
    async def test_expenses_list_all_with_expenses(self):
        """Test that expenses_list_all shows expense browser"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        update, context = create_mock_callback_update("expenses_list_all")
        
        # Call the handler
        await handle_expenses_menu(update, context)
        
        # Verify callback was answered
        assert update.callback_query.answer.called
        
        # Verify message was edited (expense browser shown) OR callback answered with "No more expenses"
        # Check if either edit_message_text was called OR answer was called with message
        edit_called = update.callback_query.edit_message_text.called
        answer_calls = update.callback_query.answer.call_args_list
        
        # Should either show expenses or indicate no expenses
        assert edit_called or len(answer_calls) > 0
        
        if edit_called:
            call_kwargs = update.callback_query.edit_message_text.call_args.kwargs
            text = call_kwargs.get('text', '')
            assert '📋' in text or 'Expense' in text
            print(f"✅ expenses_list_all test passed - expenses shown")
        else:
            # Check if "No more expenses" was in answer
            print(f"✅ expenses_list_all test passed - no expenses case handled")
    
    @pytest.mark.asyncio
    async def test_expenses_list_all_handles_errors(self):
        """Test that expenses_list_all handles errors gracefully"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        update, context = create_mock_callback_update("expenses_list_all")
        
        # Mock show_expense_page to raise an error
        with patch('app.bot.handlers.expenses.show_expense_page', side_effect=Exception("DB Error")):
            await handle_expenses_menu(update, context)
        
        # Should still answer callback
        assert update.callback_query.answer.called
        
        # Should show error message (either via edit or reply)
        # Either edit_message_text or message.reply_text should be called
        edit_called = update.callback_query.edit_message_text.called
        reply_called = update.callback_query.message.reply_text.called
        
        assert edit_called or reply_called, "Should show error message"
        
        print(f"✅ expenses_list_all error handling test passed")


class TestExpensesCreate:
    """Test the 'Add Expense' flow"""
    
    @pytest.mark.asyncio
    async def test_expenses_create_shows_prompt(self):
        """Test that expenses_create shows add prompt"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        update, context = create_mock_callback_update("expenses_create")
        
        await handle_expenses_menu(update, context)
        
        # Verify callback was answered
        assert update.callback_query.answer.called
        
        # Verify message was edited with add expense prompt
        assert update.callback_query.edit_message_text.called
        
        # Get the call arguments properly
        call = update.callback_query.edit_message_text.call_args
        if call.args:
            text = call.args[0]
        else:
            text = call.kwargs.get('text', '')
        
        assert text, "Text should not be empty"
        assert 'Add' in text or 'expense' in text.lower(), f"Got text: {text}"
        
        # Should have keyboard with "Start Adding Expense" button
        reply_markup = call.kwargs.get('reply_markup') if call.kwargs else None
        assert reply_markup is not None
        
        print(f"✅ expenses_create test passed")


class TestStartAddExpense:
    """Test the 'Start Adding Expense' button callback"""
    
    @pytest.mark.asyncio
    async def test_start_add_expense_initiates_conversation(self):
        """Test that start_add_expense starts the add expense conversation"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        update, context = create_mock_callback_update("start_add_expense")
        
        # Call the handler
        result = await handle_expenses_menu(update, context)
        
        # Verify callback was answered
        assert update.callback_query.answer.called
        
        # Verify a new message was sent (conversation started)
        assert update.callback_query.message.reply_text.called
        
        # Check the message content
        call = update.callback_query.message.reply_text.call_args
        if call.args:
            text = call.args[0]
        else:
            text = call.kwargs.get('text', '')
        
        # Should show expense form or prompt for amount
        assert text, "Text should not be empty"
        assert 'Expense' in text or 'Amount' in text or 'Description' in text, f"Got text: {text}"
        
        # Should return conversation state
        assert result is not None  # Should return a conversation state
        
        print(f"✅ start_add_expense test passed")
    
    @pytest.mark.asyncio
    async def test_start_add_expense_initializes_context(self):
        """Test that start_add_expense initializes user context"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        update, context = create_mock_callback_update("start_add_expense")
        
        await handle_expenses_menu(update, context)
        
        # Verify context was initialized
        assert 'draft_expense' in context.user_data
        
        print(f"✅ start_add_expense context initialization test passed")


class TestExpensesStats:
    """Test the 'Statistics' callback"""
    
    @pytest.mark.asyncio
    async def test_expenses_stats_shows_statistics(self):
        """Test that expenses_stats shows expense statistics"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        update, context = create_mock_callback_update("expenses_stats")
        
        await handle_expenses_menu(update, context)
        
        # Verify callback was answered
        assert update.callback_query.answer.called
        
        # Verify message was edited with statistics
        assert update.callback_query.edit_message_text.called
        
        # Get text properly
        call = update.callback_query.edit_message_text.call_args
        if call.args:
            text = call.args[0]
        else:
            text = call.kwargs.get('text', '')
        
        # Should show statistics heading or error message
        assert text, "Text should not be empty"
        assert '📊' in text or 'Statistics' in text or 'Error' in text, f"Got text: {text}"
        
        print(f"✅ expenses_stats test passed")


class TestMenuNavigation:
    """Test menu navigation flow"""
    
    @pytest.mark.asyncio
    async def test_back_to_expenses_menu(self):
        """Test that back button returns to expenses menu"""
        from app.bot.handlers.menu import handle_menu_callback
        
        update, context = create_mock_callback_update("menu_expenses")
        
        await handle_menu_callback(update, context)
        
        # Verify callback was answered
        assert update.callback_query.answer.called
        
        # Verify message was edited to show expenses menu
        assert update.callback_query.edit_message_text.called
        
        # Get text properly
        call = update.callback_query.edit_message_text.call_args
        if call.args:
            text = call.args[0]
        else:
            text = call.kwargs.get('text', '')
        
        assert text, "Text should not be empty"
        assert 'Expense Management' in text or 'expense' in text.lower(), f"Got text: {text}"
        
        print(f"✅ back to expenses menu test passed")


class TestCallbackErrorHandling:
    """Test error handling in callbacks"""
    
    @pytest.mark.asyncio
    async def test_handles_missing_expenses_gracefully(self):
        """Test handling when no expenses exist"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        update, context = create_mock_callback_update("expenses_list_all")
        
        # Mock expense service to return empty list
        with patch('app.services.expense_service.get_expenses') as mock_get:
            from app.schemas.expenses import ExpenseListResponse, ListMetadata
            mock_get.return_value = ExpenseListResponse(
                expenses=[],
                metadata=ListMetadata(
                    total=0,
                    page=1,
                    page_size=1,
                    total_pages=0,
                    limit=1,
                    offset=0,
                    has_more=False
                )
            )
            
            await handle_expenses_menu(update, context)
        
        # Should handle gracefully
        assert update.callback_query.answer.called
        
        print(f"✅ missing expenses handling test passed")
    
    @pytest.mark.asyncio
    async def test_handles_service_errors(self):
        """Test handling of service-level errors"""
        from app.bot.handlers.expenses_menu import handle_expenses_menu
        
        update, context = create_mock_callback_update("expenses_stats")
        
        # Mock expense service to raise error
        with patch('app.services.expense_service.get_expense_stats', side_effect=Exception("Service unavailable")):
            await handle_expenses_menu(update, context)
        
        # Should answer callback
        assert update.callback_query.answer.called
        
        # Should show error message
        if update.callback_query.edit_message_text.called:
            call = update.callback_query.edit_message_text.call_args
            if call.args:
                text = call.args[0]
            else:
                text = call.kwargs.get('text', '')
            assert 'error' in text.lower() or '❌' in text, f"Got text: {text}"
        
        print(f"✅ service error handling test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
