import talib
import numpy as np
import pandas as pd
from typing import Dict, List, Any
import yfinance as yf
from datetime import datetime
import logging
from models.patterns import PatternDetection, CandlestickPattern

logger = logging.getLogger(__name__)

class PatternDetectionService:
    def __init__(self):
        self.patterns_info = self._load_patterns_info()
    
    def _load_patterns_info(self) -> List[CandlestickPattern]:
        """Load all 61 candlestick patterns information"""
        return [
            CandlestickPattern(
                name="Two Crows", function_name="CDL2CROWS", 
                description="Two Crows pattern", category="complex", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Three Black Crows", function_name="CDL3BLACKCROWS",
                description="Three Black Crows pattern", category="triple", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Three Inside Up/Down", function_name="CDL3INSIDE",
                description="Three Inside Up/Down pattern", category="triple", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Three-Line Strike", function_name="CDL3LINESTRIKE",
                description="Three-Line Strike pattern", category="triple", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Three Outside Up/Down", function_name="CDL3OUTSIDE",
                description="Three Outside Up/Down pattern", category="triple", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Three Stars In The South", function_name="CDL3STARSINSOUTH",
                description="Three Stars In The South pattern", category="triple", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Three Advancing White Soldiers", function_name="CDL3WHITESOLDIERS",
                description="Three Advancing White Soldiers pattern", category="triple", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Abandoned Baby", function_name="CDLABANDONEDBABY",
                description="Abandoned Baby pattern", category="triple", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Advance Block", function_name="CDLADVANCEBLOCK",
                description="Advance Block pattern", category="triple", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Belt-hold", function_name="CDLBELTHOLD",
                description="Belt-hold pattern", category="single", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Breakaway", function_name="CDLBREAKAWAY",
                description="Breakaway pattern", category="complex", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Closing Marubozu", function_name="CDLCLOSINGMARUBOZU",
                description="Closing Marubozu pattern", category="single", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Concealing Baby Swallow", function_name="CDLCONCEALBABYSWALL",
                description="Concealing Baby Swallow pattern", category="complex", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Counterattack", function_name="CDLCOUNTERATTACK",
                description="Counterattack pattern", category="double", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Dark Cloud Cover", function_name="CDLDARKCLOUDCOVER",
                description="Dark Cloud Cover pattern", category="double", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Doji", function_name="CDLDOJI",
                description="Doji pattern indicates indecision", category="single", bullish=False, bearish=False
            ),
            CandlestickPattern(
                name="Doji Star", function_name="CDLDOJISTAR",
                description="Doji Star pattern", category="double", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Dragonfly Doji", function_name="CDLDRAGONFLYDOJI",
                description="Dragonfly Doji pattern", category="single", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Engulfing Pattern", function_name="CDLENGULFING",
                description="Engulfing pattern indicates reversal", category="double", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Evening Doji Star", function_name="CDLEVENINGDOJISTAR",
                description="Evening Doji Star pattern", category="triple", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Evening Star", function_name="CDLEVENINGSTAR",
                description="Evening Star pattern", category="triple", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Up/Down-gap side-by-side white lines", function_name="CDLGAPSIDESIDEWHITE",
                description="Up/Down-gap side-by-side white lines", category="complex", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Gravestone Doji", function_name="CDLGRAVESTONEDOJI",
                description="Gravestone Doji pattern", category="single", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Hammer", function_name="CDLHAMMER",
                description="Hammer pattern", category="single", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Hanging Man", function_name="CDLHANGINGMAN",
                description="Hanging Man pattern", category="single", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Harami Pattern", function_name="CDLHARAMI",
                description="Harami Pattern", category="double", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Harami Cross Pattern", function_name="CDLHARAMICROSS",
                description="Harami Cross Pattern", category="double", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="High-Wave Candle", function_name="CDLHIGHWAVE",
                description="High-Wave Candle pattern", category="single", bullish=False, bearish=False
            ),
            CandlestickPattern(
                name="Hikkake Pattern", function_name="CDLHIKKAKE",
                description="Hikkake Pattern", category="complex", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Modified Hikkake Pattern", function_name="CDLHIKKAKEMOD",
                description="Modified Hikkake Pattern", category="complex", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Homing Pigeon", function_name="CDLHOMINGPIGEON",
                description="Homing Pigeon pattern", category="double", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Identical Three Crows", function_name="CDLIDENTICAL3CROWS",
                description="Identical Three Crows pattern", category="triple", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="In-Neck Pattern", function_name="CDLINNECK",
                description="In-Neck Pattern", category="double", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Inverted Hammer", function_name="CDLINVERTEDHAMMER",
                description="Inverted Hammer pattern", category="single", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Kicking", function_name="CDLKICKING",
                description="Kicking pattern", category="double", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Kicking - bull/bear determined by the longer marubozu", function_name="CDLKICKINGBYLENGTH",
                description="Kicking by length pattern", category="double", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Ladder Bottom", function_name="CDLLADDERBOTTOM",
                description="Ladder Bottom pattern", category="complex", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Long Legged Doji", function_name="CDLLONGLEGGEDDOJI",
                description="Long Legged Doji pattern", category="single", bullish=False, bearish=False
            ),
            CandlestickPattern(
                name="Long Line Candle", function_name="CDLLONGLINE",
                description="Long Line Candle pattern", category="single", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Marubozu", function_name="CDLMARUBOZU",
                description="Marubozu pattern", category="single", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Matching Low", function_name="CDLMATCHINGLOW",
                description="Matching Low pattern", category="double", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Mat Hold", function_name="CDLMATHOLD",
                description="Mat Hold pattern", category="complex", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Morning Doji Star", function_name="CDLMORNINGDOJISTAR",
                description="Morning Doji Star pattern", category="triple", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Morning Star", function_name="CDLMORNINGSTAR",
                description="Morning Star pattern", category="triple", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="On-Neck Pattern", function_name="CDLONNECK",
                description="On-Neck Pattern", category="double", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Piercing Pattern", function_name="CDLPIERCING",
                description="Piercing Pattern", category="double", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Rickshaw Man", function_name="CDLRICKSHAWMAN",
                description="Rickshaw Man pattern", category="single", bullish=False, bearish=False
            ),
            CandlestickPattern(
                name="Rising/Falling Three Methods", function_name="CDLRISEFALL3METHODS",
                description="Rising/Falling Three Methods pattern", category="complex", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Separating Lines", function_name="CDLSEPARATINGLINES",
                description="Separating Lines pattern", category="double", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Shooting Star", function_name="CDLSHOOTINGSTAR",
                description="Shooting Star pattern", category="single", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Short Line Candle", function_name="CDLSHORTLINE",
                description="Short Line Candle pattern", category="single", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Spinning Top", function_name="CDLSPINNINGTOP",
                description="Spinning Top pattern", category="single", bullish=False, bearish=False
            ),
            CandlestickPattern(
                name="Stalled Pattern", function_name="CDLSTALLEDPATTERN",
                description="Stalled Pattern", category="triple", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Stick Sandwich", function_name="CDLSTICKSANDWICH",
                description="Stick Sandwich pattern", category="triple", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Takuri (Dragonfly Doji with very long lower shadow)", function_name="CDLTAKURI",
                description="Takuri pattern", category="single", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Tasuki Gap", function_name="CDLTASUKIGAP",
                description="Tasuki Gap pattern", category="triple", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Thrusting Pattern", function_name="CDLTHRUSTING",
                description="Thrusting Pattern", category="double", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Tristar Pattern", function_name="CDLTRISTAR",
                description="Tristar Pattern", category="triple", bullish=True, bearish=True
            ),
            CandlestickPattern(
                name="Unique 3 River", function_name="CDLUNIQUE3RIVER",
                description="Unique 3 River pattern", category="triple", bullish=True, bearish=False
            ),
            CandlestickPattern(
                name="Upside Gap Two Crows", function_name="CDLUPSIDEGAP2CROWS",
                description="Upside Gap Two Crows pattern", category="triple", bullish=False, bearish=True
            ),
            CandlestickPattern(
                name="Upside/Downside Gap Three Methods", function_name="CDLXSIDEGAP3METHODS",
                description="Upside/Downside Gap Three Methods pattern", category="complex", bullish=True, bearish=True
            )
        ]
    
    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """Return all available patterns"""
        return [pattern.dict() for pattern in self.patterns_info]
    
    async def get_ohlc_data(self, ticker: str, timeframe: str = "1d", limit: int = 100) -> Dict[str, Any]:
        """Get OHLC data for pattern detection"""
        try:
            # Use existing yfinance logic from market_data.py
            df = yf.download(ticker, period="6mo", interval=timeframe, progress=False)
            
            if df.empty:
                raise ValueError(f"No data found for {ticker}")
            
            # Take last 'limit' rows
            df = df.tail(limit)
            
            return {
                "ticker": ticker,
                "timeframe": timeframe,
                "timestamps": df.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
                "open": df['Open'].values.tolist(),
                "high": df['High'].values.tolist(),
                "low": df['Low'].values.tolist(),
                "close": df['Close'].values.tolist(),
                "volume": df['Volume'].values.tolist()
            }
        except Exception as e:
            logger.error(f"Error getting OHLC data: {str(e)}")
            raise
    
    def detect_patterns(self, ohlc_data: Dict[str, Any], selected_patterns: List[str]) -> List[PatternDetection]:
        """Detect specified patterns in OHLC data"""
        try:
            # Convert to numpy arrays
            open_prices = np.array(ohlc_data['open'])
            high_prices = np.array(ohlc_data['high'])
            low_prices = np.array(ohlc_data['low'])
            close_prices = np.array(ohlc_data['close'])
            timestamps = ohlc_data['timestamps']
            
            detections = []
            
            for pattern_name in selected_patterns:
                try:
                    # Get TA-Lib function
                    pattern_func = getattr(talib, pattern_name, None)
                    if not pattern_func:
                        logger.warning(f"Pattern {pattern_name} not found in TA-Lib")
                        continue
                    
                    # Detect pattern
                    result = pattern_func(open_prices, high_prices, low_prices, close_prices)
                    
                    # Convert results to PatternDetection objects
                    for i, value in enumerate(result):
                        if value != 0:  # Only store detected patterns
                            detection = PatternDetection(
                                pattern_name=pattern_name,
                                ticker=ohlc_data['ticker'],
                                timestamp=timestamps[i],
                                value=int(value),
                                confidence=abs(value) / 100.0,
                                candle_index=i
                            )
                            detections.append(detection)
                
                except Exception as e:
                    logger.error(f"Error detecting pattern {pattern_name}: {str(e)}")
                    continue
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in pattern detection: {str(e)}")
            return []