"""Handlers package"""

from app.bot.handlers import start
from app.bot.handlers import products
from app.bot.handlers import orders
from app.bot.handlers import expenses
from app.bot.handlers import stock
from app.bot.handlers import analytics

__all__ = [
    'start',
    'products',
    'orders',
    'expenses',
    'stock',
    'analytics',
]
