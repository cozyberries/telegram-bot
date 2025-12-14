# Architecture Documentation

## Overview

The Telegram bot is built using a modular, type-safe architecture with Pydantic models for validation and FastAPI best practices.

## Architecture Layers

### 1. **Handlers Layer** (`app/bot/handlers/`)
- Handles incoming Telegram commands and messages
- Validates user permissions via middleware
- Delegates to service layer for business logic
- Returns formatted responses using Pydantic models

**Example:**
```python
@admin_required
async def list_expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = expense_service.get_expenses(limit=20)
    message = response.to_telegram_message()
    await update.message.reply_text(message, parse_mode="Markdown")
```

### 2. **Services Layer** (`app/services/`)
- Contains business logic
- Interacts with database through Supabase client
- Returns Pydantic response models
- Handles data transformation

**Key Features:**
- Type-safe inputs and outputs
- Centralized error handling
- Reusable business logic

**Example:**
```python
def create_expense(expense_input: ExpenseInput) -> ExpenseResponse:
    data = expense_input.model_dump()
    response = supabase.table("expenses").insert(data).execute()
    return ExpenseResponse(**response.data[0])
```

### 3. **Schemas Layer** (`app/schemas/`)
- Pydantic models for request/response validation
- Input validation with custom validators
- Built-in formatting methods for Telegram messages
- Type safety across the application

**Structure:**
```
app/schemas/
├── __init__.py          # Public API exports
├── common.py            # Shared base models
└── expenses.py          # Expense-specific schemas
```

**Key Models:**
- `ExpenseInput`: Validates and cleans expense creation data
- `ExpenseResponse`: Structured expense data with formatting
- `ExpenseListResponse`: List of expenses with metadata
- `ExpenseStats`: Aggregated statistics

**Example:**
```python
class ExpenseInput(CommandInput):
    amount: Decimal = Field(..., gt=0)
    description: str = Field(..., min_length=3, max_length=500)
    transaction_date: Optional[date] = None
    category: Optional[str] = None
    
    @field_validator('transaction_date', mode='before')
    @classmethod
    def set_default_date(cls, v):
        return v or date.today()
```

### 4. **Parsers & Utilities** (`app/utils/`)

#### **Message Parsers** (`parsers.py`)
- Extract structured data from Telegram messages
- Handle multiple input formats
- Field aliasing for user-friendly input

**Example:**
```python
parser = ExpenseMessageParser()
parsed = parser.parse("""
Amount: 2500
Description: Office supplies
Date: 2025-12-14
""")
# Returns: {amount: Decimal('2500'), description: "Office supplies", ...}
```

**Supported Aliases:**
- Amount: `amount`, `amt`, `price`, `cost`, `total`
- Description: `description`, `desc`, `detail`, `details`, `title`
- Date: `date`, `transaction date`, `expense date`, `when`
- Category: `category`, `cat`, `type`, `tag`

#### **Validators** (`validators.py`)
- Amount validation (handles currency symbols, commas)
- Date validation (multiple formats)
- Command argument parsing

### 5. **Database Models** (`app/database/models.py`)
- ORM-style models for database tables
- Match Supabase schema
- Used for type hints in database operations

### 6. **Middleware** (`app/bot/middleware/`)
- Authentication and authorization
- User info extraction
- Admin-only command protection

## Data Flow

```
User Message
    ↓
Handler (validates input)
    ↓
Parser (extracts data)
    ↓
Pydantic Input Model (validates & cleans)
    ↓
Service Layer (business logic)
    ↓
Database (Supabase)
    ↓
Pydantic Response Model (structures data)
    ↓
to_telegram_message() (formats for display)
    ↓
Telegram Response
```

## Best Practices Implemented

### 1. **Type Safety**
- All functions have type hints
- Pydantic models enforce runtime validation
- Decimal type for currency (avoids float precision issues)

### 2. **Separation of Concerns**
- Handlers: User interaction only
- Services: Business logic only
- Parsers: Data extraction only
- Schemas: Validation and formatting

### 3. **DRY (Don't Repeat Yourself)**
- Reusable base models (`CommandInput`, `TimestampMixin`)
- Shared formatters in Pydantic models
- Generic list responses

### 4. **Error Handling**
- Pydantic validation errors caught and formatted
- User-friendly error messages
- Graceful degradation

### 5. **Modular Design**
- Each module has single responsibility
- Easy to test independently
- Easy to extend with new features

## Adding New Features

### Example: Adding a new "Invoice" entity

1. **Create Schema** (`app/schemas/invoices.py`):
```python
class InvoiceInput(CommandInput):
    amount: Decimal = Field(..., gt=0)
    client_name: str = Field(..., min_length=2)
    due_date: date
    
class InvoiceResponse(BaseModel):
    id: str
    amount: Decimal
    client_name: str
    
    def to_telegram_message(self) -> str:
        return f"📄 Invoice #{self.id}\\n{self.client_name}: ₹{self.amount}"
```

2. **Create Service** (`app/services/invoice_service.py`):
```python
def create_invoice(invoice_input: InvoiceInput) -> InvoiceResponse:
    data = invoice_input.model_dump()
    response = supabase.table("invoices").insert(data).execute()
    return InvoiceResponse(**response.data[0])
```

3. **Create Handler** (`app/bot/handlers/invoices.py`):
```python
@admin_required
async def add_invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Parse, validate, create
    invoice = create_invoice(invoice_input)
    await update.message.reply_text(invoice.to_telegram_message())
```

4. **Register Handler** in `app/bot/bot.py`

## Testing

### Unit Tests
- Test parsers independently
- Test Pydantic validation
- Test service functions

### Integration Tests
- Test full command flow
- Test database operations
- Test error handling

## Performance Considerations

1. **Pagination**: List responses include metadata for pagination
2. **Lazy Loading**: Database queries are optimized
3. **Caching**: Can be added at service layer
4. **Async/Await**: Used where appropriate for I/O operations

## Security

1. **Input Validation**: All inputs validated by Pydantic
2. **SQL Injection**: Protected by Supabase client
3. **Authentication**: Middleware checks for admin users
4. **Type Safety**: Prevents many runtime errors

## Future Enhancements

1. **Caching Layer**: Add Redis for frequently accessed data
2. **Event Sourcing**: Track all changes for audit trail
3. **API Documentation**: Auto-generate from Pydantic models
4. **Background Tasks**: Move heavy operations to Celery
5. **Rate Limiting**: Protect against abuse
6. **Webhooks**: Notify external systems of events
