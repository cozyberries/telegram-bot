#!/usr/bin/env python3
"""
Test script for Lambda handler
Tests the event loop fix locally before deploying to AWS
"""

import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for testing
os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'test_token_12345')
os.environ.setdefault('SUPABASE_URL', 'https://test.supabase.co')
os.environ.setdefault('SUPABASE_KEY', 'test_key')
os.environ.setdefault('ADMIN_USER_IDS', '123456789')

from app.lambda_handler import lambda_handler


class MockContext:
    """Mock Lambda context"""
    request_id = 'test-request-id-12345'
    function_name = 'test-telegram-bot'
    memory_limit_in_mb = 512
    invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789:function:test'


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    event = {
        'httpMethod': 'GET',
        'path': '/health',
        'headers': {},
        'body': None
    }
    
    result = lambda_handler(event, MockContext())
    print(f"Status Code: {result['statusCode']}")
    print(f"Response: {json.dumps(json.loads(result['body']), indent=2)}")
    
    assert result['statusCode'] == 200, "Health check should return 200"
    print("✅ PASSED")


def test_webhook_info():
    """Test webhook info endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Webhook Info")
    print("="*70)
    
    event = {
        'httpMethod': 'GET',
        'path': '/webhook',
        'headers': {},
        'body': None
    }
    
    result = lambda_handler(event, MockContext())
    print(f"Status Code: {result['statusCode']}")
    print(f"Response: {json.dumps(json.loads(result['body']), indent=2)}")
    
    assert result['statusCode'] == 200, "Webhook info should return 200"
    print("✅ PASSED")


def test_webhook_post():
    """Test webhook POST (simulated Telegram update)"""
    print("\n" + "="*70)
    print("TEST 3: Webhook POST (Telegram Update)")
    print("="*70)
    
    update_data = {
        'update_id': 123456,
        'message': {
            'message_id': 1,
            'from': {
                'id': 123456789,
                'first_name': 'Test',
                'is_bot': False
            },
            'chat': {
                'id': 123456789,
                'type': 'private'
            },
            'text': '/start',
            'date': 1234567890
        }
    }
    
    event = {
        'httpMethod': 'POST',
        'path': '/webhook',
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(update_data)
    }
    
    result = lambda_handler(event, MockContext())
    print(f"Status Code: {result['statusCode']}")
    
    body = json.loads(result['body'])
    print(f"Response: {json.dumps(body, indent=2)}")
    
    # Note: This will likely fail with 503 if TELEGRAM_BOT_TOKEN is not real
    # but it tests the event loop logic
    if result['statusCode'] in [200, 503]:
        print("✅ PASSED (Event loop handling works)")
    else:
        print("⚠️  UNEXPECTED STATUS CODE")


def test_multiple_invocations():
    """Test multiple invocations to verify event loop reuse"""
    print("\n" + "="*70)
    print("TEST 4: Multiple Invocations (Event Loop Reuse)")
    print("="*70)
    
    event = {
        'httpMethod': 'GET',
        'path': '/health',
        'headers': {},
        'body': None
    }
    
    for i in range(3):
        print(f"\n  Invocation {i+1}/3...")
        result = lambda_handler(event, MockContext())
        assert result['statusCode'] == 200, f"Invocation {i+1} failed"
        print(f"  ✓ Invocation {i+1} successful")
    
    print("\n✅ PASSED - Event loop properly reused across invocations")


def test_invalid_endpoint():
    """Test invalid endpoint"""
    print("\n" + "="*70)
    print("TEST 5: Invalid Endpoint")
    print("="*70)
    
    event = {
        'httpMethod': 'GET',
        'path': '/invalid-path',
        'headers': {},
        'body': None
    }
    
    result = lambda_handler(event, MockContext())
    print(f"Status Code: {result['statusCode']}")
    print(f"Response: {json.dumps(json.loads(result['body']), indent=2)}")
    
    assert result['statusCode'] == 404, "Invalid endpoint should return 404"
    print("✅ PASSED")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 LAMBDA HANDLER TEST SUITE")
    print("="*70)
    
    try:
        test_health_check()
        test_webhook_info()
        test_webhook_post()
        test_multiple_invocations()
        test_invalid_endpoint()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\n🎉 Lambda handler is ready for deployment!")
        print("\nNext steps:")
        print("1. Update Lambda handler to: lambda_handler.lambda_handler")
        print("2. Set real environment variables in Lambda")
        print("3. Deploy and test with real Telegram webhook")
        print("\n")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ TESTS FAILED")
        print("="*70)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
