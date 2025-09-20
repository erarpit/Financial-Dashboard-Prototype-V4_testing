#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Symbol Mapping Service for Indian to US Stock Symbols
# Maps NSE/BSE symbols to US equivalents for Alpha Vantage compatibility
#
# Copyright 2024 Arpit
# Licensed under the Apache License, Version 2.0

import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class SymbolMappingService:
    """
    Service for mapping Indian stock symbols to US equivalents
    and handling symbol conversions for different data sources
    """
    
    def __init__(self):
        # Mapping of Indian symbols to US equivalents for Alpha Vantage
        self.indian_to_us_mapping = {
            # Major Indian stocks and their US ADR equivalents
            "RELIANCE.NS": "RELIANCE.BSE",  # Reliance Industries
            "TCS.NS": "TCS.BSE",           # Tata Consultancy Services
            "HDFCBANK.NS": "HDB",          # HDFC Bank ADR
            "INFY.NS": "INFY",             # Infosys ADR
            "HINDUNILVR.NS": "HINDUNILEVR.BSE",  # Hindustan Unilever
            "ITC.NS": "ITC.BSE",           # ITC Limited
            "SBIN.NS": "SBIN.BSE",         # State Bank of India
            "BHARTIARTL.NS": "BHRT.BSE",   # Bharti Airtel
            "KOTAKBANK.NS": "KOTAKBANK.BSE", # Kotak Mahindra Bank
            "LT.NS": "LTT.BSE",            # Larsen & Toubro
            "WIPRO.NS": "WIT",             # Wipro ADR
            "ASIANPAINT.NS": "ASIANPAINT.BSE", # Asian Paints
            "MARUTI.NS": "MARUTI.BSE",     # Maruti Suzuki
            "NESTLEIND.NS": "NESTLEIND.BSE", # Nestle India
            "TITAN.NS": "TITAN.BSE",       # Titan Company
            "ULTRACEMCO.NS": "ULTRACEMCO.BSE", # UltraTech Cement
            "BAJFINANCE.NS": "BAJFINANCE.BSE", # Bajaj Finance
            "BAJAJFINSV.NS": "BAJAJFINSV.BSE", # Bajaj Finserv
            "HCLTECH.NS": "HCLTECH.BSE",   # HCL Technologies
            "TECHM.NS": "TECHM.BSE",       # Tech Mahindra
        }
        
        # Reverse mapping for reference
        self.us_to_indian_mapping = {v: k for k, v in self.indian_to_us_mapping.items()}
        
        # Indian stock exchanges
        self.indian_exchanges = {
            "NSE": "National Stock Exchange",
            "BSE": "Bombay Stock Exchange"
        }
        
        # Popular Indian stock symbols by sector
        self.indian_stocks_by_sector = {
            "Banking": [
                "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", 
                "AXISBANK.NS", "INDUSINDBK.NS", "BANDHANBNK.NS"
            ],
            "IT": [
                "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS",
                "MINDTREE.NS", "LTI.NS", "MPHASIS.NS"
            ],
            "FMCG": [
                "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "DABUR.NS",
                "BRITANNIA.NS", "GODREJCP.NS", "MARICO.NS"
            ],
            "Automobile": [
                "MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS",
                "M&M.NS", "EICHERMOT.NS", "TVSMOTORS.NS"
            ],
            "Pharmaceuticals": [
                "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS",
                "LUPIN.NS", "AUROPHARMA.NS", "BIOCON.NS"
            ],
            "Energy": [
                "RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "HPCL.NS",
                "GAIL.NS", "PETRONET.NS"
            ],
            "Telecom": [
                "BHARTIARTL.NS", "RCOM.NS", "IDEA.NS", "TATACOMM.NS"
            ],
            "Metals": [
                "TATASTEEL.NS", "JSWSTEEL.NS", "SAIL.NS", "HINDALCO.NS",
                "VEDL.NS", "NMDC.NS", "COALINDIA.NS"
            ]
        }
    
    def get_us_symbol(self, indian_symbol: str) -> Optional[str]:
        """
        Get US equivalent symbol for Indian symbol
        
        Args:
            indian_symbol: Indian stock symbol (e.g., 'RELIANCE.NS')
            
        Returns:
            US equivalent symbol or None if not found
        """
        return self.indian_to_us_mapping.get(indian_symbol)
    
    def get_indian_symbol(self, us_symbol: str) -> Optional[str]:
        """
        Get Indian equivalent symbol for US symbol
        
        Args:
            us_symbol: US stock symbol (e.g., 'HDB')
            
        Returns:
            Indian equivalent symbol or None if not found
        """
        return self.us_to_indian_mapping.get(us_symbol)
    
    def is_indian_symbol(self, symbol: str) -> bool:
        """
        Check if symbol is an Indian stock symbol
        
        Args:
            symbol: Stock symbol to check
            
        Returns:
            True if Indian symbol, False otherwise
        """
        return symbol.endswith('.NS') or symbol.endswith('.BSE')
    
    def get_symbol_info(self, symbol: str) -> Dict[str, str]:
        """
        Get comprehensive symbol information
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with symbol information
        """
        info = {
            "original_symbol": symbol,
            "is_indian": self.is_indian_symbol(symbol),
            "exchange": "Unknown",
            "us_equivalent": None,
            "indian_equivalent": None
        }
        
        if self.is_indian_symbol(symbol):
            info["exchange"] = "NSE" if symbol.endswith('.NS') else "BSE"
            info["us_equivalent"] = self.get_us_symbol(symbol)
        else:
            info["indian_equivalent"] = self.get_indian_symbol(symbol)
            info["exchange"] = "US"
        
        return info
    
    def get_sector_stocks(self, sector: str) -> List[str]:
        """
        Get Indian stocks for a specific sector
        
        Args:
            sector: Sector name (e.g., 'Banking', 'IT')
            
        Returns:
            List of Indian stock symbols in the sector
        """
        return self.indian_stocks_by_sector.get(sector, [])
    
    def get_all_indian_symbols(self) -> List[str]:
        """
        Get all available Indian stock symbols
        
        Returns:
            List of all Indian stock symbols
        """
        return list(self.indian_to_us_mapping.keys())
    
    def get_popular_indian_symbols(self, limit: int = 20) -> List[str]:
        """
        Get popular Indian stock symbols
        
        Args:
            limit: Maximum number of symbols to return
            
        Returns:
            List of popular Indian stock symbols
        """
        popular = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
            "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS",
            "WIPRO.NS", "ASIANPAINT.NS", "MARUTI.NS", "NESTLEIND.NS", "TITAN.NS",
            "ULTRACEMCO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "HCLTECH.NS", "TECHM.NS"
        ]
        return popular[:limit]
    
    def convert_for_alpha_vantage(self, symbol: str) -> str:
        """
        Convert symbol for Alpha Vantage API compatibility
        
        Args:
            symbol: Original symbol
            
        Returns:
            Symbol compatible with Alpha Vantage
        """
        if self.is_indian_symbol(symbol):
            us_symbol = self.get_us_symbol(symbol)
            if us_symbol:
                return us_symbol
            else:
                # If no US equivalent, try to use a generic approach
                # Remove .NS/.BSE and try as is
                base_symbol = symbol.replace('.NS', '').replace('.BSE', '')
                return base_symbol
        
        return symbol
    
    def get_alpha_vantage_fallback_symbols(self, indian_symbol: str) -> List[str]:
        """
        Get fallback symbols for Alpha Vantage when direct mapping fails
        
        Args:
            indian_symbol: Indian stock symbol
            
        Returns:
            List of fallback symbols to try
        """
        fallbacks = []
        
        # Try direct US equivalent
        us_symbol = self.get_us_symbol(indian_symbol)
        if us_symbol:
            fallbacks.append(us_symbol)
        
        # Try base symbol without exchange suffix
        base_symbol = indian_symbol.replace('.NS', '').replace('.BSE', '')
        fallbacks.append(base_symbol)
        
        # Try with different exchange suffixes
        fallbacks.append(f"{base_symbol}.BSE")
        fallbacks.append(f"{base_symbol}.NS")
        
        return fallbacks

# Global instance
symbol_mapping_service = SymbolMappingService()
