"""Pytest configuration and fixtures for integration tests

These tests use the real FastAPI app and actual Supabase database.
Configure your test database in .env.test file.
"""

import os
import sys
from typing import Generator, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import pytest
from dotenv import load_dotenv

# Add app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env.test file if it exists
env_test_path = Path(__file__).parent.parent / '.env.test'
if env_test_path.exists():
    load_dotenv(env_test_path, override=True)
    print(f"✅ Loaded environment variables from {env_test_path}")
else:
    print(f"⚠️  Warning: {env_test_path} not found. Using default/OS environment variables.")

# Set test environment variables before importing app modules
os.environ['TESTING'] = 'true'

# Use environment variables from .env.test, with fallbacks
os.environ.setdefault('TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN', 'test_bot_token'))
os.environ.setdefault('SUPABASE_URL', os.getenv('SUPABASE_URL', os.getenv('TEST_SUPABASE_URL', 'https://test.supabase.co')))
os.environ.setdefault('SUPABASE_KEY', os.getenv('SUPABASE_KEY', os.getenv('TEST_SUPABASE_KEY', 'test_supabase_key')))
os.environ.setdefault('ADMIN_USER_IDS', os.getenv('ADMIN_USER_IDS', '123456789,987654321'))

# Map environment variables to what pydantic-settings expects
# Settings class expects: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
if 'SUPABASE_URL' not in os.environ:
    os.environ['SUPABASE_URL'] = os.getenv('TEST_SUPABASE_URL', os.getenv('SUPABASE_URL', ''))
if 'SUPABASE_SERVICE_ROLE_KEY' not in os.environ:
    # Try SUPABASE_KEY first, then SUPABASE_SERVICE_ROLE_KEY
    os.environ['SUPABASE_SERVICE_ROLE_KEY'] = os.getenv('SUPABASE_KEY', os.getenv('SUPABASE_SERVICE_ROLE_KEY', ''))

# Import FastAPI TestClient
from fastapi.testclient import TestClient

# Import models
from app.database.models import (
    Expense,
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseStatus,
    ExpenseCategory,
    ExpensePriority,
    ExpensePaymentMethod
)

# Import the real FastAPI app - no mocking
from app.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """
    Create a TestClient for the real FastAPI app.
    This uses the actual app with real Supabase connection.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def mock_expense_data() -> Dict[str, Any]:
    """
    Generate mock expense data for testing.
    Scope is function to get fresh data for each test.
    """
    return {
        "title": "Test Office Supplies",
        "description": "Test expense for integration testing",
        "amount": 2500.00,
        "category": "office_supplies",
        "category_id": None,
        "priority": "medium",
        "expense_date": datetime.now().isoformat(),
        "vendor": "Test Vendor",
        "payment_method": "company_card",
        "receipt_url": "https://example.com/receipts/test.pdf",
        "notes": "Test expense - safe to delete",
        "tags": ["test", "integration"]
    }


@pytest.fixture(scope="function")
def mock_expense_create(mock_expense_data: Dict[str, Any]) -> ExpenseCreate:
    """Create ExpenseCreate model instance from mock data"""
    return ExpenseCreate(**mock_expense_data)


@pytest.fixture(scope="function")
def valid_user_id() -> str:
    """Return a valid user ID for testing - actual user from database"""
    # Use the actual test user from database: test@cozyberries.in
    # This user exists in the database and can be used for all CRUD operations
    return 'aa79eb28-baf3-4cba-9388-5d8c7d598ad9'


@pytest.fixture(scope="function")
def valid_admin_id() -> str:
    """Return a valid admin user ID for testing"""
    # Use the same test user as admin for approval operations
    # This user exists in the database: test@cozyberries.in
    return 'aa79eb28-baf3-4cba-9388-5d8c7d598ad9'


# Test data constants
TEST_EXPENSE_CATEGORIES = [
    "office_supplies",
    "travel",
    "marketing",
    "software",
    "equipment",
    "utilities",
    "professional_services",
    "training",
    "maintenance",
    "other"
]

TEST_EXPENSE_PRIORITIES = ["low", "medium", "high", "urgent"]

TEST_EXPENSE_STATUSES = ["pending", "approved", "rejected", "paid", "cancelled"]

TEST_PAYMENT_METHODS = [
    "company_card",
    "reimbursement",
    "direct_payment",
    "bank_transfer"
]
