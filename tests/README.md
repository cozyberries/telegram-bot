# Integration Tests - True Integration Testing

## Overview

These tests use the **real FastAPI application** with **real Supabase database connections**. No mocking is performed - these are true integration tests that validate the complete expense API flow.

## ✅ What Was Created

### 1. FastAPI Expense Routes (`app/routers/expenses.py`)
Complete REST API for expense management:
- `POST /api/expenses/` - Create expense
- `GET /api/expenses/` - List expenses (with pagination & filtering)
- `GET /api/expenses/{id}` - Get expense by ID
- `PUT /api/expenses/{id}` - Update expense
- `POST /api/expenses/{id}/approve` - Approve expense
- `POST /api/expenses/{id}/reject` - Reject expense
- `GET /api/expenses/pending/list` - Get pending expenses
- `GET /api/expenses/stats/count` - Get expense count
- `GET /api/expenses/stats/total-amount` - Get total expense amount

### 2. Test Suite (`tests/test_expense_api.py`)
**23 integration tests** covering:
- ✅ Create, read, update operations
- ✅ Approval and rejection workflows
- ✅ Pagination and filtering
- ✅ Statistics endpoints
- ✅ Data validation
- ✅ Error handling (404, 422, 500)
- ✅ General API endpoints (health, root, bot-info, webhook)

### 3. Test Configuration (`tests/conftest.py`)
- Real FastAPI app import
- Real Supabase connection
- Test data fixtures
- No mocking of any modules

## 🚀 Setup Instructions

### 1. Configure Test Database

Create a `.env.test` file with your **test Supabase instance credentials**:

```bash
# Copy the example file
cp env.test.example .env.test

# Edit with your test database credentials
nano .env.test
```

**Important**: Use a separate Supabase project for testing to avoid affecting production data.

Required variables in `.env.test`:
```bash
TESTING=true
TELEGRAM_BOT_TOKEN=test_bot_token

# Test Supabase instance (create a separate project for testing)
TEST_SUPABASE_URL=https://your-test-project.supabase.co
TEST_SUPABASE_KEY=your_test_supabase_anon_or_service_key
SUPABASE_URL=https://your-test-project.supabase.co
SUPABASE_KEY=your_test_supabase_anon_or_service_key

ADMIN_USER_IDS=123456789,987654321
```

### 2. Set Up Test Database Schema

Ensure your test Supabase instance has the required schema:

```sql
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    amount NUMERIC NOT NULL,
    category TEXT NOT NULL,
    category_id UUID,
    priority TEXT NOT NULL,
    expense_date TIMESTAMP NOT NULL,
    vendor TEXT,
    payment_method TEXT NOT NULL,
    receipt_url TEXT,
    notes TEXT,
    tags TEXT[],
    status TEXT NOT NULL DEFAULT 'pending',
    approved_by TEXT,
    approved_at TIMESTAMP,
    rejected_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_expenses_status ON expenses(status);
CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_created_at ON expenses(created_at DESC);
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Tests

```bash
# Run all expense API tests
pytest tests/test_expense_api.py -v

# Run specific test class
pytest tests/test_expense_api.py::TestExpenseAPIRoutes -v

# Run specific test
pytest tests/test_expense_api.py::TestExpenseAPIRoutes::test_create_expense_success -v

# Run with coverage
pytest tests/test_expense_api.py --cov=app/routers --cov-report=html

# Run and see print statements
pytest tests/test_expense_api.py -v -s
```

## 📋 Test Categories

### TestExpenseAPIRoutes (16 tests)
Tests for all expense CRUD operations:
- Create expense (success & validation)
- List expenses (with pagination, filtering)
- Get expense by ID
- Update expense
- Approve/reject expense
- Get pending expenses
- Statistics (count, total amount)

### TestExpenseAPIValidation (3 tests)
Data validation tests:
- Invalid category
- Invalid priority
- Missing required fields

### TestGeneralAPIEndpoints (4 tests)
General API health checks:
- Health check endpoint
- Root endpoint
- Bot info endpoint
- Webhook info endpoint

## 🎯 Key Features

### 1. True Integration Testing
- **No mocking**: Tests use real FastAPI app and real Supabase database
- **Real routes**: Tests actual HTTP endpoints via TestClient
- **Real validation**: Pydantic models validate data
- **Real database**: All CRUD operations hit actual Supabase

### 2. Complete API Coverage
- All expense endpoints tested
- CRUD operations validated
- Status workflows (pending → approved/rejected)
- Statistics and aggregation endpoints
- Error handling (404, 422, 500)

### 3. Production-Ready
- Clean test data (marked as "test" for easy cleanup)
- Proper HTTP status code validation
- Response structure validation
- Edge case handling

## 🔧 Test Data Management

### Creating Test Data
Tests create real data in your test database. Each test that creates data marks it with:
- Title contains "Test"
- Tags include `["test", "integration"]`
- Notes say "Test expense - safe to delete"

### Cleaning Up Test Data
You can clean up test data with:

```sql
-- Delete all test expenses
DELETE FROM expenses WHERE tags @> ARRAY['test', 'integration'];

-- Or delete all expenses from test runs
DELETE FROM expenses WHERE notes LIKE '%Test expense%';
```

## ⚠️ Important Notes

### 1. Separate Test Database
Always use a separate Supabase project/database for testing:
- ✅ Create a new Supabase project specifically for testing
- ✅ Use different credentials in `.env.test`
- ❌ Never point tests at production database

### 2. Database State
Tests create and modify real data:
- Each test may create new expense records
- Approval/rejection tests modify expense status
- Use proper cleanup between test runs

### 3. Rate Limits
Be aware of Supabase rate limits:
- Running many tests repeatedly may hit rate limits
- Use pagination wisely in list tests
- Consider adding delays for large test suites

### 4. Async Operations
The FastAPI app uses async operations:
- Tests run synchronously via TestClient
- TestClient handles async route conversion
- No special async test configuration needed

## 📊 Expected Test Results

When run against a properly configured test database:

```bash
================================= test session starts ==================================
collected 23 items

tests/test_expense_api.py::TestExpenseAPIRoutes::test_create_expense_success PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_create_expense_validation_error PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_expenses_list PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_expenses_with_pagination PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_expenses_with_status_filter PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_expense_by_id_not_found PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_update_expense PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_update_expense_not_found PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_approve_expense PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_approve_expense_not_found PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_reject_expense PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_pending_expenses PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_expense_count PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_expense_count_by_status PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_total_expense_amount PASSED
tests/test_expense_api.py::TestExpenseAPIRoutes::test_get_total_amount_by_status PASSED
tests/test_expense_api.py::TestExpenseAPIValidation::test_create_expense_invalid_category PASSED
tests/test_expense_api.py::TestExpenseAPIValidation::test_create_expense_invalid_priority PASSED
tests/test_expense_api.py::TestExpenseAPIValidation::test_create_expense_missing_required_fields PASSED
tests/test_expense_api.py::TestGeneralAPIEndpoints::test_health_check_endpoint PASSED
tests/test_expense_api.py::TestGeneralAPIEndpoints::test_root_endpoint PASSED
tests/test_expense_api.py::TestGeneralAPIEndpoints::test_bot_info_endpoint PASSED
tests/test_expense_api.py::TestGeneralAPIEndpoints::test_webhook_get_info PASSED

==================================== 23 passed in 2.45s ================================
```

## 🚨 Troubleshooting

### Tests Failing with 500 Errors
- Check `.env.test` has correct Supabase credentials
- Verify test database schema is set up correctly
- Check Supabase project is active and accessible
- Review Supabase logs for detailed error messages

### Connection Errors
- Ensure `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check network connectivity to Supabase
- Verify Supabase project isn't paused (free tier)

### Validation Errors (422)
- Review the expense model requirements
- Check all required fields are provided
- Verify enum values (category, priority, etc.) are valid

### ImportError for telegram module
```bash
pip install python-telegram-bot==21.9
```

## 📚 Additional Resources

- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Test Suite Status**: ✅ Ready for use with real database
**Total Tests**: 23
**Coverage**: Complete expense API + general endpoints
**Mocking**: None - true integration tests
