"""Expense service for database operations"""

from typing import List, Optional
from datetime import datetime
from app.database.supabase_client import supabase
from app.database.models import Expense, ExpenseCreate, ExpenseUpdate


def get_expenses(
    limit: int = 50,
    offset: int = 0
) -> List[Expense]:
    """Get list of expenses"""
    response = supabase.table("expenses")\
        .select("*")\
        .order("transaction_date", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    return [Expense(**item) for item in response.data]


def get_expense_by_id(expense_id: str) -> Optional[Expense]:
    """Get expense by ID"""
    response = supabase.table("expenses")\
        .select("*")\
        .eq("id", expense_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Expense(**response.data[0])
    return None


def create_expense(expense_data: ExpenseCreate, user_id: str) -> Expense:
    """Create a new expense"""
    data = expense_data.model_dump(exclude_none=True)
    data["user_id"] = user_id
    
    # Remove None values to avoid database errors
    data = {k: v for k, v in data.items() if v is not None}
    
    response = supabase.table("expenses")\
        .insert(data)\
        .execute()
    
    if not response.data:
        raise ValueError("Failed to create expense - no data returned")
    
    return Expense(**response.data[0])


def update_expense(expense_id: str, expense_data: ExpenseUpdate) -> Optional[Expense]:
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
        return Expense(**response.data[0])
    return None


def delete_expense(expense_id: str) -> bool:
    """Delete an expense"""
    response = supabase.table("expenses")\
        .delete()\
        .eq("id", expense_id)\
        .execute()
    
    return len(response.data) > 0


def get_expense_count() -> int:
    """Get total number of expenses"""
    response = supabase.table("expenses")\
        .select("id", count="exact")\
        .execute()
    
    return response.count or 0


def get_total_expense_amount() -> float:
    """Calculate total expense amount"""
    response = supabase.table("expenses")\
        .select("amount")\
        .execute()
    
    return sum(exp["amount"] for exp in response.data)
