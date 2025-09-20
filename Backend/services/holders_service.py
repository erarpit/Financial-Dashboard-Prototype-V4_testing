from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from models.holders import Holders, YfData
from models.schemas import OwnershipData

logger = logging.getLogger(__name__)

class HoldersService:
    """Service for managing ownership and insider data"""
    
    def __init__(self):
        self.data_fetcher = YfData()
    
    def get_ownership_data(self, symbol: str) -> Optional[OwnershipData]:
        """Get comprehensive ownership data for a symbol"""
        try:
            holders = Holders(self.data_fetcher, symbol)
            
            # Get all ownership data
            institutional = holders.institutional
            mutual_fund = holders.mutualfund
            major_breakdown = holders.major
            insider_transactions = holders.insider_transactions
            insider_roster = holders.insider_roster
            insider_purchases = holders.insider_purchases
            
            # Convert DataFrames to dictionaries
            institutional_data = institutional.to_dict('records') if not institutional.empty else []
            mutual_fund_data = mutual_fund.to_dict('records') if not mutual_fund.empty else []
            major_breakdown_data = major_breakdown.to_dict('index') if not major_breakdown.empty else {}
            insider_transactions_data = insider_transactions.to_dict('records') if not insider_transactions.empty else []
            insider_roster_data = insider_roster.to_dict('records') if not insider_roster.empty else []
            insider_purchases_data = insider_purchases.to_dict('index') if not insider_purchases.empty else {}
            
            return OwnershipData(
                symbol=symbol,
                institutional_holders=institutional_data,
                mutual_fund_holders=mutual_fund_data,
                major_holders_breakdown=major_breakdown_data,
                insider_transactions=insider_transactions_data,
                insider_roster=insider_roster_data,
                insider_purchases=insider_purchases_data,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting ownership data for {symbol}: {str(e)}")
            return None
    
    def get_institutional_holders(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get institutional holders for a symbol"""
        try:
            holders = Holders(self.data_fetcher, symbol)
            institutional = holders.institutional
            
            if institutional.empty:
                return []
            
            # Convert to records and limit
            data = institutional.to_dict('records')
            return data[:limit]
            
        except Exception as e:
            logger.error(f"Error getting institutional holders for {symbol}: {str(e)}")
            return []
    
    def get_insider_transactions(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get insider transactions for a symbol"""
        try:
            holders = Holders(self.data_fetcher, symbol)
            insider_transactions = holders.insider_transactions
            
            if insider_transactions.empty:
                return []
            
            # Convert to records and limit
            data = insider_transactions.to_dict('records')
            return data[:limit]
            
        except Exception as e:
            logger.error(f"Error getting insider transactions for {symbol}: {str(e)}")
            return []
    
    def get_major_holders_breakdown(self, symbol: str) -> Dict[str, Any]:
        """Get major holders breakdown for a symbol"""
        try:
            holders = Holders(self.data_fetcher, symbol)
            major_breakdown = holders.major
            
            if major_breakdown.empty:
                return {}
            
            return major_breakdown.to_dict('index')
            
        except Exception as e:
            logger.error(f"Error getting major holders breakdown for {symbol}: {str(e)}")
            return {}
    
    def get_insider_roster(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get insider roster for a symbol"""
        try:
            holders = Holders(self.data_fetcher, symbol)
            insider_roster = holders.insider_roster
            
            if insider_roster.empty:
                return []
            
            # Convert to records and limit
            data = insider_roster.to_dict('records')
            return data[:limit]
            
        except Exception as e:
            logger.error(f"Error getting insider roster for {symbol}: {str(e)}")
            return []

# Global instance
holders_service = HoldersService()
