#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Quick Test Script for Fixed Endpoints
# Tests the most critical fixes

import requests
import json

def test_endpoint(url, method="GET", params=None, data=None):
    """Test a single endpoint"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, params=params, timeout=10)
        
        print(f"{'✅' if response.status_code == 200 else '❌'} {method} {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text[:100]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ {method} {url}")
        print(f"   Error: {str(e)}")
        return False

def main():
    base_url = "http://localhost:8000"
    
    print("🧪 Quick Test of Fixed Endpoints")
    print("=" * 50)
    
    # Test critical fixes with Indian stocks
    tests = [
        ("GET", f"{base_url}/news", {"limit": 5}, None),
        ("GET", f"{base_url}/ask", {"q": "What is RELIANCE.NS?"}, None),
        ("GET", f"{base_url}/volume-analysis/RELIANCE.NS", None, None),
        ("GET", f"{base_url}/analysis/RELIANCE.NS", None, None),
        ("GET", f"{base_url}/stocks/RELIANCE.NS/historical", None, None),
        ("GET", f"{base_url}/ai-signals/RELIANCE.NS", None, None),
        ("GET", f"{base_url}/domain-overview", None, None),
        ("GET", f"{base_url}/market/summary", None, None),
        ("GET", f"{base_url}/ownership/RELIANCE.NS", None, None),
        ("GET", f"{base_url}/quote/RELIANCE.NS/sustainability", None, None),
        ("GET", f"{base_url}/patterns/RELIANCE.NS", None, None),
        ("GET", f"{base_url}/currency/rate", None, None),
        ("GET", f"{base_url}/currency/convert", {"amount": 100}, None),
    ]
    
    passed = 0
    total = len(tests)
    
    for method, url, params, data in tests:
        if test_endpoint(url, method, params, data):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All critical fixes working!")
    else:
        print("⚠️  Some issues remain")

if __name__ == "__main__":
    main()
