#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Alpha Vantage API Testing Script for Financial Dashboard
# Tests all Alpha Vantage endpoints specifically
#
# Copyright 2024 Arpit
# Licensed under the Apache License, Version 2.0

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List
import sys

class AlphaVantageTester:
    """Dedicated Alpha Vantage API testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "test_details": []
        }
        
        # Test symbols - using US symbols as Alpha Vantage works best with them
        self.us_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
        self.indian_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS"]
        
    def log_test(self, test_name: str, success: bool, message: str = "", response_data: Any = None):
        """Log test result"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            status = "✅ PASS"
        else:
            self.results["failed"] += 1
            status = "❌ FAIL"
            self.results["errors"].append(f"{test_name}: {message}")
        
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        
        self.results["test_details"].append({
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        })
    
    def test_endpoint(self, method: str, endpoint: str, params: Dict = None, data: Dict = None, 
                     expected_status: int = 200, test_name: str = None) -> bool:
        """Test a single endpoint"""
        if test_name is None:
            test_name = f"{method.upper()} {endpoint}"
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params, timeout=30)
            else:
                self.log_test(test_name, False, f"Unsupported method: {method}")
                return False
            
            success = response.status_code == expected_status
            message = f"Status: {response.status_code} (Expected: {expected_status})"
            
            if success:
                try:
                    response_data = response.json()
                    message += f" | Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}"
                except:
                    message += " | Response: Non-JSON"
            else:
                message += f" | Error: {response.text[:200]}"
            
            self.log_test(test_name, success, message, response.json() if success else None)
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test(test_name, False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test(test_name, False, f"Unexpected error: {str(e)}")
            return False
    
    def test_quote_endpoints(self):
        """Test Alpha Vantage quote endpoints"""
        print("\n💰 Testing Alpha Vantage Quote Endpoints...")
        
        # Test US symbols (should work)
        for symbol in self.us_symbols[:3]:  # Test first 3 US symbols
            self.test_endpoint("GET", f"/alpha-vantage/quote/{symbol}")
        
        # Test Indian symbols (may not work with Alpha Vantage)
        for symbol in self.indian_symbols[:2]:  # Test first 2 Indian symbols
            self.test_endpoint("GET", f"/alpha-vantage/quote/{symbol}")
    
    def test_daily_endpoints(self):
        """Test Alpha Vantage daily data endpoints"""
        print("\n📊 Testing Alpha Vantage Daily Data Endpoints...")
        
        for symbol in self.us_symbols[:3]:
            # Test basic daily data
            self.test_endpoint("GET", f"/alpha-vantage/daily/{symbol}")
            
            # Test with outputsize parameter
            self.test_endpoint("GET", f"/alpha-vantage/daily/{symbol}", 
                              params={"outputsize": "compact"})
            self.test_endpoint("GET", f"/alpha-vantage/daily/{symbol}", 
                              params={"outputsize": "full"})
    
    def test_intraday_endpoints(self):
        """Test Alpha Vantage intraday data endpoints"""
        print("\n⏰ Testing Alpha Vantage Intraday Data Endpoints...")
        
        for symbol in self.us_symbols[:2]:  # Test fewer symbols for intraday
            # Test different intervals
            intervals = ["1min", "5min", "15min", "30min", "60min"]
            for interval in intervals:
                self.test_endpoint("GET", f"/alpha-vantage/intraday/{symbol}", 
                                  params={"interval": interval, "outputsize": "compact"})
    
    def test_technical_indicators(self):
        """Test Alpha Vantage technical indicators"""
        print("\n📈 Testing Alpha Vantage Technical Indicators...")
        
        indicators = ["SMA", "EMA", "RSI", "MACD", "BBANDS", "STOCH", "ADX", "CCI"]
        time_periods = [10, 20, 50]
        
        for symbol in self.us_symbols[:2]:
            for indicator in indicators:
                for time_period in time_periods:
                    self.test_endpoint("GET", f"/alpha-vantage/indicators/{symbol}", 
                                      params={
                                          "function": indicator, 
                                          "time_period": time_period,
                                          "series_type": "close"
                                      })
    
    def test_fundamental_data(self):
        """Test Alpha Vantage fundamental data endpoints"""
        print("\n🏢 Testing Alpha Vantage Fundamental Data...")
        
        for symbol in self.us_symbols[:3]:
            # Test company overview
            self.test_endpoint("GET", f"/alpha-vantage/overview/{symbol}")
            
            # Test earnings calendar
            self.test_endpoint("GET", f"/alpha-vantage/earnings/{symbol}")
    
    def test_news_sentiment(self):
        """Test Alpha Vantage news sentiment"""
        print("\n📰 Testing Alpha Vantage News Sentiment...")
        
        for symbol in self.us_symbols[:2]:
            # Test with different limits
            for limit in [5, 10, 20]:
                self.test_endpoint("GET", f"/alpha-vantage/news/{symbol}", 
                                  params={"limit": limit})
    
    def test_error_handling(self):
        """Test error handling with invalid symbols"""
        print("\n🚫 Testing Error Handling...")
        
        invalid_symbols = ["INVALID", "XYZ123", "NOTFOUND"]
        for symbol in invalid_symbols:
            self.test_endpoint("GET", f"/alpha-vantage/quote/{symbol}", 
                              expected_status=404)
    
    def test_service_status(self):
        """Test if Alpha Vantage service is enabled"""
        print("\n🔧 Testing Alpha Vantage Service Status...")
        
        # Test with a simple symbol to check if service is enabled
        response = self.session.get(f"{self.base_url}/alpha-vantage/quote/AAPL")
        
        if response.status_code == 503:
            self.log_test("Alpha Vantage Service Status", False, 
                         "Alpha Vantage service is not enabled. Check API key configuration.")
        elif response.status_code == 200:
            self.log_test("Alpha Vantage Service Status", True, 
                         "Alpha Vantage service is enabled and working.")
        else:
            self.log_test("Alpha Vantage Service Status", False, 
                         f"Unexpected status code: {response.status_code}")
    
    def run_all_tests(self):
        """Run all Alpha Vantage tests"""
        print("🚀 Starting Alpha Vantage API Testing")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_service_status()
        self.test_quote_endpoints()
        self.test_daily_endpoints()
        self.test_intraday_endpoints()
        self.test_technical_indicators()
        self.test_fundamental_data()
        self.test_news_sentiment()
        self.test_error_handling()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 ALPHA VANTAGE TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(self.results['passed'] / self.results['total_tests'] * 100):.1f}%")
        
        if self.results['errors']:
            print("\n❌ ERRORS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        # Save detailed results
        self.save_results()
        
        return self.results['failed'] == 0
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"alpha_vantage_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Alpha Vantage APIs')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the API (default: http://localhost:8000)')
    parser.add_argument('--symbols', nargs='+', 
                       help='Specific symbols to test (e.g., AAPL MSFT GOOGL)')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick test (fewer symbols and indicators)')
    
    args = parser.parse_args()
    
    # Check if server is running
    try:
        response = requests.get(f"{args.url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server is not responding properly at {args.url}")
            print("Please make sure your FastAPI server is running:")
            print("  cd Backend")
            print("  python main_combined.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {args.url}")
        print("Please make sure your FastAPI server is running:")
        print("  cd Backend")
        print("  python main_combined.py")
        sys.exit(1)
    
    # Run tests
    tester = AlphaVantageTester(args.url)
    
    # Override symbols if provided
    if args.symbols:
        tester.us_symbols = args.symbols
        tester.indian_symbols = []
    
    # Reduce test scope for quick mode
    if args.quick:
        tester.us_symbols = tester.us_symbols[:2]
        tester.indian_symbols = tester.indian_symbols[:1]
    
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All Alpha Vantage tests passed! Your API is working perfectly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some Alpha Vantage tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
