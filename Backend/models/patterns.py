from pydantic import BaseModel
from typing import List, Optional

class PatternRequest(BaseModel):
    patterns: List[str]
    timeframe: str = "1d"
    limit: int = 100

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
