"""Script to test Supabase and Telegram connections"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database.supabase_client import supabase
import httpx


async def test_telegram_connection():
    """Test Telegram bot connection"""
    print("🔍 Testing Telegram connection...")
    
    try:
        api_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            result = response.json()
            
            if result.get("ok"):
                bot_info = result.get("result", {})
                print(f"✅ Telegram connection successful!")
                print(f"   Bot: @{bot_info.get('username')}")
                print(f"   Name: {bot_info.get('first_name')}")
                print(f"   ID: {bot_info.get('id')}")
                return True
            else:
                print(f"❌ Telegram connection failed: {result.get('description')}")
                return False
    
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        return False


def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        # Try to query products table
        response = supabase.table("products").select("id").limit(1).execute()
        
        print(f"✅ Supabase connection successful!")
        print(f"   URL: {settings.supabase_url}")
        print(f"   Products accessible: Yes")
        return True
    
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False


def test_configuration():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    
    errors = []
    
    try:
        settings.validate_config()
        print("✅ Configuration valid!")
        print(f"   Admin User IDs: {len(settings.admin_user_ids)} configured")
        return True
    except ValueError as e:
        print(f"❌ Configuration invalid: {e}")
        return False


async def main():
    """Main test function"""
    print("🤖 CozyBerries Telegram Bot - Connection Tester\n")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_configuration()
    
    # Test Telegram
    telegram_ok = await test_telegram_connection()
    
    # Test Supabase
    supabase_ok = test_supabase_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("\n📊 Test Summary:")
    print(f"   Configuration: {'✅' if config_ok else '❌'}")
    print(f"   Telegram: {'✅' if telegram_ok else '❌'}")
    print(f"   Supabase: {'✅' if supabase_ok else '❌'}")
    
    if config_ok and telegram_ok and supabase_ok:
        print("\n✅ All tests passed! Bot is ready to deploy.")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix issues before deploying.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
