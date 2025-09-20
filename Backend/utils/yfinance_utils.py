#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Enhanced yfinance utilities for AI Market News Impact Analyzer
# Based on yfinance library utilities with custom modifications for Arpit's project
#
# Copyright 2024 Arpit
# Licensed under the Apache License, Version 2.0

import datetime as _datetime
import logging
import re as _re
import sys as _sys
import threading
from functools import wraps
from inspect import getmembers
from types import FunctionType
from typing import List, Optional, Dict, Any, Union
import warnings

import numpy as _np
import pandas as _pd
import pytz as _tz
from dateutil.relativedelta import relativedelta
from pytz import UnknownTimeZoneError

logger = logging.getLogger(__name__)

# Enhanced logging for the AI Market News Impact Analyzer
class AILoggerAdapter(logging.LoggerAdapter):
    """Enhanced logger adapter for AI Market News Impact Analyzer"""
    def process(self, msg, kwargs):
        if logger.isEnabledFor(logging.DEBUG):
            i = ' ' * self.extra['indent']
            if not isinstance(msg, str):
                msg = str(msg)
            msg = '\n'.join([i + m for m in msg.split('\n')])
        return msg, kwargs

_indentation_level = threading.local()

class IndentationContext:
    def __init__(self, increment=1):
        self.increment = increment

    def __enter__(self):
        _indentation_level.indent = getattr(_indentation_level, 'indent', 0) + self.increment

    def __exit__(self, exc_type, exc_val, exc_tb):
        _indentation_level.indent -= self.increment

def get_indented_logger(name=None):
    """Get indented logger for better debugging"""
    return AILoggerAdapter(logging.getLogger(name), {'indent': getattr(_indentation_level, 'indent', 0)})

def log_indent_decorator(func):
    """Decorator for function-level logging with indentation"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_indented_logger('ai_market_analyzer')
        logger.debug(f'Entering {func.__name__}()')

        with IndentationContext():
            result = func(*args, **kwargs)

        logger.debug(f'Exiting {func.__name__}()')
        return result

    return wrapper

# Enhanced validation functions for AI Market News Impact Analyzer
def is_valid_ticker(ticker: str) -> bool:
    """Enhanced ticker validation for Indian and international markets"""
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Remove common suffixes for validation
    clean_ticker = ticker.replace('.NS', '').replace('.BO', '').replace('.NSE', '').replace('.BSE', '')
    
    # Basic validation: alphanumeric, 1-10 characters
    if not _re.match(r'^[A-Z0-9]{1,10}$', clean_ticker.upper()):
        return False
    
    return True

def is_valid_period_format(period: str) -> bool:
    """Enhanced period validation for AI Market News Impact Analyzer"""
    if period is None:
        return False

    # Enhanced regex pattern for AI Market News Impact Analyzer
    valid_pattern = r"^[1-9]\d*(d|wk|mo|y|h|m)$"
    return bool(_re.match(valid_pattern, period))

def is_valid_interval_format(interval: str) -> bool:
    """Validate interval format for AI Market News Impact Analyzer"""
    if interval is None:
        return False
    
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    return interval in valid_intervals

def is_valid_timezone(tz: str) -> bool:
    """Enhanced timezone validation"""
    try:
        _tz.timezone(tz)
    except UnknownTimeZoneError:
        return False
    return True

# Enhanced data processing functions for AI Market News Impact Analyzer
@log_indent_decorator
def format_financial_data_for_ai(data: _pd.DataFrame, ticker: str) -> Dict[str, Any]:
    """Format financial data specifically for AI analysis"""
    try:
        if data.empty:
            return {"error": "No data available"}
        
        # Calculate AI-specific metrics
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        # Price momentum analysis
        price_momentum = {
            "current_price": float(latest.get('Close', 0)),
            "price_change_1d": float(latest.get('Close', 0) - previous.get('Close', 0)),
            "price_change_pct_1d": float(((latest.get('Close', 0) - previous.get('Close', 0)) / previous.get('Close', 1)) * 100),
            "high_52w": float(data['High'].max()) if 'High' in data.columns else 0,
            "low_52w": float(data['Low'].min()) if 'Low' in data.columns else 0,
        }
        
        # Volume analysis for AI
        volume_analysis = {
            "current_volume": int(latest.get('Volume', 0)),
            "avg_volume_20d": int(data['Volume'].rolling(20).mean().iloc[-1]) if len(data) >= 20 else 0,
            "volume_ratio": float(latest.get('Volume', 0) / data['Volume'].rolling(20).mean().iloc[-1]) if len(data) >= 20 else 1.0,
        }
        
        # Technical indicators for AI
        technical_indicators = {}
        if len(data) >= 14:
            technical_indicators.update({
                "rsi_14": float(calculate_rsi(data['Close'], 14).iloc[-1]),
                "sma_20": float(data['Close'].rolling(20).mean().iloc[-1]),
                "ema_20": float(data['Close'].ewm(span=20).mean().iloc[-1]),
            })
        
        if len(data) >= 26:
            macd_line = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()
            macd_signal = macd_line.ewm(span=9).mean()
            technical_indicators.update({
                "macd": float(macd_line.iloc[-1]),
                "macd_signal": float(macd_signal.iloc[-1]),
            })
        
        # Bollinger Bands for AI
        if len(data) >= 20:
            sma_20 = data['Close'].rolling(20).mean()
            std_20 = data['Close'].rolling(20).std()
            technical_indicators.update({
                "bb_upper": float(sma_20.iloc[-1] + (std_20.iloc[-1] * 2)),
                "bb_middle": float(sma_20.iloc[-1]),
                "bb_lower": float(sma_20.iloc[-1] - (std_20.iloc[-1] * 2)),
                "bb_position": float((latest.get('Close', 0) - (sma_20.iloc[-1] - std_20.iloc[-1] * 2)) / (std_20.iloc[-1] * 4)),
            })
        
        return {
            "ticker": ticker,
            "timestamp": _datetime.datetime.now().isoformat(),
            "price_momentum": price_momentum,
            "volume_analysis": volume_analysis,
            "technical_indicators": technical_indicators,
            "data_points": len(data),
            "date_range": {
                "start": data.index[0].strftime('%Y-%m-%d'),
                "end": data.index[-1].strftime('%Y-%m-%d')
            }
        }
        
    except Exception as e:
        logger.error(f"Error formatting financial data for AI: {str(e)}")
        return {"error": str(e)}

def calculate_rsi(prices: _pd.Series, period: int = 14) -> _pd.Series:
    """Calculate RSI for AI analysis"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except Exception as e:
        logger.error(f"Error calculating RSI: {str(e)}")
        return _pd.Series([50] * len(prices), index=prices.index)

def calculate_macd(prices: _pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, _pd.Series]:
    """Calculate MACD for AI analysis"""
    try:
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    except Exception as e:
        logger.error(f"Error calculating MACD: {str(e)}")
        return {
            "macd": _pd.Series([0] * len(prices), index=prices.index),
            "signal": _pd.Series([0] * len(prices), index=prices.index),
            "histogram": _pd.Series([0] * len(prices), index=prices.index)
        }

def calculate_bollinger_bands(prices: _pd.Series, period: int = 20, std: float = 2.0) -> Dict[str, _pd.Series]:
    """Calculate Bollinger Bands for AI analysis"""
    try:
        sma = prices.rolling(window=period).mean()
        std_dev = prices.rolling(window=period).std()
        
        return {
            "upper": sma + (std_dev * std),
            "middle": sma,
            "lower": sma - (std_dev * std),
            "width": (std_dev * std * 2) / sma,
            "position": (prices - (sma - std_dev * std)) / (std_dev * std * 2)
        }
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {str(e)}")
        return {
            "upper": _pd.Series([0] * len(prices), index=prices.index),
            "middle": _pd.Series([0] * len(prices), index=prices.index),
            "lower": _pd.Series([0] * len(prices), index=prices.index),
            "width": _pd.Series([0] * len(prices), index=prices.index),
            "position": _pd.Series([0.5] * len(prices), index=prices.index)
        }

# Enhanced data formatting for AI Market News Impact Analyzer
def format_ai_analysis_data(data: _pd.DataFrame, analysis_type: str = "technical") -> Dict[str, Any]:
    """Format data specifically for AI analysis and reporting"""
    try:
        if data.empty:
            return {"error": "No data available for AI analysis"}
        
        # Common formatting for all analysis types
        formatted_data = {
            "analysis_type": analysis_type,
            "timestamp": _datetime.datetime.now().isoformat(),
            "data_points": len(data),
            "date_range": {
                "start": data.index[0].strftime('%Y-%m-%d %H:%M:%S'),
                "end": data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        if analysis_type == "technical":
            # Technical analysis formatting
            latest = data.iloc[-1]
            formatted_data.update({
                "current_metrics": {
                    "price": float(latest.get('Close', 0)),
                    "volume": int(latest.get('Volume', 0)),
                    "high": float(latest.get('High', 0)),
                    "low": float(latest.get('Low', 0)),
                    "open": float(latest.get('Open', 0))
                },
                "technical_indicators": {
                    "rsi": float(latest.get('RSI_14', 50)),
                    "macd": float(latest.get('MACD_12_26_9', 0)),
                    "macd_signal": float(latest.get('MACDs_12_26_9', 0)),
                    "bollinger_upper": float(latest.get('BBU_20_2.0', 0)),
                    "bollinger_lower": float(latest.get('BBL_20_2.0', 0)),
                    "sma_20": float(latest.get('SMA_20', 0)),
                    "ema_20": float(latest.get('EMA_20', 0))
                }
            })
        
        elif analysis_type == "sentiment":
            # Sentiment analysis formatting
            formatted_data.update({
                "sentiment_metrics": {
                    "overall_sentiment": data.get('sentiment_score', 0),
                    "confidence": data.get('confidence', 0),
                    "news_count": data.get('news_count', 0),
                    "positive_ratio": data.get('positive_ratio', 0.5)
                }
            })
        
        elif analysis_type == "volume":
            # Volume analysis formatting
            volume_data = data['Volume'] if 'Volume' in data.columns else _pd.Series([0])
            formatted_data.update({
                "volume_metrics": {
                    "current_volume": int(volume_data.iloc[-1]),
                    "avg_volume_20d": int(volume_data.rolling(20).mean().iloc[-1]) if len(volume_data) >= 20 else 0,
                    "volume_trend": "increasing" if len(volume_data) >= 5 and volume_data.iloc[-1] > volume_data.iloc[-5] else "decreasing",
                    "volume_spike": volume_data.iloc[-1] > volume_data.rolling(20).mean().iloc[-1] * 2 if len(volume_data) >= 20 else False
                }
            })
        
        return formatted_data
        
    except Exception as e:
        logger.error(f"Error formatting AI analysis data: {str(e)}")
        return {"error": str(e)}

# Enhanced data validation for AI Market News Impact Analyzer
def validate_data_for_ai(data: _pd.DataFrame, required_columns: List[str] = None) -> Dict[str, Any]:
    """Validate data quality for AI analysis"""
    try:
        validation_result = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "data_quality_score": 100
        }
        
        if data.empty:
            validation_result["is_valid"] = False
            validation_result["issues"].append("Data is empty")
            validation_result["data_quality_score"] = 0
            return validation_result
        
        # Check required columns
        if required_columns:
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                validation_result["is_valid"] = False
                validation_result["issues"].append(f"Missing required columns: {missing_columns}")
                validation_result["data_quality_score"] -= 20
        
        # Check for NaN values
        nan_columns = data.columns[data.isnull().any()].tolist()
        if nan_columns:
            validation_result["warnings"].append(f"Columns with NaN values: {nan_columns}")
            validation_result["data_quality_score"] -= 10
        
        # Check data consistency
        if 'Close' in data.columns and 'Open' in data.columns:
            invalid_prices = data[(data['Close'] <= 0) | (data['Open'] <= 0)]
            if not invalid_prices.empty:
                validation_result["warnings"].append(f"Found {len(invalid_prices)} rows with invalid prices")
                validation_result["data_quality_score"] -= 15
        
        # Check date index
        if not isinstance(data.index, _pd.DatetimeIndex):
            validation_result["warnings"].append("Index is not datetime")
            validation_result["data_quality_score"] -= 5
        
        # Check data recency
        if isinstance(data.index, _pd.DatetimeIndex):
            days_old = (_datetime.datetime.now() - data.index[-1]).days
            if days_old > 7:
                validation_result["warnings"].append(f"Data is {days_old} days old")
                validation_result["data_quality_score"] -= min(days_old * 2, 30)
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating data for AI: {str(e)}")
        return {
            "is_valid": False,
            "issues": [f"Validation error: {str(e)}"],
            "warnings": [],
            "data_quality_score": 0
        }

# Enhanced progress tracking for AI Market News Impact Analyzer
class AIProgressBar:
    """Enhanced progress bar for AI Market News Impact Analyzer operations"""
    
    def __init__(self, iterations, text='completed', ai_context=''):
        self.text = text
        self.iterations = iterations
        self.ai_context = ai_context
        self.prog_bar = '[]'
        self.fill_char = '█'
        self.width = 50
        self.__update_amount(0)
        self.elapsed = 1

    def completed(self):
        if self.elapsed > self.iterations:
            self.elapsed = self.iterations
        self.update_iteration(1)
        print('\r' + str(self), end='', file=_sys.stderr)
        _sys.stderr.flush()
        print("", file=_sys.stderr)

    def animate(self, iteration=None):
        if iteration is None:
            self.elapsed += 1
            iteration = self.elapsed
        else:
            self.elapsed += iteration

        print('\r' + str(self), end='', file=_sys.stderr)
        _sys.stderr.flush()
        self.update_iteration()

    def update_iteration(self, val=None):
        val = val if val is not None else self.elapsed / float(self.iterations)
        self.__update_amount(val * 100.0)
        context_text = f" | {self.ai_context}" if self.ai_context else ""
        self.prog_bar += f"  {self.elapsed} of {self.iterations} {self.text}{context_text}"

    def __update_amount(self, new_amount):
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) // 2) - len(str(percent_done))
        pct_string = f'{percent_done}%'
        self.prog_bar = self.prog_bar[0:pct_place] + (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def __str__(self):
        return str(self.prog_bar)

# Enhanced data export for AI Market News Impact Analyzer
def export_data_for_ai(data: _pd.DataFrame, format_type: str = "json", include_metadata: bool = True) -> Union[str, Dict]:
    """Export data in AI-friendly formats"""
    try:
        if format_type == "json":
            export_data = data.to_dict('records')
            if include_metadata:
                export_data = {
                    "metadata": {
                        "ticker": getattr(data, 'ticker', 'unknown'),
                        "export_timestamp": _datetime.datetime.now().isoformat(),
                        "data_points": len(data),
                        "columns": list(data.columns),
                        "date_range": {
                            "start": data.index[0].strftime('%Y-%m-%d') if len(data) > 0 else None,
                            "end": data.index[-1].strftime('%Y-%m-%d') if len(data) > 0 else None
                        }
                    },
                    "data": export_data
                }
            return export_data
        
        elif format_type == "csv":
            return data.to_csv(index=True)
        
        elif format_type == "ai_analysis":
            return format_financial_data_for_ai(data, getattr(data, 'ticker', 'unknown'))
        
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
            
    except Exception as e:
        logger.error(f"Error exporting data for AI: {str(e)}")
        return {"error": str(e)}

# Enhanced error handling for AI Market News Impact Analyzer
def handle_ai_analysis_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """Enhanced error handling for AI analysis operations"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "timestamp": _datetime.datetime.now().isoformat(),
        "suggestions": []
    }
    
    # Add context-specific suggestions
    if "connection" in str(error).lower():
        error_info["suggestions"].append("Check internet connection and try again")
    elif "timeout" in str(error).lower():
        error_info["suggestions"].append("Request timed out, try with a smaller date range")
    elif "data" in str(error).lower():
        error_info["suggestions"].append("Data format issue, check ticker symbol validity")
    elif "rate" in str(error).lower():
        error_info["suggestions"].append("Rate limit exceeded, wait before retrying")
    
    return error_info

# Utility functions for AI Market News Impact Analyzer
def snake_case_2_camelCase(s: str) -> str:
    """Convert snake_case to camelCase for AI Market News Impact Analyzer"""
    sc = s.split('_')[0] + ''.join(x.title() for x in s.split('_')[1:])
    return sc

def camel2title(strings: List[str], sep: str = ' ', acronyms: Optional[List[str]] = None) -> List[str]:
    """Convert camelCase to title case for AI Market News Impact Analyzer"""
    if isinstance(strings, str) or not hasattr(strings, '__iter__'):
        raise TypeError("camel2title() 'strings' argument must be iterable of strings")
    if len(strings) == 0:
        return strings
    if not isinstance(strings[0], str):
        raise TypeError("camel2title() 'strings' argument must be iterable of strings")
    if not isinstance(sep, str) or len(sep) != 1:
        raise ValueError(f"camel2title() 'sep' argument = '{sep}' must be single character")
    if _re.match("[a-zA-Z0-9]", sep):
        raise ValueError(f"camel2title() 'sep' argument = '{sep}' cannot be alpha-numeric")
    if _re.escape(sep) != sep and sep not in {' ', '-'}:
        raise ValueError(f"camel2title() 'sep' argument = '{sep}' cannot be special character")

    if acronyms is None:
        pat = "([a-z])([A-Z])"
        rep = rf"\g<1>{sep}\g<2>"
        return [_re.sub(pat, rep, s).title() for s in strings]

    # Handling acronyms requires more care
    if isinstance(acronyms, str) or not hasattr(acronyms, '__iter__') or not isinstance(acronyms[0], str):
        raise TypeError("camel2title() 'acronyms' argument must be iterable of strings")
    for a in acronyms:
        if not _re.match("^[A-Z]+$", a):
            raise ValueError(f"camel2title() 'acronyms' argument must only contain upper-case, but '{a}' detected")

    # Insert 'sep' between lower-then-upper-case
    pat = "([a-z])([A-Z])"
    rep = rf"\g<1>{sep}\g<2>"
    strings = [_re.sub(pat, rep, s) for s in strings]

    # Insert 'sep' after acronyms
    for a in acronyms:
        pat = f"({a})([A-Z][a-z])"
        rep = rf"\g<1>{sep}\g<2>"
        strings = [_re.sub(pat, rep, s) for s in strings]

    # Apply str.title() to non-acronym words
    strings = [s.split(sep) for s in strings]
    strings = [[j.title() if j not in acronyms else j for j in s] for s in strings]
    strings = [sep.join(s) for s in strings]

    return strings

def empty_df(index=None):
    """Create empty DataFrame for AI Market News Impact Analyzer"""
    if index is None:
        index = []
    empty = _pd.DataFrame(index=index, data={
        'Open': _np.nan, 'High': _np.nan, 'Low': _np.nan,
        'Close': _np.nan, 'Adj Close': _np.nan, 'Volume': _np.nan})
    empty.index.name = 'Date'
    return empty

def format_ai_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Format metadata for AI Market News Impact Analyzer"""
    try:
        formatted_metadata = {
            "ai_analysis_metadata": {
                "processing_timestamp": _datetime.datetime.now().isoformat(),
                "data_source": "yfinance_enhanced",
                "ai_ready": True,
                "analysis_capabilities": [
                    "technical_analysis",
                    "sentiment_analysis", 
                    "volume_analysis",
                    "pattern_recognition",
                    "trend_analysis"
                ]
            }
        }
        
        # Add original metadata
        formatted_metadata.update(metadata)
        
        return formatted_metadata
        
    except Exception as e:
        logger.error(f"Error formatting AI metadata: {str(e)}")
        return {"error": str(e)}
