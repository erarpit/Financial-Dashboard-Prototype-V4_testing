from typing import Dict, Any, Optional
import logging
from datetime import datetime
from models.ticker_base import TickerBase
from models.schemas import FastInfoData

logger = logging.getLogger(__name__)

class FastInfoService:
    """Service for managing FastInfo data"""
    
    def __init__(self):
        pass
    
    def get_fast_info(self, symbol: str) -> Optional[FastInfoData]:
        """Get comprehensive fast info for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            fast_info = ticker_base.fast_info
            
            # Convert FastInfo to dictionary
            info_dict = {}
            for key in fast_info.keys():
                try:
                    value = fast_info[key]
                    # Convert numpy types to Python types
                    if hasattr(value, 'item'):
                        value = value.item()
                    info_dict[key] = value
                except Exception as e:
                    logger.warning(f"Error getting {key} for {symbol}: {str(e)}")
                    info_dict[key] = None
            
            return FastInfoData(
                symbol=symbol,
                currency=info_dict.get('currency'),
                quote_type=info_dict.get('quote_type'),
                exchange=info_dict.get('exchange'),
                timezone=info_dict.get('timezone'),
                shares=info_dict.get('shares'),
                market_cap=info_dict.get('market_cap'),
                last_price=info_dict.get('last_price'),
                previous_close=info_dict.get('previous_close'),
                open_price=info_dict.get('open'),
                day_high=info_dict.get('day_high'),
                day_low=info_dict.get('day_low'),
                regular_market_previous_close=info_dict.get('regular_market_previous_close'),
                last_volume=info_dict.get('last_volume'),
                fifty_day_average=info_dict.get('fifty_day_average'),
                two_hundred_day_average=info_dict.get('two_hundred_day_average'),
                ten_day_average_volume=info_dict.get('ten_day_average_volume'),
                three_month_average_volume=info_dict.get('three_month_average_volume'),
                year_high=info_dict.get('year_high'),
                year_low=info_dict.get('year_low'),
                year_change=info_dict.get('year_change'),
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting fast info for {symbol}: {str(e)}")
            return None
    
    def get_price_summary(self, symbol: str) -> Dict[str, Any]:
        """Get price summary for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            fast_info = ticker_base.fast_info
            
            return {
                "symbol": symbol,
                "last_price": fast_info.last_price,
                "previous_close": fast_info.previous_close,
                "open": fast_info.open,
                "day_high": fast_info.day_high,
                "day_low": fast_info.day_low,
                "last_volume": fast_info.last_volume,
                "currency": fast_info.currency,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting price summary for {symbol}: {str(e)}")
            return {}
    
    def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Get technical indicators for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            fast_info = ticker_base.fast_info
            
            return {
                "symbol": symbol,
                "fifty_day_average": fast_info.fifty_day_average,
                "two_hundred_day_average": fast_info.two_hundred_day_average,
                "year_high": fast_info.year_high,
                "year_low": fast_info.year_low,
                "year_change": fast_info.year_change,
                "ten_day_average_volume": fast_info.ten_day_average_volume,
                "three_month_average_volume": fast_info.three_month_average_volume,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting technical indicators for {symbol}: {str(e)}")
            return {}
    
    def get_market_cap_info(self, symbol: str) -> Dict[str, Any]:
        """Get market cap information for a symbol"""
        try:
            ticker_base = TickerBase(symbol)
            fast_info = ticker_base.fast_info
            
            return {
                "symbol": symbol,
                "shares": fast_info.shares,
                "market_cap": fast_info.market_cap,
                "last_price": fast_info.last_price,
                "currency": fast_info.currency,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market cap info for {symbol}: {str(e)}")
            return {}

# Global instance
fastinfo_service = FastInfoService()
