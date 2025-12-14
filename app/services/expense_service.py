"""Expense service for database operations"""

from typing import List, Optional
from datetime import datetime
from app.database.supabase_client import supabase
from app.database.models import Expense, ExpenseCreate, ExpenseUpdate, ExpenseStatus


async def get_expenses(
    limit: int = 50,
    offset: int = 0,
    status: Optional[ExpenseStatus] = None
) -> List[Expense]:
    """Get list of expenses"""
    query = supabase.table("expenses")\
        .select("*, category_data:expense_categories(*)")
    
    if status:
        query = query.eq("status", status)
    
    response = query\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    return [Expense(**item) for item in response.data]


async def get_expense_by_id(expense_id: str) -> Optional[Expense]:
    """Get expense by ID"""
    response = supabase.table("expenses")\
        .select("*, category_data:expense_categories(*)")\
        .eq("id", expense_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Expense(**response.data[0])
    return None


async def create_expense(expense_data: ExpenseCreate, user_id: str) -> Expense:
    """Create a new expense"""
    data = expense_data.model_dump()
    data["user_id"] = user_id
    data["status"] = "pending"
    
    response = supabase.table("expenses")\
        .insert(data)\
        .execute()
    
    return Expense(**response.data[0])


async def update_expense(expense_id: str, expense_data: ExpenseUpdate) -> Optional[Expense]:
    """Update an existing expense"""
    update_data = {}
    for field, value in expense_data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if not update_data:
        return await get_expense_by_id(expense_id)
    
    response = supabase.table("expenses")\
        .update(update_data)\
        .eq("id", expense_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Expense(**response.data[0])
    return None


async def approve_expense(expense_id: str, approver_id: str) -> Optional[Expense]:
    """Approve an expense"""
    update_data = {
        "status": "approved",
        "approved_by": approver_id,
        "approved_at": datetime.now().isoformat()
    }
    
    response = supabase.table("expenses")\
        .update(update_data)\
        .eq("id", expense_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Expense(**response.data[0])
    return None


async def reject_expense(expense_id: str, reason: str) -> Optional[Expense]:
    """Reject an expense"""
    update_data = {
        "status": "rejected",
        "rejected_reason": reason
    }
    
    response = supabase.table("expenses")\
        .update(update_data)\
        .eq("id", expense_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Expense(**response.data[0])
    return None


async def get_pending_expenses() -> List[Expense]:
    """Get all pending expenses"""
    return await get_expenses(status="pending")


async def get_expense_count(status: Optional[ExpenseStatus] = None) -> int:
    """Get total number of expenses"""
    query = supabase.table("expenses").select("id", count="exact")
    
    if status:
        query = query.eq("status", status)
    
    response = query.execute()
    return response.count or 0


async def get_total_expense_amount(status: Optional[ExpenseStatus] = None) -> float:
    """Calculate total expense amount"""
    query = supabase.table("expenses").select("amount")
    
    if status:
        query = query.eq("status", status)
    
    response = query.execute()
    return sum(exp["amount"] for exp in response.data)
