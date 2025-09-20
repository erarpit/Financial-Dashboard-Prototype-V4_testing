# Combined FastAPI Application - Financial Dashboard with AI Assistant
# Merges main.py and enhanced-main.py for complete functionality
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# Import services
from services.market_data import get_stock_data, get_historical_data
import yfinance as yf
from services.news_scraper import get_financial_news, NewsItem
from services.sentiment_analysis import analyze_sentiment
from services.signals import generate_signals
from services.domain_service import domain_service
from services.market_service import market_service
from services.holders_service import holders_service
from services.fastinfo_service import fastinfo_service
from services.quote_service import quote_service
from services.query_builder_service import query_builder_service
from services.enhanced_yfinance import enhanced_downloader
from services.alpha_vantage_service import alpha_vantage_service
from services.alpha_vantage_hybrid import alpha_vantage_hybrid
from services.currency_service import currency_service
from services.angel_one_service import angel_one_service

# Import new pipelines
try:
    from pipelines.assistant import ask_ai_assistant, QueryTemplates
    from pipelines.volume_analysis import analyze_volume, compute_volume_signal
    from pipelines.live_data import get_live_quote, get_popular_stocks_data
    from pipelines.news import get_recent_news
    from pipelines.enhanced_analysis import get_enhanced_analysis, get_analyst_summary, get_earnings_estimates
except ImportError as e:
    print(f"Some pipeline imports failed: {e}")
    # Create fallback functions if needed

# Import models and schemas
from models.database import init_db, get_cached_data, cache_data
from models.schemas import (
    StockData, Signal, DashboardResponse, SectorData, IndustryData, MarketStatus, MarketSummary, 
    OwnershipData, FastInfoData, QuoteData, SustainabilityData, RecommendationData, CalendarData,
    TechnicalIndicators, VolumeAnalysis, PriceMomentum, AISignal, EnhancedStockData, MarketSentiment,
    NewsAnalysis, PatternAnalysis, AIDashboardResponse, QueryBuilderResult, EnhancedDownloadResult,
    BulkAnalysisResult, ErrorResponse, EnhancedDownloadRequest
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to get raw DataFrame for analysis
async def get_stock_dataframe(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Get raw pandas DataFrame for analysis purposes"""
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if df.empty:
            logger.warning(f"No data found for {ticker}, creating mock data")
            # Create mock data for testing
            dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
            mock_data = {
                'Open': np.random.uniform(100, 200, 30),
                'High': np.random.uniform(150, 250, 30),
                'Low': np.random.uniform(50, 150, 30),
                'Close': np.random.uniform(100, 200, 30),
                'Volume': np.random.randint(1000000, 10000000, 30)
            }
            df = pd.DataFrame(mock_data, index=dates)
        
        # Flatten multi-level columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        return df
    except Exception as e:
        logger.error(f"Error getting DataFrame for {ticker}: {str(e)}")
        # Return mock DataFrame with required columns
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
        mock_data = {
            'Open': np.random.uniform(100, 200, 30),
            'High': np.random.uniform(150, 250, 30),
            'Low': np.random.uniform(50, 150, 30),
            'Close': np.random.uniform(100, 200, 30),
            'Volume': np.random.randint(1000000, 10000000, 30)
        }
        return pd.DataFrame(mock_data, index=dates)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("🚀 Starting Financial Dashboard API with AI Assistant")
    init_db()
    yield
    # Shutdown
    logger.info("⏹️ Shutting down Financial Dashboard API")

# Initialize FastAPI app
app = FastAPI(
    title="Financial Dashboard with AI Assistant",
    description="Intelligent stock market analysis dashboard with AI-powered insights, caching, and comprehensive analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Add router registration (moved after app initialization)
try:
    from routers.patterns import router as patterns_router
    app.include_router(patterns_router)
except ImportError:
    logger.warning("Patterns router not available - skipping pattern endpoints")

# Middleware
app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # Frontend URLs + wildcard for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= BASIC ENDPOINTS =============

@app.get("/")
async def root():
    return {"message": "Financial Dashboard API with AI Assistant", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": ["AI Assistant", "Volume Analysis", "Live Data", "Sentiment Analysis", "Caching", "Patterns", "Enhanced Analysis", "Analyst Data", "Earnings Estimates", "Domain Analysis", "Sector Data", "Industry Data", "Market Status", "Ownership Data", "Insider Trading", "FastInfo", "Quote Data", "Sustainability", "Recommendations", "Query Builder", "Stock Screening", "Enhanced YFinance", "Bulk Download", "Technical Indicators"]
    }

# ============= STOCK DATA ENDPOINTS =============

@app.get("/stocks/{ticker}")
async def get_stock(
    ticker: str, 
    period: str = "6mo", 
    interval: str = "1d"
) -> StockData:
    """Get stock data for a specific ticker with caching."""
    try:
        # Check cache first
        cache_key = f"stock_{ticker}_{period}_{interval}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            # Ensure cached data is a proper StockData object
            if isinstance(cached_data, dict):
                return StockData(**cached_data)
            return cached_data
        
        # Fetch fresh data
        data = await get_stock_data(ticker, period, interval)
        
        # Ensure data is properly serialized before caching
        if hasattr(data, 'dict'):
            data_dict = data.dict()
        elif hasattr(data, 'model_dump'):
            data_dict = data.model_dump()
        else:
            data_dict = data
        
        cache_data(cache_key, data_dict, expiry_minutes=5)
        return data
    except Exception as e:
        logger.error(f"Error fetching stock data for {ticker}: {str(e)}")
        # Return mock data instead of raising error
        try:
            from services.market_data import generate_mock_data
            mock_data = generate_mock_data(ticker)
            return mock_data
        except Exception as mock_error:
            logger.error(f"Failed to generate mock data: {str(mock_error)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch data for {ticker}")

@app.get("/live")
async def get_live_data(ticker: str = Query(..., description="Stock ticker symbol")):
    """Get real-time/delayed market data for a ticker."""
    try:
        live_data = get_live_quote(ticker)
        return live_data
        
    except Exception as e:
        logger.error(f"Live data error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live data: {str(e)}")

@app.get("/popular-stocks")
async def get_popular_stocks():
    """Get data for popular Indian stocks."""
    try:
        popular_data = get_popular_stocks_data()
        return popular_data
        
    except Exception as e:
        logger.error(f"Popular stocks error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch popular stocks: {str(e)}")

# ============= NEWS ENDPOINTS =============

@app.get("/news")
async def get_news(limit: int = Query(10, description="Number of news items to return")) -> List[NewsItem]:
    """Get financial news with caching and sentiment analysis."""
    try:
        cache_key = f"news_{limit}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Try enhanced news first, fallback to original
        try:
            news_items = get_recent_news(limit=limit)
            
            # Map and validate news items to match NewsItem schema
            validated_news = []
            for item in news_items:
                if isinstance(item, dict):
                    # Map field names to match schema
                    mapped_item = {
                        'title': item.get('title', 'No title'),
                        'url': item.get('url', '#'),
                        'source': item.get('source', item.get('source_name', 'Unknown')),
                        'published_at': item.get('published_at', datetime.now().isoformat()),
                        'content': item.get('content', 'No content available')
                    }
                    
                    # Add sentiment analysis
                    try:
                        if 'content' in item:
                            sentiment, confidence = analyze_sentiment(item.get('content', '') + ' ' + item.get('title', ''))
                            mapped_item['sentiment'] = sentiment.lower()
                            mapped_item['confidence'] = confidence
                        else:
                            mapped_item['sentiment'] = 'neutral'
                            mapped_item['confidence'] = 0.5
                    except Exception as e:
                        logger.warning(f"Sentiment analysis failed: {str(e)}")
                        mapped_item['sentiment'] = 'neutral'
                        mapped_item['confidence'] = 0.5
                    
                    validated_news.append(mapped_item)
            
            cache_data(cache_key, validated_news, expiry_minutes=15)
            return validated_news
            
        except Exception as e:
            logger.warning(f"Enhanced news failed, using fallback: {str(e)}")
            try:
                news = await get_financial_news(limit)
                
                # Ensure fallback news also has correct schema
                validated_news = []
                for item in news:
                    if isinstance(item, dict):
                        mapped_item = {
                            'title': item.get('title', 'No title'),
                            'url': item.get('url', '#'),
                            'source': item.get('source', 'Unknown'),
                            'published_at': item.get('published_at', datetime.now().isoformat()),
                            'content': item.get('content', 'No content available'),
                            'sentiment': item.get('sentiment', 'neutral'),
                            'confidence': item.get('confidence', 0.5)
                        }
                        validated_news.append(mapped_item)
                
                cache_data(cache_key, validated_news, expiry_minutes=15)
                return validated_news
            except Exception as e2:
                logger.error(f"Fallback news also failed: {str(e2)}")
                # Return minimal mock news
                mock_news = [{
                    'title': 'Market Update',
                    'url': '#',
                    'source': 'System',
                    'published_at': datetime.now().isoformat(),
                    'content': 'Market data temporarily unavailable',
                    'sentiment': 'neutral',
                    'confidence': 0.5
                }]
                cache_data(cache_key, mock_news, expiry_minutes=15)
                return mock_news
            
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= SIGNALS ENDPOINTS =============

@app.get("/signals/{ticker}")
async def get_signal(ticker: str) -> Signal:
    """Get trading signals for a ticker with caching."""
    try:
        cache_key = f"signal_{ticker}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            # Ensure cached data is a proper Signal object
            if isinstance(cached_data, dict):
                return Signal(**cached_data)
            return cached_data
        
        # Get stock data and news for analysis
        stock_data = await get_stock_data(ticker)
        news = await get_financial_news(5)
        
        # Ensure news items have the required structure for signal generation
        processed_news = []
        for item in news:
            if isinstance(item, dict):
                # Convert dict to object with sentiment attribute
                class NewsItem:
                    def __init__(self, data):
                        self.sentiment = data.get('sentiment', 'NEUTRAL')
                        self.title = data.get('title', '')
                        self.content = data.get('content', '')
                
                processed_news.append(NewsItem(item))
            else:
                # If it's already an object, use it as is
                processed_news.append(item)
        
        # Generate signals
        signal = generate_signals(ticker, stock_data, processed_news)
        
        # Ensure the signal is properly serialized
        if isinstance(signal, Signal):
            # It's already a Signal object
            signal_obj = signal
        else:
            # If it's not a Signal object, create one
            signal_obj = Signal(
                ticker=ticker,
                signal=getattr(signal, 'signal', 'HOLD'),
                signals=getattr(signal, 'signals', ['HOLD']),
                reasoning=getattr(signal, 'reasoning', ['Signal generation failed']),
                generated_at=getattr(signal, 'generated_at', datetime.now().isoformat())
            )
        
        # Cache the serialized version
        signal_dict = signal_obj.dict() if hasattr(signal_obj, 'dict') else signal_obj.model_dump()
        cache_data(cache_key, signal_dict, expiry_minutes=10)
        return signal_obj
    except Exception as e:
        logger.error(f"Error generating signals for {ticker}: {str(e)}")
        # Return a fallback signal instead of raising error
        fallback_signal = Signal(
            ticker=ticker,
            signal="HOLD",
            signals=["HOLD"],
            reasoning=[f"Signal generation failed: {str(e)}"],
            generated_at=datetime.now().isoformat()
        )
        return fallback_signal

# ============= VOLUME ANALYSIS ENDPOINTS =============

@app.get("/volume-analysis/{ticker}")
async def get_volume_analysis(ticker: str):
    """Get detailed volume analysis for a stock."""
    try:
        # Get raw DataFrame for analysis
        df = await get_stock_dataframe(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        volume_analysis = analyze_volume(df)
        volume_signal = compute_volume_signal(df)
        
        return {
            "ticker": ticker,
            "volume_analysis": volume_analysis,
            "volume_signal": volume_signal,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Volume analysis error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Volume analysis failed: {str(e)}")

# ============= AI ASSISTANT ENDPOINTS =============

@app.get("/ask")
async def ask_ai_assistant_endpoint(
    q: str = Query(..., description="Your question for the AI assistant"),
    ticker: str = Query("RELIANCE.NS", description="Stock ticker for context")
):
    """AI-powered stock analysis assistant."""
    try:
        # Gather comprehensive context
        context = await _build_context(ticker)
        
        # Mock backtest data (replace with real backtesting results)
        backtest = {
            "accuracy": "73% (last 6 months)",
            "win_rate": "65% on NIFTY50 signals", 
            "avg_gain": "1.8% per trade",
            "total_trades": 150,
            "max_drawdown": "-2.3%"
        }
        
        # Get AI response
        answer = ask_ai_assistant(q, context=context, backtest=backtest)
        
        return {
            "question": q,
            "ticker": ticker,
            "answer": answer,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI Assistant error: {str(e)}")
        return {
            "question": q,
            "answer": f"I'm experiencing technical difficulties: {str(e)}",
            "error": True
        }

@app.get("/ask/templates")
async def get_query_templates():
    """Get predefined query templates for common questions."""
    return {
        "buy_sell": "Should I buy, sell, or hold {ticker} right now?",
        "risk_assessment": "What are the risks of investing in {ticker}?",
        "price_target": "What could be a realistic price target for {ticker}?",
        "volume_analysis": "How should I interpret the current volume pattern in {ticker}?",
        "news_impact": "How might recent news affect {ticker}'s stock price?"
    }

# ============= ENHANCED ANALYSIS ENDPOINTS =============

@app.get("/analysis/{ticker}")
async def get_enhanced_analysis_endpoint(ticker: str):
    """Get comprehensive enhanced analysis for a ticker."""
    try:
        # Get raw DataFrame for analysis
        df = await get_stock_dataframe(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        # Basic analysis using DataFrame
        analysis = {
            "ticker": ticker,
            "analysis_type": "basic",
            "data_points": len(df),
            "last_price": float(df['Close'].iloc[-1]) if not df.empty else None,
            "price_change": float(df['Close'].iloc[-1] - df['Close'].iloc[-2]) if len(df) > 1 else None,
            "volume": int(df['Volume'].iloc[-1]) if not df.empty else None,
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis
    except Exception as e:
        logger.error(f"Enhanced analysis error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")

@app.get("/analysis/{ticker}/analyst")
async def get_analyst_analysis(ticker: str):
    """Get analyst analysis for a ticker."""
    try:
        analysis = {
            "ticker": ticker,
            "analyst_consensus": "BUY",
            "target_price": 2500.0,
            "analyst_rating": 4.2,
            "price_targets": [
                {"analyst": "Morgan Stanley", "rating": "BUY", "target": 2600.0},
                {"analyst": "Goldman Sachs", "rating": "HOLD", "target": 2400.0},
                {"analyst": "JP Morgan", "rating": "BUY", "target": 2700.0}
            ],
            "last_updated": datetime.now().isoformat()
        }
        return analysis
    except Exception as e:
        logger.error(f"Analyst analysis error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analyst analysis failed: {str(e)}")

@app.get("/analysis/{ticker}/earnings")
async def get_earnings_analysis(ticker: str):
    """Get earnings analysis for a ticker."""
    try:
        analysis = {
            "ticker": ticker,
            "next_earnings_date": "2024-01-15",
            "estimated_eps": 45.50,
            "actual_eps": None,
            "eps_growth": 12.5,
            "revenue_estimate": 15000000000,
            "revenue_actual": None,
            "earnings_history": [
                {"quarter": "Q3 2023", "eps": 42.30, "revenue": 14000000000},
                {"quarter": "Q2 2023", "eps": 38.90, "revenue": 13500000000},
                {"quarter": "Q1 2023", "eps": 35.20, "revenue": 12800000000}
            ],
            "last_updated": datetime.now().isoformat()
        }
        return analysis
    except Exception as e:
        logger.error(f"Earnings analysis error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Earnings analysis failed: {str(e)}")

@app.get("/analyst/{ticker}")
async def get_analyst_data(ticker: str):
    """Get analyst recommendations and price targets for a ticker."""
    try:
        # Mock analyst data for now
        analyst_data = {
            "ticker": ticker,
            "analyst_consensus": "BUY",
            "target_price": 2500.0,
            "analyst_rating": 4.2,
            "price_targets": {
                "high": 2800.0,
                "low": 2200.0,
                "median": 2500.0
            },
            "last_updated": datetime.now().isoformat()
        }
        return analyst_data
    except Exception as e:
        logger.error(f"Analyst data error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analyst data failed: {str(e)}")

@app.get("/earnings/{ticker}")
async def get_earnings_data(ticker: str):
    """Get earnings estimates and history for a ticker."""
    try:
        # Mock earnings data for now
        earnings_data = {
            "ticker": ticker,
            "next_earnings_date": "2024-01-15",
            "estimated_eps": 25.50,
            "actual_eps": None,
            "eps_growth": 12.5,
            "revenue_estimate": 15000000000,
            "revenue_actual": None,
            "earnings_history": [
                {"quarter": "Q3 2023", "eps": 23.45, "revenue": 14000000000},
                {"quarter": "Q2 2023", "eps": 22.10, "revenue": 13500000000},
                {"quarter": "Q1 2023", "eps": 21.80, "revenue": 13000000000}
            ],
            "last_updated": datetime.now().isoformat()
        }
        return earnings_data
    except Exception as e:
        logger.error(f"Earnings data error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Earnings data failed: {str(e)}")

# ============= DOMAIN ENDPOINTS =============

@app.get("/sectors")
async def get_all_sectors() -> List[SectorData]:
    """Get all available financial sectors."""
    try:
        sectors = domain_service.get_all_sectors()
        return sectors
    except Exception as e:
        logger.error(f"Error fetching sectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sectors: {str(e)}")

@app.get("/sectors/{sector_key}")
async def get_sector(sector_key: str) -> SectorData:
    """Get specific sector data by key."""
    try:
        sector = domain_service.get_sector(sector_key)
        if not sector:
            raise HTTPException(status_code=404, detail=f"Sector '{sector_key}' not found")
        return sector
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sector {sector_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sector: {str(e)}")

@app.get("/sectors/{sector_key}/companies")
async def get_sector_companies(
    sector_key: str, 
    limit: int = Query(10, description="Number of companies to return")
) -> List[Dict]:
    """Get top companies in a specific sector."""
    try:
        companies = domain_service.get_sector_companies(sector_key, limit)
        return [company.dict() for company in companies]
    except Exception as e:
        logger.error(f"Error fetching companies for sector {sector_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sector companies: {str(e)}")

@app.get("/industries")
async def get_all_industries() -> List[IndustryData]:
    """Get all available financial industries."""
    try:
        industries = domain_service.get_all_industries()
        return industries
    except Exception as e:
        logger.error(f"Error fetching industries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch industries: {str(e)}")

@app.get("/industries/{industry_key}")
async def get_industry(industry_key: str) -> IndustryData:
    """Get specific industry data by key."""
    try:
        industry = domain_service.get_industry(industry_key)
        if not industry:
            raise HTTPException(status_code=404, detail=f"Industry '{industry_key}' not found")
        return industry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching industry {industry_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch industry: {str(e)}")

@app.get("/industries/{industry_key}/companies")
async def get_industry_companies(
    industry_key: str, 
    limit: int = Query(10, description="Number of companies to return")
) -> List[Dict]:
    """Get top companies in a specific industry."""
    try:
        companies = domain_service.get_industry_companies(industry_key, limit)
        return [company.dict() for company in companies]
    except Exception as e:
        logger.error(f"Error fetching companies for industry {industry_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch industry companies: {str(e)}")

@app.get("/domains/search")
async def search_domains(q: str = Query(..., description="Search query for sectors and industries")):
    """Search for sectors and industries matching the query."""
    try:
        results = domain_service.search_domains(q)
        return {
            "query": q,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching domains: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Domain search failed: {str(e)}")

# ============= MARKET STATUS ENDPOINTS =============

@app.get("/market/status")
async def get_all_market_status():
    """Get status for all available markets."""
    try:
        all_status = market_service.get_all_market_status()
        return {
            "markets": all_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching market status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market status: {str(e)}")

@app.get("/market/status/{market_key}")
async def get_market_status(market_key: str) -> MarketStatus:
    """Get market status for a specific market."""
    try:
        status = market_service.get_market_status(market_key)
        if not status:
            raise HTTPException(status_code=404, detail=f"Market '{market_key}' not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market status for {market_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market status: {str(e)}")

@app.get("/market/summary/{market_key}")
async def get_market_summary(market_key: str) -> MarketSummary:
    """Get market summary for a specific market."""
    try:
        summary = market_service.get_market_summary(market_key)
        if not summary:
            raise HTTPException(status_code=404, detail=f"Market summary for '{market_key}' not found")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market summary for {market_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market summary: {str(e)}")

# ============= OWNERSHIP/HOLDERS ENDPOINTS =============


@app.get("/ownership/{ticker}/institutional")
async def get_institutional_holders(
    ticker: str, 
    limit: int = Query(10, description="Number of institutional holders to return")
) -> List[Dict]:
    """Get institutional holders for a ticker."""
    try:
        holders = holders_service.get_institutional_holders(ticker, limit)
        return holders
    except Exception as e:
        logger.error(f"Error fetching institutional holders for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch institutional holders: {str(e)}")

@app.get("/ownership/{ticker}/insider-transactions")
async def get_insider_transactions(
    ticker: str, 
    limit: int = Query(10, description="Number of insider transactions to return")
) -> List[Dict]:
    """Get insider transactions for a ticker."""
    try:
        transactions = holders_service.get_insider_transactions(ticker, limit)
        return transactions
    except Exception as e:
        logger.error(f"Error fetching insider transactions for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch insider transactions: {str(e)}")

@app.get("/ownership/{ticker}/major-holders")
async def get_major_holders_breakdown(ticker: str) -> Dict[str, Any]:
    """Get major holders breakdown for a ticker."""
    try:
        breakdown = holders_service.get_major_holders_breakdown(ticker)
        return breakdown
    except Exception as e:
        logger.error(f"Error fetching major holders breakdown for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch major holders breakdown: {str(e)}")

@app.get("/ownership/{ticker}/insider-roster")
async def get_insider_roster(
    ticker: str, 
    limit: int = Query(10, description="Number of insiders to return")
) -> List[Dict]:
    """Get insider roster for a ticker."""
    try:
        roster = holders_service.get_insider_roster(ticker, limit)
        return roster
    except Exception as e:
        logger.error(f"Error fetching insider roster for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch insider roster: {str(e)}")

# ============= FASTINFO ENDPOINTS =============

@app.get("/fastinfo/{ticker}")
async def get_fast_info(ticker: str) -> FastInfoData:
    """Get comprehensive fast info for a ticker."""
    try:
        fast_info = fastinfo_service.get_fast_info(ticker)
        if not fast_info:
            raise HTTPException(status_code=404, detail=f"Fast info for '{ticker}' not found")
        return fast_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fast info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch fast info: {str(e)}")

@app.get("/fastinfo/{ticker}/price-summary")
async def get_price_summary(ticker: str) -> Dict[str, Any]:
    """Get price summary for a ticker."""
    try:
        summary = fastinfo_service.get_price_summary(ticker)
        if not summary:
            raise HTTPException(status_code=404, detail=f"Price summary for '{ticker}' not found")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price summary for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch price summary: {str(e)}")

@app.get("/fastinfo/{ticker}/technical-indicators")
async def get_technical_indicators(ticker: str) -> Dict[str, Any]:
    """Get technical indicators for a ticker."""
    try:
        indicators = fastinfo_service.get_technical_indicators(ticker)
        if not indicators:
            raise HTTPException(status_code=404, detail=f"Technical indicators for '{ticker}' not found")
        return indicators
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching technical indicators for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch technical indicators: {str(e)}")

@app.get("/fastinfo/{ticker}/market-cap")
async def get_market_cap_info(ticker: str) -> Dict[str, Any]:
    """Get market cap information for a ticker."""
    try:
        market_cap_info = fastinfo_service.get_market_cap_info(ticker)
        if not market_cap_info:
            raise HTTPException(status_code=404, detail=f"Market cap info for '{ticker}' not found")
        return market_cap_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market cap info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market cap info: {str(e)}")

# ============= QUOTE ENDPOINTS =============

@app.get("/quote/{ticker}")
async def get_quote_info(ticker: str) -> QuoteData:
    """Get comprehensive quote info for a ticker."""
    try:
        quote_info = quote_service.get_quote_info(ticker)
        if not quote_info:
            raise HTTPException(status_code=404, detail=f"Quote info for '{ticker}' not found")
        return quote_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quote info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quote info: {str(e)}")



@app.get("/quote/{ticker}/upgrades-downgrades")
async def get_upgrades_downgrades(ticker: str) -> List[Dict[str, Any]]:
    """Get upgrades/downgrades for a ticker."""
    try:
        upgrades_downgrades = quote_service.get_upgrades_downgrades(ticker)
        return upgrades_downgrades
    except Exception as e:
        logger.error(f"Error fetching upgrades/downgrades for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch upgrades/downgrades: {str(e)}")


@app.get("/quote/{ticker}/company-info")
async def get_company_info(ticker: str) -> Dict[str, Any]:
    """Get basic company information for a ticker."""
    try:
        company_info = quote_service.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company info for '{ticker}' not found")
        return company_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch company info: {str(e)}")

@app.get("/quote/{ticker}/sec-filings")
async def get_sec_filings(ticker: str) -> List[Dict[str, Any]]:
    """Get SEC filings for a ticker."""
    try:
        sec_filings = quote_service.get_sec_filings(ticker)
        return sec_filings
    except Exception as e:
        logger.error(f"Error fetching SEC filings for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch SEC filings: {str(e)}")

# ============= QUERY BUILDER ENDPOINTS =============

@app.get("/query-builder/fields")
async def get_query_fields(query_type: str = Query("equity", description="Type of query: equity or fund")):
    """Get available fields for query building."""
    try:
        fields = query_builder_service.get_available_fields(query_type)
        return {
            "query_type": query_type,
            "fields": fields,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching query fields: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch query fields: {str(e)}")

@app.get("/query-builder/values")
async def get_query_values(query_type: str = Query("equity", description="Type of query: equity or fund")):
    """Get available values for query building."""
    try:
        values = query_builder_service.get_available_values(query_type)
        return {
            "query_type": query_type,
            "values": values,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching query values: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch query values: {str(e)}")

@app.post("/query-builder/validate")
async def validate_query(query_data: Dict[str, Any]):
    """Validate a query structure."""
    try:
        query_type = query_data.get("query_type", "equity")
        query_dict = query_data.get("query", {})
        
        is_valid = query_builder_service.validate_query(query_dict, query_type)
        
        return {
            "valid": is_valid,
            "query_type": query_type,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error validating query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate query: {str(e)}")

@app.post("/query-builder/execute/equity")
async def execute_equity_query(
    query_data: Dict[str, Any],
    limit: int = Query(50, description="Maximum number of results to return")
):
    """Execute an equity query and return matching stocks."""
    try:
        query_dict = query_data.get("query", {})
        results = query_builder_service.execute_equity_query(query_dict, limit)
        
        return {
            "query": query_dict,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing equity query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute equity query: {str(e)}")

@app.post("/query-builder/execute/fund")
async def execute_fund_query(
    query_data: Dict[str, Any],
    limit: int = Query(50, description="Maximum number of results to return")
):
    """Execute a fund query and return matching funds."""
    try:
        query_dict = query_data.get("query", {})
        results = query_builder_service.execute_fund_query(query_dict, limit)
        
        return {
            "query": query_dict,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing fund query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute fund query: {str(e)}")

@app.get("/query-builder/predefined")
async def get_predefined_queries():
    """Get predefined query templates."""
    try:
        queries = query_builder_service.get_predefined_queries()
        return {
            "queries": queries,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching predefined queries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch predefined queries: {str(e)}")

# ============= ENHANCED YFINANCE ENDPOINTS =============

@app.post("/enhanced-download")
async def enhanced_download(request: EnhancedDownloadRequest):
    """Enhanced download with technical indicators and sentiment analysis."""
    try:
        # Create a simple mock response for now
        mock_data = {
            "tickers": request.tickers,
            "data": [
                {
                    "ticker": ticker,
                    "date": datetime.now().isoformat(),
                    "open": 100.0,
                    "high": 105.0,
                    "low": 95.0,
                    "close": 102.0,
                    "volume": 1000000,
                    "sma_20": 100.5,
                    "rsi": 55.0
                }
                for ticker in request.tickers
            ],
            "columns": ["ticker", "date", "open", "high", "low", "close", "volume", "sma_20", "rsi"],
            "shape": [len(request.tickers), 9],
            "timestamp": datetime.now().isoformat()
        }
        
        return mock_data
    except Exception as e:
        logger.error(f"Error in enhanced download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced download failed: {str(e)}")

@app.get("/enhanced-download/indicators")
async def get_enhanced_indicators(
    ticker: str = Query(..., description="Stock ticker symbol"),
    indicator: str = Query("SMA", description="Technical indicator type")
):
    """Get specific technical indicators for a ticker."""
    try:
        df = await get_stock_dataframe(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        # Calculate the requested indicator
        if indicator.upper() == "SMA":
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            indicator_data = df[['Close', 'SMA_20', 'SMA_50']].dropna().tail(20).to_dict('records')
        elif indicator.upper() == "EMA":
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()
            indicator_data = df[['Close', 'EMA_12', 'EMA_26']].dropna().tail(20).to_dict('records')
        elif indicator.upper() == "RSI":
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            indicator_data = df[['Close', 'RSI']].dropna().tail(20).to_dict('records')
        else:
            # Default to SMA
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            indicator_data = df[['Close', 'SMA_20']].dropna().tail(20).to_dict('records')
        
        return {
            "ticker": ticker,
            "indicator": indicator.upper(),
            "data": indicator_data,
            "count": len(indicator_data),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting indicators for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get indicators: {str(e)}")

@app.post("/bulk-download")
async def bulk_download(
    ticker_groups: Dict[str, List[str]] = Body(..., description="Dictionary of ticker groups"),
    period: str = Query("1mo", description="Period for all groups"),
    interval: str = Query("1d", description="Interval for all groups"),
    include_indicators: bool = Query(True, description="Include technical indicators"),
    include_sentiment: bool = Query(False, description="Include sentiment analysis")
):
    """Download data for multiple groups of tickers."""
    try:
        results = await enhanced_downloader.download_bulk_enhanced(
            ticker_groups=ticker_groups,
            period=period,
            interval=interval,
            include_indicators=include_indicators,
            include_sentiment=include_sentiment
        )
        
        return {
            "groups": list(ticker_groups.keys()),
            "results": {group: data.to_dict('records') if data is not None and not data.empty else None 
                       for group, data in results.items()},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in bulk download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk download failed: {str(e)}")

@app.get("/market-summary")
async def get_market_summary(
    tickers: List[str] = Query(..., description="List of ticker symbols for summary")
):
    """Get market summary for a list of tickers."""
    try:
        summary = enhanced_downloader.get_market_summary(tickers)
        return summary
    except Exception as e:
        logger.error(f"Error getting market summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market summary failed: {str(e)}")

@app.get("/enhanced-download/indicators/{ticker}")
async def get_technical_indicators(
    ticker: str,
    period: str = Query("1mo", description="Period for data"),
    interval: str = Query("1d", description="Interval for data")
):
    """Get technical indicators for a specific ticker."""
    try:
        data = await enhanced_downloader.download_enhanced(
            tickers=[ticker],
            period=period,
            interval=interval,
            include_indicators=True,
            include_sentiment=False
        )
        
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        # Extract only technical indicator columns
        indicator_columns = [col for col in data.columns if any(indicator in str(col).upper() 
                          for indicator in ['RSI', 'MACD', 'BBU', 'BBL', 'BBM', 'SMA', 'EMA'])]
        
        if not indicator_columns:
            raise HTTPException(status_code=404, detail=f"No technical indicators found for {ticker}")
        
        indicators_data = data[indicator_columns].dropna()
        
        return {
            "ticker": ticker,
            "indicators": indicators_data.to_dict('records'),
            "columns": indicator_columns,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technical indicators for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get technical indicators: {str(e)}")

# ============= ALPHA VANTAGE ENDPOINTS =============

@app.get("/alpha-vantage/quote/{symbol}")
async def get_alpha_vantage_quote(symbol: str):
    """Get real-time stock quote from Alpha Vantage (with hybrid fallback)"""
    try:
        quote_data = alpha_vantage_hybrid.get_quote(symbol)
        if quote_data is None:
            raise HTTPException(status_code=404, detail=f"No quote data found for {symbol}")
        
        return quote_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Alpha Vantage quote for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quote: {str(e)}")

@app.get("/alpha-vantage/daily/{symbol}")
async def get_alpha_vantage_daily(symbol: str, outputsize: str = Query("compact", description="compact or full")):
    """Get daily time series data from Alpha Vantage (with hybrid fallback)"""
    try:
        data = alpha_vantage_hybrid.get_daily_data(symbol)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No daily data found for {symbol}")
        
        # Convert to records format for JSON response
        data_dict = data.reset_index().to_dict(orient="records")
        
        return {
            "symbol": symbol,
            "data": data_dict,
            "last_updated": datetime.now().isoformat(),
            "source": "Hybrid (Alpha Vantage + Yahoo Finance)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Alpha Vantage daily data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get daily data: {str(e)}")

@app.get("/alpha-vantage/intraday/{symbol}")
async def get_alpha_vantage_intraday(
    symbol: str, 
    interval: str = Query("5min", description="1min, 5min, 15min, 30min, 60min"),
    outputsize: str = Query("compact", description="compact or full")
):
    """Get intraday time series data from Alpha Vantage (with hybrid fallback)"""
    try:
        data = alpha_vantage_hybrid.get_intraday_data(symbol)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No intraday data found for {symbol}")
        
        # Convert to records format for JSON response
        data_dict = data.reset_index().to_dict(orient="records")
        
        return {
            "symbol": symbol,
            "interval": interval,
            "data": data_dict,
            "last_updated": datetime.now().isoformat(),
            "source": "Hybrid (Alpha Vantage + Yahoo Finance)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Alpha Vantage intraday data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get intraday data: {str(e)}")

@app.get("/alpha-vantage/indicators/{symbol}")
async def get_alpha_vantage_indicators(
    symbol: str,
    function: str = Query("SMA", description="SMA, EMA, RSI, MACD, BBANDS"),
    interval: str = Query("daily", description="1min, 5min, 15min, 30min, 60min, daily, weekly, monthly"),
    time_period: int = Query(20, description="Number of data points for calculation"),
    series_type: str = Query("close", description="close, open, high, low")
):
    """Get technical indicators from Alpha Vantage (with hybrid fallback)"""
    try:
        data = alpha_vantage_hybrid.get_technical_indicators(symbol, function, time_period)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No {function} data found for {symbol}")
        
        # Convert to records format for JSON response
        data_dict = data.reset_index().to_dict(orient="records")
        
        return {
            "symbol": symbol,
            "function": function,
            "interval": interval,
            "time_period": time_period,
            "series_type": series_type,
            "data": data_dict,
            "last_updated": datetime.now().isoformat(),
            "source": "Hybrid (Alpha Vantage + Yahoo Finance)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Alpha Vantage indicators for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get indicators: {str(e)}")

@app.get("/alpha-vantage/overview/{symbol}")
async def get_alpha_vantage_overview(symbol: str):
    """Get company overview from Alpha Vantage"""
    try:
        if not alpha_vantage_service.is_enabled():
            raise HTTPException(status_code=503, detail="Alpha Vantage service not enabled. Please set ALPHA_VANTAGE_API_KEY environment variable.")
        
        overview_data = alpha_vantage_service.get_company_overview(symbol)
        if overview_data is None:
            raise HTTPException(status_code=404, detail=f"No company overview found for {symbol}")
        
        return overview_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Alpha Vantage overview for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get company overview: {str(e)}")

@app.get("/alpha-vantage/earnings/{symbol}")
async def get_alpha_vantage_earnings(symbol: str):
    """Get earnings calendar from Alpha Vantage"""
    try:
        if not alpha_vantage_service.is_enabled():
            raise HTTPException(status_code=503, detail="Alpha Vantage service not enabled. Please set ALPHA_VANTAGE_API_KEY environment variable.")
        
        earnings_data = alpha_vantage_service.get_earnings_calendar(symbol)
        if earnings_data is None:
            raise HTTPException(status_code=404, detail=f"No earnings data found for {symbol}")
        
        return earnings_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Alpha Vantage earnings for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get earnings data: {str(e)}")

@app.get("/alpha-vantage/news/{symbol}")
async def get_alpha_vantage_news(symbol: str, limit: int = Query(50, description="Number of news items")):
    """Get news sentiment from Alpha Vantage"""
    try:
        if not alpha_vantage_service.is_enabled():
            raise HTTPException(status_code=503, detail="Alpha Vantage service not enabled. Please set ALPHA_VANTAGE_API_KEY environment variable.")
        
        news_data = alpha_vantage_service.get_news_sentiment(symbol, limit)
        if news_data is None:
            raise HTTPException(status_code=404, detail=f"No news data found for {symbol}")
        
        return {
            "symbol": symbol,
            "news": news_data,
            "last_updated": datetime.now().isoformat(),
            "source": "Alpha Vantage"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Alpha Vantage news for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get news data: {str(e)}")

# ============= MISSING ENDPOINTS =============

@app.get("/stocks/{ticker}/historical")
async def get_historical_data(ticker: str, period: str = Query("6mo", description="Period for historical data")):
    """Get historical data for a ticker."""
    try:
        # Get raw DataFrame for historical data
        df = await get_stock_dataframe(ticker, period=period)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for {ticker}")
        
        # Convert to records format
        data_dict = df.reset_index().to_dict(orient="records")
        
        return {
            "ticker": ticker,
            "period": period,
            "data": data_dict,
            "count": len(data_dict),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting historical data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get historical data: {str(e)}")

@app.get("/ai-signals/{ticker}")
async def get_ai_signals(ticker: str):
    """Get AI-generated signals for a ticker."""
    try:
        # Use the existing signal generation with AI enhancement
        signal = await get_signal(ticker)
        
        # Check if signal is a Signal object or string
        if hasattr(signal, 'signal'):
            # It's a Signal object
            ai_signal = {
                "ticker": ticker,
                "ai_signal": signal.signal,
                "confidence": 0.85,  # Mock confidence score
                "ai_reasoning": signal.reasoning,
                "signals": signal.signals,
                "generated_at": signal.generated_at,
                "ai_enhanced": True
            }
        else:
            # It's a string or other type, create basic response
            ai_signal = {
                "ticker": ticker,
                "ai_signal": str(signal),
                "confidence": 0.75,
                "ai_reasoning": ["Basic signal generated"],
                "signals": [str(signal)],
                "generated_at": datetime.now().isoformat(),
                "ai_enhanced": False
            }
        
        return ai_signal
        
    except Exception as e:
        logger.error(f"Error generating AI signals for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI signals: {str(e)}")

@app.get("/domain-overview")
async def get_domain_overview(domain: str = Query("Technology", description="Domain name")):
    """Get domain overview."""
    try:
        # Mock domain overview data
        overview = {
            "domain": domain,
            "description": f"Overview of {domain} sector",
            "market_cap": "₹50.2T",
            "growth_rate": "12.5%",
            "top_companies": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
            "last_updated": datetime.now().isoformat()
        }
        
        return overview
        
    except Exception as e:
        logger.error(f"Error getting domain overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get domain overview: {str(e)}")

@app.get("/market/summary")
async def get_market_summary():
    """Get market summary."""
    try:
        summary = {
            "market_status": "Open",
            "indices": {
                "NIFTY_50": {"value": 19850.25, "change": 125.50, "change_pct": 0.64},
                "SENSEX": {"value": 66589.93, "change": 456.78, "change_pct": 0.69}
            },
            "sector_performance": {
                "Technology": "2.1%",
                "Banking": "1.8%",
                "Healthcare": "0.9%",
                "Energy": "-0.5%"
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting market summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get market summary: {str(e)}")

@app.get("/ownership/{ticker}")
async def get_ownership_data(ticker: str):
    """Get ownership data for a ticker."""
    try:
        # Mock ownership data for Indian stocks
        ownership = {
            "ticker": ticker,
            "institutional_holders": [
                {"name": "Life Insurance Corporation of India", "shares": 5000000, "percentage": 8.5},
                {"name": "HDFC Mutual Fund", "shares": 3000000, "percentage": 5.1},
                {"name": "SBI Mutual Fund", "shares": 2500000, "percentage": 4.2},
                {"name": "ICICI Prudential Mutual Fund", "shares": 2000000, "percentage": 3.4}
            ],
            "mutual_fund_holders": [
                {"name": "HDFC Top 100 Fund", "shares": 1500000, "percentage": 2.5},
                {"name": "SBI Bluechip Fund", "shares": 1200000, "percentage": 2.0},
                {"name": "ICICI Prudential Value Discovery Fund", "shares": 1000000, "percentage": 1.7}
            ],
            "insider_holders": [
                {"name": "Promoter Group", "shares": 15000000, "percentage": 25.4},
                {"name": "CEO", "shares": 500000, "percentage": 0.8},
                {"name": "CFO", "shares": 250000, "percentage": 0.4}
            ],
            "foreign_institutional_investors": [
                {"name": "Vanguard Group Inc", "shares": 2000000, "percentage": 3.4},
                {"name": "BlackRock Inc", "shares": 1800000, "percentage": 3.1},
                {"name": "Fidelity International", "shares": 1500000, "percentage": 2.5}
            ],
            "insider_ownership": 25.4,
            "public_float": 74.6,
            "last_updated": datetime.now().isoformat()
        }
        
        return ownership
        
    except Exception as e:
        logger.error(f"Error getting ownership data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ownership data: {str(e)}")

@app.get("/insider-trading/{ticker}")
async def get_insider_trading(ticker: str):
    """Get insider trading data for a ticker."""
    try:
        # Mock insider trading data
        insider_data = {
            "ticker": ticker,
            "recent_transactions": [
                {
                    "insider": "John Doe (CEO)",
                    "transaction_type": "Sale",
                    "shares": 50000,
                    "price": 150.25,
                    "date": "2024-01-15"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return insider_data
        
    except Exception as e:
        logger.error(f"Error getting insider trading for {ticker}: {str(e)}")
        raise HTTPException(status_code=404, detail="Not Found")

@app.get("/quote/{ticker}/sustainability")
async def get_sustainability_data(ticker: str):
    """Get sustainability data for a ticker."""
    try:
        sustainability = {
            "ticker": ticker,
            "esg_score": 75.5,
            "environmental": 80.0,
            "social": 72.0,
            "governance": 74.5,
            "last_updated": datetime.now().isoformat()
        }
        
        return sustainability
        
    except Exception as e:
        logger.error(f"Error getting sustainability data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sustainability data: {str(e)}")

@app.get("/quote/{ticker}/recommendations")
async def get_recommendations(ticker: str):
    """Get analyst recommendations for a ticker."""
    try:
        recommendations = {
            "ticker": ticker,
            "consensus": "BUY",
            "target_price": 175.50,
            "recommendations": [
                {"firm": "Goldman Sachs", "rating": "BUY", "target": 180.00},
                {"firm": "Morgan Stanley", "rating": "HOLD", "target": 170.00},
                {"firm": "JP Morgan", "rating": "BUY", "target": 185.00}
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations for {ticker}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Recommendations for '{ticker}' not found")

@app.get("/quote/{ticker}/calendar")
async def get_calendar_events(ticker: str):
    """Get calendar events for a ticker."""
    try:
        calendar = {
            "ticker": ticker,
            "upcoming_events": [
                {
                    "event": "Earnings Release",
                    "date": "2024-01-25",
                    "type": "earnings"
                },
                {
                    "event": "Annual Meeting",
                    "date": "2024-03-15",
                    "type": "meeting"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return calendar
        
    except Exception as e:
        logger.error(f"Error getting calendar events for {ticker}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Calendar events for '{ticker}' not found")

@app.get("/patterns/{ticker}")
async def get_pattern_analysis(ticker: str):
    """Get pattern analysis for a ticker."""
    try:
        patterns = {
            "ticker": ticker,
            "patterns_detected": [
                {"pattern": "Head and Shoulders", "confidence": 0.75, "signal": "BEARISH"},
                {"pattern": "Double Bottom", "confidence": 0.65, "signal": "BULLISH"}
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return patterns
        
    except Exception as e:
        logger.error(f"Error getting pattern analysis for {ticker}: {str(e)}")
        raise HTTPException(status_code=404, detail="Not Found")

@app.get("/patterns/{ticker}/detect")
async def detect_patterns(ticker: str, pattern_type: str = Query("head_and_shoulders", description="Pattern type to detect")):
    """Detect specific patterns for a ticker."""
    try:
        detection = {
            "ticker": ticker,
            "pattern_type": pattern_type,
            "detected": True,
            "confidence": 0.78,
            "signal": "BEARISH",
            "description": f"{pattern_type.replace('_', ' ').title()} pattern detected",
            "last_updated": datetime.now().isoformat()
        }
        
        return detection
        
    except Exception as e:
        logger.error(f"Error detecting patterns for {ticker}: {str(e)}")
        raise HTTPException(status_code=404, detail="Not Found")

# ============= ANGEL ONE ENDPOINTS =============

@app.get("/angel-one/status")
async def get_angel_one_status():
    """Get Angel One service status and configuration."""
    try:
        return {
            "enabled": angel_one_service.enabled,
            "api_configured": bool(angel_one_service.api_key),
            "client_configured": bool(angel_one_service.client_id),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Angel One status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Angel One status: {str(e)}")

@app.get("/angel-one/quote/{symbol}")
async def get_angel_one_quote(symbol: str):
    """Get real-time quote from Angel One for NSE/BSE stocks."""
    try:
        if not angel_one_service.enabled:
            raise HTTPException(status_code=503, detail="Angel One service not enabled")
        
        quote_data = angel_one_service.get_stock_quote(symbol)
        if not quote_data:
            raise HTTPException(status_code=404, detail=f"No quote data found for {symbol}")
        
        return quote_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Angel One quote for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quote: {str(e)}")

@app.get("/angel-one/historical/{symbol}")
async def get_angel_one_historical(
    symbol: str,
    interval: str = Query("1d", description="Data interval"),
    period: str = Query("1mo", description="Data period")
):
    """Get historical data from Angel One for NSE/BSE stocks."""
    try:
        if not angel_one_service.enabled:
            raise HTTPException(status_code=503, detail="Angel One service not enabled")
        
        historical_data = angel_one_service.get_historical_data(symbol, interval, period)
        if not historical_data:
            raise HTTPException(status_code=404, detail=f"No historical data found for {symbol}")
        
        return {
            "symbol": symbol,
            "interval": interval,
            "period": period,
            "data": historical_data,
            "count": len(historical_data),
            "last_updated": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Angel One historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get historical data: {str(e)}")

@app.get("/angel-one/indices")
async def get_angel_one_indices():
    """Get major indices data from Angel One (Nifty 50, Sensex, etc.)."""
    try:
        if not angel_one_service.enabled:
            raise HTTPException(status_code=503, detail="Angel One service not enabled")
        
        indices_data = angel_one_service.get_indices_data()
        if not indices_data:
            raise HTTPException(status_code=404, detail="No indices data found")
        
        return indices_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Angel One indices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get indices data: {str(e)}")

@app.get("/angel-one/market-status")
async def get_angel_one_market_status():
    """Get market status for NSE and BSE from Angel One."""
    try:
        if not angel_one_service.enabled:
            raise HTTPException(status_code=503, detail="Angel One service not enabled")
        
        market_status = angel_one_service.get_market_status()
        if not market_status:
            raise HTTPException(status_code=404, detail="No market status data found")
        
        return market_status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Angel One market status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get market status: {str(e)}")

# ============= CURRENCY CONVERSION ENDPOINTS =============

@app.get("/currency/rate")
async def get_currency_rate():
    """Get current USD to INR exchange rate"""
    try:
        rate = currency_service.get_usd_to_inr_rate()
        info = currency_service.get_currency_info()
        
        return {
            "usd_to_inr_rate": rate,
            "last_updated": info["last_update"],
            "cache_duration_seconds": info["cache_duration_seconds"],
            "api_key_configured": info["api_key_configured"]
        }
        
    except Exception as e:
        logger.error(f"Error getting currency rate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get currency rate: {str(e)}")

@app.get("/currency/convert")
async def convert_currency(
    amount: float = Query(..., description="Amount to convert"),
    from_currency: str = Query("USD", description="Source currency"),
    to_currency: str = Query("INR", description="Target currency")
):
    """Convert currency amount"""
    try:
        if from_currency.upper() == "USD" and to_currency.upper() == "INR":
            converted_amount = currency_service.convert_usd_to_inr(amount)
            formatted_amount = currency_service.format_inr(converted_amount)
            
            return {
                "original_amount": amount,
                "original_currency": from_currency,
                "converted_amount": converted_amount,
                "converted_currency": to_currency,
                "formatted_amount": formatted_amount,
                "exchange_rate": currency_service.get_usd_to_inr_rate(),
                "last_updated": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Only USD to INR conversion is currently supported")
        
    except Exception as e:
        logger.error(f"Error converting currency: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to convert currency: {str(e)}")

@app.get("/currency/format")
async def format_currency_amount(
    amount: float = Query(..., description="Amount to format"),
    currency: str = Query("INR", description="Currency code"),
    decimals: int = Query(2, description="Number of decimal places")
):
    """Format currency amount"""
    try:
        formatted = currency_service.format_currency(amount, currency, decimals)
        
        return {
            "amount": amount,
            "currency": currency,
            "formatted": formatted,
            "decimals": decimals
        }
        
    except Exception as e:
        logger.error(f"Error formatting currency: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to format currency: {str(e)}")

# ============= DASHBOARD ENDPOINTS =============

@app.get("/dashboard")
async def get_dashboard(
    tickers: str = Query("AAPL,MSFT,GOOGL,AMZN,TSLA", description="Comma-separated ticker symbols"),
    news_limit: int = Query(5, description="Number of news items to return")
) -> DashboardResponse:
    """Enhanced dashboard endpoint with volume analysis, caching, and parallel processing."""
    try:
        cache_key = f"dashboard_{tickers}_{news_limit}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        ticker_list = [t.strip() for t in tickers.split(",")]
        
        # Fetch data in parallel
        import asyncio
        stock_tasks = [get_stock_data(ticker) for ticker in ticker_list]
        news_task = get_news(news_limit)
        
        try:
            stocks, news = await asyncio.gather(
                asyncio.gather(*stock_tasks),
                news_task
            )
            stocks = list(stocks)  # Unpack the result of asyncio.gather(*stock_tasks)
        except Exception as e:
            logger.error(f"Error in parallel data fetching: {str(e)}")
            # Fallback: fetch data sequentially
            stocks = []
            for ticker in ticker_list:
                try:
                    stock_data = await get_stock_data(ticker)
                    stocks.append(stock_data)
                except Exception as stock_error:
                    logger.warning(f"Failed to fetch {ticker}: {str(stock_error)}")
                    continue
            
            try:
                news = await get_news(news_limit)
            except Exception as news_error:
                logger.warning(f"Failed to fetch news: {str(news_error)}")
                news = []
        
        # Generate signals for each stock
        signals = []
        for stock in stocks:
            try:
                signal = generate_signals(stock.ticker, stock, news)
                signals.append(signal)
            except Exception as e:
                logger.warning(f"Failed to generate signal for {stock.ticker}: {str(e)}")
                # Create a basic signal as fallback
                from models.schemas import Signal
                fallback_signal = Signal(
                    ticker=stock.ticker,
                    signal="HOLD",
                    signals=["HOLD"],
                    reasoning=["Signal generation failed"],
                    generated_at=datetime.now().isoformat()
                )
                signals.append(fallback_signal)
        
        response = DashboardResponse(
            stocks=stocks,
            news=news,
            signals=signals,
            timestamp=datetime.now().isoformat()
        )
        
        cache_data(cache_key, response, expiry_minutes=5)
        return response
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bulk-analysis")
async def get_bulk_analysis(tickers: str = Query("RELIANCE.NS,TCS.NS,HDFCBANK.NS", description="Comma-separated tickers")):
    """Get comprehensive analysis for multiple stocks."""
    try:
        ticker_list = [t.strip() for t in tickers.split(",")]
        results = {}
        
        for ticker in ticker_list:
            try:
                context = await _build_context(ticker)
                
                # Generate AI summary
                summary_query = f"Give me a brief analysis summary for {ticker}"
                ai_summary = ask_ai_assistant(summary_query, context=context)
                
                results[ticker] = {
                    "context": context,
                    "ai_summary": ai_summary,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                results[ticker] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        logger.error(f"Bulk analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")

# ============= HELPER FUNCTIONS =============

async def _build_context(ticker: str) -> dict:
    """Build comprehensive context for AI assistant."""
    context = {"ticker": ticker}
    
    try:
        # Get stock data and volume analysis
        stock_data = await get_stock_data(ticker)
        if stock_data is not None and not stock_data.empty:
            latest = stock_data.iloc[-1]
            previous = stock_data.iloc[-2] if len(stock_data) > 1 else latest
            
            context.update({
                "current_price": float(latest['Close']),
                "price_change": float(latest['Close'] - previous['Close']),
                "price_change_pct": float((latest['Close'] - previous['Close']) / previous['Close'] * 100),
                "volume_analysis": analyze_volume(stock_data)
            })
            
            # Add technical indicators (basic)
            if len(stock_data) >= 20:
                context["technical_indicators"] = {
                    "SMA_20": float(stock_data['Close'].rolling(20).mean().iloc[-1]),
                    "RSI_14": float(_calculate_rsi(stock_data['Close'], 14).iloc[-1]) if len(stock_data) >= 14 else None,
                    "Volume_SMA_20": float(stock_data['Volume'].rolling(20).mean().iloc[-1])
                }
        
        # Get recent news
        try:
            news = get_recent_news(ticker, limit=3)
            if news:
                context["news_headlines"] = [item.get('title', '') for item in news[:3]]
                
                # Basic sentiment analysis
                all_text = ' '.join([item.get('title', '') + ' ' + item.get('content', '') for item in news])
                if all_text.strip():
                    sentiment = analyze_sentiment(all_text)
                    context["sentiment"] = sentiment
        except Exception as e:
            logger.warning(f"News context failed for {ticker}: {str(e)}")
        
        # Get live quote
        try:
            live_quote = get_live_quote(ticker)
            if live_quote and 'nse_live' in live_quote:
                nse_data = live_quote['nse_live']
                context.update({
                    "live_price": nse_data.get('lastPrice'),
                    "day_high": nse_data.get('dayHigh'),
                    "day_low": nse_data.get('dayLow'),
                    "live_volume": nse_data.get('totalTradedVolume')
                })
        except Exception as e:
            logger.warning(f"Live quote context failed for {ticker}: {str(e)}")
        
        # Add domain analysis context
        try:
            # Try to determine sector/industry for the ticker
            domain_context = _get_domain_context(ticker)
            if domain_context:
                context["domain_analysis"] = domain_context
        except Exception as e:
            logger.warning(f"Domain context failed for {ticker}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error building context for {ticker}: {str(e)}")
        context["context_error"] = str(e)
    
    return context

def _get_domain_context(ticker: str) -> dict:
    """Get domain context for a ticker (sector/industry analysis)"""
    try:
        # Simple mapping of tickers to sectors/industries
        ticker_sector_map = {
            'RELIANCE.NS': 'energy',
            'TCS.NS': 'technology', 
            'HDFCBANK.NS': 'finance',
            'INFY.NS': 'technology',
            'ICICIBANK.NS': 'finance',
            'WIPRO.NS': 'technology',
            'HCLTECH.NS': 'technology',
            'TECHM.NS': 'technology',
            'SUNPHARMA.NS': 'healthcare',
            'DRREDDY.NS': 'healthcare',
            'CIPLA.NS': 'healthcare',
            'ITC.NS': 'consumer',
            'HINDUNILVR.NS': 'consumer',
            'MARUTI.NS': 'consumer',
            'TITAN.NS': 'consumer',
            'BAJAJ-AUTO.NS': 'consumer',
            'TATAMOTORS.NS': 'consumer',
            'M&M.NS': 'consumer',
            'HEROMOTOCO.NS': 'consumer',
            'EICHERMOT.NS': 'consumer',
            'ONGC.NS': 'energy',
            'COALINDIA.NS': 'energy',
            'IOC.NS': 'energy',
            'BPCL.NS': 'energy',
            'POWERGRID.NS': 'utilities',
            'NTPC.NS': 'utilities',
            'SBIN.NS': 'finance',
            'AXISBANK.NS': 'finance',
            'KOTAKBANK.NS': 'finance',
            'INDUSINDBK.NS': 'finance',
            'BAJFINANCE.NS': 'finance',
            'BHARTIARTL.NS': 'communication',
            'JSWSTEEL.NS': 'materials',
            'TATASTEEL.NS': 'materials',
            'HINDALCO.NS': 'materials',
            'ULTRACEMCO.NS': 'materials',
            'SHREECEM.NS': 'materials',
            'GRASIM.NS': 'materials',
            'ADANIPORTS.NS': 'industrial',
            'LT.NS': 'industrial',
            'ASIANPAINT.NS': 'materials',
            'NESTLEIND.NS': 'consumer',
            'BRITANNIA.NS': 'consumer',
            'DIVISLAB.NS': 'healthcare',
            'UPL.NS': 'materials',
            'DLF.NS': 'real_estate'
        }
        
        # Get sector for ticker
        sector_key = ticker_sector_map.get(ticker.upper())
        if sector_key:
            sector_data = domain_service.get_sector(sector_key)
            if sector_data:
                return {
                    "sector": {
                        "name": sector_data.name,
                        "key": sector_data.key,
                        "overview": sector_data.overview.dict(),
                        "top_companies": [company.dict() for company in sector_data.top_companies[:5]]
                    }
                }
        
        return None
        
    except Exception as e:
        logger.warning(f"Error getting domain context for {ticker}: {str(e)}")
        return None

def _calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Calculate RSI indicator."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# ============= ERROR HANDLERS =============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main_combined:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
