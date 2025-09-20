#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Indian Stocks Alpha Vantage Testing Script
# Tests Alpha Vantage endpoints specifically with Indian stock symbols
#
# Copyright 2024 Arpit
# Licensed under the Apache License, Version 2.0

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import sys

class IndianAlphaVantageTester:
    """Dedicated Indian stocks Alpha Vantage testing class"""
    
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
        
        # Popular Indian stock symbols
        self.indian_symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
            "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS",
            "WIPRO.NS", "ASIANPAINT.NS", "MARUTI.NS", "NESTLEIND.NS", "TITAN.NS"
        ]
        
        # US symbols for comparison
        self.us_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        
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
                    
                    # Check if we got data for Indian symbols
                    if 'alpha_vantage_symbol' in response_data:
                        message += f" | Mapped to: {response_data['alpha_vantage_symbol']}"
                    
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
    
    def test_indian_quotes(self):
        """Test Alpha Vantage quotes for Indian symbols"""
        print("\n🇮🇳 Testing Indian Stock Quotes...")
        
        for symbol in self.indian_symbols[:5]:  # Test first 5 Indian symbols
            self.test_endpoint("GET", f"/alpha-vantage/quote/{symbol}")
    
    def test_us_quotes(self):
        """Test Alpha Vantage quotes for US symbols (for comparison)"""
        print("\n🇺🇸 Testing US Stock Quotes (for comparison)...")
        
        for symbol in self.us_symbols[:3]:  # Test first 3 US symbols
            self.test_endpoint("GET", f"/alpha-vantage/quote/{symbol}")
    
    def test_indian_daily_data(self):
        """Test Alpha Vantage daily data for Indian symbols"""
        print("\n📊 Testing Indian Stock Daily Data...")
        
        for symbol in self.indian_symbols[:3]:  # Test first 3 Indian symbols
            self.test_endpoint("GET", f"/alpha-vantage/daily/{symbol}")
            self.test_endpoint("GET", f"/alpha-vantage/daily/{symbol}", 
                              params={"outputsize": "compact"})
    
    def test_indian_intraday_data(self):
        """Test Alpha Vantage intraday data for Indian symbols"""
        print("\n⏰ Testing Indian Stock Intraday Data...")
        
        for symbol in self.indian_symbols[:2]:  # Test first 2 Indian symbols
            intervals = ["5min", "15min", "30min"]
            for interval in intervals:
                self.test_endpoint("GET", f"/alpha-vantage/intraday/{symbol}", 
                                  params={"interval": interval, "outputsize": "compact"})
    
    def test_indian_technical_indicators(self):
        """Test Alpha Vantage technical indicators for Indian symbols"""
        print("\n📈 Testing Indian Stock Technical Indicators...")
        
        # Test basic indicators that might work with free tier
        basic_indicators = ["SMA", "EMA"]
        time_periods = [20, 50]
        
        for symbol in self.indian_symbols[:2]:
            for indicator in basic_indicators:
                for time_period in time_periods:
                    self.test_endpoint("GET", f"/alpha-vantage/indicators/{symbol}", 
                                      params={
                                          "function": indicator, 
                                          "time_period": time_period,
                                          "series_type": "close"
                                      })
    
    def test_service_status(self):
        """Test if Alpha Vantage service is enabled and working"""
        print("\n🔧 Testing Alpha Vantage Service Status...")
        
        # Test with a simple US symbol first
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
    
    def test_symbol_mapping(self):
        """Test symbol mapping functionality"""
        print("\n🔄 Testing Symbol Mapping...")
        
        # Test if the service can handle Indian symbols
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for symbol in test_symbols:
            response = self.session.get(f"{self.base_url}/alpha-vantage/quote/{symbol}")
            
            if response.status_code == 200:
                data = response.json()
                if 'alpha_vantage_symbol' in data:
                    self.log_test(f"Symbol Mapping for {symbol}", True, 
                                 f"Successfully mapped to {data['alpha_vantage_symbol']}")
                else:
                    self.log_test(f"Symbol Mapping for {symbol}", True, 
                                 "Quote retrieved but no mapping info")
            else:
                self.log_test(f"Symbol Mapping for {symbol}", False, 
                             f"Failed to get quote: {response.status_code}")
    
    def run_all_tests(self):
        """Run all Indian Alpha Vantage tests"""
        print("🚀 Starting Indian Stocks Alpha Vantage API Testing")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_service_status()
        self.test_symbol_mapping()
        self.test_us_quotes()
        self.test_indian_quotes()
        self.test_indian_daily_data()
        self.test_indian_intraday_data()
        self.test_indian_technical_indicators()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 INDIAN ALPHA VANTAGE TEST SUMMARY")
        print("=" * 70)
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
        filename = f"indian_alpha_vantage_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Alpha Vantage APIs with Indian stocks')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the API (default: http://localhost:8000)')
    parser.add_argument('--symbols', nargs='+', 
                       help='Specific Indian symbols to test (e.g., RELIANCE.NS TCS.NS)')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick test (fewer symbols)')
    
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
    tester = IndianAlphaVantageTester(args.url)
    
    # Override symbols if provided
    if args.symbols:
        tester.indian_symbols = args.symbols
    
    # Reduce test scope for quick mode
    if args.quick:
        tester.indian_symbols = tester.indian_symbols[:3]
        tester.us_symbols = tester.us_symbols[:2]
    
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All Indian Alpha Vantage tests passed! Your API is working perfectly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some Indian Alpha Vantage tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
