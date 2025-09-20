from abc import ABC, abstractmethod
import numbers
from typing import List, Union, Dict, TypeVar, Tuple
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Union[str, numbers.Real])

# Simplified field definitions for your project
EQUITY_SCREENER_FIELDS = {
    "Basic": [
        "symbol", "longName", "shortName", "exchange", "sector", "industry",
        "marketCap", "enterpriseValue", "trailingPE", "forwardPE", "pegRatio"
    ],
    "Financial": [
        "totalRevenue", "revenueGrowth", "profitMargins", "operatingMargins",
        "grossMargins", "ebitda", "ebitdaMargins", "netIncomeToCommon"
    ],
    "Trading": [
        "regularMarketPrice", "regularMarketChange", "regularMarketChangePercent",
        "regularMarketVolume", "averageVolume", "fiftyTwoWeekHigh", "fiftyTwoWeekLow"
    ],
    "Valuation": [
        "priceToBook", "priceToSalesTrailing12Months", "enterpriseToRevenue",
        "enterpriseToEbitda", "beta", "bookValue", "priceToCashflowPerShare"
    ]
}

EQUITY_SCREENER_EQ_MAP = {
    "exchange": ["NMS", "NYQ", "NCM", "NGM", "BSE", "NSE", "LSE", "TSE"],
    "sector": [
        "Technology", "Healthcare", "Financial Services", "Consumer Cyclical",
        "Consumer Defensive", "Energy", "Industrials", "Communication Services",
        "Utilities", "Real Estate", "Basic Materials"
    ],
    "industry": [
        "Software—Infrastructure", "Software—Application", "Banks—Diversified",
        "Drug Manufacturers—General", "Oil & Gas Integrated", "Auto Manufacturers",
        "Semiconductors", "Biotechnology", "Insurance—Life", "Retail—Apparel & Specialty"
    ]
}

FUND_SCREENER_FIELDS = {
    "Basic": [
        "symbol", "longName", "shortName", "categoryName", "exchange",
        "totalAssets", "ytdReturn", "beta3Year", "expenseRatio"
    ],
    "Performance": [
        "annualReportExpenseRatio", "fundInceptionDate", "ytdReturn",
        "return1Y", "return3Y", "return5Y", "return10Y", "return30Y"
    ],
    "Risk": [
        "beta3Year", "alpha3Year", "sharpeRatio3Year", "treynorRatio3Year",
        "volatility3Year", "maxDrawdown3Year"
    ]
}

FUND_SCREENER_EQ_MAP = {
    "categoryName": [
        "Large Growth", "Large Value", "Large Blend", "Mid-Cap Growth",
        "Mid-Cap Value", "Mid-Cap Blend", "Small Growth", "Small Value",
        "Small Blend", "International Large Growth", "International Large Value"
    ],
    "exchange": ["NMS", "NYQ", "NAS", "BSE", "NSE", "LSE", "TSE"]
}

class YFNotImplementedError(Exception):
    """Custom exception for not implemented methods"""
    pass

class QueryBase(ABC):
    """Abstract base class for building financial data queries"""
    
    def __init__(self, operator: str, operand: Union[List['QueryBase'], Tuple[str, Tuple[Union[str, numbers.Real], ...]]]):
        operator = operator.upper()

        if not isinstance(operand, list):
            raise TypeError('Invalid operand type')
        if len(operand) <= 0:
            raise ValueError('Invalid field for Query')

        if operator == 'IS-IN':
            self._validate_isin_operand(operand)
        elif operator in {'OR', 'AND'}:
            self._validate_or_and_operand(operand)
        elif operator == 'EQ':
            self._validate_eq_operand(operand)
        elif operator == 'BTWN':
            self._validate_btwn_operand(operand)
        elif operator in {'GT', 'LT', 'GTE', 'LTE'}:
            self._validate_gt_lt(operand)
        else:
            raise ValueError('Invalid Operator Value')

        self.operator = operator
        self.operands = operand

    @property
    @abstractmethod
    def valid_fields(self) -> Dict:
        raise YFNotImplementedError('valid_fields() needs to be implemented by child')

    @property
    @abstractmethod
    def valid_values(self) -> Dict:
        raise YFNotImplementedError('valid_values() needs to be implemented by child')

    def _validate_or_and_operand(self, operand: List['QueryBase']) -> None:
        if len(operand) <= 1:
            raise ValueError('Operand must be length longer than 1')
        if all(isinstance(e, QueryBase) for e in operand) is False:
            raise TypeError(f'Operand must be type {type(self)} for OR/AND')

    def _validate_eq_operand(self, operand: List[Union[str, numbers.Real]]) -> None:
        if len(operand) != 2:
            raise ValueError('Operand must be length 2 for EQ')

        if not any(operand[0] in fields_by_type for fields_by_type in self.valid_fields.values()):
            raise ValueError(f'Invalid field for {type(self)} "{operand[0]}"')
        if operand[0] in self.valid_values:
            vv = self.valid_values[operand[0]]
            if isinstance(vv, dict):
                vv = set().union(*[e for e in vv.values()])
            if operand[1] not in vv:
                raise ValueError(f'Invalid EQ value "{operand[1]}"')

    def _validate_btwn_operand(self, operand: List[Union[str, numbers.Real]]) -> None:
        if len(operand) != 3:
            raise ValueError('Operand must be length 3 for BTWN')
        if not any(operand[0] in fields_by_type for fields_by_type in self.valid_fields.values()):
            raise ValueError(f'Invalid field for {type(self)}')
        if isinstance(operand[1], numbers.Real) is False:
            raise TypeError('Invalid comparison type for BTWN')
        if isinstance(operand[2], numbers.Real) is False:
            raise TypeError('Invalid comparison type for BTWN')

    def _validate_gt_lt(self, operand: List[Union[str, numbers.Real]]) -> None:
        if len(operand) != 2:
            raise ValueError('Operand must be length 2 for GT/LT')
        if not any(operand[0] in fields_by_type for fields_by_type in self.valid_fields.values()):
            raise ValueError(f'Invalid field for {type(self)} "{operand[0]}"')
        if isinstance(operand[1], numbers.Real) is False:
            raise TypeError('Invalid comparison type for GT/LT')

    def _validate_isin_operand(self, operand: List['QueryBase']) -> None:
        if len(operand) < 2:
            raise ValueError('Operand must be length 2+ for IS-IN')

        if not any(operand[0] in fields_by_type for fields_by_type in self.valid_fields.values()):
            raise ValueError(f'Invalid field for {type(self)} "{operand[0]}"')
        if operand[0] in self.valid_values:
            vv = self.valid_values[operand[0]]
            if isinstance(vv, dict):
                vv = set().union(*[e for e in vv.values()])
            for i in range(1, len(operand)):
                if operand[i] not in vv:
                    raise ValueError(f'Invalid EQ value "{operand[i]}"')

    def to_dict(self) -> Dict:
        op = self.operator
        ops = self.operands
        if self.operator == 'IS-IN':
            op = 'OR'
            ops = [type(self)('EQ', [self.operands[0], v]) for v in self.operands[1:]]
        return {
            "operator": op,
            "operands": [o.to_dict() if isinstance(o, QueryBase) else o for o in ops]
        }

    def __repr__(self, indent=0) -> str:
        indent_str = "  " * indent
        class_name = self.__class__.__name__

        if isinstance(self.operands, list):
            if any(isinstance(op, QueryBase) for op in self.operands):
                operands_str = ",\n".join(
                    f"{indent_str}  {op.__repr__(indent + 1) if isinstance(op, QueryBase) else repr(op)}"
                    for op in self.operands
                )
                return f"{class_name}({self.operator}, [\n{operands_str}\n{indent_str}])"
            else:
                return f"{class_name}({self.operator}, {repr(self.operands)})"
        else:
            return f"{class_name}({self.operator}, {repr(self.operands)})"

    def __str__(self) -> str:
        return self.__repr__()


class EquityQuery(QueryBase):
    """
    The EquityQuery class constructs filters for stocks based on specific criteria.
    
    Example:
        EquityQuery('and', [
            EquityQuery('is-in', ['exchange', 'NSE', 'BSE']), 
            EquityQuery('lt', ['trailingPE', 20]),
            EquityQuery('gt', ['marketCap', 1000000000])
        ])
    """

    @property
    def valid_fields(self) -> Dict:
        """Valid operands, grouped by category."""
        return EQUITY_SCREENER_FIELDS

    @property
    def valid_values(self) -> Dict:
        """Most operands take number values, but some have restricted valid values."""
        return EQUITY_SCREENER_EQ_MAP


class FundQuery(QueryBase):
    """
    The FundQuery class constructs filters for mutual funds based on specific criteria.
    
    Example:
        FundQuery('and', [
            FundQuery('eq', ['categoryName', 'Large Growth']), 
            FundQuery('lt', ['expenseRatio', 0.01]),
            FundQuery('gt', ['return3Y', 0.1])
        ])
    """

    @property
    def valid_fields(self) -> Dict:
        """Valid operands, grouped by category."""
        return FUND_SCREENER_FIELDS

    @property
    def valid_values(self) -> Dict:
        """Most operands take number values, but some have restricted valid values."""
        return FUND_SCREENER_EQ_MAP
