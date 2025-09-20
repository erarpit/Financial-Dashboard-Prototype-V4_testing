#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Comprehensive API Testing Script for Financial Dashboard
# Tests all endpoints including YFinance and Alpha Vantage
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

class APITester:
    """Comprehensive API testing class for Financial Dashboard"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_counter = 0  # Add test counter
        self.test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]  # Add test symbols
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "test_details": []
        }
        
    def log_test(self, test_name: str, success: bool, message: str = "", response_data: Any = None):
        """Log test result with test case number"""
        self.test_counter += 1
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            status = "✅ PASS"
        else:
            self.results["failed"] += 1
            status = "❌ FAIL"
            self.results["errors"].append(f"Test #{self.test_counter}: {test_name}: {message}")
        
        print(f"Test #{self.test_counter:03d} {status} {test_name}")
        if message:
            print(f"   {message}")
        
        self.results["test_details"].append({
            "test_number": self.test_counter,
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
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n🏥 Testing Health Check...")
        self.test_endpoint("GET", "/health", test_name="Health Check")
    
    def test_basic_endpoints(self):
        """Test basic endpoints"""
        print("\n📊 Testing Basic Endpoints...")
        self.test_endpoint("GET", "/", test_name="Root Endpoint")
        self.test_endpoint("GET", "/dashboard", params={"tickers": "RELIANCE.NS,TCS.NS"}, test_name="Dashboard with Indian Stocks")
        self.test_endpoint("GET", "/news", params={"limit": 5}, test_name="News Endpoint")
        self.test_endpoint("GET", "/live", params={"ticker": "RELIANCE.NS"}, test_name="Live Data for RELIANCE.NS")
        self.test_endpoint("GET", "/popular-stocks", test_name="Popular Stocks")
    
    def test_stock_data_endpoints(self):
        """Test stock data endpoints"""
        print("\n📈 Testing Stock Data Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS"]
        
        for i, symbol in enumerate(test_symbols, 1):
            self.test_endpoint("GET", f"/stocks/{symbol}", test_name=f"Stock Data - {symbol}")
            self.test_endpoint("GET", f"/stocks/{symbol}/historical", params={"period": "1mo"}, test_name=f"Historical Data - {symbol}")
    
    def test_signals_endpoints(self):
        """Test signals endpoints"""
        print("\n🎯 Testing Signals Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for i, symbol in enumerate(test_symbols, 1):
            self.test_endpoint("GET", f"/signals/{symbol}", test_name=f"Signals - {symbol}")
            self.test_endpoint("GET", f"/ai-signals/{symbol}", test_name=f"AI Signals - {symbol}")
    
    def test_volume_analysis_endpoints(self):
        """Test volume analysis endpoints"""
        print("\n📊 Testing Volume Analysis Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for i, symbol in enumerate(test_symbols, 1):
            self.test_endpoint("GET", f"/volume-analysis/{symbol}", test_name=f"Volume Analysis - {symbol}")
    
    def test_ai_assistant_endpoints(self):
        """Test AI assistant endpoints"""
        print("\n🤖 Testing AI Assistant Endpoints...")
        self.test_endpoint("GET", "/ask", params={"q": "What is the market trend for RELIANCE.NS?"}, test_name="AI Ask - Market Trend")
        self.test_endpoint("GET", "/ask", params={"q": "Tell me about TCS.NS earnings"}, test_name="AI Ask - Earnings")
        self.test_endpoint("GET", "/ask/templates", test_name="AI Ask Templates")
    
    def test_enhanced_analysis_endpoints(self):
        """Test enhanced analysis endpoints"""
        print("\n🔍 Testing Enhanced Analysis Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for i, symbol in enumerate(test_symbols, 1):
            self.test_endpoint("GET", f"/analysis/{symbol}", test_name=f"Analysis - {symbol}")
            self.test_endpoint("GET", f"/analysis/{symbol}/analyst", test_name=f"Analysis Analyst - {symbol}")
            self.test_endpoint("GET", f"/analysis/{symbol}/earnings", test_name=f"Analysis Earnings - {symbol}")
            self.test_endpoint("GET", f"/analyst/{symbol}", test_name=f"Analyst - {symbol}")
            self.test_endpoint("GET", f"/earnings/{symbol}", test_name=f"Earnings - {symbol}")
    
    def test_domain_endpoints(self):
        """Test domain endpoints"""
        print("\n🏢 Testing Domain Endpoints...")
        self.test_endpoint("GET", "/sectors", test_name="Sectors List")
        self.test_endpoint("GET", "/industries", test_name="Industries List")
        self.test_endpoint("GET", "/domain-overview", params={"domain": "Technology"}, test_name="Domain Overview - Technology")
        
        # Test specific sector endpoints
        self.test_endpoint("GET", "/sectors/technology", test_name="Sector - Technology")
        self.test_endpoint("GET", "/sectors/technology/companies", params={"limit": 5}, test_name="Sector Companies - Technology")
        
        # Test specific industry endpoints
        self.test_endpoint("GET", "/industries/software", test_name="Industry - Software")
        self.test_endpoint("GET", "/industries/software/companies", params={"limit": 5}, test_name="Industry Companies - Software")
        
        # Test domain search
        self.test_endpoint("GET", "/domains/search", params={"q": "technology"}, test_name="Domain Search - Technology")
    
    def test_market_status_endpoints(self):
        """Test market status endpoints"""
        print("\n🌍 Testing Market Status Endpoints...")
        self.test_endpoint("GET", "/market/status")
        self.test_endpoint("GET", "/market/summary")
        
        # Test specific market status
        self.test_endpoint("GET", "/market/status/nse")
        self.test_endpoint("GET", "/market/summary/nse")
    
    def test_ownership_endpoints(self):
        """Test ownership/holders endpoints"""
        print("\n👥 Testing Ownership Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for symbol in test_symbols:
            self.test_endpoint("GET", f"/ownership/{symbol}")
            self.test_endpoint("GET", f"/insider-trading/{symbol}")
            
            # Test detailed ownership endpoints
            self.test_endpoint("GET", f"/ownership/{symbol}/institutional", params={"limit": 5})
            self.test_endpoint("GET", f"/ownership/{symbol}/insider-transactions", params={"limit": 5})
            self.test_endpoint("GET", f"/ownership/{symbol}/major-holders")
            self.test_endpoint("GET", f"/ownership/{symbol}/insider-roster", params={"limit": 5})
    
    def test_fastinfo_endpoints(self):
        """Test FastInfo endpoints"""
        print("\n⚡ Testing FastInfo Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for symbol in test_symbols:
            self.test_endpoint("GET", f"/fastinfo/{symbol}")
            
            # Test detailed FastInfo endpoints
            self.test_endpoint("GET", f"/fastinfo/{symbol}/price-summary")
            self.test_endpoint("GET", f"/fastinfo/{symbol}/technical-indicators")
            self.test_endpoint("GET", f"/fastinfo/{symbol}/market-cap")
    
    def test_quote_endpoints(self):
        """Test quote endpoints"""
        print("\n💰 Testing Quote Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for symbol in test_symbols:
            self.test_endpoint("GET", f"/quote/{symbol}")
            self.test_endpoint("GET", f"/quote/{symbol}/sustainability")
            self.test_endpoint("GET", f"/quote/{symbol}/recommendations")
            self.test_endpoint("GET", f"/quote/{symbol}/calendar")
            
            # Test detailed quote endpoints
            self.test_endpoint("GET", f"/quote/{symbol}/upgrades-downgrades")
            self.test_endpoint("GET", f"/quote/{symbol}/company-info")
            self.test_endpoint("GET", f"/quote/{symbol}/sec-filings")
    
    def test_query_builder_endpoints(self):
        """Test query builder endpoints"""
        print("\n🔍 Testing Query Builder Endpoints...")
        self.test_endpoint("GET", "/query-builder/fields")
        self.test_endpoint("GET", "/query-builder/predefined")
        self.test_endpoint("GET", "/query-builder/values", params={"field": "sector"})
        
        # Test query builder POST endpoints
        query_data = {
            "query_type": "equity",
            "query": {
                "sector": "technology",
                "market_cap": {"min": 1000000000}
            }
        }
        self.test_endpoint("POST", "/query-builder/validate", data=query_data)
        
        # Test equity query execution
        equity_query = {
            "query": {
                "sector": "technology",
                "market_cap": {"min": 1000000000}
            }
        }
        self.test_endpoint("POST", "/query-builder/execute/equity", data=equity_query, params={"limit": 10})
        
        # Test fund query execution
        fund_query = {
            "query": {
                "category": "equity",
                "expense_ratio": {"max": 1.0}
            }
        }
        self.test_endpoint("POST", "/query-builder/execute/fund", data=fund_query, params={"limit": 10})
    
    def test_enhanced_yfinance_endpoints(self):
        """Test enhanced YFinance endpoints"""
        print("\n📊 Testing Enhanced YFinance Endpoints...")
        
        # Test enhanced download
        download_data = {
            "tickers": ["RELIANCE.NS", "TCS.NS"],
            "period": "1mo",
            "interval": "1d",
            "include_indicators": True
        }
        self.test_endpoint("POST", "/enhanced-download", data=download_data)
        
        # Test bulk download
        bulk_data = {
            "tech_stocks": ["RELIANCE.NS", "TCS.NS"],
            "banking_stocks": ["HDFCBANK.NS", "ICICIBANK.NS"]
        }
        self.test_endpoint("POST", "/bulk-download", data=bulk_data, 
                          params={"period": "1mo", "interval": "1d"})
        
        # Test technical indicators
        self.test_endpoint("GET", "/enhanced-download/indicators", 
                          params={"ticker": "RELIANCE.NS", "indicator": "SMA"})
        
        # Test specific ticker indicators
        self.test_endpoint("GET", "/enhanced-download/indicators/RELIANCE.NS", 
                          params={"period": "1mo", "interval": "1d"})
    
    def test_alpha_vantage_endpoints(self):
        """Test Alpha Vantage endpoints"""
        print("\n🔮 Testing Alpha Vantage Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for symbol in test_symbols:
            # Test quote
            self.test_endpoint("GET", f"/alpha-vantage/quote/{symbol}")
            
            # Test daily data
            self.test_endpoint("GET", f"/alpha-vantage/daily/{symbol}")
            self.test_endpoint("GET", f"/alpha-vantage/daily/{symbol}", 
                              params={"outputsize": "compact"})
            
            # Test intraday data
            self.test_endpoint("GET", f"/alpha-vantage/intraday/{symbol}")
            self.test_endpoint("GET", f"/alpha-vantage/intraday/{symbol}", 
                              params={"interval": "5min", "outputsize": "compact"})
            
            # Test technical indicators
            indicators = ["SMA", "EMA", "RSI", "MACD"]
            for indicator in indicators:
                self.test_endpoint("GET", f"/alpha-vantage/indicators/{symbol}", 
                                  params={"function": indicator, "time_period": 20})
            
            # Test company overview
            self.test_endpoint("GET", f"/alpha-vantage/overview/{symbol}")
            
            # Test earnings
            self.test_endpoint("GET", f"/alpha-vantage/earnings/{symbol}")
            
            # Test news
            self.test_endpoint("GET", f"/alpha-vantage/news/{symbol}", 
                              params={"limit": 10})
    
    def test_currency_endpoints(self):
        """Test currency conversion endpoints"""
        print("\n💱 Testing Currency Conversion Endpoints...")
        
        # Test currency rate
        self.test_endpoint("GET", "/currency/rate")
        
        # Test currency conversion
        test_amounts = [1, 10, 100, 1000, 10000]
        for amount in test_amounts:
            self.test_endpoint("GET", "/currency/convert", 
                              params={"amount": amount, "from_currency": "USD", "to_currency": "INR"})
        
        # Test currency formatting
        test_formats = [
            {"amount": 1234.56, "currency": "INR", "decimals": 2},
            {"amount": 1000000, "currency": "INR", "decimals": 0},
            {"amount": 99.99, "currency": "USD", "decimals": 2}
        ]
        for format_test in test_formats:
            self.test_endpoint("GET", "/currency/format", params=format_test)
    
    def test_angel_one_endpoints(self):
        """Test Angel One API endpoints"""
        print("\n👼 Testing Angel One Endpoints...")
        
        # Test Angel One status
        self.test_endpoint("GET", "/angel-one/status")
        
        # Test Angel One quotes for Indian stocks
        for symbol in self.test_symbols:
            self.test_endpoint("GET", f"/angel-one/quote/{symbol}")
        
        # Test Angel One historical data
        for symbol in self.test_symbols[:3]:  # Test first 3 symbols
            self.test_endpoint("GET", f"/angel-one/historical/{symbol}", 
                              params={"interval": "1d", "period": "1mo"})
        
        # Test Angel One indices
        self.test_endpoint("GET", "/angel-one/indices")
        
        # Test Angel One market status
        self.test_endpoint("GET", "/angel-one/market-status")
    
    def test_pattern_endpoints(self):
        """Test pattern detection endpoints"""
        print("\n🔍 Testing Pattern Detection Endpoints...")
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        for symbol in test_symbols:
            self.test_endpoint("GET", f"/patterns/{symbol}")
            self.test_endpoint("GET", f"/patterns/{symbol}/detect", 
                              params={"pattern_type": "head_and_shoulders"})
    
    def test_bulk_analysis_endpoints(self):
        """Test bulk analysis endpoints"""
        print("\n📊 Testing Bulk Analysis Endpoints...")
        self.test_endpoint("GET", "/bulk-analysis", 
                          params={"tickers": "RELIANCE.NS,TCS.NS,HDFCBANK.NS"})
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Testing for Financial Dashboard")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_health_check()
        self.test_basic_endpoints()
        self.test_stock_data_endpoints()
        self.test_signals_endpoints()
        self.test_volume_analysis_endpoints()
        self.test_ai_assistant_endpoints()
        self.test_enhanced_analysis_endpoints()
        self.test_domain_endpoints()
        self.test_market_status_endpoints()
        self.test_ownership_endpoints()
        self.test_fastinfo_endpoints()
        self.test_quote_endpoints()
        self.test_query_builder_endpoints()
        self.test_enhanced_yfinance_endpoints()
        self.test_alpha_vantage_endpoints()
        self.test_currency_endpoints()
        self.test_angel_one_endpoints()
        self.test_pattern_endpoints()
        self.test_bulk_analysis_endpoints()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(self.results['passed'] / self.results['total_tests'] * 100):.1f}%")
        
        if self.results['errors']:
            print("\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
            
            # Show failed test numbers for easy reference
            failed_tests = [detail for detail in self.results['test_details'] if not detail['success']]
            if failed_tests:
                print(f"\n📋 Failed Test Numbers: {', '.join([str(test['test_number']) for test in failed_tests])}")
                print(f"📊 Failed Test Categories:")
                categories = {}
                for test in failed_tests:
                    category = test['test_name'].split(' - ')[0] if ' - ' in test['test_name'] else test['test_name']
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(test['test_number'])
                
                for category, test_numbers in categories.items():
                    print(f"   • {category}: Tests {', '.join(map(str, test_numbers))}")
        
        # Show category summary
        self.show_test_summary_by_category()
        
        # Save detailed results
        self.save_results()
        
        return self.results['failed'] == 0
    
    def show_test_summary_by_category(self):
        """Show test results grouped by category"""
        print("\n📊 TEST RESULTS BY CATEGORY:")
        print("=" * 50)
        
        categories = {}
        for test in self.results['test_details']:
            category = test['test_name'].split(' - ')[0] if ' - ' in test['test_name'] else test['test_name']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
            
            categories[category]['total'] += 1
            if test['success']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
            categories[category]['tests'].append(test)
        
        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status_icon = "✅" if stats['failed'] == 0 else "❌" if stats['passed'] == 0 else "⚠️"
            
            print(f"{status_icon} {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
            
            if stats['failed'] > 0:
                failed_test_numbers = [str(test['test_number']) for test in stats['tests'] if not test['success']]
                print(f"   Failed Tests: {', '.join(failed_test_numbers)}")
        
        print("=" * 50)
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"api_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Financial Dashboard APIs')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the API (default: http://localhost:8000)')
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
    tester = APITester(args.url)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Your API is working perfectly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
