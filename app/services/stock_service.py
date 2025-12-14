"""Stock management service"""

from app.services.product_service import (
    get_products,
    get_low_stock_products,
    update_product_stock,
    get_product_by_id,
)

# Re-export for convenience
__all__ = [
    'get_products',
    'get_low_stock_products',
    'update_product_stock',
    'get_product_by_id',
]
