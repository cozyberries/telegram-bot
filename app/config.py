"""Configuration management for Telegram bot"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Telegram Configuration
    telegram_bot_token: str
    admin_telegram_user_ids: str
    
    # Supabase Configuration
    supabase_url: str
    supabase_service_role_key: str
    
    # Server Configuration
    bot_webhook_url: str = ""
    log_level: str = "INFO"
    
    # Vercel Configuration (automatically set by Vercel)
    vercel_url: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
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
            raise ValueError(
                f"Invalid admin user ID format: {self.admin_telegram_user_ids}. "
                f"Expected comma-separated integers. Error: {e}"
            )
    
    @property
    def webhook_url(self) -> str:
        """Get the webhook URL, preferring explicit config over Vercel URL"""
        if self.bot_webhook_url:
            return self.bot_webhook_url
        
        if self.vercel_url:
            return f"https://{self.vercel_url}/api/webhook"
        
        return ""
    
    def validate_config(self) -> None:
        """Validate critical configuration"""
        errors = []
        
        if not self.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if not self.supabase_url:
            errors.append("SUPABASE_URL is required")
        
        if not self.supabase_service_role_key:
            errors.append("SUPABASE_SERVICE_ROLE_KEY is required")
        
        if not self.admin_telegram_user_ids:
            errors.append("ADMIN_TELEGRAM_USER_IDS is required")
        
        try:
            admin_ids = self.admin_user_ids
            if not admin_ids:
                errors.append("At least one admin user ID must be configured")
        except ValueError as e:
            errors.append(str(e))
        
        if errors:
            raise ValueError(
                "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )


# Global settings instance
settings = Settings()
