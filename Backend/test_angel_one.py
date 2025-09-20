#!/usr/bin/env python3
"""
Test script for Angel One API integration
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(method, url, params=None, data=None, expected_status=200):
    """Test a single endpoint"""
    try:
        full_url = f"{BASE_URL}{url}"
        print(f"Testing {method} {url}...")
        
        if method == "GET":
            response = requests.get(full_url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(full_url, json=data, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ {method} {url} - Status: {response.status_code}")
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"   Response keys: {list(data.keys())}")
                else:
                    print(f"   Response type: {type(data)}")
            except:
                print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ {method} {url} - Status: {response.status_code} (Expected: {expected_status})")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {url} - Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ {method} {url} - Error: {str(e)}")
        return False

def main():
    """Run Angel One API tests"""
    print("🚀 Testing Angel One API Integration")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test Angel One status
    print("\n👼 Testing Angel One Status...")
    test_endpoint("GET", "/angel-one/status")
    
    # Test Angel One market status
    print("\n📊 Testing Angel One Market Status...")
    test_endpoint("GET", "/angel-one/market-status")
    
    # Test Angel One indices
    print("\n📈 Testing Angel One Indices...")
    test_endpoint("GET", "/angel-one/indices")
    
    # Test Angel One quotes for Indian stocks
    print("\n💰 Testing Angel One Quotes...")
    test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    for symbol in test_symbols:
        test_endpoint("GET", f"/angel-one/quote/{symbol}")
    
    # Test Angel One historical data
    print("\n📊 Testing Angel One Historical Data...")
    for symbol in test_symbols[:2]:  # Test first 2 symbols
        test_endpoint("GET", f"/angel-one/historical/{symbol}", 
                     params={"interval": "1d", "period": "1mo"})
    
    # Test NSE/BSE market status through main endpoints
    print("\n🏛️ Testing NSE/BSE Market Status...")
    test_endpoint("GET", "/market/status/nse")
    test_endpoint("GET", "/market/summary/nse")
    test_endpoint("GET", "/market/status/bse")
    test_endpoint("GET", "/market/summary/bse")
    
    print("\n" + "=" * 50)
    print("✅ Angel One API testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
