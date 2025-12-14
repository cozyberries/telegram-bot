"""Expense service for database operations"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.database.supabase_client import supabase
from app.database.models import Expense, ExpenseCreate, ExpenseUpdate
from app.schemas.expenses import (
    ExpenseInput,
    ExpenseResponse,
    ExpenseListResponse,
    ExpenseDeleteResponse,
    ExpenseStats
)
from app.schemas.common import ListMetadata


def get_expenses(
    limit: int = 50,
    offset: int = 0
) -> ExpenseListResponse:
    """Get list of expenses with metadata"""
    # Get total count
    count_response = supabase.table("expenses")\
        .select("id", count="exact")\
        .execute()
    
    total = count_response.count or 0
    
    # Get expenses
    response = supabase.table("expenses")\
        .select("*")\
        .order("transaction_date", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    expenses = [ExpenseResponse(**item) for item in response.data]
    
    metadata = ListMetadata(
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )
    
    return ExpenseListResponse(expenses=expenses, metadata=metadata)


def get_expense_by_id(expense_id: str) -> Optional[ExpenseResponse]:
    """Get expense by ID"""
    response = supabase.table("expenses")\
        .select("*")\
        .eq("id", expense_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return ExpenseResponse(**response.data[0])
    return None


def create_expense(expense_input: ExpenseInput) -> ExpenseResponse:
    """Create a new expense from validated input"""
    data = {
        "title": expense_input.title,
        "description": expense_input.description,
        "amount": float(expense_input.amount),
        "transaction_date": expense_input.transaction_date.isoformat(),
        "category": expense_input.category,
        "user_id": expense_input.user_id
    }
    
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    
    response = supabase.table("expenses")\
        .insert(data)\
        .execute()
    
    if not response.data:
        raise ValueError("Failed to create expense - no data returned")
    
    return ExpenseResponse(**response.data[0])


def update_expense(expense_id: str, expense_data: ExpenseUpdate) -> Optional[ExpenseResponse]:
    """Update an existing expense"""
    update_data = {}
    for field, value in expense_data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if not update_data:
        return get_expense_by_id(expense_id)
    
    response = supabase.table("expenses")\
        .update(update_data)\
        .eq("id", expense_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return ExpenseResponse(**response.data[0])
    return None


def delete_expense(expense_id: str) -> Optional[ExpenseDeleteResponse]:
    """Delete an expense and return deletion response"""
    # Get expense first
    expense = get_expense_by_id(expense_id)
    
    if not expense:
        return None
    
    # Delete the expense
    response = supabase.table("expenses")\
        .delete()\
        .eq("id", expense_id)\
        .execute()
    
    success = len(response.data) > 0
    
    return ExpenseDeleteResponse(
        success=success,
        expense_id=expense_id,
        title=expense.title,
        amount=expense.amount
    )


def get_expense_stats() -> ExpenseStats:
    """Get expense statistics"""
    response = supabase.table("expenses")\
        .select("amount")\
        .execute()
    
    total_expenses = len(response.data)
    total_amount = Decimal(sum(exp["amount"] for exp in response.data))
    average_expense = total_amount / total_expenses if total_expenses > 0 else Decimal(0)
    
    return ExpenseStats(
        total_expenses=total_expenses,
        total_amount=total_amount,
        average_expense=average_expense
    )


# Backward compatibility functions
def get_expense_count() -> int:
    """Get total number of expenses (backward compatibility)"""
    response = supabase.table("expenses")\
        .select("id", count="exact")\
        .execute()
    
    return response.count or 0


def get_total_expense_amount() -> float:
    """Calculate total expense amount (backward compatibility)"""
    response = supabase.table("expenses")\
        .select("amount")\
        .execute()
    
    return sum(exp["amount"] for exp in response.data)
