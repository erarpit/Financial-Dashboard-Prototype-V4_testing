#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Enhanced yfinance downloader for AI Market News Impact Analyzer
# Based on yfinance library with custom modifications for Arpit's project
#
# Copyright 2024 Arpit
# Licensed under the Apache License, Version 2.0

import logging
import time as _time
import traceback
from typing import Union, List, Dict, Any, Optional
import warnings
import asyncio
from datetime import datetime, timedelta

import pandas as _pd
import numpy as np
from curl_cffi import requests
import yfinance as yf

logger = logging.getLogger(__name__)

class EnhancedYFinanceDownloader:
    """
    Enhanced yfinance downloader with custom features for the AI Market News Impact Analyzer
    """
    
    def __init__(self, session=None, timeout=30, max_retries=3):
        self.session = session or requests.Session(impersonate="chrome")
        self.timeout = timeout
        self.max_retries = max_retries
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache:
            return False
        cache_time, _ = self._cache[key]
        return datetime.now() - cache_time < timedelta(seconds=self._cache_ttl)
    
    def _get_cache(self, key: str) -> Optional[_pd.DataFrame]:
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            _, data = self._cache[key]
            return data
        return None
    
    def _set_cache(self, key: str, data: _pd.DataFrame):
        """Set data in cache"""
        self._cache[key] = (datetime.now(), data)
    
    async def download_enhanced(
        self,
        tickers: Union[str, List[str]],
        start: Optional[str] = None,
        end: Optional[str] = None,
        period: str = "1mo",
        interval: str = "1d",
        actions: bool = False,
        threads: bool = True,
        ignore_tz: bool = None,
        group_by: str = 'column',
        auto_adjust: bool = True,
        back_adjust: bool = False,
        repair: bool = False,
        keepna: bool = False,
        progress: bool = True,
        prepost: bool = False,
        rounding: bool = False,
        timeout: int = 10,
        multi_level_index: bool = True,
        include_indicators: bool = True,
        include_sentiment: bool = False
    ) -> Union[_pd.DataFrame, None]:
        """
        Enhanced download function with additional features for the AI Market News Impact Analyzer
        
        Parameters:
        -----------
        tickers : str, list
            List of tickers to download
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        include_indicators : bool
            Include technical indicators (RSI, MACD, Bollinger Bands, etc.)
        include_sentiment : bool
            Include sentiment analysis for news data
        """
        
        # Create cache key
        cache_key = f"{tickers}_{period}_{interval}_{start}_{end}_{include_indicators}_{include_sentiment}"
        
        # Check cache first
        cached_data = self._get_cache(cache_key)
        if cached_data is not None:
            logger.info(f"Returning cached data for {tickers}")
            return cached_data
        
        try:
            # Use the original yfinance download function
            data = yf.download(
                tickers=tickers,
                start=start,
                end=end,
                period=period,
                interval=interval,
                actions=actions,
                threads=threads,
                ignore_tz=ignore_tz,
                group_by=group_by,
                auto_adjust=auto_adjust,
                back_adjust=back_adjust,
                repair=repair,
                keepna=keepna,
                progress=progress,
                prepost=prepost,
                rounding=rounding,
                timeout=timeout,
                multi_level_index=multi_level_index
            )
            
            if data is None or data.empty:
                logger.warning(f"No data found for tickers: {tickers}")
                return None
            
            # Add technical indicators if requested
            if include_indicators:
                data = await self._add_technical_indicators(data, tickers)
            
            # Add sentiment analysis if requested
            if include_sentiment:
                data = await self._add_sentiment_analysis(data, tickers)
            
            # Cache the result
            self._set_cache(cache_key, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error downloading data for {tickers}: {str(e)}")
            return None
    
    async def _add_technical_indicators(self, data: _pd.DataFrame, tickers: Union[str, List[str]]) -> _pd.DataFrame:
        """Add technical indicators to the data"""
        try:
            if isinstance(tickers, str):
                tickers = [tickers]
            
            # Calculate indicators for each ticker
            for ticker in tickers:
                if isinstance(data.columns, _pd.MultiIndex):
                    # Multi-level columns
                    ticker_data = data[ticker] if ticker in data.columns.levels[0] else None
                else:
                    # Single level columns
                    ticker_data = data
                
                if ticker_data is not None and not ticker_data.empty:
                    # Calculate RSI
                    ticker_data = self._calculate_rsi(ticker_data)
                    
                    # Calculate MACD
                    ticker_data = self._calculate_macd(ticker_data)
                    
                    # Calculate Bollinger Bands
                    ticker_data = self._calculate_bollinger_bands(ticker_data)
                    
                    # Calculate Moving Averages
                    ticker_data = self._calculate_moving_averages(ticker_data)
                    
                    # Update the main dataframe
                    if isinstance(data.columns, _pd.MultiIndex):
                        data[ticker] = ticker_data
                    else:
                        data = ticker_data
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding technical indicators: {str(e)}")
            return data
    
    def _calculate_rsi(self, df: _pd.DataFrame, period: int = 14) -> _pd.DataFrame:
        """Calculate RSI indicator"""
        try:
            if 'Close' not in df.columns:
                return df
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
            return df
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return df
    
    def _calculate_macd(self, df: _pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> _pd.DataFrame:
        """Calculate MACD indicator"""
        try:
            if 'Close' not in df.columns:
                return df
            
            exp1 = df['Close'].ewm(span=fast).mean()
            exp2 = df['Close'].ewm(span=slow).mean()
            df[f'MACD_{fast}_{slow}_{signal}'] = exp1 - exp2
            df[f'MACDs_{fast}_{slow}_{signal}'] = df[f'MACD_{fast}_{slow}_{signal}'].ewm(span=signal).mean()
            df[f'MACDh_{fast}_{slow}_{signal}'] = df[f'MACD_{fast}_{slow}_{signal}'] - df[f'MACDs_{fast}_{slow}_{signal}']
            return df
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return df
    
    def _calculate_bollinger_bands(self, df: _pd.DataFrame, period: int = 20, std: float = 2.0) -> _pd.DataFrame:
        """Calculate Bollinger Bands"""
        try:
            if 'Close' not in df.columns:
                return df
            
            sma = df['Close'].rolling(window=period).mean()
            std_dev = df['Close'].rolling(window=period).std()
            df[f'BBU_{period}_{std}'] = sma + (std_dev * std)
            df[f'BBL_{period}_{std}'] = sma - (std_dev * std)
            df[f'BBM_{period}_{std}'] = sma
            return df
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return df
    
    def _calculate_moving_averages(self, df: _pd.DataFrame) -> _pd.DataFrame:
        """Calculate various moving averages"""
        try:
            if 'Close' not in df.columns:
                return df
            
            # Simple Moving Averages
            for period in [5, 10, 20, 50, 200]:
                df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
            
            # Exponential Moving Averages
            for period in [12, 26, 50]:
                df[f'EMA_{period}'] = df['Close'].ewm(span=period).mean()
            
            return df
        except Exception as e:
            logger.error(f"Error calculating moving averages: {str(e)}")
            return df
    
    async def _add_sentiment_analysis(self, data: _pd.DataFrame, tickers: Union[str, List[str]]) -> _pd.DataFrame:
        """Add sentiment analysis to the data"""
        try:
            # This would integrate with your existing sentiment analysis service
            # For now, we'll add placeholder columns
            if isinstance(tickers, str):
                tickers = [tickers]
            
            for ticker in tickers:
                if isinstance(data.columns, _pd.MultiIndex):
                    if ticker in data.columns.levels[0]:
                        data[(ticker, 'Sentiment_Score')] = 0.0
                        data[(ticker, 'Sentiment_Label')] = 'Neutral'
                else:
                    data['Sentiment_Score'] = 0.0
                    data['Sentiment_Label'] = 'Neutral'
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding sentiment analysis: {str(e)}")
            return data
    
    async def download_bulk_enhanced(
        self,
        ticker_groups: Dict[str, List[str]],
        **kwargs
    ) -> Dict[str, _pd.DataFrame]:
        """
        Download data for multiple groups of tickers with enhanced features
        
        Parameters:
        -----------
        ticker_groups : dict
            Dictionary where keys are group names and values are lists of tickers
            Example: {
                'indian_stocks': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS'],
                'us_stocks': ['AAPL', 'MSFT', 'GOOGL'],
                'crypto': ['BTC-USD', 'ETH-USD']
            }
        """
        results = {}
        
        for group_name, tickers in ticker_groups.items():
            logger.info(f"Downloading data for group: {group_name}")
            try:
                data = await self.download_enhanced(tickers, **kwargs)
                if data is not None and not data.empty:
                    results[group_name] = data
                    logger.info(f"Successfully downloaded {len(tickers)} tickers for {group_name}")
                else:
                    logger.warning(f"No data found for group: {group_name}")
            except Exception as e:
                logger.error(f"Error downloading data for group {group_name}: {str(e)}")
                results[group_name] = None
        
        return results
    
    def get_market_summary(self, tickers: List[str]) -> Dict[str, Any]:
        """Get market summary for a list of tickers"""
        try:
            summary = {
                'total_tickers': len(tickers),
                'successful_downloads': 0,
                'failed_downloads': 0,
                'timestamp': datetime.now().isoformat(),
                'tickers': {}
            }
            
            for ticker in tickers:
                try:
                    # Quick info fetch
                    ticker_obj = yf.Ticker(ticker)
                    info = ticker_obj.info
                    
                    summary['tickers'][ticker] = {
                        'name': info.get('longName', ticker),
                        'sector': info.get('sector', 'N/A'),
                        'market_cap': info.get('marketCap', 0),
                        'price': info.get('regularMarketPrice', 0),
                        'change': info.get('regularMarketChange', 0),
                        'change_percent': info.get('regularMarketChangePercent', 0)
                    }
                    summary['successful_downloads'] += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to get info for {ticker}: {str(e)}")
                    summary['tickers'][ticker] = {'error': str(e)}
                    summary['failed_downloads'] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
            return {'error': str(e)}

# Global instance
enhanced_downloader = EnhancedYFinanceDownloader()
