"""
Simplified expense schemas for Telegram bot

Expense table now only has:
- title
- description
- amount
- expense_date
- paid_by (user_id)
"""

from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CommandInput(BaseModel):
    """Base class for command inputs"""
    user_id: str
    username: str


class ExpenseInput(CommandInput):
    """Simplified input schema for creating expenses"""
    amount: Decimal = Field(..., gt=0, description="Expense amount (must be positive)")
    description: str = Field(..., min_length=3, max_length=500, description="Expense description")
    expense_date: date = Field(default_factory=date.today, description="Expense date (defaults to today)")
    
    @field_validator('description')
    @classmethod
    def clean_description(cls, v: str) -> str:
        """Clean and validate description"""
        return v.strip()
    
    @property
    def title(self) -> str:
        """Generate title from description (first 100 chars)"""
        return self.description[:100]
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }


class ExpenseResponse(BaseModel):
    """Simplified response schema for expense operations"""
    id: str
    title: str
    description: str
    amount: Decimal
    expense_date: date
    paid_by: str  # user_id
    created_at: datetime
    updated_at: datetime
    
    @property
    def formatted_amount(self) -> str:
        """Format amount with currency symbol"""
        return f"₹{self.amount:,.2f}"
    
    @property
    def formatted_date(self) -> str:
        """Format date for display"""
        return self.expense_date.strftime("%d %b %Y")
    
    def to_telegram_message(self) -> str:
        """Convert to formatted Telegram message"""
        message = (
            f"💳 *{self.title}*\n\n"
            f"*Amount:* {self.formatted_amount}\n"
            f"*Date:* {self.formatted_date}\n"
        )
        
        if self.description != self.title:
            message += f"\n{self.description}\n"
        
        message += f"\n*ID:* `{self.id}`\n"
        
        return message
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class ExpenseUpdate(BaseModel):
    """Schema for updating expenses"""
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    expense_date: Optional[date] = None


class ExpenseDeleteResponse(BaseModel):
    """Response schema for expense deletion"""
    success: bool
    expense_id: str
    title: str
    amount: Decimal
    
    def to_telegram_message(self) -> str:
        """Format deletion response for Telegram"""
        return (
            f"✅ Expense deleted successfully!\n\n"
            f"*{self.title}*\n"
            f"Amount: ₹{self.amount:,.2f}\n"
            f"ID: `{self.expense_id}`"
        )


class ListMetadata(BaseModel):
    """Metadata for paginated lists"""
    total: int
    limit: int
    offset: int
    has_more: bool


class ExpenseListResponse(BaseModel):
    """Response schema for expense list with pagination"""
    expenses: list[ExpenseResponse]
    metadata: ListMetadata


class ExpenseStats(BaseModel):
    """Simplified expense statistics"""
    total_expenses: int
    total_amount: Decimal
    average_expense: Decimal
    
    def to_telegram_message(self) -> str:
        """Format stats for Telegram display"""
        return (
            f"📊 *Expense Statistics*\n\n"
            f"📝 *Total Expenses:* {self.total_expenses}\n"
            f"💰 *Total Amount:* ₹{self.total_amount:,.2f}\n"
            f"📊 *Avg Expense:* ₹{self.average_expense:,.2f}\n"
        )
