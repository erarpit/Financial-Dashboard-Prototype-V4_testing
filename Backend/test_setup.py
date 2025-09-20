#!/usr/bin/env python3
"""
Test script to verify API setup
"""

import os
from dotenv import load_dotenv

def test_api_setup():
    """Test if API keys are properly configured"""
    print("🔍 Testing API Setup...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test Alpha Vantage
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    print(f"✅ Alpha Vantage API Key: {'✓ Configured' if alpha_key and alpha_key != 'your_alpha_vantage_api_key_here' else '❌ Not configured'}")
    
    # Test Angel One
    angel_api = os.getenv('ANGEL_ONE_API_KEY')
    angel_client = os.getenv('ANGEL_ONE_CLIENT_ID')
    angel_password = os.getenv('ANGEL_ONE_PASSWORD')
    angel_pin = os.getenv('ANGEL_ONE_PIN')
    
    angel_configured = all([angel_api, angel_client, angel_password, angel_pin]) and \
                      all(key != f'your_angel_one_{key.split("_")[-1]}_here' for key in [angel_api, angel_client, angel_password, angel_pin])
    
    print(f"✅ Angel One API: {'✓ Configured' if angel_configured else '❌ Not configured'}")
    if not angel_configured:
        print("   Missing: ANGEL_ONE_API_KEY, ANGEL_ONE_CLIENT_ID, ANGEL_ONE_PASSWORD, ANGEL_ONE_PIN")
    
    # Test Currency
    currency_key = os.getenv('CURRENCY_API_KEY')
    print(f"✅ Currency API: {'✓ Configured' if currency_key and currency_key != 'your_currency_api_key_here' else '❌ Not configured'}")
    
    # Test OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"✅ OpenAI API: {'✓ Configured' if openai_key and openai_key != 'your_openai_api_key_here' else '❌ Not configured'}")
    
    print("=" * 50)
    
    if angel_configured:
        print("🎉 All APIs are configured! You can now test the endpoints.")
    else:
        print("⚠️  Some APIs are not configured. Please update your .env file.")
    
    return angel_configured

if __name__ == "__main__":
    test_api_setup()
