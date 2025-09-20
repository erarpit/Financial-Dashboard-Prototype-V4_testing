from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from models.ticker_base import TickerBase
from models.schemas import QuoteData, SustainabilityData, RecommendationData, CalendarData

logger = logging.getLogger(__name__)

class QuoteService:
    """Service for managing Quote data"""
    
    def __init__(self):
        pass
    
    def get_quote_info(self, symbol: str) -> Optional[QuoteData]:
        """Get comprehensive quote info for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            quote = ticker_base.quote
            info = quote.info
            
            return QuoteData(
                symbol=symbol,
                info=info,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting quote info for {symbol}: {str(e)}")
            return None
    
    def get_sustainability_data(self, symbol: str) -> Optional[SustainabilityData]:
        """Get sustainability data for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            quote = ticker_base.quote
            sustainability = quote.sustainability
            
            if sustainability.empty:
                return SustainabilityData(
                    symbol=symbol,
                    data={},
                    last_updated=datetime.now().isoformat()
                )
            
            # Convert DataFrame to dictionary
            data = sustainability.to_dict('index')
            return SustainabilityData(
                symbol=symbol,
                data=data,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting sustainability data for {symbol}: {str(e)}")
            return None
    
    def get_recommendations(self, symbol: str) -> Optional[RecommendationData]:
        """Get analyst recommendations for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            quote = ticker_base.quote
            recommendations = quote.recommendations
            
            if recommendations.empty:
                return RecommendationData(
                    symbol=symbol,
                    data=[],
                    last_updated=datetime.now().isoformat()
                )
            
            # Convert DataFrame to list of dictionaries
            data = recommendations.to_dict('records')
            return RecommendationData(
                symbol=symbol,
                data=data,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting recommendations for {symbol}: {str(e)}")
            return None
    
    def get_upgrades_downgrades(self, symbol: str) -> List[Dict[str, Any]]:
        """Get upgrades/downgrades for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            quote = ticker_base.quote
            upgrades_downgrades = quote.upgrades_downgrades
            
            if upgrades_downgrades.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            return upgrades_downgrades.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting upgrades/downgrades for {symbol}: {str(e)}")
            return []
    
    def get_calendar_events(self, symbol: str) -> Optional[CalendarData]:
        """Get calendar events for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            quote = ticker_base.quote
            calendar = quote.calendar
            
            return CalendarData(
                symbol=symbol,
                events=calendar,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting calendar events for {symbol}: {str(e)}")
            return None
    
    def get_sec_filings(self, symbol: str) -> List[Dict[str, Any]]:
        """Get SEC filings for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            quote = ticker_base.quote
            sec_filings = quote.sec_filings
            
            if not sec_filings:
                return []
            
            return sec_filings
            
        except Exception as e:
            logger.error(f"Error getting SEC filings for {symbol}: {str(e)}")
            return []
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get basic company information"""
        try:
            ticker_base = TickerBase(symbol)
            quote = ticker_base.quote
            info = quote.info
            
            # Extract key company information
            company_info = {
                "symbol": symbol,
                "long_name": info.get("longName", ""),
                "short_name": info.get("shortName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "website": info.get("website", ""),
                "city": info.get("city", ""),
                "state": info.get("state", ""),
                "country": info.get("country", ""),
                "full_time_employees": info.get("fullTimeEmployees", 0),
                "description": info.get("longBusinessSummary", ""),
                "market_cap": info.get("marketCap", 0),
                "currency": info.get("currency", "USD"),
                "last_updated": datetime.now().isoformat()
            }
            
            return company_info
            
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {str(e)}")
            return {}

# Global instance
quote_service = QuoteService()
