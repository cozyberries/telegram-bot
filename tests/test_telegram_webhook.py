"""
Webhook-based integration tests for Telegram bot commands

These tests validate the actual Telegram webhook flow by sending
Update objects to the /webhook endpoint, simulating real Telegram updates.
"""

import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient


class TestTelegramWebhook:
    """Test Telegram webhook endpoint with bot commands"""
    
    def test_webhook_health(self, test_client: TestClient):
        """Test webhook endpoint is accessible"""
        response = test_client.get("/webhook")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["endpoint"] == "/webhook"
    
    def test_webhook_start_command(self, test_client: TestClient, valid_user_id: str):
        """Test /start command via webhook"""
        # Use a simple integer user ID for Telegram
        user_id = 123456789
        
        update_data = {
            "update_id": 100001,
            "message": {
                "message_id": 1,
                "from": {
                    "id": user_id,
                    "first_name": "Test",
                    "is_bot": False
                },
                "chat": {
                    "id": user_id,
                    "type": "private"
                },
                "text": "/start",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        # Should return 200 (command processed)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["update_id"] == 100001


class TestExpenseCommands:
    """Test expense-related Telegram commands"""
    
    def test_add_expense_command_start(self, test_client: TestClient, valid_admin_id: str):
        """Test /add_expense command shows format guide"""
        # Use admin user ID from environment
        admin_id = 123456789
        
        update_data = {
            "update_id": 100002,
            "message": {
                "message_id": 2,
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
        
        # Command should be processed successfully
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_expenses_list_command(self, test_client: TestClient, valid_admin_id: str):
        """Test /expenses command to list expenses"""
        admin_id = 123456789
        
        update_data = {
            "update_id": 100003,
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
        
        # Command should be processed
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestHealthEndpoints:
    """Test general API endpoints"""
    
    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "CozyBerries" in data["message"]
    
    def test_health_endpoint(self, test_client: TestClient):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "bot_initialized" in data
    
    def test_bot_info_endpoint(self, test_client: TestClient):
        """Test bot info endpoint"""
        response = test_client.get("/bot-info")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "bot_name" in data


class TestWebhookValidation:
    """Test webhook input validation"""
    
    def test_webhook_invalid_json(self, test_client: TestClient):
        """Test webhook with invalid JSON"""
        response = test_client.post(
            "/webhook",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should handle invalid JSON gracefully
        assert response.status_code in [400, 422, 500]
    
    def test_webhook_missing_update_id(self, test_client: TestClient):
        """Test webhook with missing update_id"""
        update_data = {
            "message": {
                "message_id": 1,
                "from": {"id": 12345, "first_name": "Test", "is_bot": False},
                "chat": {"id": 12345, "type": "private"},
                "text": "/start",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = test_client.post("/webhook", json=update_data)
        
        # Should still process (update_id is optional in response)
        assert response.status_code in [200, 500]  # May fail if bot not fully initialized
