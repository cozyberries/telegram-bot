"""Configuration management for Telegram bot"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Telegram Configuration
    telegram_bot_token: Optional[str] = None
    admin_telegram_user_ids: Optional[str] = None
    
    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # Server Configuration
    bot_webhook_url: str = ""
    log_level: str = "INFO"
    
    # Vercel Configuration (automatically set by Vercel)
    vercel_url: str = ""
    
    model_config = SettingsConfigDict(
        env_file=[".env.test", ".env"] if os.getenv("TESTING") == "true" else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def admin_user_ids(self) -> List[int]:
        """Parse and return list of admin Telegram user IDs"""
        if not self.admin_telegram_user_ids:
            return []
        
        try:
            return [
                int(user_id.strip())
                for user_id in self.admin_telegram_user_ids.split(",")
                if user_id.strip()
            ]
        except ValueError as e:
            return []
    
    @property
    def webhook_url(self) -> str:
        """Get the webhook URL, preferring explicit config over Vercel URL"""
        if self.bot_webhook_url:
            return self.bot_webhook_url
        
        if self.vercel_url:
            return f"https://{self.vercel_url}/webhook"
        
        return ""
    
    def is_configured(self) -> bool:
        """Check if critical configuration is present"""
        return bool(
            self.telegram_bot_token and
            self.supabase_url and
            self.supabase_service_role_key and
            self.admin_telegram_user_ids
        )


# Global settings instance - will not fail if env vars missing
try:
    settings = Settings()
except Exception:
    # Create empty settings if loading fails
    settings = Settings(
        telegram_bot_token="",
        admin_telegram_user_ids="",
        supabase_url="",
        supabase_service_role_key=""
    )
