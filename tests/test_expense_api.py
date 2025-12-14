"""Integration tests for Expense API Routes

These tests call the actual FastAPI expense routes without mocking.
They use a real Supabase test database configured in .env.test.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.database.models import ExpenseCreate, ExpenseUpdate


@pytest.mark.integration
@pytest.mark.expense
class TestExpenseAPIRoutes:
    """Test suite for expense API routes using real endpoints"""
    
    def test_create_expense_success(self, test_client: TestClient, mock_expense_data, valid_user_id):
        """Test POST /api/expenses/ - Create a new expense"""
        # Act
        response = test_client.post(
            "/api/expenses/",
            json=mock_expense_data,
            params={"user_id": valid_user_id}
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == mock_expense_data["title"]
        assert data["amount"] == mock_expense_data["amount"]
        assert data["status"] == "pending"
        assert data["user_id"] == valid_user_id
        assert "id" in data
        assert "created_at" in data
    
    def test_create_expense_validation_error(self, test_client: TestClient, valid_user_id):
        """Test POST /api/expenses/ with invalid data returns 422"""
        # Arrange
        invalid_data = {
            "title": "Test",
            # Missing required fields
        }
        
        # Act
        response = test_client.post(
            "/api/expenses/",
            json=invalid_data,
            params={"user_id": valid_user_id}
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_get_expenses_list(self, test_client: TestClient):
        """Test GET /api/expenses/ - Get list of expenses"""
        # Act
        response = test_client.get("/api/expenses/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_expenses_with_pagination(self, test_client: TestClient):
        """Test GET /api/expenses/ with pagination parameters"""
        # Act
        response = test_client.get("/api/expenses/?limit=10&offset=0")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_expenses_with_status_filter(self, test_client: TestClient):
        """Test GET /api/expenses/ with status filter"""
        # Act
        response = test_client.get("/api/expenses/?status=pending")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify all returned expenses have pending status
        for expense in data:
            assert expense["status"] == "pending"
    
    def test_get_expense_by_id_not_found(self, test_client: TestClient):
        """Test GET /api/expenses/{id} with non-existent ID returns 404"""
        # Act - Use a valid UUID format that doesn't exist
        import uuid
        fake_uuid = str(uuid.uuid4())
        response = test_client.get(f"/api/expenses/{fake_uuid}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_update_expense(self, test_client: TestClient, mock_expense_data, valid_user_id):
        """Test PUT /api/expenses/{id} - Update an expense"""
        # Arrange - First create an expense
        create_response = test_client.post(
            "/api/expenses/",
            json=mock_expense_data,
            params={"user_id": valid_user_id}
        )
        assert create_response.status_code == 201
        expense_id = create_response.json()["id"]
        
        # Act - Update the expense
        update_data = {
            "title": "Updated Test Expense",
            "amount": 3500.00,
            "priority": "high"
        }
        response = test_client.put(
            f"/api/expenses/{expense_id}",
            json=update_data
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["amount"] == update_data["amount"]
        assert data["priority"] == update_data["priority"]
    
    def test_update_expense_not_found(self, test_client: TestClient):
        """Test PUT /api/expenses/{id} with non-existent ID returns 404"""
        # Act - Use a valid UUID format that doesn't exist
        import uuid
        fake_uuid = str(uuid.uuid4())
        response = test_client.put(
            f"/api/expenses/{fake_uuid}",
            json={"title": "Updated"}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_approve_expense(self, test_client: TestClient, mock_expense_data, valid_user_id, valid_admin_id):
        """Test POST /api/expenses/{id}/approve - Approve an expense"""
        # Arrange - Create a pending expense
        create_response = test_client.post(
            "/api/expenses/",
            json=mock_expense_data,
            params={"user_id": valid_user_id}
        )
        assert create_response.status_code == 201
        expense_id = create_response.json()["id"]
        
        # Act - Approve the expense
        response = test_client.post(
            f"/api/expenses/{expense_id}/approve",
            params={"approver_id": valid_admin_id}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["approved_by"] == valid_admin_id
        assert data["approved_at"] is not None
    
    def test_approve_expense_not_found(self, test_client: TestClient, valid_admin_id):
        """Test POST /api/expenses/{id}/approve with non-existent ID"""
        # Act - Use a valid UUID format that doesn't exist
        import uuid
        fake_uuid = str(uuid.uuid4())
        response = test_client.post(
            f"/api/expenses/{fake_uuid}/approve",
            params={"approver_id": valid_admin_id}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_reject_expense(self, test_client: TestClient, mock_expense_data, valid_user_id):
        """Test POST /api/expenses/{id}/reject - Reject an expense"""
        # Arrange - Create a pending expense
        create_response = test_client.post(
            "/api/expenses/",
            json=mock_expense_data,
            params={"user_id": valid_user_id}
        )
        assert create_response.status_code == 201
        expense_id = create_response.json()["id"]
        
        # Act - Reject the expense
        rejection_reason = "Test rejection - insufficient documentation"
        response = test_client.post(
            f"/api/expenses/{expense_id}/reject",
            params={"reason": rejection_reason}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["rejected_reason"] == rejection_reason
    
    def test_get_pending_expenses(self, test_client: TestClient):
        """Test GET /api/expenses/pending/list - Get pending expenses"""
        # Act
        response = test_client.get("/api/expenses/pending/list")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify all are pending
        for expense in data:
            assert expense["status"] == "pending"
    
    def test_get_expense_count(self, test_client: TestClient):
        """Test GET /api/expenses/stats/count - Get expense count"""
        # Act
        response = test_client.get("/api/expenses/stats/count")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 0
    
    def test_get_expense_count_by_status(self, test_client: TestClient):
        """Test GET /api/expenses/stats/count with status filter"""
        # Act
        response = test_client.get("/api/expenses/stats/count?status=pending")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["status"] == "pending"
        assert isinstance(data["count"], int)
    
    def test_get_total_expense_amount(self, test_client: TestClient):
        """Test GET /api/expenses/stats/total-amount - Get total amount"""
        # Act
        response = test_client.get("/api/expenses/stats/total-amount")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_amount" in data
        assert isinstance(data["total_amount"], (int, float))
        assert data["total_amount"] >= 0
        assert data["currency"] == "INR"
    
    def test_get_total_amount_by_status(self, test_client: TestClient):
        """Test GET /api/expenses/stats/total-amount with status filter"""
        # Act
        response = test_client.get("/api/expenses/stats/total-amount?status=approved")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_amount" in data
        assert data["status"] == "approved"
        assert isinstance(data["total_amount"], (int, float))


@pytest.mark.integration
@pytest.mark.expense
class TestExpenseAPIValidation:
    """Test data validation on expense endpoints"""
    
    def test_create_expense_invalid_category(self, test_client: TestClient, mock_expense_data, valid_user_id):
        """Test creating expense with invalid category returns validation error"""
        # Arrange
        mock_expense_data["category"] = "invalid_category_xyz"
        
        # Act
        response = test_client.post(
            "/api/expenses/",
            json=mock_expense_data,
            params={"user_id": valid_user_id}
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_create_expense_invalid_priority(self, test_client: TestClient, mock_expense_data, valid_user_id):
        """Test creating expense with invalid priority returns validation error"""
        # Arrange
        mock_expense_data["priority"] = "invalid_priority"
        
        # Act
        response = test_client.post(
            "/api/expenses/",
            json=mock_expense_data,
            params={"user_id": valid_user_id}
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_create_expense_missing_required_fields(self, test_client: TestClient, valid_user_id):
        """Test creating expense with missing required fields"""
        # Arrange
        incomplete_data = {
            "title": "Test Expense"
            # Missing: amount, category, priority, expense_date, payment_method
        }
        
        # Act
        response = test_client.post(
            "/api/expenses/",
            json=incomplete_data,
            params={"user_id": valid_user_id}
        )
        
        # Assert
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.expense
class TestGeneralAPIEndpoints:
    """Test general API endpoints (health, info, webhook)"""
    
    def test_health_check_endpoint(self, test_client: TestClient):
        """Test GET /health - Health check endpoint"""
        # Act
        response = test_client.get("/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_root_endpoint(self, test_client: TestClient):
        """Test GET / - Root endpoint"""
        # Act
        response = test_client.get("/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_bot_info_endpoint(self, test_client: TestClient):
        """Test GET /bot-info - Bot information endpoint"""
        # Act
        response = test_client.get("/bot-info")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "features" in data
        assert "Expenses Management" in data["features"]
    
    def test_webhook_get_info(self, test_client: TestClient):
        """Test GET /webhook - Webhook info endpoint"""
        # Act
        response = test_client.get("/webhook")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["endpoint"] == "/webhook"
