"""Pydantic schemas for expense operations"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from decimal import Decimal

from app.schemas.common import CommandInput, ListMetadata


class ExpenseInput(CommandInput):
    """Input schema for creating/updating expenses"""
    amount: Decimal = Field(..., gt=0, description="Expense amount (must be positive)")
    description: str = Field(..., min_length=3, max_length=500, description="Expense description")
    transaction_date: Optional[date] = Field(None, description="Transaction date (defaults to today)")
    category: Optional[str] = Field(None, max_length=100, description="Expense category")
    
    @field_validator('transaction_date', mode='before')
    @classmethod
    def set_default_date(cls, v):
        """Set default date to today if not provided"""
        if v is None:
            return date.today()
        if isinstance(v, str):
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v
    
    @field_validator('description')
    @classmethod
    def clean_description(cls, v: str) -> str:
        """Clean and validate description"""
        return v.strip()
    
    @field_validator('category')
    @classmethod
    def clean_category(cls, v: Optional[str]) -> Optional[str]:
        """Clean category if provided"""
        if v:
            return v.strip()
        return v
    
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
    """Response schema for expense operations"""
    id: str
    title: str
    description: str
    amount: Decimal
    transaction_date: date
    category: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    @property
    def formatted_amount(self) -> str:
        """Format amount with currency symbol"""
        return f"₹{self.amount:,.2f}"
    
    @property
    def formatted_date(self) -> str:
        """Format date for display"""
        return self.transaction_date.strftime("%d %b %Y")
    
    def to_telegram_message(self) -> str:
        """Convert to formatted Telegram message"""
        message = (
            f"💳 *{self.title}*\n\n"
            f"*Amount:* {self.formatted_amount}\n"
            f"*Date:* {self.formatted_date}\n"
        )
        
        if self.category:
            message += f"*Category:* {self.category}\n"
        
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


class ExpenseListResponse(BaseModel):
    """Response schema for listing expenses"""
    expenses: List[ExpenseResponse]
    metadata: ListMetadata
    
    def to_telegram_message(self) -> str:
        """Convert to formatted Telegram message"""
        if not self.expenses:
            return "No expenses found."
        
        message = f"📋 *Recent Expenses*\n\n_Found {self.metadata.total} items_\n"
        
        for expense in self.expenses:
            message += f"\n{expense.to_telegram_message()}\n---\n"
        
        return message


class ExpenseDeleteResponse(BaseModel):
    """Response schema for deleting an expense"""
    success: bool
    expense_id: str
    title: str
    amount: Decimal
    
    def to_telegram_message(self) -> str:
        """Convert to formatted Telegram message"""
        if self.success:
            return (
                f"✅ Expense deleted successfully!\n\n"
                f"Deleted: {self.title}\n"
                f"Amount: ₹{self.amount:,.2f}"
            )
        return "❌ Failed to delete expense"
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ExpenseStats(BaseModel):
    """Response schema for expense statistics"""
    total_expenses: int
    total_amount: Decimal
    average_expense: Decimal
    
    def to_telegram_message(self) -> str:
        """Convert to formatted Telegram message"""
        return (
            "📊 *Expense Statistics*\n\n"
            f"*Total Expenses:* {self.total_expenses}\n"
            f"*Total Amount:* ₹{self.total_amount:,.2f}\n"
            f"*Avg Expense:* ₹{self.average_expense:,.2f}\n"
        )
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
