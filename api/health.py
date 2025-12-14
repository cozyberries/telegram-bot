"""Health check endpoint for Vercel"""

import json
from http.server import BaseHTTPRequestHandler
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    """Health check handler"""
    
    def do_GET(self):
        """Handle health check requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "service": "CozyBerries Telegram Bot",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        self.wfile.write(json.dumps(response).encode())
