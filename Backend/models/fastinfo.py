import curl_cffi
import datetime
import json
import numpy as _np
import pandas as pd
import warnings
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Constants
_BASE_URL_ = "https://query1.finance.yahoo.com"
_QUERY1_URL_ = "https://query1.finance.yahoo.com"
_SENTINEL_ = object()

class YfData:
    """Yahoo Finance data fetcher with session management"""
    
    def __init__(self, session=None):
        self.session = session or curl_cffi.requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_raw_json(self, url: str, params: Dict = None) -> Dict:
        """Fetch JSON data from URL"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching JSON from {url}: {str(e)}")
            return {}
    
    def cache_get(self, url: str, params: Dict = None) -> Optional[curl_cffi.requests.Response]:
        """Fetch data from URL with caching"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Error fetching data from {url}: {str(e)}")
            return None

def snake_case_2_camelCase(snake_str):
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def _interval_to_timedelta(interval):
    """Convert interval string to timedelta"""
    if interval == "1d":
        return datetime.timedelta(days=1)
    elif interval == "1h":
        return datetime.timedelta(hours=1)
    elif interval == "1m":
        return datetime.timedelta(minutes=1)
    elif interval == "1y":
        return datetime.timedelta(days=365)
    elif interval == "3mo":
        return datetime.timedelta(days=90)
    else:
        return datetime.timedelta(days=1)

class FastInfo:
    """Enhanced stock information with fast access to key metrics"""
    
    def __init__(self, ticker_base_object, proxy=_SENTINEL_):
        self._tkr = ticker_base_object
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._tkr._data._set_proxy(proxy)

        self._prices_1y = None
        self._prices_1wk_1h_prepost = None
        self._prices_1wk_1h_reg = None
        self._md = None

        self._currency = None
        self._quote_type = None
        self._exchange = None
        self._timezone = None

        self._shares = None
        self._mcap = None

        self._open = None
        self._day_high = None
        self._day_low = None
        self._last_price = None
        self._last_volume = None

        self._prev_close = None
        self._reg_prev_close = None

        self._50d_day_average = None
        self._200d_day_average = None
        self._year_high = None
        self._year_low = None
        self._year_change = None

        self._10d_avg_vol = None
        self._3mo_avg_vol = None

        # Define properties for dict-like interface
        _properties = ["currency", "quote_type", "exchange", "timezone"]
        _properties += ["shares", "market_cap"]
        _properties += ["last_price", "previous_close", "open", "day_high", "day_low"]
        _properties += ["regular_market_previous_close"]
        _properties += ["last_volume"]
        _properties += ["fifty_day_average", "two_hundred_day_average", "ten_day_average_volume", "three_month_average_volume"]
        _properties += ["year_high", "year_low", "year_change"]

        # Support both snake_case and camelCase
        base_keys = [k for k in _properties if '_' not in k]
        sc_keys = [k for k in _properties if '_' in k]
        self._sc_to_cc_key = {k: snake_case_2_camelCase(k) for k in sc_keys}
        self._cc_to_sc_key = {v: k for k, v in self._sc_to_cc_key.items()}
        self._public_keys = sorted(base_keys + list(self._sc_to_cc_key.values()))
        self._keys = sorted(self._public_keys + sc_keys)

    def keys(self):
        return self._public_keys

    def items(self):
        return [(k, self[k]) for k in self._public_keys]

    def values(self):
        return [self[k] for k in self._public_keys]

    def get(self, key, default=None):
        if key in self.keys():
            if key in self._cc_to_sc_key:
                key = self._cc_to_sc_key[key]
            return self[key]
        return default

    def __getitem__(self, k):
        if not isinstance(k, str):
            raise KeyError("key must be a string")
        if k not in self._keys:
            raise KeyError(f"'{k}' not valid key. Examine 'FastInfo.keys()'")
        if k in self._cc_to_sc_key:
            k = self._cc_to_sc_key[k]
        return getattr(self, k)

    def __contains__(self, k):
        return k in self.keys()

    def __iter__(self):
        return iter(self.keys())

    def __str__(self):
        return "lazy-loading dict with keys = " + str(self.keys())

    def __repr__(self):
        return self.__str__()

    def toJSON(self, indent=4):
        return json.dumps({k: self[k] for k in self.keys()}, indent=indent)

    def _get_1y_prices(self, fullDaysOnly=False):
        if self._prices_1y is None:
            try:
                # Use yfinance to get historical data
                import yfinance as yf
                ticker = yf.Ticker(self._tkr.ticker)
                self._prices_1y = ticker.history(period="1y", auto_adjust=False, keepna=True)
                self._md = ticker.get_history_metadata()
            except Exception as e:
                logger.error(f"Error fetching 1y prices: {str(e)}")
                self._prices_1y = pd.DataFrame()
                self._md = {}

        if self._prices_1y.empty:
            return self._prices_1y

        return self._prices_1y

    def _get_1wk_1h_prepost_prices(self):
        if self._prices_1wk_1h_prepost is None:
            try:
                import yfinance as yf
                ticker = yf.Ticker(self._tkr.ticker)
                self._prices_1wk_1h_prepost = ticker.history(period="5d", interval="1h", auto_adjust=False, prepost=True)
            except Exception as e:
                logger.error(f"Error fetching 1wk 1h prepost prices: {str(e)}")
                self._prices_1wk_1h_prepost = pd.DataFrame()
        return self._prices_1wk_1h_prepost

    def _get_1wk_1h_reg_prices(self):
        if self._prices_1wk_1h_reg is None:
            try:
                import yfinance as yf
                ticker = yf.Ticker(self._tkr.ticker)
                self._prices_1wk_1h_reg = ticker.history(period="5d", interval="1h", auto_adjust=False, prepost=False)
            except Exception as e:
                logger.error(f"Error fetching 1wk 1h reg prices: {str(e)}")
                self._prices_1wk_1h_reg = pd.DataFrame()
        return self._prices_1wk_1h_reg

    def _get_exchange_metadata(self):
        if self._md is not None:
            return self._md

        self._get_1y_prices()
        return self._md

    def _exchange_open_now(self):
        # Simplified implementation
        return True

    @property
    def currency(self):
        if self._currency is not None:
            return self._currency

        md = self._get_exchange_metadata()
        self._currency = md.get("currency", "USD")
        return self._currency

    @property
    def quote_type(self):
        if self._quote_type is not None:
            return self._quote_type

        md = self._get_exchange_metadata()
        self._quote_type = md.get("instrumentType", "EQUITY")
        return self._quote_type

    @property
    def exchange(self):
        if self._exchange is not None:
            return self._exchange

        self._exchange = self._get_exchange_metadata().get("exchangeName", "NSE")
        return self._exchange

    @property
    def timezone(self):
        if self._timezone is not None:
            return self._timezone

        self._timezone = self._get_exchange_metadata().get("exchangeTimezoneName", "Asia/Kolkata")
        return self._timezone

    @property
    def shares(self):
        if self._shares is not None:
            return self._shares

        try:
            import yfinance as yf
            ticker = yf.Ticker(self._tkr.ticker)
            shares = ticker.get_shares_full(start=pd.Timestamp.utcnow().date()-pd.Timedelta(days=548))
            if shares is not None:
                if isinstance(shares, pd.DataFrame):
                    shares = shares[shares.columns[0]]
                self._shares = int(shares.iloc[-1])
        except Exception as e:
            logger.error(f"Error fetching shares: {str(e)}")
            self._shares = None
        return self._shares

    @property
    def last_price(self):
        if self._last_price is not None:
            return self._last_price
        prices = self._get_1y_prices()
        if prices.empty:
            md = self._get_exchange_metadata()
            if "regularMarketPrice" in md:
                self._last_price = md["regularMarketPrice"]
        else:
            self._last_price = float(prices["Close"].iloc[-1])
            if _np.isnan(self._last_price):
                md = self._get_exchange_metadata()
                if "regularMarketPrice" in md:
                    self._last_price = md["regularMarketPrice"]
        return self._last_price

    @property
    def previous_close(self):
        if self._prev_close is not None:
            return self._prev_close
        prices = self._get_1wk_1h_prepost_prices()
        if prices.empty:
            self._prev_close = None
        else:
            prices = prices[["Close"]].groupby(prices.index.date).last()
            if prices.shape[0] < 2:
                self._prev_close = None
            else:
                self._prev_close = float(prices["Close"].iloc[-2])
        return self._prev_close

    @property
    def regular_market_previous_close(self):
        if self._reg_prev_close is not None:
            return self._reg_prev_close
        prices = self._get_1y_prices()
        if prices.shape[0] == 1:
            prices = self._get_1wk_1h_reg_prices()
            prices = prices[["Close"]].groupby(prices.index.date).last()
        if prices.shape[0] < 2:
            self._reg_prev_close = None
        else:
            self._reg_prev_close = float(prices["Close"].iloc[-2])
        return self._reg_prev_close

    @property
    def open(self):
        if self._open is not None:
            return self._open
        prices = self._get_1y_prices()
        if prices.empty:
            self._open = None
        else:
            self._open = float(prices["Open"].iloc[-1])
            if _np.isnan(self._open):
                self._open = None
        return self._open

    @property
    def day_high(self):
        if self._day_high is not None:
            return self._day_high
        prices = self._get_1y_prices()
        if prices.empty:
            self._day_high = None
        else:
            self._day_high = float(prices["High"].iloc[-1])
            if _np.isnan(self._day_high):
                self._day_high = None
        return self._day_high

    @property
    def day_low(self):
        if self._day_low is not None:
            return self._day_low
        prices = self._get_1y_prices()
        if prices.empty:
            self._day_low = None
        else:
            self._day_low = float(prices["Low"].iloc[-1])
            if _np.isnan(self._day_low):
                self._day_low = None
        return self._day_low

    @property
    def last_volume(self):
        if self._last_volume is not None:
            return self._last_volume
        prices = self._get_1y_prices()
        self._last_volume = None if prices.empty else int(prices["Volume"].iloc[-1])
        return self._last_volume

    @property
    def fifty_day_average(self):
        if self._50d_day_average is not None:
            return self._50d_day_average

        prices = self._get_1y_prices(fullDaysOnly=True)
        if prices.empty:
            self._50d_day_average = None
        else:
            n = prices.shape[0]
            a = n-50
            b = n
            if a < 0:
                a = 0
            self._50d_day_average = float(prices["Close"].iloc[a:b].mean())
        return self._50d_day_average

    @property
    def two_hundred_day_average(self):
        if self._200d_day_average is not None:
            return self._200d_day_average

        prices = self._get_1y_prices(fullDaysOnly=True)
        if prices.empty:
            self._200d_day_average = None
        else:
            n = prices.shape[0]
            a = n-200
            b = n
            if a < 0:
                a = 0
            self._200d_day_average = float(prices["Close"].iloc[a:b].mean())
        return self._200d_day_average

    @property
    def ten_day_average_volume(self):
        if self._10d_avg_vol is not None:
            return self._10d_avg_vol

        prices = self._get_1y_prices(fullDaysOnly=True)
        if prices.empty:
            self._10d_avg_vol = None
        else:
            n = prices.shape[0]
            a = n-10
            b = n
            if a < 0:
                a = 0
            self._10d_avg_vol = int(prices["Volume"].iloc[a:b].mean())
        return self._10d_avg_vol

    @property
    def three_month_average_volume(self):
        if self._3mo_avg_vol is not None:
            return self._3mo_avg_vol

        prices = self._get_1y_prices(fullDaysOnly=True)
        if prices.empty:
            self._3mo_avg_vol = None
        else:
            dt1 = prices.index[-1]
            dt0 = dt1 - _interval_to_timedelta("3mo") + _interval_to_timedelta("1d")
            self._3mo_avg_vol = int(prices.loc[dt0:dt1, "Volume"].mean())
        return self._3mo_avg_vol

    @property
    def year_high(self):
        if self._year_high is not None:
            return self._year_high

        prices = self._get_1y_prices(fullDaysOnly=True)
        if prices.empty:
            prices = self._get_1y_prices(fullDaysOnly=False)
        self._year_high = float(prices["High"].max())
        return self._year_high

    @property
    def year_low(self):
        if self._year_low is not None:
            return self._year_low

        prices = self._get_1y_prices(fullDaysOnly=True)
        if prices.empty:
            prices = self._get_1y_prices(fullDaysOnly=False)
        self._year_low = float(prices["Low"].min())
        return self._year_low

    @property
    def year_change(self):
        if self._year_change is not None:
            return self._year_change

        prices = self._get_1y_prices(fullDaysOnly=True)
        if prices.shape[0] >= 2:
            self._year_change = (prices["Close"].iloc[-1] - prices["Close"].iloc[0]) / prices["Close"].iloc[0]
            self._year_change = float(self._year_change)
        return self._year_change

    @property
    def market_cap(self):
        if self._mcap is not None:
            return self._mcap

        try:
            shares = self.shares
        except Exception as e:
            logger.error(f"Error getting shares for market cap: {str(e)}")
            shares = None

        if shares is None:
            self._mcap = None
        else:
            self._mcap = float(shares * self.last_price)
        return self._mcap
