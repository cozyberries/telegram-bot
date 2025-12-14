"""Help endpoint - returns available bot commands"""

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Handle help requests"""
    
    def do_GET(self):
        """Return bot commands and help"""
        try:
            help_data = {
                "bot": "CozyBerries Assistant",
                "description": "Telegram bot for managing CozyBerries operations",
                "commands": {
                    "general": {
                        "/start": "Show all available commands and welcome message"
                    },
                    "products": {
                        "/products": "List all products",
                        "/add_product": "Add a new product",
                        "/edit_product": "Edit an existing product",
                        "/delete_product": "Delete a product"
                    },
                    "orders": {
                        "/orders": "List all orders",
                        "/order_details": "Get details of a specific order",
                        "/update_order_status": "Update order status"
                    },
                    "expenses": {
                        "/expenses": "List all expenses",
                        "/add_expense": "Add a new expense",
                        "/approve_expense": "Approve a pending expense",
                        "/reject_expense": "Reject a pending expense"
                    },
                    "stock": {
                        "/stock": "View stock levels",
                        "/update_stock": "Update stock quantity",
                        "/low_stock": "View items with low stock"
                    },
                    "analytics": {
                        "/stats": "View statistics and analytics",
                        "/daily_summary": "Get today's summary",
                        "/weekly_report": "Get this week's report"
                    }
                },
                "usage": "Send any command to the bot via Telegram",
                "authentication": "Admin-only access (verified by Telegram user ID)",
                "endpoints": {
                    "/health": "Health check endpoint",
                    "/webhook": "Telegram webhook (POST only)",
                    "/notify-order": "Order notification webhook (POST)",
                    "/help": "This help page",
                    "/docs": "API documentation"
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(help_data, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
