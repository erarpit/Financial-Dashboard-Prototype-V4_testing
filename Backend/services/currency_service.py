#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Currency Conversion Service for AI Market News Impact Analyzer
# Handles USD to INR conversion and currency formatting
#
# Copyright 2024 Arpit
# Licensed under the Apache License, Version 2.0

import os
import logging
import requests
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CurrencyService:
    """
    Service for currency conversion and formatting
    """
    
    def __init__(self):
        self.usd_to_inr_rate = 83.0  # Default rate, will be updated from API
        self.last_update = None
        self.cache_duration = 3600  # 1 hour cache
        self.api_key = os.getenv('CURRENCY_API_KEY')  # Optional API key for real-time rates
        
    def get_usd_to_inr_rate(self) -> float:
        """Get current USD to INR exchange rate"""
        # Check if we have a recent cached rate
        if (self.last_update and 
            datetime.now() - self.last_update < timedelta(seconds=self.cache_duration)):
            return self.usd_to_inr_rate
        
        # Try to get real-time rate from API
        if self.api_key:
            try:
                rate = self._fetch_real_time_rate()
                if rate:
                    self.usd_to_inr_rate = rate
                    self.last_update = datetime.now()
                    logger.info(f"Updated USD to INR rate: {rate}")
                    return rate
            except Exception as e:
                logger.warning(f"Failed to fetch real-time rate: {e}")
        
        # Fallback to default rate
        logger.info(f"Using default USD to INR rate: {self.usd_to_inr_rate}")
        return self.usd_to_inr_rate
    
    def _fetch_real_time_rate(self) -> Optional[float]:
        """Fetch real-time exchange rate from API"""
        try:
            # Using exchangerate-api.com (free, no API key required)
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            inr_rate = data.get('rates', {}).get('INR')
            
            if inr_rate:
                return float(inr_rate)
            
        except Exception as e:
            logger.error(f"Error fetching real-time rate: {e}")
        
        return None
    
    def convert_usd_to_inr(self, usd_amount: Union[float, int]) -> float:
        """Convert USD amount to INR"""
        if usd_amount is None:
            return 0.0
        
        rate = self.get_usd_to_inr_rate()
        return float(usd_amount) * rate
    
    def format_currency(self, amount: Union[float, int], currency: str = "INR", 
                       decimals: int = 2, show_symbol: bool = True) -> str:
        """
        Format currency amount with proper symbol and formatting
        
        Args:
            amount: The amount to format
            currency: Currency code (INR, USD)
            decimals: Number of decimal places
            show_symbol: Whether to show currency symbol
        """
        if amount is None:
            return 'N/A'
        
        amount = float(amount)
        
        # Format large numbers with K, M, B, T suffixes
        if abs(amount) >= 1e12:
            formatted = f"{amount / 1e12:.{decimals}f}T"
        elif abs(amount) >= 1e9:
            formatted = f"{amount / 1e9:.{decimals}f}B"
        elif abs(amount) >= 1e6:
            formatted = f"{amount / 1e6:.{decimals}f}M"
        elif abs(amount) >= 1e3:
            formatted = f"{amount / 1e3:.{decimals}f}K"
        else:
            formatted = f"{amount:.{decimals}f}"
        
        # Add currency symbol
        if show_symbol:
            if currency.upper() == "INR":
                return f"₹{formatted}"
            elif currency.upper() == "USD":
                return f"${formatted}"
            else:
                return f"{currency} {formatted}"
        
        return formatted
    
    def format_inr(self, amount: Union[float, int], decimals: int = 2) -> str:
        """Format amount in INR"""
        return self.format_currency(amount, "INR", decimals, True)
    
    def format_usd(self, amount: Union[float, int], decimals: int = 2) -> str:
        """Format amount in USD"""
        return self.format_currency(amount, "USD", decimals, True)
    
    def convert_and_format(self, usd_amount: Union[float, int], 
                          decimals: int = 2) -> str:
        """Convert USD to INR and format"""
        inr_amount = self.convert_usd_to_inr(usd_amount)
        return self.format_inr(inr_amount, decimals)
    
    def format_percentage(self, value: Union[float, int], decimals: int = 2) -> str:
        """Format percentage value"""
        if value is None:
            return 'N/A'
        
        return f"{float(value):.{decimals}f}%"
    
    def format_volume(self, volume: Union[float, int]) -> str:
        """Format volume with appropriate suffixes"""
        if volume is None:
            return 'N/A'
        
        volume = float(volume)
        
        if abs(volume) >= 1e9:
            return f"{volume / 1e9:.2f}B"
        elif abs(volume) >= 1e6:
            return f"{volume / 1e6:.2f}M"
        elif abs(volume) >= 1e3:
            return f"{volume / 1e3:.2f}K"
        else:
            return f"{volume:,.0f}"
    
    def get_currency_info(self) -> Dict[str, Any]:
        """Get currency service information"""
        return {
            "usd_to_inr_rate": self.usd_to_inr_rate,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "cache_duration_seconds": self.cache_duration,
            "api_key_configured": bool(self.api_key)
        }

# Global instance
currency_service = CurrencyService()
