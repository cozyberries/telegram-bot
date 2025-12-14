"""Documentation redirector for Vercel"""

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Redirect to FastAPI docs"""
    
    def do_GET(self):
        """Return documentation info"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "CozyBerries Telegram Admin Bot API",
            "version": "1.0.0",
            "documentation": {
                "note": "Full Swagger UI available when running locally",
                "command": "uvicorn app.main:app --reload",
                "local_docs": "http://localhost:8000/docs",
                "local_redoc": "http://localhost:8000/redoc"
            },
            "endpoints": {
                "health": "/health",
                "webhook": "/webhook (POST)",
                "notify_order": "/notify-order (POST)"
            },
            "features": [
                "Products Management",
                "Orders Management",
                "Expenses Management",
                "Stock Management",
                "Analytics",
                "Notifications"
            ]
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
