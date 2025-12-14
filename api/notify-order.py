"""Vercel serverless function for order notifications"""

import json
import logging
from http.server import BaseHTTPRequestHandler
from app.services.notification_service import send_order_notification
from app.database.models import Order

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """Handle order notification requests from Supabase webhook"""
    
    def do_POST(self):
        """Process order notification request"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(body.decode('utf-8'))
            
            logger.info(f"Received order notification request")
            
            # Extract order data
            # Supabase webhook sends data in different formats depending on configuration
            order_data = data.get('record') or data.get('data') or data
            
            if not order_data:
                raise ValueError("No order data found in request")
            
            # Create Order object
            order = Order(**order_data)
            
            # Send notification asynchronously
            import asyncio
            asyncio.run(send_order_notification(order))
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": True,
                "message": "Notification sent",
                "order_id": order.id
            }).encode())
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}", exc_info=True)
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": False,
                "error": str(e)
            }).encode())
    
    def do_GET(self):
        """Handle GET requests - return endpoint info"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "endpoint": "order-notifications",
            "description": "Receives order notifications from Supabase webhook"
        }
        
        self.wfile.write(json.dumps(response).encode())
