"""
Hybrid Alpha Vantage service that combines Alpha Vantage with Yahoo Finance
for better Indian stock support and fallback mechanisms
"""

import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yfinance as yf

logger = logging.getLogger(__name__)

class AlphaVantageHybrid:
    """Hybrid service that combines Alpha Vantage with Yahoo Finance for better coverage"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("Alpha Vantage API key not found. Using Yahoo Finance only.")
            return
        
        # Import Alpha Vantage
        try:
            from alpha_vantage.timeseries import TimeSeries
            from alpha_vantage.techindicators import TechIndicators
            from alpha_vantage.fundamentaldata import FundamentalData
            
            self.ts = TimeSeries(key=self.api_key, output_format='pandas')
            self.ti = TechIndicators(key=self.api_key, output_format='pandas')
            self.fd = FundamentalData(key=self.api_key, output_format='pandas')
            
            logger.info("Alpha Vantage Hybrid service initialized successfully")
        except ImportError:
            logger.error("Alpha Vantage package not installed")
            self.enabled = False
    
    def _is_indian_symbol(self, symbol: str) -> bool:
        """Check if symbol is an Indian stock"""
        return symbol.endswith('.NS') or symbol.endswith('.BSE')
    
    def _get_yahoo_fallback(self, symbol: str, data_type: str = 'quote') -> Optional[Any]:
        """Get data from Yahoo Finance as fallback"""
        try:
            ticker = yf.Ticker(symbol)
            
            if data_type == 'quote':
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if hist.empty or not info:
                    return None
                
                current_price = hist['Close'].iloc[-1]
                previous_close = info.get('previousClose', current_price)
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                
                return {
                    'symbol': symbol,
                    'price': float(current_price),
                    'change': float(change),
                    'change_percent': float(change_percent),
                    'volume': int(hist['Volume'].iloc[-1]),
                    'high': float(hist['High'].iloc[-1]),
                    'low': float(hist['Low'].iloc[-1]),
                    'open': float(hist['Open'].iloc[-1]),
                    'previous_close': float(previous_close),
                    'market_cap': info.get('marketCap', 0),
                    'currency': info.get('currency', 'INR'),
                    'last_updated': datetime.now().isoformat(),
                    'source': 'Yahoo Finance (Hybrid Fallback)'
                }
            
            elif data_type == 'daily':
                hist = ticker.history(period="1mo")
                if hist.empty:
                    return None
                
                # Rename columns to match Alpha Vantage format
                hist.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                hist.index.name = 'Date'
                return hist
            
            elif data_type == 'intraday':
                hist = ticker.history(period="1d", interval="5m")
                if hist.empty:
                    return None
                
                hist.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                hist.index.name = 'Datetime'
                return hist
            
            elif data_type == 'indicators':
                hist = ticker.history(period="3mo")
                if hist.empty:
                    return None
                
                # Calculate basic indicators
                close_prices = hist['Close']
                
                # SMA
                sma_20 = close_prices.rolling(window=20).mean()
                sma_50 = close_prices.rolling(window=50).mean()
                
                # RSI
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                # MACD
                ema_12 = close_prices.ewm(span=12).mean()
                ema_26 = close_prices.ewm(span=26).mean()
                macd = ema_12 - ema_26
                signal = macd.ewm(span=9).mean()
                histogram = macd - signal
                
                indicators = pd.DataFrame({
                    'SMA_20': sma_20,
                    'SMA_50': sma_50,
                    'RSI': rsi,
                    'MACD': macd,
                    'MACD_Signal': signal,
                    'MACD_Histogram': histogram
                })
                
                return indicators.dropna()
            
            return None
            
        except Exception as e:
            logger.error(f"Yahoo Finance fallback failed for {symbol}: {str(e)}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock quote with hybrid approach"""
        # For Indian stocks, use Yahoo Finance directly
        if self._is_indian_symbol(symbol):
            logger.info(f"Using Yahoo Finance for Indian symbol: {symbol}")
            return self._get_yahoo_fallback(symbol, 'quote')
        
        # For US stocks, try Alpha Vantage first
        if self.enabled:
            try:
                data, meta_data = self.ts.get_quote_endpoint(symbol=symbol)
                
                if data is not None and not data.empty:
                    # Convert to dictionary with proper numpy handling
                    quote_data = {}
                    for key, value in data.iloc[0].items():
                        if hasattr(value, 'item'):
                            quote_data[key] = value.item()
                        elif hasattr(value, 'tolist'):
                            quote_data[key] = value.tolist()
                        else:
                            quote_data[key] = value
                    
                    quote_data['symbol'] = symbol
                    quote_data['last_updated'] = datetime.now().isoformat()
                    quote_data['source'] = 'Alpha Vantage'
                    
                    return quote_data
                    
            except Exception as e:
                error_msg = str(e)
                if any(phrase in error_msg.lower() for phrase in ["rate limit", "api calls", "25 requests", "premium"]):
                    logger.warning("Alpha Vantage rate limit reached, using Yahoo Finance fallback")
                else:
                    logger.warning(f"Alpha Vantage error for {symbol}: {error_msg}")
        
        # Fallback to Yahoo Finance
        return self._get_yahoo_fallback(symbol, 'quote')
    
    def get_daily_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get daily data with hybrid approach"""
        # For Indian stocks, use Yahoo Finance directly
        if self._is_indian_symbol(symbol):
            logger.info(f"Using Yahoo Finance for Indian symbol: {symbol}")
            return self._get_yahoo_fallback(symbol, 'daily')
        
        # For US stocks, try Alpha Vantage first
        if self.enabled:
            try:
                data, meta_data = self.ts.get_daily(symbol=symbol, outputsize='compact')
                
                if data is not None and not data.empty:
                    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    data.index.name = 'Date'
                    return data
                    
            except Exception as e:
                error_msg = str(e)
                if any(phrase in error_msg.lower() for phrase in ["rate limit", "api calls", "25 requests", "premium"]):
                    logger.warning("Alpha Vantage rate limit reached, using Yahoo Finance fallback")
                else:
                    logger.warning(f"Alpha Vantage error for {symbol}: {error_msg}")
        
        # Fallback to Yahoo Finance
        return self._get_yahoo_fallback(symbol, 'daily')
    
    def get_intraday_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get intraday data with hybrid approach"""
        # For Indian stocks, use Yahoo Finance directly
        if self._is_indian_symbol(symbol):
            logger.info(f"Using Yahoo Finance for Indian symbol: {symbol}")
            return self._get_yahoo_fallback(symbol, 'intraday')
        
        # For US stocks, try Alpha Vantage first
        if self.enabled:
            try:
                data, meta_data = self.ts.get_intraday(symbol=symbol, interval='5min', outputsize='compact')
                
                if data is not None and not data.empty:
                    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    data.index.name = 'Datetime'
                    return data
                    
            except Exception as e:
                error_msg = str(e)
                if any(phrase in error_msg.lower() for phrase in ["rate limit", "api calls", "25 requests", "premium"]):
                    logger.warning("Alpha Vantage rate limit reached, using Yahoo Finance fallback")
                else:
                    logger.warning(f"Alpha Vantage error for {symbol}: {error_msg}")
        
        # Fallback to Yahoo Finance
        return self._get_yahoo_fallback(symbol, 'intraday')
    
    def get_technical_indicators(self, symbol: str, function: str = 'SMA', time_period: int = 20) -> Optional[pd.DataFrame]:
        """Get technical indicators with hybrid approach"""
        # For Indian stocks, use Yahoo Finance directly
        if self._is_indian_symbol(symbol):
            logger.info(f"Using Yahoo Finance for Indian symbol: {symbol}")
            return self._get_yahoo_fallback(symbol, 'indicators')
        
        # For US stocks, try Alpha Vantage first
        if self.enabled:
            try:
                if function.upper() == 'SMA':
                    data, meta_data = self.ti.get_sma(symbol=symbol, interval='daily', time_period=time_period)
                elif function.upper() == 'EMA':
                    data, meta_data = self.ti.get_ema(symbol=symbol, interval='daily', time_period=time_period)
                elif function.upper() == 'RSI':
                    data, meta_data = self.ti.get_rsi(symbol=symbol, interval='daily', time_period=time_period)
                elif function.upper() == 'MACD':
                    data, meta_data = self.ti.get_macd(symbol=symbol, interval='daily')
                else:
                    logger.warning(f"Unsupported indicator: {function}")
                    return None
                
                if data is not None and not data.empty:
                    return data
                    
            except Exception as e:
                error_msg = str(e)
                if any(phrase in error_msg.lower() for phrase in ["rate limit", "api calls", "25 requests", "premium"]):
                    logger.warning("Alpha Vantage rate limit reached, using Yahoo Finance fallback")
                else:
                    logger.warning(f"Alpha Vantage error for {symbol}: {error_msg}")
        
        # Fallback to Yahoo Finance
        return self._get_yahoo_fallback(symbol, 'indicators')

# Global instance
alpha_vantage_hybrid = AlphaVantageHybrid()
