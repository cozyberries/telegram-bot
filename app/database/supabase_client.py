"""Supabase client setup and management"""

from supabase import create_client, Client
from app.config import settings


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance
    
    Returns:
        Client: Configured Supabase client
    """
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_role_key
    )


# Global client instance (reused across function calls for efficiency)
supabase: Client = get_supabase_client()
