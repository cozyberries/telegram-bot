"""Main entry point for Vercel deployment"""

from app.main import app

# Export for Vercel
handler = app
