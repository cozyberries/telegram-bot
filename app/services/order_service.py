"""Order management service with Logfire logging"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database.supabase_client import supabase
from app.database.models import Order, OrderStats

logger = logging.getLogger(__name__)


async def get_orders(
    limit: int = 10,
    status: Optional[str] = None,
    customer_email: Optional[str] = None
) -> List[Order]:
    """
    Get orders from database with optional filters
    
    Args:
        limit: Maximum number of orders to return
        status: Filter by order status
        customer_email: Filter by customer email
        
    Returns:
        List of Order objects
    """
    try:
        # Log database operation
        try:
            from app.logging_config import log_database_operation
            with log_database_operation("SELECT", "orders"):
                result = await _fetch_orders(limit, status, customer_email)
                return result
        except ImportError:
            return await _fetch_orders(limit, status, customer_email)
            
    except Exception as e:
        logger.error(f"Error fetching orders: {e}", exc_info=True)
        
        # Log error to Logfire
        try:
            from app.logging_config import log_error
            log_error(e, {"operation": "get_orders", "limit": limit, "status": status})
        except:
            pass
        
        raise


async def _fetch_orders(limit: int, status: Optional[str], customer_email: Optional[str]) -> List[Order]:
    """Internal method to fetch orders"""
    query = supabase.table("orders").select("*")
    
    if status:
        query = query.eq("status", status)
    
    if customer_email:
        query = query.eq("customer_email", customer_email)
    
    query = query.order("created_at", desc=True).limit(limit)
    
    response = query.execute()
    
    return [Order(**order) for order in response.data]


async def get_order_by_id(order_id: str) -> Optional[Order]:
    """
    Get a specific order by ID
    
    Args:
        order_id: Order ID
        
    Returns:
        Order object or None if not found
    """
    try:
        # Log database operation
        try:
            from app.logging_config import log_database_operation
            with log_database_operation("SELECT", "orders", order_id):
                response = supabase.table("orders").select("*").eq("id", order_id).execute()
                
                if response.data:
                    return Order(**response.data[0])
                return None
        except ImportError:
            response = supabase.table("orders").select("*").eq("id", order_id).execute()
            if response.data:
                return Order(**response.data[0])
            return None
            
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}", exc_info=True)
        
        # Log error to Logfire
        try:
            from app.logging_config import log_error
            log_error(e, {"operation": "get_order_by_id", "order_id": order_id})
        except:
            pass
        
        raise


async def update_order_status(order_id: str, status: str, updated_by: str) -> Order:
    """
    Update order status
    
    Args:
        order_id: Order ID
        status: New status
        updated_by: User ID making the update
        
    Returns:
        Updated Order object
    """
    try:
        # Log database operation
        try:
            from app.logging_config import log_database_operation, log_metric
            
            with log_database_operation("UPDATE", "orders", order_id):
                response = supabase.table("orders").update({
                    "status": status,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", order_id).execute()
                
                if not response.data:
                    raise ValueError(f"Order {order_id} not found")
                
                # Log metric
                log_metric("order_status_updated", 1, {"status": status})
                
                return Order(**response.data[0])
                
        except ImportError:
            response = supabase.table("orders").update({
                "status": status,
                "updated_at": datetime.now().isoformat()
            }).eq("id", order_id).execute()
            
            if not response.data:
                raise ValueError(f"Order {order_id} not found")
            
            return Order(**response.data[0])
            
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {e}", exc_info=True)
        
        # Log error to Logfire
        try:
            from app.logging_config import log_error
            log_error(e, {"operation": "update_order_status", "order_id": order_id, "status": status})
        except:
            pass
        
        raise


async def get_order_stats() -> OrderStats:
    """
    Get order statistics
    
    Returns:
        OrderStats object with aggregated data
    """
    try:
        # Get all orders from last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        response = supabase.table("orders").select("*").gte(
            "created_at", thirty_days_ago
        ).execute()
        
        orders = [Order(**order) for order in response.data]
        
        # Calculate stats
        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        
        pending_orders = len([o for o in orders if o.status == "pending"])
        processing_orders = len([o for o in orders if o.status == "processing"])
        completed_orders = len([o for o in orders if o.status == "completed"])
        cancelled_orders = len([o for o in orders if o.status == "cancelled"])
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Log metrics
        try:
            from app.logging_config import log_metric
            log_metric("total_orders", total_orders)
            log_metric("total_revenue", total_revenue)
            log_metric("avg_order_value", avg_order_value)
        except:
            pass
        
        return OrderStats(
            total_orders=total_orders,
            pending_orders=pending_orders,
            processing_orders=processing_orders,
            completed_orders=completed_orders,
            cancelled_orders=cancelled_orders,
            total_revenue=total_revenue,
            average_order_value=avg_order_value
        )
        
    except Exception as e:
        logger.error(f"Error getting order stats: {e}", exc_info=True)
        
        # Log error to Logfire
        try:
            from app.logging_config import log_error
            log_error(e, {"operation": "get_order_stats"})
        except:
            pass
        
        raise
