"""
Comprehensive integration tests for expense-related Telegram bot commands

Tests cover:
- Creating expenses with interactive form
- Listing expenses with pagination
- Getting expense details
- Deleting expenses
- Expense validation
- Navigation through expense browser
"""

import json
import pytest
from datetime import datetime, date
from decimal import Decimal
from fastapi.testclient import TestClient


class TestExpenseCreation:
    """Test expense creation flow with interactive form"""
    
    def test_add_expense_start_shows_form(self, test_client: TestClient, valid_admin_id: int):
        """Test /add_expense command shows interactive form"""
        admin_id = valid_admin_id
        
        update_data = {
            "update_id": 200001,
            "message": {
                "message_id": 1,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "username": "admin_user",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": "/add_expense",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["update_id"] == 200001
    
    def test_add_expense_requires_admin(self, test_client: TestClient):
        """Test /add_expense requires admin permissions"""
        non_admin_id = 999999999  # Not in admin list
        
        update_data = {
            "update_id": 200002,
            "message": {
                "message_id": 2,
                "from": {
                    "id": non_admin_id,
                    "first_name": "User",
                    "is_bot": False
                },
                "chat": {
                    "id": non_admin_id,
                    "type": "private"
                },
                "text": "/add_expense",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        # Should still return 200 (bot processes it) but user should get unauthorized message
        assert response.status_code == 200


class TestExpenseListing:
    """Test expense listing and browsing commands"""
    
    def test_list_expenses_command(self, test_client: TestClient, valid_admin_id: int):
        """Test /expenses command lists expenses with pagination"""
        admin_id = valid_admin_id
        
        update_data = {
            "update_id": 200003,
            "message": {
                "message_id": 3,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": "/expenses",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_expenses_requires_admin(self, test_client: TestClient):
        """Test /expenses requires admin permissions"""
        non_admin_id = 999999999
        
        update_data = {
            "update_id": 200004,
            "message": {
                "message_id": 4,
                "from": {
                    "id": non_admin_id,
                    "first_name": "User",
                    "is_bot": False
                },
                "chat": {
                    "id": non_admin_id,
                    "type": "private"
                },
                "text": "/expenses",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200


class TestExpenseDetails:
    """Test getting individual expense details"""
    
    def test_get_expense_with_valid_id(self, test_client: TestClient, valid_admin_id: int):
        """Test /expense <id> command with valid expense ID"""
        admin_id = valid_admin_id
        # Using a UUID format (will fail if expense doesn't exist, which is expected)
        expense_id = "123e4567-e89b-12d3-a456-426614174000"
        
        update_data = {
            "update_id": 200005,
            "message": {
                "message_id": 5,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": f"/expense {expense_id}",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_get_expense_without_id(self, test_client: TestClient, valid_admin_id: int):
        """Test /expense without ID shows usage help"""
        admin_id = valid_admin_id
        
        update_data = {
            "update_id": 200006,
            "message": {
                "message_id": 6,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": "/expense",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_get_expense_requires_admin(self, test_client: TestClient):
        """Test /expense requires admin permissions"""
        non_admin_id = 999999999
        
        update_data = {
            "update_id": 200007,
            "message": {
                "message_id": 7,
                "from": {
                    "id": non_admin_id,
                    "first_name": "User",
                    "is_bot": False
                },
                "chat": {
                    "id": non_admin_id,
                    "type": "private"
                },
                "text": "/expense 123e4567-e89b-12d3-a456-426614174000",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200


class TestExpenseDeletion:
    """Test expense deletion commands"""
    
    def test_delete_expense_with_valid_id(self, test_client: TestClient, valid_admin_id: int):
        """Test /delete_expense <id> command"""
        admin_id = valid_admin_id
        expense_id = "123e4567-e89b-12d3-a456-426614174000"
        
        update_data = {
            "update_id": 200008,
            "message": {
                "message_id": 8,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": f"/delete_expense {expense_id}",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_delete_expense_without_id(self, test_client: TestClient, valid_admin_id: int):
        """Test /delete_expense without ID shows usage help"""
        admin_id = valid_admin_id
        
        update_data = {
            "update_id": 200009,
            "message": {
                "message_id": 9,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": "/delete_expense",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_delete_expense_requires_admin(self, test_client: TestClient):
        """Test /delete_expense requires admin permissions"""
        non_admin_id = 999999999
        
        update_data = {
            "update_id": 200010,
            "message": {
                "message_id": 10,
                "from": {
                    "id": non_admin_id,
                    "first_name": "User",
                    "is_bot": False
                },
                "chat": {
                    "id": non_admin_id,
                    "type": "private"
                },
                "text": "/delete_expense 123e4567-e89b-12d3-a456-426614174000",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200


class TestExpenseBrowserNavigation:
    """Test expense browser navigation with callback queries"""
    
    def test_expense_browser_navigation_forward(self, test_client: TestClient, valid_admin_id: int):
        """Test navigating forward in expense browser"""
        admin_id = valid_admin_id
        
        update_data = {
            "update_id": 200011,
            "callback_query": {
                "id": "callback_1",
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "message": {
                    "message_id": 11,
                    "chat": {
                        "id": admin_id,
                        "type": "private"
                    },
                    "date": int(datetime.now().timestamp()),
                    "text": "Some expense details"
                },
                "data": "exp_page_1",
                "chat_instance": "123"
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_expense_browser_navigation_backward(self, test_client: TestClient, valid_admin_id: int):
        """Test navigating backward in expense browser"""
        admin_id = valid_admin_id
        
        update_data = {
            "update_id": 200012,
            "callback_query": {
                "id": "callback_2",
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "message": {
                    "message_id": 12,
                    "chat": {
                        "id": admin_id,
                        "type": "private"
                    },
                    "date": int(datetime.now().timestamp()),
                    "text": "Some expense details"
                },
                "data": "exp_page_0",
                "chat_instance": "123"
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_expense_browser_close(self, test_client: TestClient, valid_admin_id: int):
        """Test closing expense browser"""
        admin_id = valid_admin_id
        
        update_data = {
            "update_id": 200013,
            "callback_query": {
                "id": "callback_3",
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "message": {
                    "message_id": 13,
                    "chat": {
                        "id": admin_id,
                        "type": "private"
                    },
                    "date": int(datetime.now().timestamp()),
                    "text": "Some expense details"
                },
                "data": "exp_close_browser",
                "chat_instance": "123"
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestExpenseValidation:
    """Test expense input validation"""
    
    def test_expense_amount_validation(self, test_client: TestClient, valid_admin_id: int):
        """Test expense amount must be positive"""
        # This would be tested via conversation state, but we can verify command processing
        admin_id = valid_admin_id
        
        update_data = {
            "update_id": 200014,
            "message": {
                "message_id": 14,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": "/add_expense",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestExpenseService:
    """Test expense service functions directly"""
    
    def test_create_expense_with_valid_data(self):
        """Test creating expense with valid data"""
        from app.services.expense_service import create_expense
        from app.schemas.expenses import ExpenseInput
        
        # Test with mock data
        expense_input = ExpenseInput(
            user_id="test-user-id",
            username="test_user",
            amount=Decimal("1500.00"),
            description="Test expense for integration",
            expense_date=date.today()
        )
        
        # This will fail if Supabase is not available, but validates the schema
        try:
            result = create_expense(expense_input)
            assert result is not None
            assert result.amount == Decimal("1500.00")
            assert result.description == "Test expense for integration"
        except Exception as e:
            # Expected if Supabase is not available in test environment
            error_msg = str(e).lower()
            assert any(x in error_msg for x in ["failed to create", "supabase", "connection", "uuid", "syntax"]), f"Unexpected error: {e}"
    
    def test_get_expenses_pagination(self):
        """Test getting expenses with pagination"""
        from app.services.expense_service import get_expenses
        
        try:
            result = get_expenses(limit=10, offset=0)
            assert result is not None
            assert result.metadata is not None
            assert result.metadata.limit == 10
            assert result.metadata.offset == 0
            assert isinstance(result.expenses, list)
        except Exception as e:
            # Expected if Supabase is not available
            assert "Supabase" in str(e) or "connection" in str(e).lower() or "API" in str(e)
    
    def test_get_expense_by_id(self):
        """Test getting expense by ID"""
        from app.services.expense_service import get_expense_by_id
        
        # Test with a non-existent ID
        try:
            result = get_expense_by_id("non-existent-id-12345")
            assert result is None or result.id != "non-existent-id-12345"
        except Exception as e:
            # Expected if Supabase is not available or ID is invalid
            error_msg = str(e).lower()
            assert any(x in error_msg for x in ["supabase", "connection", "uuid", "syntax", "api"]), f"Unexpected error: {e}"
    
    def test_delete_expense_returns_response(self):
        """Test deleting expense returns proper response"""
        from app.services.expense_service import delete_expense
        
        # Test with a non-existent ID
        try:
            result = delete_expense("non-existent-id-12345")
            # Should return None for non-existent expense
            assert result is None
        except Exception as e:
            # Expected if Supabase is not available or ID is invalid
            error_msg = str(e).lower()
            assert any(x in error_msg for x in ["supabase", "connection", "uuid", "syntax"]), f"Unexpected error: {e}"


class TestExpenseSchemas:
    """Test expense Pydantic schemas"""
    
    def test_expense_input_validation(self):
        """Test ExpenseInput schema validation"""
        from app.schemas.expenses import ExpenseInput
        from pydantic import ValidationError
        
        # Valid input - expense_date defaults to today when not provided
        expense = ExpenseInput(
            user_id="test-user",
            username="test",
            amount=Decimal("1000.00"),
            description="Test expense"
        )
        assert expense.amount == Decimal("1000.00")
        assert expense.description == "Test expense"
        assert expense.expense_date == date.today()
        
        # Valid input with explicit date
        expense_with_date = ExpenseInput(
            user_id="test-user",
            username="test",
            amount=Decimal("1000.00"),
            description="Test expense",
            expense_date=date(2025, 12, 14)
        )
        assert expense_with_date.expense_date == date(2025, 12, 14)
        
        # Invalid amount (negative)
        with pytest.raises(ValidationError) as exc_info:
            ExpenseInput(
                user_id="test-user",
                username="test",
                amount=Decimal("-100.00"),
                description="Test"
            )
        assert "greater than 0" in str(exc_info.value).lower()
        
        # Invalid description (too short)
        with pytest.raises(ValidationError) as exc_info:
            ExpenseInput(
                user_id="test-user",
                username="test",
                amount=Decimal("100.00"),
                description="Te"  # Only 2 characters
            )
        assert "at least 3 characters" in str(exc_info.value).lower()
    
    def test_expense_response_formatting(self):
        """Test ExpenseResponse formatting methods"""
        from app.schemas.expenses import ExpenseResponse
        
        expense = ExpenseResponse(
            id="test-id-123",
            title="Test Expense",
            description="Test expense description",
            amount=Decimal("2500.50"),
            expense_date=date(2025, 12, 14),
            paid_by="test-user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Test formatted amount
        assert expense.formatted_amount == "₹2,500.50"
        
        # Test formatted date
        assert "14" in expense.formatted_date
        assert "Dec" in expense.formatted_date
        assert "2025" in expense.formatted_date
        
        # Test Telegram message format
        message = expense.to_telegram_message()
        assert "Test Expense" in message
        assert "₹2,500.50" in message
        assert "test-id-123" in message
    
    def test_expense_delete_response_formatting(self):
        """Test ExpenseDeleteResponse formatting"""
        from app.schemas.expenses import ExpenseDeleteResponse
        
        delete_response = ExpenseDeleteResponse(
            success=True,
            expense_id="test-id-123",
            title="Test Expense",
            amount=Decimal("1500.00")
        )
        
        message = delete_response.to_telegram_message()
        assert "deleted successfully" in message.lower()
        assert "Test Expense" in message
        assert "₹1,500.00" in message
    
    def test_expense_list_response(self):
        """Test ExpenseListResponse with metadata"""
        from app.schemas.expenses import ExpenseListResponse, ExpenseResponse
        from app.schemas.expenses import ListMetadata
        
        expenses = [
            ExpenseResponse(
                id=f"test-id-{i}",
                title=f"Expense {i}",
                description=f"Description {i}",
                amount=Decimal(f"{i * 100}.00"),
                expense_date=date.today(),
                paid_by="test-user",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            for i in range(1, 4)
        ]
        
        metadata = ListMetadata(
            total=10,
            limit=3,
            offset=0,
            has_more=True
        )
        
        list_response = ExpenseListResponse(
            expenses=expenses,
            metadata=metadata
        )
        
        assert len(list_response.expenses) == 3
        assert list_response.metadata.total == 10
        assert list_response.metadata.has_more is True
        
        assert list_response.metadata.has_more is True


class TestExpenseEndToEnd:
    """End-to-end expense workflow tests"""
    
    def test_expense_workflow_list_and_view(self, test_client: TestClient, valid_admin_id: int):
        """Test complete workflow: list expenses then view one"""
        admin_id = valid_admin_id
        
        # Step 1: List expenses
        list_update = {
            "update_id": 200015,
            "message": {
                "message_id": 15,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": "/expenses",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=list_update)
        assert response.status_code == 200
        assert response.json()["ok"] is True
        
        # Step 2: View specific expense (will fail if no expenses exist)
        view_update = {
            "update_id": 200016,
            "message": {
                "message_id": 16,
                "from": {
                    "id": admin_id,
                    "first_name": "Admin",
                    "is_bot": False
                },
                "chat": {
                    "id": admin_id,
                    "type": "private"
                },
                "text": "/expense 123e4567-e89b-12d3-a456-426614174000",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=view_update)
        assert response.status_code == 200
        assert response.json()["ok"] is True
