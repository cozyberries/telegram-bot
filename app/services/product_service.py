"""Product service for database operations"""

from typing import List, Optional, Dict, Any
from app.database.supabase_client import supabase
from app.database.models import Product, ProductCreate, ProductUpdate


async def get_products(limit: int = 50, offset: int = 0) -> List[Product]:
    """
    Get list of products
    
    Args:
        limit: Maximum number of products to return
        offset: Number of products to skip
    
    Returns:
        List of Product objects
    """
    response = supabase.table("products")\
        .select("*")\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    return [Product(**item) for item in response.data]


async def get_product_by_id(product_id: str) -> Optional[Product]:
    """
    Get product by ID
    
    Args:
        product_id: Product ID
    
    Returns:
        Product object or None if not found
    """
    response = supabase.table("products")\
        .select("*")\
        .eq("id", product_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Product(**response.data[0])
    return None


async def search_products(query: str, limit: int = 20) -> List[Product]:
    """
    Search products by name or description
    
    Args:
        query: Search query
        limit: Maximum results
    
    Returns:
        List of matching products
    """
    response = supabase.table("products")\
        .select("*")\
        .or_(f"name.ilike.%{query}%,description.ilike.%{query}%")\
        .limit(limit)\
        .execute()
    
    return [Product(**item) for item in response.data]


async def create_product(product_data: ProductCreate) -> Product:
    """
    Create a new product
    
    Args:
        product_data: Product creation data
    
    Returns:
        Created Product object
    """
    # Generate slug from name
    slug = product_data.name.lower().replace(' ', '-').replace('/', '-')
    
    data = {
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "slug": slug,
        "stock_quantity": product_data.stock_quantity,
        "is_featured": product_data.is_featured,
        "category_id": product_data.category_id,
        "images": product_data.images or [],
    }
    
    response = supabase.table("products")\
        .insert(data)\
        .execute()
    
    return Product(**response.data[0])


async def update_product(product_id: str, product_data: ProductUpdate) -> Optional[Product]:
    """
    Update an existing product
    
    Args:
        product_id: Product ID
        product_data: Product update data
    
    Returns:
        Updated Product object or None if not found
    """
    # Build update dict with only provided fields
    update_data = {}
    for field, value in product_data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if not update_data:
        return await get_product_by_id(product_id)
    
    response = supabase.table("products")\
        .update(update_data)\
        .eq("id", product_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Product(**response.data[0])
    return None


async def delete_product(product_id: str) -> bool:
    """
    Delete a product
    
    Args:
        product_id: Product ID
    
    Returns:
        True if deleted successfully
    """
    response = supabase.table("products")\
        .delete()\
        .eq("id", product_id)\
        .execute()
    
    return len(response.data) > 0


async def update_product_stock(product_id: str, quantity: int) -> Optional[Product]:
    """
    Update product stock quantity
    
    Args:
        product_id: Product ID
        quantity: New stock quantity
    
    Returns:
        Updated Product object or None if not found
    """
    response = supabase.table("products")\
        .update({"stock_quantity": quantity})\
        .eq("id", product_id)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return Product(**response.data[0])
    return None


async def get_low_stock_products(threshold: int = 10) -> List[Product]:
    """
    Get products with stock below threshold
    
    Args:
        threshold: Stock quantity threshold
    
    Returns:
        List of low stock products
    """
    response = supabase.table("products")\
        .select("*")\
        .lte("stock_quantity", threshold)\
        .order("stock_quantity", desc=False)\
        .execute()
    
    return [Product(**item) for item in response.data]


async def get_product_count() -> int:
    """Get total number of products"""
    response = supabase.table("products")\
        .select("id", count="exact")\
        .execute()
    
    return response.count or 0
