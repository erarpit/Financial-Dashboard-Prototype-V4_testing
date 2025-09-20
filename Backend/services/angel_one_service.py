import os
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AngelOneService:
    """Service for Angel One API integration for NSE and BSE markets"""
    
    def __init__(self):
        self.api_key = os.getenv('ANGEL_ONE_API_KEY')
        self.client_id = os.getenv('ANGEL_ONE_CLIENT_ID')
        self.password = os.getenv('ANGEL_ONE_PASSWORD')
        self.pin = os.getenv('ANGEL_ONE_PIN')
        
        self.enabled = bool(self.api_key and self.client_id and self.password and self.pin)
        
        if not self.enabled:
            logger.warning("Angel One API credentials not found. Set ANGEL_ONE_API_KEY, ANGEL_ONE_CLIENT_ID, ANGEL_ONE_PASSWORD, ANGEL_ONE_PIN environment variables.")
            return
        
        # API endpoints
        self.base_url = "https://apiconnect.angelbroking.com"
        self.login_url = f"{self.base_url}/rest/auth/angelbroking/user/v1/loginByPassword"
        self.quote_url = f"{self.base_url}/rest/secure/angelbroking/market/v1/quote"
        self.historical_url = f"{self.base_url}/rest/secure/angelbroking/historical/v1/getCandleData"
        self.market_status_url = f"{self.base_url}/rest/secure/angelbroking/market/v1/marketStatus"
        
        # Session management
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': '192.168.1.1',
            'X-ClientPublicIP': '192.168.1.1',
            'X-MACAddress': '00:00:00:00:00:00',
            'X-PrivateKey': self.api_key
        })
        
        # Authentication token
        self.auth_token = None
        self.token_expiry = None
        
        logger.info("Angel One service initialized successfully")
    
    def _authenticate(self) -> bool:
        """Authenticate with Angel One API"""
        try:
            if self.auth_token and self.token_expiry and datetime.now() < self.token_expiry:
                return True
            
            login_data = {
                "clientcode": self.client_id,
                "password": self.password,
                "totp": self.pin
            }
            
            response = self.session.post(self.login_url, json=login_data)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') and data.get('data'):
                self.auth_token = data['data']['jwtToken']
                self.session.headers['Authorization'] = f'Bearer {self.auth_token}'
                
                # Set token expiry (typically 24 hours)
                self.token_expiry = datetime.now() + timedelta(hours=23)
                
                logger.info("Successfully authenticated with Angel One API")
                return True
            else:
                logger.error(f"Authentication failed: {data.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _convert_symbol_to_angel_one(self, symbol: str) -> str:
        """Convert NSE/BSE symbol to Angel One format"""
        try:
            # Remove .NS or .BSE suffix
            clean_symbol = symbol.replace('.NS', '').replace('.BSE', '')
            
            # Map common Indian stocks to Angel One format
            symbol_mapping = {
                'RELIANCE': 'RELIANCE',
                'TCS': 'TCS',
                'HDFCBANK': 'HDFCBANK',
                'INFY': 'INFY',
                'HINDUNILVR': 'HINDUNILVR',
                'ITC': 'ITC',
                'SBIN': 'SBIN',
                'BHARTIARTL': 'BHARTIARTL',
                'KOTAKBANK': 'KOTAKBANK',
                'LT': 'LT'
            }
            
            return symbol_mapping.get(clean_symbol, clean_symbol)
        except Exception as e:
            logger.error(f"Error converting symbol {symbol}: {str(e)}")
            return symbol
    
    def get_market_status(self) -> Optional[Dict[str, Any]]:
        """Get market status for NSE and BSE"""
        try:
            if not self._authenticate():
                return None
            
            response = self.session.get(self.market_status_url)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') and data.get('data'):
                market_data = data['data']
                
                return {
                    'nse': {
                        'is_open': market_data.get('nse', {}).get('marketOpen', False),
                        'last_updated': datetime.now().isoformat(),
                        'exchange': 'NSE'
                    },
                    'bse': {
                        'is_open': market_data.get('bse', {}).get('marketOpen', False),
                        'last_updated': datetime.now().isoformat(),
                        'exchange': 'BSE'
                    },
                    'last_updated': datetime.now().isoformat()
                }
            else:
                logger.error(f"Market status API error: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting market status: {str(e)}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote"""
        try:
            if not self._authenticate():
                return None
            
            angel_symbol = self._convert_symbol_to_angel_one(symbol)
            
            quote_data = {
                "mode": "FULL",
                "exchangeTokens": {
                    "NSE": [angel_symbol] if symbol.endswith('.NS') else [],
                    "BSE": [angel_symbol] if symbol.endswith('.BSE') else []
                }
            }
            
            response = self.session.post(self.quote_url, json=quote_data)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') and data.get('data'):
                quote_info = data['data']
                
                # Extract quote data
                if 'fetched' in quote_info and quote_info['fetched']:
                    quote = quote_info['fetched'][0]
                    
                    return {
                        'symbol': symbol,
                        'price': float(quote.get('ltp', 0)),
                        'open': float(quote.get('open', 0)),
                        'high': float(quote.get('high', 0)),
                        'low': float(quote.get('low', 0)),
                        'close': float(quote.get('close', 0)),
                        'volume': int(quote.get('volume', 0)),
                        'change': float(quote.get('netPrice', 0)),
                        'change_percent': float(quote.get('netPrice', 0)) / float(quote.get('close', 1)) * 100 if quote.get('close') else 0,
                        'market_cap': float(quote.get('marketCap', 0)),
                        'currency': 'INR',
                        'exchange': 'NSE' if symbol.endswith('.NS') else 'BSE',
                        'last_updated': datetime.now().isoformat(),
                        'source': 'Angel One'
                    }
                else:
                    logger.warning(f"No quote data found for {symbol}")
                    return None
            else:
                logger.error(f"Quote API error: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol: str, interval: str = "1d", period: str = "1mo") -> Optional[List[Dict[str, Any]]]:
        """Get historical data for a symbol"""
        try:
            if not self._authenticate():
                return None
            
            angel_symbol = self._convert_symbol_to_angel_one(symbol)
            exchange = "NSE" if symbol.endswith('.NS') else "BSE"
            
            # Convert period to days
            period_days = {
                "1d": 1,
                "1w": 7,
                "1mo": 30,
                "3mo": 90,
                "6mo": 180,
                "1y": 365
            }.get(period, 30)
            
            # Convert interval to Angel One format
            interval_mapping = {
                "1m": "ONE_MINUTE",
                "5m": "FIVE_MINUTE",
                "15m": "FIFTEEN_MINUTE",
                "1h": "ONE_HOUR",
                "1d": "ONE_DAY"
            }
            angel_interval = interval_mapping.get(interval, "ONE_DAY")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            historical_data = {
                "mode": "FULL",
                "exchangeTokens": {
                    exchange: [angel_symbol]
                },
                "fromDate": start_date.strftime("%d-%m-%Y"),
                "toDate": end_date.strftime("%d-%m-%Y"),
                "resolution": angel_interval
            }
            
            response = self.session.post(self.historical_url, json=historical_data)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') and data.get('data'):
                historical_info = data['data']
                
                if 'fetched' in historical_info and historical_info['fetched']:
                    candles = historical_info['fetched'][0].get('data', [])
                    
                    formatted_data = []
                    for candle in candles:
                        formatted_data.append({
                            'date': candle[0],  # Timestamp
                            'open': float(candle[1]),
                            'high': float(candle[2]),
                            'low': float(candle[3]),
                            'close': float(candle[4]),
                            'volume': int(candle[5])
                        })
                    
                    return formatted_data
                else:
                    logger.warning(f"No historical data found for {symbol}")
                    return None
            else:
                logger.error(f"Historical data API error: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return None
    
    def get_indices_data(self) -> Optional[Dict[str, Any]]:
        """Get major indices data (Nifty 50, Sensex, etc.)"""
        try:
            if not self._authenticate():
                return None
            
            # Major indices symbols
            indices_data = {
                "mode": "FULL",
                "exchangeTokens": {
                    "NSE": ["NIFTY 50", "NIFTY BANK", "NIFTY IT"],
                    "BSE": ["SENSEX"]
                }
            }
            
            response = self.session.post(self.quote_url, json=indices_data)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') and data.get('data'):
                quote_info = data['data']
                
                indices = {}
                if 'fetched' in quote_info and quote_info['fetched']:
                    for index in quote_info['fetched']:
                        index_name = index.get('symbol', '')
                        indices[index_name] = {
                            'price': float(index.get('ltp', 0)),
                            'change': float(index.get('netPrice', 0)),
                            'change_percent': float(index.get('netPrice', 0)) / float(index.get('close', 1)) * 100 if index.get('close') else 0,
                            'last_updated': datetime.now().isoformat()
                        }
                
                return {
                    'indices': indices,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'Angel One'
                }
            else:
                logger.error(f"Indices API error: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting indices data: {str(e)}")
            return None

# Global instance
angel_one_service = AngelOneService()
