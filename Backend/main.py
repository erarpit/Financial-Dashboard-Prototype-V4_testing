from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from services.market_data import get_stock_data, get_historical_data
from services.news_scraper import get_financial_news
from services.sentiment_analysis import analyze_sentiment
from services.signals import generate_signals
from models.database import init_db, get_cached_data, cache_data
from models.schemas import StockData, NewsItem, Signal, DashboardResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Financial Dashboard API")
    init_db()
    yield
    # Shutdown
    logger.info("Shutting down Financial Dashboard API")

# Initialize app
app = FastAPI(
    title="Financial Dashboard API",
    version="1.0.0",
    description="Advanced trading analysis API with sentiment analysis and technical indicators",
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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Financial Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/stocks/{ticker}")
async def get_stock(
    ticker: str, 
    period: str = "6mo", 
    interval: str = "1d"
) -> StockData:
    """Get stock data for a specific ticker"""
    try:
        # Check cache first
        cache_key = f"stock_{ticker}_{period}_{interval}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch fresh data
        data = await get_stock_data(ticker, period, interval)
        cache_data(cache_key, data, expiry_minutes=5)
        return data
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news")
async def get_news(limit: int = 10) -> List[NewsItem]:
    """Get financial news"""
    try:
        cache_key = f"news_{limit}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        news = await get_financial_news(limit)
        cache_data(cache_key, news, expiry_minutes=15)
        return news
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/{ticker}")
async def get_signal(ticker: str) -> Signal:
    """Get trading signals for a ticker"""
    try:
        cache_key = f"signal_{ticker}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Get stock data and news for analysis
        stock_data = await get_stock_data(ticker)
        news = await get_financial_news(5)
        
        # Generate signals
        signal = generate_signals(ticker, stock_data, news)
        cache_data(cache_key, signal, expiry_minutes=10)
        return signal
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def get_dashboard(
    tickers: str = Query("AAPL,MSFT,GOOGL,AMZN,TSLA"),
    news_limit: int = 5
) -> DashboardResponse:
    """Get all data for dashboard in a single call"""
    try:
        cache_key = f"dashboard_{tickers}_{news_limit}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        ticker_list = [t.strip() for t in tickers.split(",")]
        
        # Fetch data in parallel
        import asyncio
        stock_tasks = [get_stock_data(ticker) for ticker in ticker_list]
        news_task = get_financial_news(news_limit)
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
                news = await get_financial_news(news_limit)
            except Exception as news_error:
                logger.warning(f"Failed to fetch news: {str(news_error)}")
                news = []
        
        # Generate signals for each stock
        signals = []
        for stock in stocks:
            signal = generate_signals(stock.ticker, stock, news)
            signals.append(signal)
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
