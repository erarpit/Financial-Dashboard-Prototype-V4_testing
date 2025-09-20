from typing import Dict, List, Any, Optional
import logging
import yfinance as yf
import pandas as pd
from models.query_builder import EquityQuery, FundQuery

logger = logging.getLogger(__name__)

class QueryBuilderService:
    """Service for building and executing financial data queries"""
    
    def __init__(self):
        self.supported_tickers = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
            'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS', 'SUNPHARMA.NS', 'DRREDDY.NS',
            'CIPLA.NS', 'ITC.NS', 'HINDUNILVR.NS', 'MARUTI.NS', 'TITAN.NS',
            'BAJAJ-AUTO.NS', 'TATAMOTORS.NS', 'M&M.NS', 'HEROMOTOCO.NS',
            'EICHERMOT.NS', 'ONGC.NS', 'COALINDIA.NS', 'IOC.NS', 'BPCL.NS',
            'POWERGRID.NS', 'NTPC.NS', 'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
            'INDUSINDBK.NS', 'BAJFINANCE.NS', 'BHARTIARTL.NS', 'JSWSTEEL.NS',
            'TATASTEEL.NS', 'HINDALCO.NS', 'ULTRACEMCO.NS', 'SHREECEM.NS',
            'GRASIM.NS', 'ADANIPORTS.NS', 'LT.NS', 'ASIANPAINT.NS', 'NESTLEIND.NS',
            'BRITANNIA.NS', 'DIVISLAB.NS', 'UPL.NS', 'DLF.NS'
        ]
    
    def get_available_fields(self, query_type: str = 'equity') -> Dict[str, List[str]]:
        """Get available fields for query building"""
        if query_type == 'equity':
            return EquityQuery('EQ', ['symbol', 'NSE']).valid_fields
        elif query_type == 'fund':
            return FundQuery('EQ', ['symbol', 'NSE']).valid_fields
        else:
            raise ValueError(f"Invalid query type: {query_type}")
    
    def get_available_values(self, query_type: str = 'equity') -> Dict[str, List[str]]:
        """Get available values for query building"""
        if query_type == 'equity':
            return EquityQuery('EQ', ['symbol', 'NSE']).valid_values
        elif query_type == 'fund':
            return FundQuery('EQ', ['symbol', 'NSE']).valid_values
        else:
            raise ValueError(f"Invalid query type: {query_type}")
    
    def validate_query(self, query_dict: Dict[str, Any], query_type: str = 'equity') -> bool:
        """Validate a query dictionary"""
        try:
            if query_type == 'equity':
                query = self._dict_to_equity_query(query_dict)
            elif query_type == 'fund':
                query = self._dict_to_fund_query(query_dict)
            else:
                raise ValueError(f"Invalid query type: {query_type}")
            
            # Test if query can be converted to dict (validates structure)
            query.to_dict()
            return True
        except Exception as e:
            logger.error(f"Query validation failed: {str(e)}")
            return False
    
    def execute_equity_query(self, query_dict: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """Execute an equity query and return matching stocks"""
        try:
            # For now, we'll simulate query execution with our supported tickers
            # In a real implementation, this would connect to a financial data provider
            results = []
            
            for ticker in self.supported_tickers[:limit]:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Apply basic filtering based on query
                    if self._matches_equity_query(info, query_dict):
                        results.append({
                            'symbol': ticker,
                            'name': info.get('longName', ticker),
                            'sector': info.get('sector', 'N/A'),
                            'industry': info.get('industry', 'N/A'),
                            'marketCap': info.get('marketCap', 0),
                            'trailingPE': info.get('trailingPE', 0),
                            'regularMarketPrice': info.get('regularMarketPrice', 0),
                            'regularMarketChange': info.get('regularMarketChange', 0),
                            'regularMarketChangePercent': info.get('regularMarketChangePercent', 0),
                            'regularMarketVolume': info.get('regularMarketVolume', 0),
                            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 0),
                            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 0)
                        })
                except Exception as e:
                    logger.warning(f"Error fetching data for {ticker}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing equity query: {str(e)}")
            return []
    
    def execute_fund_query(self, query_dict: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """Execute a fund query and return matching funds"""
        try:
            # For now, return empty results as we don't have fund data
            # In a real implementation, this would connect to a fund data provider
            return []
            
        except Exception as e:
            logger.error(f"Error executing fund query: {str(e)}")
            return []
    
    def _dict_to_equity_query(self, query_dict: Dict[str, Any]) -> EquityQuery:
        """Convert dictionary to EquityQuery object"""
        operator = query_dict.get('operator', 'EQ')
        operands = query_dict.get('operands', [])
        
        # Handle nested queries
        processed_operands = []
        for operand in operands:
            if isinstance(operand, dict) and 'operator' in operand:
                processed_operands.append(self._dict_to_equity_query(operand))
            else:
                processed_operands.append(operand)
        
        return EquityQuery(operator, processed_operands)
    
    def _dict_to_fund_query(self, query_dict: Dict[str, Any]) -> FundQuery:
        """Convert dictionary to FundQuery object"""
        operator = query_dict.get('operator', 'EQ')
        operands = query_dict.get('operands', [])
        
        # Handle nested queries
        processed_operands = []
        for operand in operands:
            if isinstance(operand, dict) and 'operator' in operand:
                processed_operands.append(self._dict_to_fund_query(operand))
            else:
                processed_operands.append(operand)
        
        return FundQuery(operator, processed_operands)
    
    def _matches_equity_query(self, stock_info: Dict[str, Any], query_dict: Dict[str, Any]) -> bool:
        """Check if stock info matches the query criteria"""
        try:
            operator = query_dict.get('operator', 'EQ')
            operands = query_dict.get('operands', [])
            
            if operator == 'EQ':
                if len(operands) != 2:
                    return False
                field, value = operands
                return stock_info.get(field) == value
            
            elif operator == 'GT':
                if len(operands) != 2:
                    return False
                field, value = operands
                stock_value = stock_info.get(field, 0)
                return isinstance(stock_value, (int, float)) and stock_value > value
            
            elif operator == 'LT':
                if len(operands) != 2:
                    return False
                field, value = operands
                stock_value = stock_info.get(field, 0)
                return isinstance(stock_value, (int, float)) and stock_value < value
            
            elif operator == 'GTE':
                if len(operands) != 2:
                    return False
                field, value = operands
                stock_value = stock_info.get(field, 0)
                return isinstance(stock_value, (int, float)) and stock_value >= value
            
            elif operator == 'LTE':
                if len(operands) != 2:
                    return False
                field, value = operands
                stock_value = stock_info.get(field, 0)
                return isinstance(stock_value, (int, float)) and stock_value <= value
            
            elif operator == 'BTWN':
                if len(operands) != 3:
                    return False
                field, min_val, max_val = operands
                stock_value = stock_info.get(field, 0)
                return isinstance(stock_value, (int, float)) and min_val <= stock_value <= max_val
            
            elif operator == 'IS-IN':
                if len(operands) < 2:
                    return False
                field = operands[0]
                values = operands[1:]
                stock_value = stock_info.get(field)
                return stock_value in values
            
            elif operator == 'AND':
                return all(self._matches_equity_query(stock_info, op) for op in operands if isinstance(op, dict))
            
            elif operator == 'OR':
                return any(self._matches_equity_query(stock_info, op) for op in operands if isinstance(op, dict))
            
            return False
            
        except Exception as e:
            logger.error(f"Error matching query: {str(e)}")
            return False
    
    def get_predefined_queries(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined query templates"""
        return {
            "large_cap_growth": {
                "name": "Large Cap Growth Stocks",
                "description": "Large cap stocks with growth characteristics",
                "query": {
                    "operator": "AND",
                    "operands": [
                        {"operator": "GT", "operands": ["marketCap", 10000000000]},
                        {"operator": "LT", "operands": ["trailingPE", 25]},
                        {"operator": "IS-IN", "operands": ["sector", "Technology", "Healthcare"]}
                    ]
                }
            },
            "value_stocks": {
                "name": "Value Stocks",
                "description": "Stocks with low P/E ratios and high dividends",
                "query": {
                    "operator": "AND",
                    "operands": [
                        {"operator": "LT", "operands": ["trailingPE", 15]},
                        {"operator": "GT", "operands": ["trailingPE", 5]},
                        {"operator": "GT", "operands": ["marketCap", 1000000000]}
                    ]
                }
            },
            "high_volume": {
                "name": "High Volume Stocks",
                "description": "Stocks with high trading volume",
                "query": {
                    "operator": "GT",
                    "operands": ["regularMarketVolume", 1000000]
                }
            },
            "tech_sector": {
                "name": "Technology Sector",
                "description": "All technology sector stocks",
                "query": {
                    "operator": "EQ",
                    "operands": ["sector", "Technology"]
                }
            }
        }

# Global instance
query_builder_service = QueryBuilderService()
