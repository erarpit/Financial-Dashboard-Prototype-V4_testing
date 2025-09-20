import datetime as dt
import json as _json
import warnings
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Constants
_QUERY1_URL_ = "https://query1.finance.yahoo.com"
_SENTINEL_ = object()

class YfData:
    """Yahoo Finance data fetcher with session management"""
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def cache_get(self, url: str, params: Dict = None, timeout: int = 30) -> Optional[requests.Response]:
        """Fetch data from URL with caching"""
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Error fetching data from {url}: {str(e)}")
            return None
    
    def get_raw_json(self, url: str, params: Dict = None) -> Dict:
        """Fetch JSON data from URL"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching JSON from {url}: {str(e)}")
            return {}

class Market:
    """Market status and summary data fetcher"""
    
    def __init__(self, market: str, session=None, proxy=_SENTINEL_, timeout=30):
        self.market = market
        self.session = session
        self.timeout = timeout

        self._data = YfData(session=self.session)
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._data._set_proxy(proxy)

        self._logger = logger
        
        self._status = None
        self._summary = None

    def _fetch_json(self, url, params):
        data = self._data.cache_get(url=url, params=params, timeout=self.timeout)
        if data is None or "Will be right back" in data.text:
            raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***\n"
                               "Our engineers are working quickly to resolve "
                               "the issue. Thank you for your patience.")
        try:
            return data.json()
        except _json.JSONDecodeError:
            self._logger.error(f"{self.market}: Failed to retrieve market data and received faulty data.")
            return {}
        
    def _parse_data(self):
        # Fetch both to ensure they are at the same time
        if (self._status is not None) and (self._summary is not None):
            return
        
        self._logger.debug(f"{self.market}: Parsing market data")

        # Summary
        summary_url = f"{_QUERY1_URL_}/v6/finance/quote/marketSummary"
        summary_fields = ["shortName", "regularMarketPrice", "regularMarketChange", "regularMarketChangePercent"]
        summary_params = {
            "fields": ",".join(summary_fields),
            "formatted": False,
            "lang": "en-US",
            "market": self.market
        }

        status_url = f"{_QUERY1_URL_}/v6/finance/markettime"
        status_params = {
            "formatted": True,
            "key": "finance",
            "lang": "en-US",
            "market": self.market
        }

        self._summary = self._fetch_json(summary_url, summary_params)
        self._status = self._fetch_json(status_url, status_params)

        try:
            self._summary = self._summary['marketSummaryResponse']['result']
            self._summary = {x['exchange']:x for x in self._summary}
        except Exception as e:
            self._logger.error(f"{self.market}: Failed to parse market summary")
            self._logger.debug(f"{type(e)}: {e}")

        try:
            # Unpack
            self._status = self._status['finance']['marketTimes'][0]['marketTime'][0]
            self._status['timezone'] = self._status['timezone'][0]
            del self._status['time']  # redundant
            try:
                self._status.update({
                    "open": dt.datetime.fromisoformat(self._status["open"]),
                    "close": dt.datetime.fromisoformat(self._status["close"]),
                    "tz": dt.timezone(dt.timedelta(hours=int(self._status["timezone"]["gmtoffset"]))/1000, self._status["timezone"]["short"])
                })
            except Exception as e:
                self._logger.error(f"{self.market}: Failed to update market status")
                self._logger.debug(f"{type(e)}: {e}")
        except Exception as e:
            self._logger.error(f"{self.market}: Failed to parse market status")
            self._logger.debug(f"{type(e)}: {e}")

    @property
    def status(self):
        self._parse_data()
        return self._status

    @property
    def summary(self):
        self._parse_data()
        return self._summary
