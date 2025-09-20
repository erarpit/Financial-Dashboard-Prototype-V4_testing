from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Optional
import warnings
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Constants for Yahoo Finance API
_QUERY1_URL_ = "https://query1.finance.yahoo.com"
_SENTINEL_ = object()

class YfData:
    """Yahoo Finance data fetcher with session management"""
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
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
            logger.error(f"Error fetching data from {url}: {str(e)}")
            return {}

class Ticker:
    """Simple ticker wrapper for domain entities"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol

class Domain(ABC):
    """
    Abstract base class representing a domain entity in financial data, with key attributes 
    and methods for fetching and parsing data. Derived classes must implement the `_fetch_and_parse()` method.
    """

    def __init__(self, key: str, session=None, proxy=_SENTINEL_):
        """
        Initializes the Domain object with a key, session, and proxy.

        Args:
            key (str): Unique key identifying the domain entity.
            session (Optional[requests.Session]): Session object for HTTP requests. Defaults to None.
        """
        self._key: str = key
        self.session = session
        self._data: YfData = YfData(session=session)
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._data._set_proxy(proxy)

        self._name: Optional[str] = None
        self._symbol: Optional[str] = None
        self._overview: Optional[Dict] = None
        self._top_companies: Optional[pd.DataFrame] = None
        self._research_reports: Optional[List[Dict[str, str]]] = None

    @property
    def key(self) -> str:
        """
        Retrieves the key of the domain entity.

        Returns:
            str: The unique key of the domain entity.
        """
        return self._key

    @property
    def name(self) -> str:
        """
        Retrieves the name of the domain entity.

        Returns:
            str: The name of the domain entity.
        """
        self._ensure_fetched(self._name)
        return self._name

    @property
    def symbol(self) -> str:
        """
        Retrieves the symbol of the domain entity.

        Returns:
            str: The symbol representing the domain entity.
        """
        self._ensure_fetched(self._symbol)
        return self._symbol

    @property
    def ticker(self) -> Ticker:
        """
        Retrieves a Ticker object based on the domain entity's symbol.

        Returns:
            Ticker: A Ticker object associated with the domain entity.
        """
        self._ensure_fetched(self._symbol)
        return Ticker(self._symbol)

    @property
    def overview(self) -> Dict:
        """
        Retrieves the overview information of the domain entity.

        Returns:
            Dict: A dictionary containing an overview of the domain entity.
        """
        self._ensure_fetched(self._overview)
        return self._overview

    @property
    def top_companies(self) -> Optional[pd.DataFrame]:
        """
        Retrieves the top companies within the domain entity.

        Returns:
            pandas.DataFrame: A DataFrame containing the top companies in the domain.
        """
        self._ensure_fetched(self._top_companies)
        return self._top_companies 

    @property
    def research_reports(self) -> List[Dict[str, str]]:
        """
        Retrieves research reports related to the domain entity.

        Returns:
            List[Dict[str, str]]: A list of research reports, where each report is a dictionary with metadata.
        """
        self._ensure_fetched(self._research_reports)
        return self._research_reports

    def _fetch(self, query_url) -> Dict:
        """
        Fetches data from the given query URL.

        Args:
            query_url (str): The URL used for the data query.

        Returns:
            Dict: The JSON response data from the request.
        """
        params_dict = {"formatted": "true", "withReturns": "true", "lang": "en-US", "region": "US"}
        result = self._data.get_raw_json(query_url, params=params_dict)
        return result

    def _parse_and_assign_common(self, data) -> None:
        """
        Parses and assigns common data fields such as name, symbol, overview, and top companies.

        Args:
            data (Dict): The raw data received from the API.
        """
        self._name = data.get('name')
        self._symbol = data.get('symbol')
        self._overview = self._parse_overview(data.get('overview', {}))
        self._top_companies = self._parse_top_companies(data.get('topCompanies', {}))
        self._research_reports = data.get('researchReports')

    def _parse_overview(self, overview) -> Dict:
        """
        Parses the overview data for the domain entity.

        Args:
            overview (Dict): The raw overview data.

        Returns:
            Dict: A dictionary containing parsed overview information.
        """
        return {
            "companies_count": overview.get('companiesCount', None),
            "market_cap": overview.get('marketCap', {}).get('raw', None),
            "message_board_id": overview.get('messageBoardId', None),
            "description": overview.get('description', None),
            "industries_count": overview.get('industriesCount', None),
            "market_weight": overview.get('marketWeight', {}).get('raw', None),
            "employee_count": overview.get('employeeCount', {}).get('raw', None)
        }

    def _parse_top_companies(self, top_companies) -> Optional[pd.DataFrame]:
        """
        Parses the top companies data and converts it into a pandas DataFrame.

        Args:
            top_companies (Dict): The raw top companies data.

        Returns:
            Optional[pandas.DataFrame]: A DataFrame containing top company data, or None if no data is available.
        """
        top_companies_column = ['symbol', 'name', 'rating', 'market weight']
        top_companies_values = [(c.get('symbol'), 
                                c.get('name'), 
                                c.get('rating'), 
                                c.get('marketWeight',{}).get('raw',None)) for c in top_companies]

        if not top_companies_values: 
            return None
        
        return pd.DataFrame(top_companies_values, columns=top_companies_column).set_index('symbol')

    @abstractmethod
    def _fetch_and_parse(self) -> None:
        """
        Abstract method for fetching and parsing domain-specific data. 
        Must be implemented by derived classes.
        """
        raise NotImplementedError("_fetch_and_parse() needs to be implemented by children classes")

    def _ensure_fetched(self, attribute) -> None:
        """
        Ensures that the given attribute is fetched by calling `_fetch_and_parse()` if the attribute is None.

        Args:
            attribute: The attribute to check and potentially fetch.
        """
        if attribute is None:
            self._fetch_and_parse()


class Sector(Domain):
    """Represents a financial sector domain"""
    
    def __init__(self, sector_key: str, session=None):
        super().__init__(sector_key, session)
        self._query_url = f"{_QUERY1_URL_}/v1/finance/screener"
    
    def _fetch_and_parse(self) -> None:
        """Fetch and parse sector-specific data"""
        try:
            # For now, we'll create mock data since Yahoo Finance sector API is complex
            # In a real implementation, you'd fetch from the actual API
            self._name = f"Sector {self._key.title()}"
            self._symbol = f"{self._key.upper()}_SECTOR"
            self._overview = {
                "companies_count": 50,
                "market_cap": 1000000000000,  # 1T
                "description": f"Financial sector: {self._key}",
                "industries_count": 10,
                "market_weight": 15.5,
                "employee_count": 500000
            }
            self._top_companies = self._create_mock_companies()
            self._research_reports = [
                {"title": f"{self._key.title()} Sector Analysis", "url": "#", "date": datetime.now().isoformat()},
                {"title": f"{self._key.title()} Market Outlook", "url": "#", "date": datetime.now().isoformat()}
            ]
        except Exception as e:
            logger.error(f"Error fetching sector data for {self._key}: {str(e)}")
            self._name = f"Sector {self._key}"
            self._symbol = f"{self._key.upper()}_SECTOR"
            self._overview = {}
            self._top_companies = None
            self._research_reports = []
    
    def _create_mock_companies(self) -> pd.DataFrame:
        """Create mock top companies data"""
        companies_data = [
            ("AAPL", "Apple Inc.", "BUY", 25.5),
            ("MSFT", "Microsoft Corp.", "BUY", 20.3),
            ("GOOGL", "Alphabet Inc.", "HOLD", 15.8),
            ("AMZN", "Amazon.com Inc.", "BUY", 12.2),
            ("TSLA", "Tesla Inc.", "HOLD", 8.7)
        ]
        return pd.DataFrame(companies_data, columns=['symbol', 'name', 'rating', 'market weight']).set_index('symbol')


class Industry(Domain):
    """Represents a financial industry domain"""
    
    def __init__(self, industry_key: str, session=None):
        super().__init__(industry_key, session)
        self._query_url = f"{_QUERY1_URL_}/v1/finance/screener"
    
    def _fetch_and_parse(self) -> None:
        """Fetch and parse industry-specific data"""
        try:
            self._name = f"Industry {self._key.title()}"
            self._symbol = f"{self._key.upper()}_INDUSTRY"
            self._overview = {
                "companies_count": 25,
                "market_cap": 500000000000,  # 500B
                "description": f"Industry: {self._key}",
                "industries_count": 1,
                "market_weight": 8.2,
                "employee_count": 250000
            }
            self._top_companies = self._create_mock_companies()
            self._research_reports = [
                {"title": f"{self._key.title()} Industry Report", "url": "#", "date": datetime.now().isoformat()}
            ]
        except Exception as e:
            logger.error(f"Error fetching industry data for {self._key}: {str(e)}")
            self._name = f"Industry {self._key}"
            self._symbol = f"{self._key.upper()}_INDUSTRY"
            self._overview = {}
            self._top_companies = None
            self._research_reports = []
    
    def _create_mock_companies(self) -> pd.DataFrame:
        """Create mock top companies data for industry"""
        companies_data = [
            ("RELIANCE.NS", "Reliance Industries", "BUY", 18.5),
            ("TCS.NS", "Tata Consultancy Services", "BUY", 15.2),
            ("HDFCBANK.NS", "HDFC Bank", "HOLD", 12.8),
            ("INFY.NS", "Infosys Ltd", "BUY", 10.3),
            ("ICICIBANK.NS", "ICICI Bank", "HOLD", 8.7)
        ]
        return pd.DataFrame(companies_data, columns=['symbol', 'name', 'rating', 'market weight']).set_index('symbol')
