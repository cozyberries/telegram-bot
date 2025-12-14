# Telegram Webhook Tests

## Overview

These tests validate the Telegram bot by sending webhook updates to the `/webhook` endpoint, simulating real Telegram message flows.

## Test Strategy

**Focus:** Telegram webhook integration (not REST API)

All bot commands use the `/webhook` endpoint, so tests validate:
- Webhook endpoint functionality
- Command processing
- Bot initialization
- Error handling

## Test Files

### `conftest.py`
- Test configuration and fixtures
- FastAPI TestClient setup
- Environment variable management
- Test user fixtures

### `test_telegram_webhook.py`
- Webhook endpoint tests
- Telegram command tests (/start, /add_expense, /expenses)
- Health check endpoints
- Input validation tests

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_telegram_webhook.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term

# Run specific test class
pytest tests/test_telegram_webhook.py::TestExpenseCommands -v
```

## Test Coverage

### Telegram Webhook Tests
- ✅ Webhook endpoint availability
- ✅ /start command processing
- ✅ /add_expense command
- ✅ /expenses list command
- ✅ Invalid JSON handling
- ✅ Missing fields handling

### Health Endpoints
- ✅ Root endpoint (/)
- ✅ Health check (/health)
- ✅ Bot info (/api/bot/info)

## Environment Setup

### Required Variables

Create `.env.test`:
```bash
TELEGRAM_BOT_TOKEN=your_test_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ADMIN_USER_IDS=aa79eb28-baf3-4cba-9388-5d8c7d598ad9
```

### Test User

Tests use this existing user:
```
User ID: aa79eb28-baf3-4cba-9388-5d8c7d598ad9
Email: test@cozyberries.in
```

## Test Structure

```python
# Example webhook test
def test_start_command(test_client, valid_user_id):
    update_data = {
        "update_id": 100001,
        "message": {
            "message_id": 1,
            "from": {"id": 12345, "first_name": "Test", "is_bot": False},
            "chat": {"id": 12345, "type": "private"},
            "text": "/start",
            "date": int(datetime.now().timestamp())
        }
    }
    
    response = test_client.post("/webhook", json=update_data)
    
    assert response.status_code == 200
    assert response.json()["ok"] is True
```

## Important Notes

1. **No REST API Tests**: We removed REST API endpoints (/api/expenses/*) as they're not used
2. **Webhook Only**: All bot commands go through /webhook
3. **Real Bot**: Tests use the actual bot initialization (may require valid token)
4. **Async Safe**: Tests handle async bot operations correctly

## Troubleshooting

### Bot Not Initialized
If tests fail with "bot not initialized":
1. Check TELEGRAM_BOT_TOKEN in .env.test
2. Ensure bot can connect to Telegram API
3. Check network connectivity

### Invalid User ID
If tests fail with user ID errors:
1. Verify test user exists in database
2. Check ADMIN_USER_IDS environment variable
3. Ensure user ID format is correct

## Future Enhancements

- [ ] Add tests for conversation flows (multi-message)
- [ ] Test callback button handling
- [ ] Test file upload handling
- [ ] Add performance benchmarks
- [ ] Test rate limiting

---

**Status:** ✅ Ready
**Test Count:** 9 tests
**Coverage:** Webhook and health endpoints
