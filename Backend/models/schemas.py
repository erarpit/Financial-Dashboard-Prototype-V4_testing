

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class StockData(BaseModel):
    ticker: str
    price: float
    price_change_1d: float
    price_change_5d: float
    rsi: float
    rsi_status: str
    macd: float
    macd_signal: float
    ema20: float
    bollinger_high: float
    bollinger_low: float
    atr: float
    trend: str
    volume: int
    last_updated: str

class NewsItem(BaseModel):
    title: str
    url: str
    source: str
    published_at: str
    content: str
    sentiment: str
    confidence: float

class Signal(BaseModel):
    ticker: str
    signal: str
    signals: List[str]
    reasoning: List[str]
    generated_at: str

class DashboardResponse(BaseModel):
    stocks: List[StockData]
    news: List[NewsItem]
    signals: List[Signal]
    timestamp: str
# ADD these new classes at the end of the file

class OHLCData(BaseModel):
    ticker: str
    timeframe: str
    timestamps: List[str]
    open: List[float]
    high: List[float]
    low: List[float]
    close: List[float]
    volume: List[int]

class PatternDetection(BaseModel):
    pattern_name: str
    ticker: str
    timestamp: str
    value: int
    confidence: float
    candle_index: int

class PatternAnalysis(BaseModel):
    ticker: str
    timeframe: str
    detections: List[PatternDetection]
    total_patterns: int
    bullish_count: int
    bearish_count: int

# Domain-related schemas
class DomainOverview(BaseModel):
    companies_count: Optional[int] = None
    market_cap: Optional[float] = None
    message_board_id: Optional[str] = None
    description: Optional[str] = None
    industries_count: Optional[int] = None
    market_weight: Optional[float] = None
    employee_count: Optional[int] = None

class TopCompany(BaseModel):
    symbol: str
    name: str
    rating: Optional[str] = None
    market_weight: Optional[float] = None

class ResearchReport(BaseModel):
    title: str
    url: str
    date: str

class DomainData(BaseModel):
    key: str
    name: str
    symbol: str
    overview: DomainOverview
    top_companies: List[TopCompany]
    research_reports: List[ResearchReport]
    last_updated: str

class SectorData(DomainData):
    sector_type: str = "sector"

class IndustryData(DomainData):
    industry_type: str = "industry"

# Market and Holders schemas
class MarketStatus(BaseModel):
    market: str
    is_open: bool
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    timezone: Optional[str] = None
    last_updated: str

class MarketSummary(BaseModel):
    market: str
    exchanges: Dict[str, Any]
    last_updated: str

class OwnershipData(BaseModel):
    symbol: str
    institutional_holders: List[Dict[str, Any]]
    mutual_fund_holders: List[Dict[str, Any]]
    major_holders_breakdown: Dict[str, Any]
    insider_transactions: List[Dict[str, Any]]
    insider_roster: List[Dict[str, Any]]
    insider_purchases: Dict[str, Any]
    last_updated: str

# FastInfo and Quote schemas
class FastInfoData(BaseModel):
    symbol: str
    currency: Optional[str] = None
    quote_type: Optional[str] = None
    exchange: Optional[str] = None
    timezone: Optional[str] = None
    shares: Optional[int] = None
    market_cap: Optional[float] = None
    last_price: Optional[float] = None
    previous_close: Optional[float] = None
    open_price: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    regular_market_previous_close: Optional[float] = None
    last_volume: Optional[int] = None
    fifty_day_average: Optional[float] = None
    two_hundred_day_average: Optional[float] = None
    ten_day_average_volume: Optional[int] = None
    three_month_average_volume: Optional[int] = None
    year_high: Optional[float] = None
    year_low: Optional[float] = None
    year_change: Optional[float] = None
    last_updated: str

class QuoteData(BaseModel):
    symbol: str
    info: Dict[str, Any]
    last_updated: str

class SustainabilityData(BaseModel):
    symbol: str
    data: Dict[str, Any]
    last_updated: str

class RecommendationData(BaseModel):
    symbol: str
    data: List[Dict[str, Any]]
    last_updated: str

class CalendarData(BaseModel):
    symbol: str
    events: Dict[str, Any]
    last_updated: str

# Enhanced schemas for AI Market News Impact Analyzer
class TechnicalIndicators(BaseModel):
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    ema_50: Optional[float] = None
    atr_14: Optional[float] = None
    current_price: Optional[float] = None
    last_updated: str

class VolumeAnalysis(BaseModel):
    current_volume: int
    avg_volume_20d: Optional[int] = None
    volume_ratio: Optional[float] = None
    volume_trend: Optional[str] = None  # "increasing", "decreasing", "stable"
    volume_spike: Optional[bool] = None
    last_updated: str

class PriceMomentum(BaseModel):
    current_price: float
    price_change_1d: float
    price_change_pct_1d: float
    price_change_5d: Optional[float] = None
    price_change_pct_5d: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    last_updated: str

class AISignal(BaseModel):
    signal_type: str  # "BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL"
    confidence: float  # 0.0 to 1.0
    reasoning: List[str]
    technical_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    volume_score: Optional[float] = None
    generated_at: str

class EnhancedStockData(StockData):
    """Enhanced stock data with AI analysis capabilities"""
    technical_indicators: Optional[TechnicalIndicators] = None
    volume_analysis: Optional[VolumeAnalysis] = None
    price_momentum: Optional[PriceMomentum] = None
    ai_signals: Optional[List[AISignal]] = None
    data_quality_score: Optional[float] = None
    analysis_timestamp: str

class MarketSentiment(BaseModel):
    overall_sentiment: str  # "POSITIVE", "NEGATIVE", "NEUTRAL"
    sentiment_score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    news_count: int
    positive_ratio: float
    negative_ratio: float
    neutral_ratio: float
    last_updated: str

class NewsAnalysis(BaseModel):
    ticker: str
    sentiment: MarketSentiment
    top_news: List[NewsItem]
    news_impact_score: Optional[float] = None
    trending_topics: Optional[List[str]] = None
    last_updated: str

class PatternAnalysis(BaseModel):
    ticker: str
    timeframe: str
    patterns: List[PatternDetection]
    bullish_patterns: int
    bearish_patterns: int
    pattern_strength: Optional[float] = None
    last_updated: str

class AIDashboardResponse(BaseModel):
    """Enhanced dashboard response with AI analysis"""
    stocks: List[EnhancedStockData]
    news_analysis: List[NewsAnalysis]
    market_sentiment: Optional[MarketSentiment] = None
    pattern_analysis: List[PatternAnalysis]
    ai_insights: Optional[List[str]] = None
    timestamp: str
    ai_version: str = "1.0.0"

class QueryBuilderResult(BaseModel):
    """Result from query builder screening"""
    query: Dict[str, Any]
    results: List[Dict[str, Any]]
    count: int
    execution_time: Optional[float] = None
    timestamp: str

class EnhancedDownloadResult(BaseModel):
    """Result from enhanced download with technical indicators"""
    tickers: List[str]
    data: List[Dict[str, Any]]
    columns: List[str]
    shape: List[int]  # [rows, columns]
    technical_indicators_included: bool
    sentiment_analysis_included: bool
    timestamp: str

class BulkAnalysisResult(BaseModel):
    """Result from bulk analysis"""
    groups: List[str]
    results: Dict[str, Optional[List[Dict[str, Any]]]]
    total_tickers: int
    successful_downloads: int
    failed_downloads: int
    execution_time: Optional[float] = None
    timestamp: str

class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    error_type: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str
    suggestions: Optional[List[str]] = None

class EnhancedDownloadRequest(BaseModel):
    tickers: List[str]
    start: Optional[str] = None
    end: Optional[str] = None
    period: str = "1mo"
    interval: str = "1d"
    include_indicators: bool = True
    include_sentiment: bool = False
    threads: bool = True
    timeout: int = 30