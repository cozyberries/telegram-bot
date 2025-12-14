"""Script to setup Telegram webhook"""

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings


async def set_webhook(webhook_url: str = None):
    """
    Set Telegram webhook
    
    Args:
        webhook_url: Optional webhook URL (defaults to config)
    """
    url = webhook_url or settings.webhook_url
    
    if not url:
        print("❌ No webhook URL configured!")
        print("Set BOT_WEBHOOK_URL environment variable or provide URL as argument")
        return False
    
    api_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/setWebhook"
    
    print(f"Setting webhook to: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                json={"url": url}
            )
            
            result = response.json()
            
            if result.get("ok"):
                print("✅ Webhook set successfully!")
                print(f"Description: {result.get('description', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to set webhook: {result.get('description')}")
                return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def get_webhook_info():
    """Get current webhook information"""
    api_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getWebhookInfo"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            result = response.json()
            
            if result.get("ok"):
                info = result.get("result", {})
                print("\n📊 Current Webhook Info:")
                print(f"URL: {info.get('url', 'Not set')}")
                print(f"Has Custom Certificate: {info.get('has_custom_certificate', False)}")
                print(f"Pending Update Count: {info.get('pending_update_count', 0)}")
                
                if info.get('last_error_date'):
                    print(f"Last Error: {info.get('last_error_message')}")
                
                return info
            else:
                print(f"❌ Failed to get webhook info: {result.get('description')}")
                return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def delete_webhook():
    """Delete webhook (use for polling mode)"""
    api_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/deleteWebhook"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url)
            result = response.json()
            
            if result.get("ok"):
                print("✅ Webhook deleted successfully!")
                return True
            else:
                print(f"❌ Failed to delete webhook: {result.get('description')}")
                return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Telegram bot webhook")
    parser.add_argument(
        "action",
        choices=["set", "info", "delete"],
        help="Action to perform"
    )
    parser.add_argument(
        "--url",
        help="Webhook URL (for set action)"
    )
    
    args = parser.parse_args()
    
    print("🤖 CozyBerries Telegram Bot - Webhook Manager\n")
    
    if args.action == "set":
        await set_webhook(args.url)
    elif args.action == "info":
        await get_webhook_info()
    elif args.action == "delete":
        await delete_webhook()


if __name__ == "__main__":
    asyncio.run(main())
