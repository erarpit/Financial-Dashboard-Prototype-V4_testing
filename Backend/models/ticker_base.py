import logging
from typing import Optional
from .fastinfo import FastInfo
from .quote import Quote, YfData

logger = logging.getLogger(__name__)

class TickerBase:
    """Base ticker class that provides access to FastInfo and Quote"""
    
    def __init__(self, ticker: str, session=None):
        self.ticker = ticker
        self._data = YfData(session=session)
        self._fast_info = None
        self._quote = None
    
    @property
    def fast_info(self) -> FastInfo:
        """Get FastInfo instance for this ticker"""
        if self._fast_info is None:
            self._fast_info = FastInfo(self)
        return self._fast_info
    
    @property
    def quote(self) -> Quote:
        """Get Quote instance for this ticker"""
        if self._quote is None:
            self._quote = Quote(self._data, self.ticker)
        return self._quote
    
    def get_history_metadata(self) -> dict:
        """Get history metadata for the ticker"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(self.ticker)
            return ticker.get_history_metadata()
        except Exception as e:
            logger.error(f"Error getting history metadata for {self.ticker}: {str(e)}")
            return {}
    
    def history(self, period="1y", interval="1d", auto_adjust=True, keepna=True, **kwargs):
        """Get historical data for the ticker"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(self.ticker)
            return ticker.history(period=period, interval=interval, auto_adjust=auto_adjust, keepna=keepna, **kwargs)
        except Exception as e:
            logger.error(f"Error getting history for {self.ticker}: {str(e)}")
            import pandas as pd
            return pd.DataFrame()
    
    def get_shares_full(self, start=None, end=None):
        """Get shares data for the ticker"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(self.ticker)
            return ticker.get_shares_full(start=start, end=end)
        except Exception as e:
            logger.error(f"Error getting shares for {self.ticker}: {str(e)}")
            return None
