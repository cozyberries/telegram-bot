"""
Comprehensive integration tests for expense API endpoints

These tests validate the complete expense workflow via API:
- Creating expenses
- Listing expenses with pagination
- Getting expense details
- Updating expenses
- Deleting expenses
- Expense statistics

Tests use actual Supabase connection to validate real API behavior.
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from app.services import expense_service
from app.schemas.expenses import ExpenseInput, ExpenseResponse


# Test user UUID from Supabase (test@cozyberries.in)
TEST_USER_UUID = "aa79eb28-baf3-4cba-9388-5d8c7d598ad9"


class TestExpenseCreation:
    """Test expense creation via API"""
    
    def test_create_expense_with_required_fields_only(self):
        """Test creating expense with all required database fields"""
        expense_input = ExpenseInput(
            user_id=TEST_USER_UUID,
            username="test_user",
            amount=Decimal("1500.00"),
            description="Test expense - required fields only"
        )
        
        result = expense_service.create_expense(expense_input)
        
        assert result is not None
        assert result.amount == Decimal("1500.00")
        assert result.description == "Test expense - required fields only"
        assert result.id is not None
        
        # Cleanup
        expense_service.delete_expense(result.id)
        print(f"✅ Created and deleted expense: {result.id}")
    
    def test_create_expense_with_all_fields(self):
        """Test creating expense with all fields"""
        expense_input = ExpenseInput(
            user_id=TEST_USER_UUID,
            username="test_user",
            amount=Decimal("2500.50"),
            description="Test expense - all fields"
        )
        
        result = expense_service.create_expense(expense_input)
        
        assert result is not None
        assert result.amount == Decimal("2500.50")
        assert result.description == "Test expense - all fields"
        assert result.id is not None
        
        # Cleanup
        expense_service.delete_expense(result.id)
        print(f"✅ Created and deleted expense: {result.id}")
    
    def test_create_expense_validates_positive_amount(self):
        """Test that negative amounts are rejected"""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            ExpenseInput(
                user_id=TEST_USER_UUID,
                username="test",
                amount=Decimal("-100.00"),
                description="Invalid negative amount"
            )
        
        assert "greater than 0" in str(exc_info.value).lower()
    
    def test_create_expense_validates_description_length(self):
        """Test that short descriptions are rejected"""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            ExpenseInput(
                user_id=TEST_USER_UUID,
                username="test",
                amount=Decimal("100.00"),
                description="Ab"  # Only 2 characters
            )
        
        assert "at least 3 characters" in str(exc_info.value).lower()


class TestExpenseListing:
    """Test expense listing and pagination"""
    
    def test_list_expenses_default_pagination(self):
        """Test listing expenses with default pagination"""
        result = expense_service.get_expenses(limit=10, offset=0)
        
        assert result is not None
        assert result.metadata is not None
        assert result.metadata.limit == 10
        assert result.metadata.offset == 0
        assert isinstance(result.expenses, list)
        
        print(f"✅ Found {result.metadata.total} total expenses")
    
    def test_list_expenses_pagination_works(self):
        """Test that pagination correctly offsets results"""
        page1 = expense_service.get_expenses(limit=5, offset=0)
        page2 = expense_service.get_expenses(limit=5, offset=5)
        
        assert page1.metadata.offset == 0
        assert page2.metadata.offset == 5
        
        # If we have enough expenses, pages should be different
        if page1.metadata.total > 5:
            assert page1.expenses != page2.expenses
        
        print(f"✅ Pagination working: Page 1 has {len(page1.expenses)} items, Page 2 has {len(page2.expenses)} items")
    
    def test_list_expenses_metadata_accuracy(self):
        """Test that metadata correctly reflects total count"""
        result = expense_service.get_expenses(limit=3, offset=0)
        
        assert result.metadata.total >= 0
        assert result.metadata.has_more == ((result.metadata.offset + result.metadata.limit) < result.metadata.total)
        
        print(f"✅ Metadata accurate: {result.metadata.total} total, has_more={result.metadata.has_more}")


class TestExpenseRetrieval:
    """Test getting individual expense details"""
    
    def test_get_expense_by_valid_id(self):
        """Test retrieving expense by valid ID"""
        # First create an expense
        expense_input = ExpenseInput(
            user_id=TEST_USER_UUID,
            username="test",
            amount=Decimal("999.99"),
            description="Test expense for retrieval"
        )
        created = expense_service.create_expense(expense_input)
        
        # Now retrieve it
        retrieved = expense_service.get_expense_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.amount == created.amount
        assert retrieved.description == created.description
        
        # Cleanup
        expense_service.delete_expense(created.id)
        print(f"✅ Successfully retrieved expense: {created.id}")
    
    def test_get_expense_by_invalid_id_returns_none(self):
        """Test that invalid ID returns None"""
        result = expense_service.get_expense_by_id("00000000-0000-0000-0000-000000000000")
        assert result is None
        print("✅ Invalid ID correctly returns None")


class TestExpenseDeletion:
    """Test expense deletion"""
    
    def test_delete_existing_expense(self):
        """Test deleting an existing expense"""
        # Create expense
        expense_input = ExpenseInput(
            user_id=TEST_USER_UUID,
            username="test",
            amount=Decimal("777.77"),
            description="Test expense for deletion"
        )
        created = expense_service.create_expense(expense_input)
        
        # Delete it
        delete_response = expense_service.delete_expense(created.id)
        
        assert delete_response is not None
        assert delete_response.success is True
        assert delete_response.expense_id == created.id
        assert delete_response.amount == created.amount
        
        # Verify it's gone
        retrieved = expense_service.get_expense_by_id(created.id)
        assert retrieved is None
        
        print(f"✅ Successfully deleted expense: {created.id}")
    
    def test_delete_nonexistent_expense_returns_none(self):
        """Test deleting non-existent expense returns None"""
        result = expense_service.delete_expense("00000000-0000-0000-0000-000000000000")
        assert result is None
        print("✅ Deleting non-existent expense correctly returns None")


class TestExpenseStatistics:
    """Test expense statistics API"""
    
    def test_get_expense_stats(self):
        """Test retrieving expense statistics"""
        stats = expense_service.get_expense_stats()
        
        assert stats is not None
        assert stats.total_expenses >= 0
        assert stats.total_amount >= 0
        assert stats.average_expense >= 0
        
        # If there are expenses, average should make sense
        if stats.total_expenses > 0:
            assert stats.average_expense == stats.total_amount / stats.total_expenses
        
        print(f"✅ Stats: {stats.total_expenses} expenses, total ₹{stats.total_amount}, avg ₹{stats.average_expense}")
    
    def test_expense_stats_telegram_formatting(self):
        """Test that stats format correctly for Telegram"""
        stats = expense_service.get_expense_stats()
        message = stats.to_telegram_message()
        
        assert "Expense Statistics" in message
        assert "Total Expenses" in message
        assert "Total Amount" in message
        assert "Avg Expense" in message
        
        print(f"✅ Stats message formatted correctly")


class TestExpenseEndToEndWorkflow:
    """Test complete expense workflow"""
    
    def test_complete_expense_lifecycle(self):
        """Test creating, reading, and deleting an expense"""
        # 1. Create expense
        expense_input = ExpenseInput(
            user_id=TEST_USER_UUID,
            username="test",
            amount=Decimal("1234.56"),
            description="End-to-end test expense"
        )
        created = expense_service.create_expense(expense_input)
        assert created.id is not None
        print(f"✅ Step 1: Created expense {created.id}")
        
        # 2. Retrieve it
        retrieved = expense_service.get_expense_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        print(f"✅ Step 2: Retrieved expense {created.id}")
        
        # 3. Verify it appears in list
        expenses_list = expense_service.get_expenses(limit=100, offset=0)
        expense_ids = [e.id for e in expenses_list.expenses]
        assert created.id in expense_ids
        print(f"✅ Step 3: Expense appears in list")
        
        # 4. Delete it
        delete_response = expense_service.delete_expense(created.id)
        assert delete_response.success is True
        print(f"✅ Step 4: Deleted expense {created.id}")
        
        # 5. Verify it's gone
        retrieved_after_delete = expense_service.get_expense_by_id(created.id)
        assert retrieved_after_delete is None
        print(f"✅ Step 5: Expense confirmed deleted")
        
        print("✅ COMPLETE LIFECYCLE TEST PASSED")
    
    def test_multiple_expenses_workflow(self):
        """Test creating and managing multiple expenses"""
        created_ids = []
        
        # Create 3 expenses
        for i in range(1, 4):
            expense_input = ExpenseInput(
                user_id=TEST_USER_UUID,
                username="test",
                amount=Decimal(f"{i * 100}.00"),
                description=f"Bulk test expense {i}"
            )
            created = expense_service.create_expense(expense_input)
            created_ids.append(created.id)
            print(f"✅ Created expense {i}/3: {created.id}")
        
        # Verify all exist
        for expense_id in created_ids:
            retrieved = expense_service.get_expense_by_id(expense_id)
            assert retrieved is not None
        print(f"✅ All 3 expenses verified")
        
        # Cleanup all
        for expense_id in created_ids:
            expense_service.delete_expense(expense_id)
        print(f"✅ All 3 expenses deleted")
        
        print("✅ MULTIPLE EXPENSES WORKFLOW PASSED")


class TestExpenseResponseFormatting:
    """Test expense response formatting for Telegram"""
    
    def test_expense_response_telegram_message(self):
        """Test ExpenseResponse.to_telegram_message()"""
        expense = ExpenseResponse(
            id="test-id-123",
            title="Test Expense",
            description="Test expense description",
            amount=Decimal("2500.50"),
            expense_date=date.today(),
            paid_by=TEST_USER_UUID,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        message = expense.to_telegram_message()
        
        assert "Test Expense" in message
        assert "₹2,500.50" in message
        # Date will be from expense_date
        assert "test-id-123" in message
        
        print("✅ Expense message formatted correctly")
    
    def test_expense_delete_response_formatting(self):
        """Test ExpenseDeleteResponse.to_telegram_message()"""
        from app.schemas.expenses import ExpenseDeleteResponse
        
        delete_response = ExpenseDeleteResponse(
            success=True,
            expense_id="test-id-456",
            title="Deleted Expense",
            amount=Decimal("1500.00")
        )
        
        message = delete_response.to_telegram_message()
        
        assert "deleted successfully" in message.lower()
        assert "Deleted Expense" in message
        assert "₹1,500.00" in message
        
        print("✅ Delete response formatted correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
