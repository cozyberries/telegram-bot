"""Order service for database operations"""

from typing import List, Optional
from datetime import datetime, timedelta
from app.database.supabase_client import supabase
from app.database.models import Order, OrderCreate, OrderStatus


async def get_orders(
    limit: int = 50,
    offset: int = 0,
    status: Optional[OrderStatus] = None
) -> List[Order]:
    """
    Get list of orders
    
    Args:
        limit: Maximum number of orders to return
        offset: Number of orders to skip
        status: Filter by order status
    
    Returns:
        List of Order objects
    """
    query = supabase.table("orders").select("*")
    
    if status:
        query = query.eq("status", status)
    
    response = query\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    return [Order(**item) for item in response.data]


async def get_order_by_id(order_id: str) -> Optional[Order]:
    """
    Get order by ID
    
    Args:
        order_id: Order ID
    
    Returns:
        Order object or None if not found
    """
    response = supabase.table("orders")\
        .select("*")\
        .eq("id", order_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Order(**response.data[0])
    return None


async def update_order_status(order_id: str, status: OrderStatus) -> Optional[Order]:
    """
    Update order status
    
    Args:
        order_id: Order ID
        status: New status
    
    Returns:
        Updated Order object or None if not found
    """
    update_data = {"status": status}
    
    # Set delivered date if status is delivered
    if status == "delivered":
        update_data["actual_delivery_date"] = datetime.now().isoformat()
    
    response = supabase.table("orders")\
        .update(update_data)\
        .eq("id", order_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Order(**response.data[0])
    return None


async def get_recent_orders(days: int = 7) -> List[Order]:
    """
    Get orders from the last N days
    
    Args:
        days: Number of days to look back
    
    Returns:
        List of recent orders
    """
    since_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    response = supabase.table("orders")\
        .select("*")\
        .gte("created_at", since_date)\
        .order("created_at", desc=True)\
        .execute()
    
    return [Order(**item) for item in response.data]


async def get_orders_by_status(status: OrderStatus) -> List[Order]:
    """
    Get all orders with a specific status
    
    Args:
        status: Order status to filter by
    
    Returns:
        List of orders with that status
    """
    response = supabase.table("orders")\
        .select("*")\
        .eq("status", status)\
        .order("created_at", desc=True)\
        .execute()
    
    return [Order(**item) for item in response.data]


async def get_order_count(status: Optional[OrderStatus] = None) -> int:
    """Get total number of orders, optionally filtered by status"""
    query = supabase.table("orders").select("id", count="exact")
    
    if status:
        query = query.eq("status", status)
    
    response = query.execute()
    return response.count or 0


async def get_total_revenue() -> float:
    """Calculate total revenue from all completed orders"""
    response = supabase.table("orders")\
        .select("total_amount")\
        .in_("status", ["delivered", "payment_confirmed"])\
        .execute()
    
    return sum(order["total_amount"] for order in response.data)
