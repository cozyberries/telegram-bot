"""Pydantic models matching TypeScript interfaces from the admin app"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Order Models
# ============================================================================

OrderStatus = Literal[
    "payment_pending",
    "payment_confirmed",
    "processing",
    "shipped",
    "delivered",
    "cancelled",
    "refunded"
]

PaymentStatus = Literal[
    "pending",
    "processing",
    "completed",
    "failed",
    "cancelled",
    "refunded",
    "partially_refunded"
]

PaymentMethod = Literal[
    "credit_card",
    "debit_card",
    "net_banking",
    "upi",
    "wallet",
    "cod",
    "emi",
    "bank_transfer"
]

PaymentGateway = Literal[
    "razorpay",
    "stripe",
    "payu",
    "paypal",
    "phonepe",
    "googlepay",
    "paytm",
    "manual"
]


class ShippingAddress(BaseModel):
    """Shipping address information"""
    full_name: str
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None
    address_type: Optional[Literal["home", "office", "other"]] = None
    label: Optional[str] = None


class OrderItem(BaseModel):
    """Individual item in an order"""
    id: str
    name: str
    price: float
    quantity: int
    image: Optional[str] = None
    product_details: Optional[Dict[str, Any]] = None


class OrderBase(BaseModel):
    """Base order information"""
    user_id: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: ShippingAddress
    billing_address: Optional[ShippingAddress] = None
    items: List[OrderItem]
    subtotal: float
    delivery_charge: float
    tax_amount: float
    total_amount: float
    currency: str = "INR"
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Model for creating new orders"""
    pass


class Order(OrderBase):
    """Complete order model with all fields"""
    id: str
    order_number: str
    status: OrderStatus
    estimated_delivery_date: Optional[str] = None
    actual_delivery_date: Optional[str] = None
    tracking_number: Optional[str] = None
    delivery_notes: Optional[str] = None
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


class Payment(BaseModel):
    """Payment information"""
    id: str
    order_id: str
    user_id: str
    internal_reference: str
    payment_reference: str
    payment_method: PaymentMethod
    gateway_provider: PaymentGateway
    status: PaymentStatus
    amount: float
    currency: str = "INR"
    net_amount: float
    gateway_fee: Optional[float] = None
    refunded_amount: Optional[float] = None
    refund_reference: Optional[str] = None
    refund_reason: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    card_type: Optional[str] = None
    upi_id: Optional[str] = None
    bank_name: Optional[str] = None
    bank_reference: Optional[str] = None
    initiated_at: str
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    failure_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Product Models
# ============================================================================

class ProductBase(BaseModel):
    """Base product information"""
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    images: Optional[List[str]] = None


class ProductCreate(ProductBase):
    """Model for creating new products"""
    stock_quantity: int = 0
    is_featured: bool = False
    category_id: Optional[str] = None


class ProductUpdate(BaseModel):
    """Model for updating products"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_featured: Optional[bool] = None
    images: Optional[List[str]] = None


class Product(ProductBase):
    """Complete product model"""
    id: str
    created_at: str
    updated_at: Optional[str] = None
    slug: Optional[str] = None
    stock_quantity: Optional[int] = 0
    is_featured: Optional[bool] = False
    category_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class Category(BaseModel):
    """Product category"""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Expense Models
# ============================================================================

class ExpenseBase(BaseModel):
    """Base expense information - simplified for recording completed transactions"""
    title: str
    description: Optional[str] = None
    amount: float
    transaction_date: str
    category: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """Model for creating new expenses"""
    pass


class ExpenseUpdate(BaseModel):
    """Model for updating expenses"""
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    transaction_date: Optional[str] = None
    category: Optional[str] = None


class Expense(ExpenseBase):
    """Complete expense model"""
    id: str
    user_id: str
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Statistics Models
# ============================================================================

class OrderStats(BaseModel):
    """Order statistics"""
    total_orders: int
    pending_orders: int
    processing_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    average_order_value: float


class ExpenseStats(BaseModel):
    """Expense statistics"""
    total_expenses: int
    total_amount: float


class ProductStats(BaseModel):
    """Product statistics"""
    total_products: int
    active_products: int
    low_stock_count: int
    out_of_stock_count: int
    featured_products: int
