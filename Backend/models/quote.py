import curl_cffi
import datetime
import json
import pandas as pd
import warnings
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Constants
_BASE_URL_ = "https://query1.finance.yahoo.com"
_QUERY1_URL_ = "https://query1.finance.yahoo.com"
_SENTINEL_ = object()
_QUOTE_SUMMARY_URL_ = f"{_BASE_URL_}/v10/finance/quoteSummary"

# Valid modules for quote summary
quote_summary_valid_modules = [
    'assetProfile', 'summaryDetail', 'recommendationTrend', 'upgradeDowngradeHistory',
    'institutionOwnership', 'fundOwnership', 'majorDirectHolders', 'majorHoldersBreakdown',
    'insiderTransactions', 'insiderHolders', 'netSharePurchaseActivity', 'earnings',
    'earningsHistory', 'earningsTrend', 'industryTrend', 'indexTrend', 'sectorTrend',
    'calendarEvents', 'secFilings', 'upgradeDowngradeHistory', 'institutionOwnership',
    'fundOwnership', 'majorDirectHolders', 'majorHoldersBreakdown', 'insiderTransactions',
    'insiderHolders', 'netSharePurchaseActivity', 'esgScores', 'price', 'summaryProfile'
]

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

class YFDataException(Exception):
    """Custom exception for Yahoo Finance data errors"""
    pass

class YFException(Exception):
    """Custom exception for Yahoo Finance errors"""
    pass

class Quote:
    """Comprehensive quote data fetcher"""
    
    def __init__(self, data: YfData, symbol: str, proxy=_SENTINEL_):
        self._data = data
        self._symbol = symbol
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._data._set_proxy(proxy)

        self._info = None
        self._retired_info = None
        self._sustainability = None
        self._recommendations = None
        self._upgrades_downgrades = None
        self._calendar = None
        self._sec_filings = None

        self._already_scraped = False
        self._already_fetched = False
        self._already_fetched_complementary = False

    @property
    def info(self) -> dict:
        if self._info is None:
            self._fetch_info()
            self._fetch_complementary()

        return self._info

    @property
    def sustainability(self) -> pd.DataFrame:
        if self._sustainability is None:
            result = self._fetch(modules=['esgScores'])
            if result is None:
                self._sustainability = pd.DataFrame()
            else:
                try:
                    data = result["quoteSummary"]["result"][0]
                except (KeyError, IndexError):
                    raise YFDataException(f"Failed to parse json response from Yahoo Finance: {result}")
                self._sustainability = pd.DataFrame(data)
        return self._sustainability

    @property
    def recommendations(self) -> pd.DataFrame:
        if self._recommendations is None:
            result = self._fetch(modules=['recommendationTrend'])
            if result is None:
                self._recommendations = pd.DataFrame()
            else:
                try:
                    data = result["quoteSummary"]["result"][0]["recommendationTrend"]["trend"]
                except (KeyError, IndexError):
                    raise YFDataException(f"Failed to parse json response from Yahoo Finance: {result}")
                self._recommendations = pd.DataFrame(data)
        return self._recommendations

    @property
    def upgrades_downgrades(self) -> pd.DataFrame:
        if self._upgrades_downgrades is None:
            result = self._fetch(modules=['upgradeDowngradeHistory'])
            if result is None:
                self._upgrades_downgrades = pd.DataFrame()
            else:
                try:
                    data = result["quoteSummary"]["result"][0]["upgradeDowngradeHistory"]["history"]
                    if len(data) == 0:
                        raise YFDataException(f"No upgrade/downgrade history found for {self._symbol}")
                    df = pd.DataFrame(data)
                    df.rename(columns={"epochGradeDate": "GradeDate", 'firm': 'Firm', 'toGrade': 'ToGrade', 'fromGrade': 'FromGrade', 'action': 'Action'}, inplace=True)
                    df.set_index('GradeDate', inplace=True)
                    df.index = pd.to_datetime(df.index, unit='s')
                    self._upgrades_downgrades = df
                except (KeyError, IndexError):
                    raise YFDataException(f"Failed to parse json response from Yahoo Finance: {result}")
        return self._upgrades_downgrades

    @property
    def calendar(self) -> dict:
        if self._calendar is None:
            self._fetch_calendar()
        return self._calendar

    @property
    def sec_filings(self) -> dict:
        if self._sec_filings is None:
            f = self._fetch_sec_filings()
            self._sec_filings = {} if f is None else f
        return self._sec_filings

    @staticmethod
    def valid_modules():
        return quote_summary_valid_modules

    def _fetch(self, modules: list):
        if not isinstance(modules, list):
            raise YFException("Should provide a list of modules, see available modules using `valid_modules`")

        modules = ','.join([m for m in modules if m in quote_summary_valid_modules])
        if len(modules) == 0:
            raise YFException("No valid modules provided, see available modules using `valid_modules`")
        params_dict = {"modules": modules, "corsDomain": "finance.yahoo.com", "formatted": "false", "symbol": self._symbol}
        try:
            result = self._data.get_raw_json(_QUOTE_SUMMARY_URL_ + f"/{self._symbol}", params=params_dict)
        except curl_cffi.requests.exceptions.HTTPError as e:
            logger.error(str(e))
            return None
        return result

    def _fetch_additional_info(self):
        params_dict = {"symbols": self._symbol, "formatted": "false"}
        try:
            result = self._data.get_raw_json(f"{_QUERY1_URL_}/v7/finance/quote?", params=params_dict)
        except curl_cffi.requests.exceptions.HTTPError as e:
            logger.error(str(e))
            return None
        return result

    def _fetch_info(self):
        if self._already_fetched:
            return
        self._already_fetched = True
        modules = ['financialData', 'quoteType', 'defaultKeyStatistics', 'assetProfile', 'summaryDetail']
        result = self._fetch(modules=modules)
        additional_info = self._fetch_additional_info()
        if additional_info is not None and result is not None:
            result.update(additional_info)
        else:
            result = additional_info

        query1_info = {}
        for quote in ["quoteSummary", "quoteResponse"]:
            if quote in result and len(result[quote]["result"]) > 0:
                result[quote]["result"][0]["symbol"] = self._symbol
                query_info = next(
                    (info for info in result.get(quote, {}).get("result", [])
                    if info["symbol"] == self._symbol),
                    None,
                )
                if query_info:
                    query1_info.update(query_info)

        # Normalize and flatten nested dictionaries
        processed_info = {}
        for k, v in query1_info.items():
            if isinstance(v, dict):
                for k1, v1 in v.items():
                    if v1 is not None:
                        processed_info[k1] = 86400 if k1 == "maxAge" and v1 == 1 else v1
            elif v is not None:
                processed_info[k] = v

        query1_info = processed_info

        def _format(k, v):
            if isinstance(v, dict) and "raw" in v and "fmt" in v:
                v2 = v["fmt"] if k in {"regularMarketTime", "postMarketTime"} else v["raw"]
            elif isinstance(v, list):
                v2 = [_format(None, x) for x in v]
            elif isinstance(v, dict):
                v2 = {k: _format(k, x) for k, x in v.items()}
            elif isinstance(v, str):
                v2 = v.replace("\xa0", " ")
            else:
                v2 = v
            return v2

        self._info = {k: _format(k, v) for k, v in query1_info.items()}

    def _fetch_complementary(self):
        if self._already_fetched_complementary:
            return
        self._already_fetched_complementary = True

        self._fetch_info()
        if self._info is None:
            return

        # Complementary key-statistics
        keys = {"trailingPegRatio"}
        if keys:
            url = f"https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{self._symbol}?symbol={self._symbol}"
            for k in keys:
                url += "&type=" + k
            
            start = pd.Timestamp.utcnow().floor("D") - datetime.timedelta(days=365 // 2)
            start = int(start.timestamp())
            end = pd.Timestamp.utcnow().ceil("D")
            end = int(end.timestamp())
            url += f"&period1={start}&period2={end}"

            try:
                response = self._data.cache_get(url=url)
                if response:
                    json_str = response.text
                    json_data = json.loads(json_str)
                    json_result = json_data.get("timeseries") or json_data.get("finance")
                    if json_result["error"] is not None:
                        raise YFException("Failed to parse json response from Yahoo Finance: " + str(json_result["error"]))
                    for k in keys:
                        keydict = json_result["result"][0]
                        if k in keydict:
                            self._info[k] = keydict[k][-1]["reportedValue"]["raw"]
                        else:
                            self._info[k] = None
            except Exception as e:
                logger.error(f"Error fetching complementary data: {str(e)}")
                for k in keys:
                    self._info[k] = None

    def _fetch_calendar(self):
        result = self._fetch(modules=['calendarEvents'])
        if result is None:
            self._calendar = {}
            return

        try:
            self._calendar = dict()
            _events = result["quoteSummary"]["result"][0]["calendarEvents"]
            if 'dividendDate' in _events:
                self._calendar['Dividend Date'] = datetime.datetime.fromtimestamp(_events['dividendDate']).date()
            if 'exDividendDate' in _events:
                self._calendar['Ex-Dividend Date'] = datetime.datetime.fromtimestamp(_events['exDividendDate']).date()
            
            earnings = _events.get('earnings')
            if earnings is not None:
                self._calendar['Earnings Date'] = [datetime.datetime.fromtimestamp(d).date() for d in earnings.get('earningsDate', [])]
                self._calendar['Earnings High'] = earnings.get('earningsHigh', None)
                self._calendar['Earnings Low'] = earnings.get('earningsLow', None)
                self._calendar['Earnings Average'] = earnings.get('earningsAverage', None)
                self._calendar['Revenue High'] = earnings.get('revenueHigh', None)
                self._calendar['Revenue Low'] = earnings.get('revenueLow', None)
                self._calendar['Revenue Average'] = earnings.get('revenueAverage', None)
        except (KeyError, IndexError):
            raise YFDataException(f"Failed to parse json response from Yahoo Finance: {result}")

    def _fetch_sec_filings(self):
        result = self._fetch(modules=['secFilings'])
        if result is None:
            return None

        try:
            filings = result["quoteSummary"]["result"][0]["secFilings"]["filings"]

            # Improve structure
            for f in filings:
                if 'exhibits' in f:
                    f['exhibits'] = {e['type']:e['url'] for e in f['exhibits']}
                f['date'] = datetime.datetime.strptime(f['date'], '%Y-%m-%d').date()

            return filings
        except (KeyError, IndexError):
            raise YFDataException(f"Failed to parse json response from Yahoo Finance: {result}")
