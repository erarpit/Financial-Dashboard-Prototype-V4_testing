from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
from pydantic import BaseModel
from models.patterns import PatternRequest, PatternAnalysis

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/patterns", tags=["patterns"])

# Mock pattern service for now
class MockPatternService:
    def get_all_patterns(self):
        return ["DOJI", "HAMMER", "SHOOTING_STAR", "ENGULFING", "HARAMI"]
    
    async def get_ohlc_data(self, ticker: str, timeframe: str, limit: int):
        return {"ticker": ticker, "timeframe": timeframe, "limit": limit}
    
    def detect_patterns(self, ohlc_data, patterns):
        return []

pattern_service = MockPatternService()

@router.get("/available")
async def get_available_patterns():
    """Get list of all 61 available candlestick patterns"""
    try:
        return pattern_service.get_all_patterns()
    except Exception as e:
        logger.error(f"Error getting available patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/{ticker}")
async def detect_patterns(ticker: str, request: PatternRequest):
    """Detect specified patterns for a ticker"""
    try:
        # Get OHLC data
        ohlc_data = await pattern_service.get_ohlc_data(ticker, request.timeframe, request.limit)
        
        # Detect patterns
        detections = pattern_service.detect_patterns(ohlc_data, request.patterns)
        
        # Format response
        analysis = PatternAnalysis(
            ticker=ticker.upper(),
            timeframe=request.timeframe,
            detections=detections,
            total_patterns=len([d for d in detections if d.value != 0]),
            bullish_count=len([d for d in detections if d.value > 0]),
            bearish_count=len([d for d in detections if d.value < 0])
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error detecting patterns for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/ohlc")
async def get_ohlc_data(ticker: str, timeframe: str = "1d", limit: int = 100):
    """Get OHLC candlestick data for charts"""
    try:
        data = await pattern_service.get_ohlc_data(ticker, timeframe, limit)
        return data
    except Exception as e:
        logger.error(f"Error getting OHLC data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
