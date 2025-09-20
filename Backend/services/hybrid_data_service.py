#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Hybrid Data Service for Indian Stocks
# Combines multiple data sources for comprehensive Indian stock data
#
# Copyright 2024 Arpit
# Licensed under the Apache License, Version 2.0

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from .symbol_mapping import symbol_mapping_service
from .alpha_vantage_service import alpha_vantage_service

logger = logging.getLogger(__name__)

class HybridDataService:
    """
    Hybrid service that combines multiple data sources for Indian stocks
    - Yahoo Finance for basic data (works with Indian symbols)
    - Alpha Vantage for additional data when available
    - Fallback mechanisms for premium features
    """
    
    def __init__(self):
        self.alpha_vantage_enabled = alpha_vantage_service.is_enabled()
        logger.info(f"Hybrid Data Service initialized. Alpha Vantage enabled: {self.alpha_vantage_enabled}")
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive stock quote using multiple data sources
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS', 'AAPL')
            
        Returns:
            Dictionary containing comprehensive quote data
        """
        try:
            # Primary: Use Yahoo Finance (works with Indian symbols)
            yf_data = self._get_yahoo_quote(symbol)
            
            if yf_data:
                # Try to enhance with Alpha Vantage data if available
                if self.alpha_vantage_enabled:
                    av_data = self._get_alpha_vantage_quote(symbol)
                    if av_data:
                        # Merge Alpha Vantage data
                        yf_data.update({
                            'alpha_vantage_data': av_data,
                            'data_sources': ['Yahoo Finance', 'Alpha Vantage']
                        })
                    else:
                        yf_data['data_sources'] = ['Yahoo Finance']
                else:
                    yf_data['data_sources'] = ['Yahoo Finance']
                
                return yf_data
            
            # Fallback: Try Alpha Vantage only if Yahoo Finance fails
            if self.alpha_vantage_enabled:
                return self._get_alpha_vantage_quote(symbol)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting hybrid quote for {symbol}: {str(e)}")
            return None
    
    def get_daily_data(self, symbol: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """
        Get daily historical data using multiple sources
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with daily OHLCV data
        """
        try:
            # Primary: Use Yahoo Finance
            yf_data = self._get_yahoo_daily_data(symbol, period)
            
            if yf_data is not None and not yf_data.empty:
                return yf_data
            
            # Fallback: Try Alpha Vantage
            if self.alpha_vantage_enabled:
                return self._get_alpha_vantage_daily_data(symbol)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting hybrid daily data for {symbol}: {str(e)}")
            return None
    
    def get_technical_indicators(self, symbol: str, indicators: List[str] = None) -> Dict[str, Any]:
        """
        Get technical indicators using multiple sources
        
        Args:
            symbol: Stock symbol
            indicators: List of indicators to calculate
            
        Returns:
            Dictionary with technical indicators
        """
        if indicators is None:
            indicators = ['SMA_20', 'SMA_50', 'EMA_20', 'RSI', 'MACD', 'BBANDS']
        
        try:
            # Get historical data first
            df = self.get_daily_data(symbol, "6mo")
            
            if df is None or df.empty:
                return {"error": "No historical data available"}
            
            # Calculate indicators using pandas/TA
            result = {}
            
            for indicator in indicators:
                try:
                    if indicator.startswith('SMA_'):
                        period = int(indicator.split('_')[1])
                        result[indicator] = df['Close'].rolling(window=period).mean().iloc[-1]
                    elif indicator.startswith('EMA_'):
                        period = int(indicator.split('_')[1])
                        result[indicator] = df['Close'].ewm(span=period).mean().iloc[-1]
                    elif indicator == 'RSI':
                        result[indicator] = self._calculate_rsi(df['Close'])
                    elif indicator == 'MACD':
                        macd_data = self._calculate_macd(df['Close'])
                        result[indicator] = macd_data
                    elif indicator == 'BBANDS':
                        bb_data = self._calculate_bollinger_bands(df['Close'])
                        result[indicator] = bb_data
                except Exception as e:
                    logger.warning(f"Error calculating {indicator} for {symbol}: {str(e)}")
                    result[indicator] = None
            
            result['symbol'] = symbol
            result['last_updated'] = datetime.now().isoformat()
            result['data_source'] = 'Yahoo Finance + Calculated'
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting technical indicators for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company information using multiple sources
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company information
        """
        try:
            # Use Yahoo Finance for company info
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info:
                # Extract relevant information
                company_info = {
                    'symbol': symbol,
                    'name': info.get('longName', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'market_cap': info.get('marketCap', 0),
                    'employees': info.get('fullTimeEmployees', 0),
                    'website': info.get('website', ''),
                    'description': info.get('longBusinessSummary', ''),
                    'country': info.get('country', ''),
                    'currency': info.get('currency', ''),
                    'data_source': 'Yahoo Finance',
                    'last_updated': datetime.now().isoformat()
                }
                
                return company_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {str(e)}")
            return None
    
    def _get_yahoo_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            # Get current price
            hist = ticker.history(period="1d")
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            quote_data = {
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
                'last_updated': datetime.now().isoformat()
            }
            
            return quote_data
            
        except Exception as e:
            logger.warning(f"Error getting Yahoo Finance quote for {symbol}: {str(e)}")
            return None
    
    def _get_alpha_vantage_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote from Alpha Vantage"""
        try:
            return alpha_vantage_service.get_stock_quote(symbol)
        except Exception as e:
            logger.warning(f"Error getting Alpha Vantage quote for {symbol}: {str(e)}")
            return None
    
    def _get_yahoo_daily_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get daily data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return None
            
            # Ensure proper column names
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df.index.name = 'Date'
            
            return df
            
        except Exception as e:
            logger.warning(f"Error getting Yahoo Finance daily data for {symbol}: {str(e)}")
            return None
    
    def _get_alpha_vantage_daily_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get daily data from Alpha Vantage"""
        try:
            return alpha_vantage_service.get_daily_data(symbol)
        except Exception as e:
            logger.warning(f"Error getting Alpha Vantage daily data for {symbol}: {str(e)}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return None
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line.iloc[-1],
                'signal': signal_line.iloc[-1],
                'histogram': histogram.iloc[-1]
            }
        except:
            return None
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            return {
                'upper': (sma + (std * std_dev)).iloc[-1],
                'middle': sma.iloc[-1],
                'lower': (sma - (std * std_dev)).iloc[-1]
            }
        except:
            return None

# Global instance
hybrid_data_service = HybridDataService()
