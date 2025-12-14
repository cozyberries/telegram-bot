"""Test configuration and fixtures for Telegram webhook tests"""

import os
import sys
from typing import Generator
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
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

# Use environment variables from .env.test
os.environ.setdefault('TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN', 'test_bot_token'))
os.environ.setdefault('SUPABASE_URL', os.getenv('SUPABASE_URL', 'https://test.supabase.co'))
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', os.getenv('SUPABASE_KEY', os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'test_key')))
os.environ.setdefault('ADMIN_USER_IDS', os.getenv('ADMIN_USER_IDS', '123456789'))

# Import app after environment is set
from app.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def valid_user_id() -> str:
    """Return a valid user ID for testing"""
    # Use the actual test user from database: test@cozyberries.in
    return 'aa79eb28-baf3-4cba-9388-5d8c7d598ad9'


@pytest.fixture(scope="function")
def valid_admin_id() -> str:
    """Return a valid admin user ID for testing"""
    # Use the same test user as admin
    return 'aa79eb28-baf3-4cba-9388-5d8c7d598ad9'
