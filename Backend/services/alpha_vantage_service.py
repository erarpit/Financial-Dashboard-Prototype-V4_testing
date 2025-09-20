#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Alpha Vantage Service for AI Market News Impact Analyzer
# Provides financial data from Alpha Vantage API
#
# Copyright 2024 Arpit
# Licensed under the Apache License, Version 2.0

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.foreignexchange import ForeignExchange
from .symbol_mapping import symbol_mapping_service

logger = logging.getLogger(__name__)

class AlphaVantageService:
    """
    Service for fetching financial data from Alpha Vantage API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage service
        
        Args:
            api_key: Alpha Vantage API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        
        if not self.api_key:
            logger.warning("Alpha Vantage API key not found. Set ALPHA_VANTAGE_API_KEY environment variable.")
            self.enabled = False
            return
            
        self.enabled = True
        
        # Initialize API clients
        self.ts = TimeSeries(key=self.api_key, output_format='pandas')
        self.fd = FundamentalData(key=self.api_key, output_format='pandas')
        self.ti = TechIndicators(key=self.api_key, output_format='pandas')
        self.cc = CryptoCurrencies(key=self.api_key, output_format='pandas')
        self.fx = ForeignExchange(key=self.api_key, output_format='pandas')
        
        logger.info("Alpha Vantage service initialized successfully")
    
    def is_enabled(self) -> bool:
        """Check if Alpha Vantage service is enabled"""
        return self.enabled
    
    def _convert_symbol_for_alpha_vantage(self, symbol: str) -> str:
        """
        Convert Indian symbol to Alpha Vantage compatible symbol
        
        Args:
            symbol: Original symbol (may be Indian)
            
        Returns:
            Alpha Vantage compatible symbol
        """
        return symbol_mapping_service.convert_for_alpha_vantage(symbol)
    
    def _get_fallback_symbols(self, symbol: str) -> List[str]:
        """
        Get fallback symbols for Alpha Vantage when direct mapping fails
        
        Args:
            symbol: Original symbol
            
        Returns:
            List of fallback symbols to try
        """
        if symbol_mapping_service.is_indian_symbol(symbol):
            return symbol_mapping_service.get_alpha_vantage_fallback_symbols(symbol)
        return [symbol]
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time stock quote with rate limit handling
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT', 'RELIANCE.NS')
            
        Returns:
            Dictionary containing quote data or None if error
        """
        if not self.enabled:
            logger.warning("Alpha Vantage service not enabled")
            return None
        
        # Check if we've hit rate limits
        if self._is_rate_limited():
            logger.warning("Alpha Vantage rate limit reached, using fallback")
            return self._get_fallback_quote(symbol)
        
        # Try multiple symbol variations for Indian stocks
        symbols_to_try = self._get_fallback_symbols(symbol)
        
        for try_symbol in symbols_to_try:
            try:
                logger.info(f"Trying Alpha Vantage quote for symbol: {try_symbol}")
                data, meta_data = self.ts.get_quote_endpoint(symbol=try_symbol)
                
                if data is not None and not data.empty:
                    # Convert to dictionary format with proper numpy handling
                    quote_data = {}
                    try:
                        for key, value in data.iloc[0].items():
                            # Convert numpy types to Python types safely
                            if hasattr(value, 'item'):  # numpy scalar
                                quote_data[key] = value.item()
                            elif hasattr(value, 'tolist'):  # numpy array
                                quote_data[key] = value.tolist()
                            elif hasattr(value, 'dtype'):  # other numpy types
                                quote_data[key] = value.astype(str)
                            else:
                                quote_data[key] = value
                    except Exception as e:
                        logger.error(f"Error converting numpy data: {str(e)}")
                        # Fallback: convert everything to string
                        quote_data = {str(k): str(v) for k, v in data.iloc[0].items()}
                    
                    quote_data['symbol'] = symbol  # Keep original symbol
                    quote_data['alpha_vantage_symbol'] = try_symbol  # Add the symbol that worked
                    quote_data['last_updated'] = datetime.now().isoformat()
                    quote_data['source'] = 'Alpha Vantage'
                    
                    logger.info(f"Successfully got quote for {symbol} using {try_symbol}")
                    return quote_data
                else:
                    logger.warning(f"No quote data found for {try_symbol}")
                    
            except Exception as e:
                error_msg = str(e)
                if "rate limit" in error_msg.lower() or "25 requests per day" in error_msg:
                    logger.warning("Alpha Vantage rate limit reached")
                    self._mark_rate_limited()
                    return self._get_fallback_quote(symbol)
                logger.warning(f"Error getting quote for {try_symbol}: {error_msg}")
                continue
        
        logger.error(f"No quote data found for {symbol} after trying all fallback symbols")
        return self._get_fallback_quote(symbol)
    
    def get_daily_data(self, symbol: str, outputsize: str = 'compact') -> Optional[pd.DataFrame]:
        """
        Get daily time series data
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'RELIANCE.NS')
            outputsize: 'compact' (last 100 data points) or 'full' (full historical data)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        if not self.enabled:
            logger.warning("Alpha Vantage service not enabled")
            return None
        
        # Try multiple symbol variations for Indian stocks
        symbols_to_try = self._get_fallback_symbols(symbol)
        
        for try_symbol in symbols_to_try:
            try:
                logger.info(f"Trying Alpha Vantage daily data for symbol: {try_symbol}")
                data, meta_data = self.ts.get_daily(symbol=try_symbol, outputsize=outputsize)
                
                if data is not None and not data.empty:
                    # Rename columns to match yfinance format
                    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    data.index.name = 'Date'
                    
                    logger.info(f"Successfully got daily data for {symbol} using {try_symbol}")
                    return data
                else:
                    logger.warning(f"No daily data found for {try_symbol}")
                    
            except Exception as e:
                error_msg = str(e)
                if any(phrase in error_msg.lower() for phrase in ["rate limit", "api calls", "25 requests", "premium"]):
                    logger.warning("Alpha Vantage rate limit reached")
                    self._mark_rate_limited()
                    return None
                logger.warning(f"Error getting daily data for {try_symbol}: {error_msg}")
                continue
        
        logger.error(f"No daily data found for {symbol} after trying all fallback symbols")
        return None
    
    def get_intraday_data(self, symbol: str, interval: str = '5min', outputsize: str = 'compact') -> Optional[pd.DataFrame]:
        """
        Get intraday time series data
        
        Args:
            symbol: Stock symbol
            interval: '1min', '5min', '15min', '30min', '60min'
            outputsize: 'compact' or 'full'
            
        Returns:
            DataFrame with intraday OHLCV data or None if error
        """
        if not self.enabled:
            logger.warning("Alpha Vantage service not enabled")
            return None
            
        try:
            data, meta_data = self.ts.get_intraday(symbol=symbol, interval=interval, outputsize=outputsize)
            
            if data is None or data.empty:
                logger.warning(f"No intraday data found for {symbol}")
                return None
            
            # Rename columns to match yfinance format
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            data.index.name = 'Datetime'
            
            return data
            
        except Exception as e:
            error_msg = str(e)
            if any(phrase in error_msg.lower() for phrase in ["rate limit", "api calls", "25 requests", "premium"]):
                logger.warning("Alpha Vantage rate limit reached")
                self._mark_rate_limited()
            logger.error(f"Error getting intraday data for {symbol}: {error_msg}")
            return None
    
    def get_technical_indicators(self, symbol: str, function: str = 'SMA', interval: str = 'daily', 
                               time_period: int = 20, series_type: str = 'close') -> Optional[pd.DataFrame]:
        """
        Get technical indicators
        
        Args:
            symbol: Stock symbol
            function: Technical indicator function (SMA, EMA, RSI, MACD, etc.)
            interval: '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'
            time_period: Number of data points used to calculate the indicator
            series_type: 'close', 'open', 'high', 'low'
            
        Returns:
            DataFrame with technical indicator data or None if error
        """
        if not self.enabled:
            logger.warning("Alpha Vantage service not enabled")
            return None
            
        try:
            if function.upper() == 'SMA':
                data, meta_data = self.ti.get_sma(symbol=symbol, interval=interval, 
                                                time_period=time_period, series_type=series_type)
            elif function.upper() == 'EMA':
                data, meta_data = self.ti.get_ema(symbol=symbol, interval=interval, 
                                                time_period=time_period, series_type=series_type)
            elif function.upper() == 'RSI':
                data, meta_data = self.ti.get_rsi(symbol=symbol, interval=interval, 
                                                time_period=time_period, series_type=series_type)
            elif function.upper() == 'MACD':
                data, meta_data = self.ti.get_macd(symbol=symbol, interval=interval, 
                                                 series_type=series_type)
            elif function.upper() == 'BBANDS':
                data, meta_data = self.ti.get_bbands(symbol=symbol, interval=interval, 
                                                   time_period=time_period, series_type=series_type)
            else:
                logger.warning(f"Unsupported technical indicator: {function}")
                return None
            
            if data is None or data.empty:
                logger.warning(f"No {function} data found for {symbol}")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting {function} for {symbol}: {str(e)}")
            return None
    
    def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company overview/fundamental data
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company overview data or None if error
        """
        if not self.enabled:
            logger.warning("Alpha Vantage service not enabled")
            return None
            
        try:
            data, meta_data = self.fd.get_company_overview(symbol=symbol)
            
            if data is None or data.empty:
                logger.warning(f"No company overview found for {symbol}")
                return None
            
            # Convert to dictionary
            overview_data = data.iloc[0].to_dict()
            overview_data['symbol'] = symbol
            overview_data['last_updated'] = datetime.now().isoformat()
            overview_data['source'] = 'Alpha Vantage'
            
            return overview_data
            
        except Exception as e:
            logger.error(f"Error getting company overview for {symbol}: {str(e)}")
            return None
    
    def get_earnings_calendar(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get earnings calendar data
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with earnings data or None if error
        """
        if not self.enabled:
            logger.warning("Alpha Vantage service not enabled")
            return None
            
        try:
            data, meta_data = self.fd.get_earnings_calendar(symbol=symbol)
            
            if data is None or data.empty:
                logger.warning(f"No earnings data found for {symbol}")
                return None
            
            # Convert to dictionary
            earnings_data = data.to_dict('records')
            
            return {
                'symbol': symbol,
                'earnings': earnings_data,
                'last_updated': datetime.now().isoformat(),
                'source': 'Alpha Vantage'
            }
            
        except Exception as e:
            logger.error(f"Error getting earnings data for {symbol}: {str(e)}")
            return None
    
    def get_news_sentiment(self, symbol: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Get news sentiment data
        
        Args:
            symbol: Stock symbol
            limit: Number of news items to return
            
        Returns:
            List of news items with sentiment or None if error
        """
        if not self.enabled:
            logger.warning("Alpha Vantage service not enabled")
            return None
            
        try:
            data, meta_data = self.fd.get_news_sentiment(symbol=symbol, limit=limit)
            
            if data is None or data.empty:
                logger.warning(f"No news sentiment data found for {symbol}")
                return None
            
            # Convert to list of dictionaries
            news_data = data.to_dict('records')
            
            return news_data
            
        except Exception as e:
            logger.error(f"Error getting news sentiment for {symbol}: {str(e)}")
            return None
    
    def _is_rate_limited(self) -> bool:
        """Check if we're currently rate limited"""
        if not hasattr(self, 'rate_limited') or not self.rate_limited:
            return False
        
        if hasattr(self, 'rate_limit_reset_time') and self.rate_limit_reset_time and datetime.now() > self.rate_limit_reset_time:
            self.rate_limited = False
            self.rate_limit_reset_time = None
            logger.info("Alpha Vantage rate limit reset")
            return False
        
        return True
    
    def _mark_rate_limited(self):
        """Mark that we've hit rate limits"""
        self.rate_limited = True
        # Reset after 24 hours (daily limit)
        self.rate_limit_reset_time = datetime.now() + timedelta(hours=24)
        logger.warning("Alpha Vantage marked as rate limited until tomorrow")
    
    def _get_fallback_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get fallback quote data when Alpha Vantage is unavailable"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            # Get current price
            hist = ticker.history(period="1d")
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'price': current_price,
                'open': hist['Open'].iloc[-1],
                'high': hist['High'].iloc[-1],
                'low': hist['Low'].iloc[-1],
                'volume': hist['Volume'].iloc[-1],
                'previous_close': info.get('previousClose', current_price),
                'change': current_price - info.get('previousClose', current_price),
                'change_percent': ((current_price - info.get('previousClose', current_price)) / info.get('previousClose', current_price)) * 100,
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'INR'),
                'last_updated': datetime.now().isoformat(),
                'source': 'Yahoo Finance (Alpha Vantage Fallback)'
            }
        except Exception as e:
            logger.warning(f"Fallback quote failed for {symbol}: {str(e)}")
            return None

# Global instance
alpha_vantage_service = AlphaVantageService()
