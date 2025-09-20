# Updated main.py - Enhanced FastAPI Application

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import services
from services.market_data import get_stock_data
from services.news_scraper import NewsItem
from services.sentiment_analysis import analyze_sentiment

# Import new pipelines
from pipelines.assistant import ask_ai_assistant, QueryTemplates
from pipelines.volume_analysis import analyze_volume, compute_volume_signal
from pipelines.live_data import get_live_quote, get_popular_stocks_data
from pipelines.news import get_recent_news

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    logger.info("🚀 Starting Financial Dashboard API with AI Assistant")
    yield
    logger.info("⏹️ Shutting down Financial Dashboard API")

# Initialize FastAPI app
app = FastAPI(
    title="Financial Dashboard with AI Assistant",
    description="Intelligent stock market analysis dashboard with AI-powered insights",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= EXISTING ENDPOINTS (Enhanced) =============

@app.get("/dashboard")
async def get_dashboard_data(tickers: str = Query(..., description="Comma-separated ticker symbols")):
    """Enhanced dashboard endpoint with volume analysis."""
    try:
        ticker_list = [t.strip() for t in tickers.split(",")]
        dashboard_data = {}
        
        for ticker in ticker_list:
            try:
                # Get stock data
                stock_data = get_stock_data(ticker)
                if stock_data is None:
                    continue
                
                # Add volume analysis
                volume_analysis = analyze_volume(stock_data)
                
                # Get live quote if available
                live_quote = get_live_quote(ticker)
                
                dashboard_data[ticker] = {
                    "stock_data": stock_data.tail(50).to_dict(orient="records") if hasattr(stock_data, 'tail') else stock_data,
                    "volume_analysis": volume_analysis,
                    "live_quote": live_quote,
                    "last_updated": live_quote.get("timestamp")
                }
                
            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)}")
                dashboard_data[ticker] = {"error": str(e)}
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard data error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")

@app.get("/news")
async def get_news(limit: int = Query(5, description="Number of news items to return")):
    """Enhanced news endpoint with sentiment analysis."""
    try:
        news_items = get_recent_news(limit=limit)
        
        # Add sentiment analysis to each news item
        for item in news_items:
            if isinstance(item, dict) and 'content' in item:
                sentiment = analyze_sentiment(item.get('content', '') + ' ' + item.get('title', ''))
                item['sentiment_analysis'] = sentiment
        
        return {"news": news_items, "count": len(news_items)}
        
    except Exception as e:
        logger.error(f"News error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

# ============= NEW AI ASSISTANT ENDPOINTS =============

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
            "timestamp": pd.Timestamp.now().isoformat()
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

# ============= LIVE DATA ENDPOINTS =============

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

# ============= VOLUME ANALYSIS ENDPOINTS =============

@app.get("/volume-analysis/{ticker}")
async def get_volume_analysis(ticker: str):
    """Get detailed volume analysis for a stock."""
    try:
        stock_data = get_stock_data(ticker)
        if stock_data is None:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        volume_analysis = analyze_volume(stock_data)
        volume_signal = compute_volume_signal(stock_data)
        
        return {
            "ticker": ticker,
            "volume_analysis": volume_analysis,
            "volume_signal": volume_signal,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Volume analysis error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Volume analysis failed: {str(e)}")

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
                    "timestamp": pd.Timestamp.now().isoformat()
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
    import pandas as pd
    
    context = {"ticker": ticker}
    
    try:
        # Get stock data and volume analysis
        stock_data = get_stock_data(ticker)
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
        news = get_recent_news(ticker, limit=3)
        if news:
            context["news_headlines"] = [item.get('title', '') for item in news[:3]]
            
            # Basic sentiment analysis
            all_text = ' '.join([item.get('title', '') + ' ' + item.get('content', '') for item in news])
            if all_text.strip():
                sentiment = analyze_sentiment(all_text)
                context["sentiment"] = sentiment
        
        # Get live quote
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
        logger.error(f"Error building context for {ticker}: {str(e)}")
        context["context_error"] = str(e)
    
    return context

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

# ============= HEALTH CHECK =============

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": pd.Timestamp.now().isoformat(),
        "version": "2.0.0",
        "features": ["AI Assistant", "Volume Analysis", "Live Data", "Sentiment Analysis"]
    }

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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )