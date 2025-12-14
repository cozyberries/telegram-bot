"""Test configuration and fixtures for Telegram webhook tests"""

import os
import sys
import json
from typing import Generator
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from telegram.ext import Application

# Add app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded environment variables from {env_path}")
else:
    print(f"⚠️  Warning: {env_path} not found. Using default/OS environment variables.")

# Set test environment variables before importing app modules
os.environ['TESTING'] = 'true'

# Use environment variables from .env.test
os.environ.setdefault('TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN', '123456789:TEST_TOKEN'))
os.environ.setdefault('SUPABASE_URL', os.getenv('SUPABASE_URL', 'https://test.supabase.co'))
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', os.getenv('SUPABASE_KEY', os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'test_key')))

# Ensure test admin ID is allowed (append to existing or set new)
existing_admins = os.getenv('ADMIN_TELEGRAM_USER_IDS', '')
test_admin_id = '123456789'
if test_admin_id not in existing_admins:
    os.environ['ADMIN_TELEGRAM_USER_IDS'] = f"{existing_admins},{test_admin_id}" if existing_admins else test_admin_id

# Import app after environment is set
from app.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def valid_user_id() -> int:
    """Return a valid user ID for testing"""
    return 123456789


@pytest.fixture(scope="function")
def valid_admin_id() -> int:
    """Return a valid admin user ID for testing"""
    return 123456789


@pytest.fixture(autouse=True)
def mock_telegram_request(mocker):
    """Mock Telegram API requests to prevent real network calls"""
    async def mock_do_request(url, method, request_data=None, *args, **kwargs):
        # Default dummy response (Message)
        result = {
            "message_id": 123, 
            "date": 1234567890, 
            "chat": {"id": 123456789, "type": "private"},
            "text": "mock response"
        }
        
        # If getMe is called, return User object
        if "getMe" in str(url):
            result = {
                "id": 88888888,
                "is_bot": True,
                "first_name": "TestBot",
                "username": "TestBot"
            }
            
            
        return 200, json.dumps({"ok": True, "result": result}).encode('utf-8')

    # Patch the HTTPXRequest.do_request method in python-telegram-bot
    mocker.patch('telegram.request._httpxrequest.HTTPXRequest.do_request', side_effect=mock_do_request)
