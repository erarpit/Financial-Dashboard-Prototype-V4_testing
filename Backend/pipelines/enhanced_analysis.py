# pipelines/enhanced_analysis.py - Enhanced Financial Analysis Module

import curl_cffi
import pandas as pd
import warnings
from typing import Dict, Any, Optional

from yfinance import utils
# Define quote_summary_valid_modules locally since it's not available in newer yfinance versions
quote_summary_valid_modules = [
    'assetProfile', 'summaryProfile', 'financialData', 'quoteType', 'calendarEvents',
    'incomeStatementHistory', 'incomeStatementHistoryQuarterly', 'balanceSheetHistory',
    'balanceSheetHistoryQuarterly', 'cashflowStatementHistory', 'cashflowStatementHistoryQuarterly',
    'defaultKeyStatistics', 'institutionOwnership', 'fundOwnership', 'majorDirectHolders',
    'majorHoldersBreakdown', 'insiderTransactions', 'insiderHolders', 'netSharePurchaseActivity',
    'earnings', 'earningsHistory', 'earningsTrend', 'industryTrend', 'indexTrend',
    'sectorTrend', 'recommendationTrend', 'upgradeDowngradeHistory', 'esgScores',
    'price', 'summaryDetail', 'topHoldings', 'fundProfile', 'fundPerformance',
    'prePostMarketChange', 'prePostMarketPrice', 'postMarketChange', 'postMarketPrice',
    'regularMarketChange', 'regularMarketChangePercent', 'regularMarketPrice',
    'regularMarketTime', 'regularMarketDayHigh', 'regularMarketDayLow',
    'regularMarketOpen', 'regularMarketPreviousClose', 'regularMarketVolume',
    'twoHundredDayAverage', 'fiftyDayAverage', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow',
    'averageVolume', 'averageVolume10days', 'maxAge', 'fromCurrency', 'toCurrency',
    'lastMarket', 'volume24Hr', 'volumeAllCurrencies', 'circulatingSupply',
    'marketCap', 'enterpriseValue', 'impliedSharesOutstanding', 'bookValue',
    'priceToBook', 'priceToSalesTrailing12Months', 'priceToCashflow', 'priceToEarnings',
    'priceToEarningsTrailing12Months', 'priceToEarningsForward', 'pegRatio',
    'trailingPE', 'forwardPE', 'trailingAnnualDividendRate', 'trailingAnnualDividendYield',
    'dividendRate', 'dividendYield', 'exDividendDate', 'dividendDate', 'payoutRatio',
    'beta', 'trailingPegRatio', 'totalCash', 'totalCashPerShare', 'totalDebt',
    'totalRevenue', 'revenuePerShare', 'revenueGrowth', 'grossMargins', 'operatingMargins',
    'profitMargins', 'returnOnAssets', 'returnOnEquity', 'returnOnInvestment',
    'debtToEquity', 'currentRatio', 'quickRatio', 'cashRatio', 'grossProfit',
    'freeCashflow', 'operatingCashflow', 'earningsGrowth', 'revenueGrowth',
    'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice',
    'recommendationMean', 'recommendationKey', 'numberOfAnalystOpinions',
    'totalCash', 'totalCashPerShare', 'totalDebt', 'totalRevenue', 'revenuePerShare',
    'revenueGrowth', 'grossMargins', 'operatingMargins', 'profitMargins',
    'returnOnAssets', 'returnOnEquity', 'returnOnInvestment', 'debtToEquity',
    'currentRatio', 'quickRatio', 'cashRatio', 'grossProfit', 'freeCashflow',
    'operatingCashflow', 'earningsGrowth', 'revenueGrowth', 'targetHighPrice',
    'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice', 'recommendationMean',
    'recommendationKey', 'numberOfAnalystOpinions', 'maxAge', 'fromCurrency',
    'toCurrency', 'lastMarket', 'volume24Hr', 'volumeAllCurrencies', 'circulatingSupply'
]

_SENTINEL_ = object()
from yfinance.data import YfData
from yfinance.exceptions import YFException
from yfinance.scrapers.quote import _QUOTE_SUMMARY_URL_

class EnhancedAnalysis:
    """
    Enhanced financial analysis class that extends yfinance capabilities.
    Provides detailed earnings estimates, analyst targets, and growth projections.
    """

    def __init__(self, data: YfData, symbol: str, proxy=_SENTINEL_):
        """
        Initialize the enhanced analysis module.
        
        Args:
            data: YfData object from yfinance
            symbol: Stock symbol (e.g., 'AAPL', 'RELIANCE.NS')
            proxy: Optional proxy configuration (deprecated)
        """
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            data._set_proxy(proxy)

        self._data = data
        self._symbol = symbol

        # In quoteSummary the 'earningsTrend' module contains most of the data below.
        # The format of data is not optimal so each function will process it's part of the data.
        # This variable works as a cache.
        self._earnings_trend = None

        # Cache for various analysis components
        self._analyst_price_targets = None
        self._earnings_estimate = None
        self._revenue_estimate = None
        self._earnings_history = None
        self._eps_trend = None
        self._eps_revisions = None
        self._growth_estimates = None

    def _get_periodic_df(self, key: str) -> pd.DataFrame:
        """
        Helper method to extract periodic data from earnings trend.
        
        Args:
            key: The key to extract from earnings trend data
            
        Returns:
            DataFrame with periodic data
        """
        if self._earnings_trend is None:
            self._fetch_earnings_trend()

        data = []
        for item in self._earnings_trend[:4]:  # Get last 4 periods
            row = {'period': item['period']}
            for k, v in item[key].items():
                if not isinstance(v, dict) or len(v) == 0:
                    continue
                row[k] = v['raw']
            data.append(row)
        
        if len(data) == 0:
            return pd.DataFrame()
        return pd.DataFrame(data).set_index('period')

    @property
    def earnings_estimate(self) -> pd.DataFrame:
        """
        Get earnings estimates for different periods.
        
        Returns:
            DataFrame with earnings estimates by period
        """
        if self._earnings_estimate is not None:
            return self._earnings_estimate
        self._earnings_estimate = self._get_periodic_df('earningsEstimate')
        return self._earnings_estimate

    @property
    def revenue_estimate(self) -> pd.DataFrame:
        """
        Get revenue estimates for different periods.
        
        Returns:
            DataFrame with revenue estimates by period
        """
        if self._revenue_estimate is not None:
            return self._revenue_estimate
        self._revenue_estimate = self._get_periodic_df('revenueEstimate')
        return self._revenue_estimate

    @property
    def eps_trend(self) -> pd.DataFrame:
        """
        Get EPS trend data for different periods.
        
        Returns:
            DataFrame with EPS trend by period
        """
        if self._eps_trend is not None:
            return self._eps_trend
        self._eps_trend = self._get_periodic_df('epsTrend')
        return self._eps_trend

    @property
    def eps_revisions(self) -> pd.DataFrame:
        """
        Get EPS revisions data for different periods.
        
        Returns:
            DataFrame with EPS revisions by period
        """
        if self._eps_revisions is not None:
            return self._eps_revisions
        self._eps_revisions = self._get_periodic_df('epsRevisions')
        return self._eps_revisions

    @property
    def analyst_price_targets(self) -> Dict[str, Any]:
        """
        Get analyst price targets and current price.
        
        Returns:
            Dictionary with price targets and current price
        """
        if self._analyst_price_targets is not None:
            return self._analyst_price_targets

        try:
            data = self._fetch(['financialData'])
            data = data['quoteSummary']['result'][0]['financialData']
        except (TypeError, KeyError):
            self._analyst_price_targets = {}
            return self._analyst_price_targets

        result = {}
        for key, value in data.items():
            if key.startswith('target'):
                new_key = key.replace('target', '').lower().replace('price', '').strip()
                result[new_key] = value
            elif key == 'currentPrice':
                result['current'] = value

        self._analyst_price_targets = result
        return self._analyst_price_targets

    @property
    def earnings_history(self) -> pd.DataFrame:
        """
        Get historical earnings data.
        
        Returns:
            DataFrame with historical earnings by quarter
        """
        if self._earnings_history is not None:
            return self._earnings_history

        try:
            data = self._fetch(['earningsHistory'])
            data = data['quoteSummary']['result'][0]['earningsHistory']['history']
        except (TypeError, KeyError):
            self._earnings_history = pd.DataFrame()
            return self._earnings_history

        rows = []
        for item in data:
            row = {'quarter': item.get('quarter', {}).get('fmt', None)}
            for k, v in item.items():
                if k == 'quarter':
                    continue
                if not isinstance(v, dict) or len(v) == 0:
                    continue
                row[k] = v.get('raw', None)
            rows.append(row)
        
        if len(data) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        if 'quarter' in df.columns:
            df['quarter'] = pd.to_datetime(df['quarter'], format='%Y-%m-%d')
            df.set_index('quarter', inplace=True)

        self._earnings_history = df
        return self._earnings_history

    @property
    def growth_estimates(self) -> pd.DataFrame:
        """
        Get growth estimates comparing stock vs industry/sector/index.
        
        Returns:
            DataFrame with growth estimates by period
        """
        if self._growth_estimates is not None:
            return self._growth_estimates

        if self._earnings_trend is None:
            self._fetch_earnings_trend()

        try:
            trends = self._fetch(['industryTrend', 'sectorTrend', 'indexTrend'])
            trends = trends['quoteSummary']['result'][0]
        except (TypeError, KeyError):
            self._growth_estimates = pd.DataFrame()
            return self._growth_estimates

        data = []
        for item in self._earnings_trend:
            period = item['period']
            row = {'period': period, 'stockTrend': item.get('growth', {}).get('raw', None)}
            data.append(row)

        for trend_name, trend_info in trends.items():
            if trend_info.get('estimates'):
                for estimate in trend_info['estimates']:
                    period = estimate['period']
                    existing_row = next((row for row in data if row['period'] == period), None)
                    if existing_row:
                        existing_row[trend_name] = estimate.get('growth')
                    else:
                        row = {'period': period, trend_name: estimate.get('growth')}
                        data.append(row)
        
        if len(data) == 0:
            return pd.DataFrame()

        self._growth_estimates = pd.DataFrame(data).set_index('period').dropna(how='all')
        return self._growth_estimates

    def _fetch(self, modules: list) -> Optional[Dict]:
        """
        Fetch data from Yahoo Finance API.
        
        Args:
            modules: List of modules to fetch
            
        Returns:
            JSON data from Yahoo Finance or None if error
        """
        if not isinstance(modules, list):
            raise YFException("Should provide a list of modules, see available modules using `valid_modules`")

        modules = ','.join([m for m in modules if m in quote_summary_valid_modules])
        if len(modules) == 0:
            raise YFException("No valid modules provided, see available modules using `valid_modules`")
        
        params_dict = {
            "modules": modules, 
            "corsDomain": "finance.yahoo.com", 
            "formatted": "false", 
            "symbol": self._symbol
        }
        
        try:
            result = self._data.get_raw_json(_QUOTE_SUMMARY_URL_ + f"/{self._symbol}", params=params_dict)
        except curl_cffi.requests.exceptions.HTTPError as e:
            utils.get_yf_logger().error(str(e))
            return None
        return result

    def _fetch_earnings_trend(self) -> None:
        """
        Fetch earnings trend data and cache it.
        """
        try:
            data = self._fetch(['earningsTrend'])
            self._earnings_trend = data['quoteSummary']['result'][0]['earningsTrend']['trend']
        except (TypeError, KeyError):
            self._earnings_trend = []

    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive financial analysis combining all available data.
        
        Returns:
            Dictionary with comprehensive analysis results
        """
        analysis = {
            'symbol': self._symbol,
            'timestamp': pd.Timestamp.now().isoformat(),
            'analyst_targets': self.analyst_price_targets,
            'earnings_estimates': self.earnings_estimate.to_dict() if not self.earnings_estimate.empty else {},
            'revenue_estimates': self.revenue_estimate.to_dict() if not self.revenue_estimate.empty else {},
            'eps_trend': self.eps_trend.to_dict() if not self.eps_trend.empty else {},
            'eps_revisions': self.eps_revisions.to_dict() if not self.eps_revisions.empty else {},
            'growth_estimates': self.growth_estimates.to_dict() if not self.growth_estimates.empty else {},
            'earnings_history': self.earnings_history.to_dict() if not self.earnings_history.empty else {}
        }
        
        return analysis

    def get_analyst_summary(self) -> Dict[str, Any]:
        """
        Get a summary of analyst recommendations and targets.
        
        Returns:
            Dictionary with analyst summary
        """
        targets = self.analyst_price_targets
        
        if not targets:
            return {'error': 'No analyst data available'}
        
        summary = {
            'current_price': targets.get('current', {}).get('raw', 0),
            'target_high': targets.get('high', {}).get('raw', 0),
            'target_low': targets.get('low', {}).get('raw', 0),
            'target_mean': targets.get('mean', {}).get('raw', 0),
            'target_median': targets.get('median', {}).get('raw', 0)
        }
        
        # Calculate potential upside/downside
        current = summary['current_price']
        if current > 0:
            if summary['target_high'] > 0:
                summary['upside_potential'] = ((summary['target_high'] - current) / current) * 100
            if summary['target_low'] > 0:
                summary['downside_risk'] = ((current - summary['target_low']) / current) * 100
            if summary['target_mean'] > 0:
                summary['mean_upside'] = ((summary['target_mean'] - current) / current) * 100
        
        return summary

# Convenience functions for easy integration
def get_enhanced_analysis(symbol: str) -> Optional[EnhancedAnalysis]:
    """
    Create an enhanced analysis instance for a given symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        EnhancedAnalysis instance or None if error
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        return EnhancedAnalysis(ticker._data, symbol)
    except Exception as e:
        print(f"Error creating enhanced analysis for {symbol}: {e}")
        return None

def get_analyst_summary(symbol: str) -> Dict[str, Any]:
    """
    Get analyst summary for a symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Dictionary with analyst summary
    """
    analysis = get_enhanced_analysis(symbol)
    if analysis:
        return analysis.get_analyst_summary()
    return {'error': f'Could not get analysis for {symbol}'}

def get_earnings_estimates(symbol: str) -> Dict[str, Any]:
    """
    Get earnings estimates for a symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Dictionary with earnings estimates
    """
    analysis = get_enhanced_analysis(symbol)
    if analysis:
        return analysis.earnings_estimate.to_dict() if not analysis.earnings_estimate.empty else {}
    return {'error': f'Could not get earnings estimates for {symbol}'}
