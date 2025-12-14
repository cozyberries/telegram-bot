# Simplified Expense Schema

## Overview
The expense table has been simplified to contain only essential fields, removing all foreign key constraints and unnecessary complexity.

## New Simplified Schema

```sql
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    expense_date DATE NOT NULL,
    paid_by UUID NOT NULL,  -- No foreign key constraint
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_expenses_paid_by ON expenses(paid_by);
CREATE INDEX idx_expenses_expense_date ON expenses(expense_date DESC);
CREATE INDEX idx_expenses_created_at ON expenses(created_at DESC);
```

## Migration SQL

Run this SQL in your Supabase SQL Editor to migrate to the simplified schema:

```sql
-- Step 1: Drop old tables if they exist
DROP TABLE IF EXISTS expense_attachments CASCADE;
DROP TABLE IF EXISTS expense_categories CASCADE;

-- Step 2: Create new simplified expenses table
CREATE TABLE IF NOT EXISTS expenses_new (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    expense_date DATE NOT NULL,
    paid_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Migrate data from old expenses table if it exists
INSERT INTO expenses_new (id, title, description, amount, expense_date, paid_by, created_at, updated_at)
SELECT 
    id,
    title,
    COALESCE(description, title) as description,
    amount,
    COALESCE(expense_date, CURRENT_DATE) as expense_date,
    COALESCE(user_id, paid_by, '00000000-0000-0000-0000-000000000000'::UUID) as paid_by,
    created_at,
    updated_at
FROM expenses
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'expenses');

-- Step 4: Drop old expenses table and rename new one
DROP TABLE IF EXISTS expenses CASCADE;
ALTER TABLE expenses_new RENAME TO expenses;

-- Step 5: Create indexes
CREATE INDEX idx_expenses_paid_by ON expenses(paid_by);
CREATE INDEX idx_expenses_expense_date ON expenses(expense_date DESC);
CREATE INDEX idx_expenses_created_at ON expenses(created_at DESC);

-- Step 6: Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Step 7: Enable RLS (Row Level Security)
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

-- Step 8: Create RLS policies
CREATE POLICY "Users can view their own expenses"
    ON expenses FOR SELECT
    USING (paid_by = auth.uid());

CREATE POLICY "Users can create their own expenses"
    ON expenses FOR INSERT
    WITH CHECK (paid_by = auth.uid());

CREATE POLICY "Users can update their own expenses"
    ON expenses FOR UPDATE
    USING (paid_by = auth.uid());

CREATE POLICY "Users can delete their own expenses"
    ON expenses FOR DELETE
    USING (paid_by = auth.uid());
```

## What Was Removed

1. **expense_categories table** - Categories are no longer stored
2. **expense_attachments table** - Attachments are no longer supported
3. **Foreign key constraints** - `paid_by` is now just a UUID field without FK
4. **Complex fields removed**:
   - category / category_id
   - payment_method
   - status / priority
   - vendor
   - receipt_url
   - notes / tags
   - approval fields

## What Remains

Only the essential expense tracking fields:
- **id**: Unique identifier
- **title**: Short expense title
- **description**: Full expense description
- **amount**: Expense amount (must be positive)
- **expense_date**: Date of the expense
- **paid_by**: User ID who paid (no FK constraint)
- **created_at**: When record was created
- **updated_at**: When record was last updated

## Benefits

✅ **Simplified**: No complex relationships or constraints  
✅ **Fast**: Fewer indexes, no FK lookups  
✅ **Flexible**: Easy to modify without cascade issues  
✅ **Clear**: Only fields that matter for basic expense tracking  
✅ **Independent**: No dependencies on other tables  

## Python Schema Updates

The Python schemas and services have been updated to match:

- `app/schemas/expenses.py` - Simplified to match new fields
- `app/services/expense_service.py` - Updated to work with new schema
- `tests/test_expense_api_integration.py` - Tests updated accordingly

## Testing

Run the integration tests to validate everything works:

```bash
cd /Users/abdul.azeez/Personal/cozyberries/telegram-bot
python -m pytest tests/test_expense_api_integration.py -v
```

All 17 tests should pass with the simplified schema.
