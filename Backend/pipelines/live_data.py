# pipelines/live_data.py

import requests
import yfinance as yf
import pandas as pd
import datetime
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LiveDataProvider:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/117.0.5938.62 Safari/537.36 Edg/117.0.2045.43"
            )
        })

    def get_yf_data(self, ticker: str, period="1d", interval="5m") -> Optional[Dict]:
        """
        Fetch OHLCV data from Yahoo Finance.
        Works for NSE (.NS) and BSE (.BO) tickers.
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {ticker}")
                return None
            
            # Convert to records format
            df = df.reset_index()
            data = df.tail(20).to_dict(orient="records")
            
            # Format timestamps
            for record in data:
                if 'Datetime' in record:
                    record['Datetime'] = record['Datetime'].strftime('%Y-%m-%d %H:%M:%S')
                elif 'Date' in record:
                    record['Date'] = record['Date'].strftime('%Y-%m-%d')
            
            return {
                "ticker": ticker,
                "data": data,
                "last_updated": datetime.datetime.now().isoformat(),
                "source": "Yahoo Finance"
            }
            
        except Exception as e:
            logger.error(f"YFinance error for {ticker}: {str(e)}")
            return None
    
    def get_nse_quote(self, symbol: str) -> Optional[Dict]:
        """
        Fetch live quote from NSE India (unofficial API).
        Example: symbol="RELIANCE" (without .NS suffix)
        """
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        
        try:
            # First get cookies from main page
            self.session.get("https://www.nseindia.com", timeout=10)
            time.sleep(0.5)  # Small delay
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"NSE API returned status {response.status_code} for {symbol}")
                return None
            
            data = response.json()
            
            if 'priceInfo' not in data:
                logger.warning(f"Invalid NSE response structure for {symbol}")
                return None
            
            price_info = data['priceInfo']
            
            return {
                "symbol": symbol,
                "lastPrice": float(price_info.get('lastPrice', 0)),
                "change": float(price_info.get('change', 0)),
                "pChange": float(price_info.get('pChange', 0)),
                "dayHigh": float(price_info.get('intraDayHighLow', {}).get('max', 0)),
                "dayLow": float(price_info.get('intraDayHighLow', {}).get('min', 0)),
                "previousClose": float(price_info.get('previousClose', 0)),
                "totalTradedVolume": int(data.get('securityWiseDP', {}).get('quantityTraded', 0)),
                "last_updated": datetime.datetime.now().isoformat(),
                "source": "NSE India"
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"NSE API timeout for {symbol}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"NSE API request error for {symbol}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"NSE API error for {symbol}: {str(e)}")
            return None
    
    def get_bse_quote(self, symbol: str) -> Optional[Dict]:
        """
        Fetch BSE quote (placeholder - would need BSE API integration).
        """
        # BSE doesn't have a free public API like NSE
        # This is a placeholder for future BSE integration
        return {
            "symbol": symbol,
            "error": "BSE API not implemented yet",
            "suggestion": "Use .NS suffix for NSE data instead"
        }
    
    def get_combined_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive quote data from multiple sources.
        """
        result = {
            "ticker": ticker,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Yahoo Finance data (delayed but reliable)
        yf_data = self.get_yf_data(ticker, period="1d", interval="1m")
        if yf_data:
            result["yahoo_finance"] = yf_data
        
        # NSE live quote (if NSE ticker)
        if ticker.endswith(".NS"):
            nse_symbol = ticker.replace(".NS", "")
            nse_quote = self.get_nse_quote(nse_symbol)
            if nse_quote:
                result["nse_live"] = nse_quote
        
        # BSE quote (if BSE ticker)
        elif ticker.endswith(".BO"):
            bse_symbol = ticker.replace(".BO", "")
            bse_quote = self.get_bse_quote(bse_symbol)
            if bse_quote:
                result["bse_live"] = bse_quote
        
        return result

# Global instance
live_data_provider = LiveDataProvider()

# Convenience functions
def get_stock_data(ticker: str, period="1d", interval="5m") -> Optional[Dict]:
    """Get stock data from Yahoo Finance."""
    return live_data_provider.get_yf_data(ticker, period, interval)

def get_live_quote(ticker: str) -> Dict[str, Any]:
    """Get live quote data."""
    return live_data_provider.get_combined_quote(ticker)

def get_nse_data(symbol: str) -> Optional[Dict]:
    """Get NSE live data."""
    return live_data_provider.get_nse_quote(symbol)

# Popular Indian stock tickers
POPULAR_TICKERS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services", 
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "ITC.NS": "ITC Limited",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "LT.NS": "Larsen & Toubro"
}

def get_popular_stocks_data() -> Dict[str, Any]:
    """Get data for popular Indian stocks."""
    results = {}
    
    for ticker, name in POPULAR_TICKERS.items():
        try:
            data = get_live_quote(ticker)
            results[ticker] = {
                "name": name,
                "data": data
            }
        except Exception as e:
            results[ticker] = {
                "name": name,
                "error": str(e)
            }
    
    return results