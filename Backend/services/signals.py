from datetime import datetime
from models.schemas import Signal, AISignal, TechnicalIndicators, VolumeAnalysis, PriceMomentum, MarketSentiment
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def generate_signals(ticker: str, stock_data, news: List) -> Signal:
    """Generate trading signals based on technical analysis and news sentiment"""
    
    # Technical analysis signals
    signals = []
    reasoning = []
    
    # RSI-based signal (with NaN handling)
    rsi = getattr(stock_data, 'rsi', 50)
    if not isinstance(rsi, (int, float)) or pd.isna(rsi):
        rsi = 50
        reasoning.append("RSI data unavailable, using neutral value")
    
    if rsi > 70:
        signals.append("OVERBOUGHT")
        reasoning.append("RSI indicates overbought conditions")
    elif rsi < 30:
        signals.append("OVERSOLD")
        reasoning.append("RSI indicates oversold conditions")
    
    # Trend-based signal
    trend = getattr(stock_data, 'trend', 'NEUTRAL')
    if trend == "BULLISH":
        signals.append("BULLISH_TREND")
        reasoning.append("Price above 20-day EMA indicates bullish trend")
    elif trend == "BEARISH":
        signals.append("BEARISH_TREND")
        reasoning.append("Price below 20-day EMA indicates bearish trend")
    
    # MACD signal (with NaN handling)
    macd = getattr(stock_data, 'macd', 0)
    macd_signal = getattr(stock_data, 'macd_signal', 0)
    
    if not isinstance(macd, (int, float)) or pd.isna(macd):
        macd = 0
    if not isinstance(macd_signal, (int, float)) or pd.isna(macd_signal):
        macd_signal = 0
    
    if macd > macd_signal:
        signals.append("MACD_BULLISH")
        reasoning.append("MACD line above signal line")
    else:
        signals.append("MACD_BEARISH")
        reasoning.append("MACD line below signal line")
    
    # News sentiment analysis
    positive_news = sum(1 for item in news if item.sentiment == "POSITIVE")
    negative_news = sum(1 for item in news if item.sentiment == "NEGATIVE")
    
    if positive_news > negative_news:
        signals.append("POSITIVE_NEWS")
        reasoning.append(f"More positive news ({positive_news} positive vs {negative_news} negative)")
    elif negative_news > positive_news:
        signals.append("NEGATIVE_NEWS")
        reasoning.append(f"More negative news ({negative_news} negative vs {positive_news} positive)")
    
    # Generate final signal
    if "OVERSOLD" in signals and "BULLISH_TREND" in signals and "POSITIVE_NEWS" in signals:
        final_signal = "STRONG_BUY"
    elif "OVERBOUGHT" in signals and "BEARISH_TREND" in signals and "NEGATIVE_NEWS" in signals:
        final_signal = "STRONG_SELL"
    elif "BULLISH_TREND" in signals and "POSITIVE_NEWS" in signals:
        final_signal = "BUY"
    elif "BEARISH_TREND" in signals and "NEGATIVE_NEWS" in signals:
        final_signal = "SELL"
    else:
        final_signal = "HOLD"
        reasoning.append("Mixed signals - recommend holding")
    
    return Signal(
        ticker=ticker,
        signal=final_signal,
        signals=signals,
        reasoning=reasoning,
        generated_at=datetime.now().isoformat()
    )

def generate_ai_signals(
    ticker: str, 
    technical_indicators: Optional[TechnicalIndicators] = None,
    volume_analysis: Optional[VolumeAnalysis] = None,
    price_momentum: Optional[PriceMomentum] = None,
    market_sentiment: Optional[MarketSentiment] = None,
    news_analysis: Optional[List[Dict[str, Any]]] = None
) -> List[AISignal]:
    """Generate AI-powered trading signals with confidence scores"""
    
    ai_signals = []
    current_time = datetime.now().isoformat()
    
    try:
        # Technical Analysis Signal
        if technical_indicators:
            tech_signal = _generate_technical_signal(ticker, technical_indicators, current_time)
            if tech_signal:
                ai_signals.append(tech_signal)
        
        # Volume Analysis Signal
        if volume_analysis:
            volume_signal = _generate_volume_signal(ticker, volume_analysis, current_time)
            if volume_signal:
                ai_signals.append(volume_signal)
        
        # Price Momentum Signal
        if price_momentum:
            momentum_signal = _generate_momentum_signal(ticker, price_momentum, current_time)
            if momentum_signal:
                ai_signals.append(momentum_signal)
        
        # Sentiment Analysis Signal
        if market_sentiment:
            sentiment_signal = _generate_sentiment_signal(ticker, market_sentiment, current_time)
            if sentiment_signal:
                ai_signals.append(sentiment_signal)
        
        # News Impact Signal
        if news_analysis:
            news_signal = _generate_news_signal(ticker, news_analysis, current_time)
            if news_signal:
                ai_signals.append(news_signal)
        
        # Overall AI Signal (weighted combination)
        if ai_signals:
            overall_signal = _generate_overall_ai_signal(ticker, ai_signals, current_time)
            ai_signals.append(overall_signal)
        
    except Exception as e:
        logger.error(f"Error generating AI signals for {ticker}: {str(e)}")
        # Return a neutral signal on error
        ai_signals.append(AISignal(
            signal_type="HOLD",
            confidence=0.0,
            reasoning=[f"Error in signal generation: {str(e)}"],
            generated_at=current_time
        ))
    
    return ai_signals

def _generate_technical_signal(ticker: str, indicators: TechnicalIndicators, timestamp: str) -> Optional[AISignal]:
    """Generate signal based on technical indicators"""
    reasoning = []
    technical_score = 0.0
    signal_type = "HOLD"
    
    # RSI Analysis
    if indicators.rsi_14 is not None:
        if indicators.rsi_14 > 80:
            reasoning.append(f"RSI extremely overbought at {indicators.rsi_14:.1f}")
            technical_score -= 0.3
        elif indicators.rsi_14 > 70:
            reasoning.append(f"RSI overbought at {indicators.rsi_14:.1f}")
            technical_score -= 0.2
        elif indicators.rsi_14 < 20:
            reasoning.append(f"RSI extremely oversold at {indicators.rsi_14:.1f}")
            technical_score += 0.3
        elif indicators.rsi_14 < 30:
            reasoning.append(f"RSI oversold at {indicators.rsi_14:.1f}")
            technical_score += 0.2
    
    # MACD Analysis
    if indicators.macd is not None and indicators.macd_signal is not None:
        if indicators.macd > indicators.macd_signal:
            reasoning.append("MACD bullish crossover")
            technical_score += 0.2
        else:
            reasoning.append("MACD bearish crossover")
            technical_score -= 0.2
    
    # Bollinger Bands Analysis
    if all(x is not None for x in [indicators.bollinger_upper, indicators.bollinger_middle, indicators.bollinger_lower]):
        if hasattr(indicators, 'current_price'):
            price = indicators.current_price
            bb_position = (price - indicators.bollinger_lower) / (indicators.bollinger_upper - indicators.bollinger_lower)
            if bb_position > 0.8:
                reasoning.append("Price near upper Bollinger Band")
                technical_score -= 0.1
            elif bb_position < 0.2:
                reasoning.append("Price near lower Bollinger Band")
                technical_score += 0.1
    
    # Moving Averages Analysis
    if indicators.sma_20 is not None and indicators.sma_50 is not None:
        if indicators.sma_20 > indicators.sma_50:
            reasoning.append("SMA 20 above SMA 50 - bullish trend")
            technical_score += 0.15
        else:
            reasoning.append("SMA 20 below SMA 50 - bearish trend")
            technical_score -= 0.15
    
    # Determine signal type based on technical score
    if technical_score >= 0.4:
        signal_type = "STRONG_BUY"
    elif technical_score >= 0.2:
        signal_type = "BUY"
    elif technical_score <= -0.4:
        signal_type = "STRONG_SELL"
    elif technical_score <= -0.2:
        signal_type = "SELL"
    else:
        signal_type = "HOLD"
        reasoning.append("Technical indicators show mixed signals")
    
    confidence = min(abs(technical_score) * 2, 1.0)
    
    return AISignal(
        signal_type=signal_type,
        confidence=confidence,
        reasoning=reasoning,
        technical_score=technical_score,
        generated_at=timestamp
    )

def _generate_volume_signal(ticker: str, volume: VolumeAnalysis, timestamp: str) -> Optional[AISignal]:
    """Generate signal based on volume analysis"""
    reasoning = []
    volume_score = 0.0
    signal_type = "HOLD"
    
    # Volume ratio analysis
    if volume.volume_ratio is not None:
        if volume.volume_ratio > 2.0:
            reasoning.append(f"Volume spike detected: {volume.volume_ratio:.1f}x average")
            volume_score += 0.3
        elif volume.volume_ratio > 1.5:
            reasoning.append(f"High volume: {volume.volume_ratio:.1f}x average")
            volume_score += 0.2
        elif volume.volume_ratio < 0.5:
            reasoning.append(f"Low volume: {volume.volume_ratio:.1f}x average")
            volume_score -= 0.1
    
    # Volume trend analysis
    if volume.volume_trend is not None:
        if volume.volume_trend == "increasing":
            reasoning.append("Volume trend is increasing")
            volume_score += 0.1
        elif volume.volume_trend == "decreasing":
            reasoning.append("Volume trend is decreasing")
            volume_score -= 0.1
    
    # Volume spike detection
    if volume.volume_spike is not None and volume.volume_spike:
        reasoning.append("Significant volume spike detected")
        volume_score += 0.2
    
    # Determine signal type
    if volume_score >= 0.3:
        signal_type = "BUY"  # High volume often precedes price movement
    elif volume_score <= -0.2:
        signal_type = "SELL"
    else:
        signal_type = "HOLD"
        reasoning.append("Volume analysis shows neutral conditions")
    
    confidence = min(abs(volume_score) * 2, 1.0)
    
    return AISignal(
        signal_type=signal_type,
        confidence=confidence,
        reasoning=reasoning,
        volume_score=volume_score,
        generated_at=timestamp
    )

def _generate_momentum_signal(ticker: str, momentum: PriceMomentum, timestamp: str) -> Optional[AISignal]:
    """Generate signal based on price momentum"""
    reasoning = []
    momentum_score = 0.0
    signal_type = "HOLD"
    
    # Daily price change analysis
    if momentum.price_change_pct_1d is not None:
        if momentum.price_change_pct_1d > 5.0:
            reasoning.append(f"Strong positive momentum: +{momentum.price_change_pct_1d:.1f}%")
            momentum_score += 0.3
        elif momentum.price_change_pct_1d > 2.0:
            reasoning.append(f"Positive momentum: +{momentum.price_change_pct_1d:.1f}%")
            momentum_score += 0.2
        elif momentum.price_change_pct_1d < -5.0:
            reasoning.append(f"Strong negative momentum: {momentum.price_change_pct_1d:.1f}%")
            momentum_score -= 0.3
        elif momentum.price_change_pct_1d < -2.0:
            reasoning.append(f"Negative momentum: {momentum.price_change_pct_1d:.1f}%")
            momentum_score -= 0.2
    
    # 5-day momentum analysis
    if momentum.price_change_pct_5d is not None:
        if momentum.price_change_pct_5d > 10.0:
            reasoning.append(f"Strong 5-day momentum: +{momentum.price_change_pct_5d:.1f}%")
            momentum_score += 0.2
        elif momentum.price_change_pct_5d < -10.0:
            reasoning.append(f"Strong 5-day decline: {momentum.price_change_pct_5d:.1f}%")
            momentum_score -= 0.2
    
    # 52-week high/low analysis
    if momentum.high_52w is not None and momentum.current_price is not None:
        distance_from_high = (momentum.current_price - momentum.high_52w) / momentum.high_52w
        if distance_from_high > -0.05:  # Within 5% of 52-week high
            reasoning.append("Near 52-week high")
            momentum_score += 0.1
        elif distance_from_high < -0.3:  # More than 30% below 52-week high
            reasoning.append("Significantly below 52-week high")
            momentum_score -= 0.1
    
    # Determine signal type
    if momentum_score >= 0.4:
        signal_type = "STRONG_BUY"
    elif momentum_score >= 0.2:
        signal_type = "BUY"
    elif momentum_score <= -0.4:
        signal_type = "STRONG_SELL"
    elif momentum_score <= -0.2:
        signal_type = "SELL"
    else:
        signal_type = "HOLD"
        reasoning.append("Price momentum shows mixed signals")
    
    confidence = min(abs(momentum_score) * 2, 1.0)
    
    return AISignal(
        signal_type=signal_type,
        confidence=confidence,
        reasoning=reasoning,
        generated_at=timestamp
    )

def _generate_sentiment_signal(ticker: str, sentiment: MarketSentiment, timestamp: str) -> Optional[AISignal]:
    """Generate signal based on market sentiment"""
    reasoning = []
    sentiment_score = sentiment.sentiment_score
    signal_type = "HOLD"
    
    # Sentiment score analysis
    if sentiment_score > 0.5:
        reasoning.append(f"Strong positive sentiment: {sentiment_score:.2f}")
        sentiment_score = 0.3
    elif sentiment_score > 0.2:
        reasoning.append(f"Positive sentiment: {sentiment_score:.2f}")
        sentiment_score = 0.2
    elif sentiment_score < -0.5:
        reasoning.append(f"Strong negative sentiment: {sentiment_score:.2f}")
        sentiment_score = -0.3
    elif sentiment_score < -0.2:
        reasoning.append(f"Negative sentiment: {sentiment_score:.2f}")
        sentiment_score = -0.2
    
    # News count analysis
    if sentiment.news_count > 10:
        reasoning.append(f"High news activity: {sentiment.news_count} articles")
        sentiment_score *= 1.2  # Amplify signal with more news
    elif sentiment.news_count < 3:
        reasoning.append(f"Low news activity: {sentiment.news_count} articles")
        sentiment_score *= 0.8  # Reduce signal with less news
    
    # Confidence adjustment
    if sentiment.confidence > 0.8:
        reasoning.append(f"High confidence sentiment: {sentiment.confidence:.2f}")
        sentiment_score *= 1.1
    elif sentiment.confidence < 0.5:
        reasoning.append(f"Low confidence sentiment: {sentiment.confidence:.2f}")
        sentiment_score *= 0.7
    
    # Determine signal type
    if sentiment_score >= 0.3:
        signal_type = "BUY"
    elif sentiment_score <= -0.3:
        signal_type = "SELL"
    else:
        signal_type = "HOLD"
        reasoning.append("Sentiment analysis shows neutral conditions")
    
    confidence = min(abs(sentiment_score) * 2, 1.0)
    
    return AISignal(
        signal_type=signal_type,
        confidence=confidence,
        reasoning=reasoning,
        sentiment_score=sentiment_score,
        generated_at=timestamp
    )

def _generate_news_signal(ticker: str, news_analysis: List[Dict[str, Any]], timestamp: str) -> Optional[AISignal]:
    """Generate signal based on news analysis"""
    reasoning = []
    news_score = 0.0
    signal_type = "HOLD"
    
    if not news_analysis:
        reasoning.append("No news analysis available")
        return AISignal(
            signal_type="HOLD",
            confidence=0.0,
            reasoning=reasoning,
            generated_at=timestamp
        )
    
    # Analyze news impact scores
    impact_scores = [item.get('impact_score', 0) for item in news_analysis if 'impact_score' in item]
    if impact_scores:
        avg_impact = np.mean(impact_scores)
        if avg_impact > 0.5:
            reasoning.append(f"High impact news: {avg_impact:.2f} average impact")
            news_score += 0.3
        elif avg_impact < -0.5:
            reasoning.append(f"Negative impact news: {avg_impact:.2f} average impact")
            news_score -= 0.3
    
    # Analyze trending topics
    trending_topics = []
    for item in news_analysis:
        if 'trending_topics' in item:
            trending_topics.extend(item['trending_topics'])
    
    if trending_topics:
        unique_topics = len(set(trending_topics))
        if unique_topics > 5:
            reasoning.append(f"High topic diversity: {unique_topics} unique topics")
            news_score += 0.1
    
    # Determine signal type
    if news_score >= 0.2:
        signal_type = "BUY"
    elif news_score <= -0.2:
        signal_type = "SELL"
    else:
        signal_type = "HOLD"
        reasoning.append("News analysis shows neutral impact")
    
    confidence = min(abs(news_score) * 2, 1.0)
    
    return AISignal(
        signal_type=signal_type,
        confidence=confidence,
        reasoning=reasoning,
        generated_at=timestamp
    )

def _generate_overall_ai_signal(ticker: str, ai_signals: List[AISignal], timestamp: str) -> AISignal:
    """Generate overall AI signal by combining all individual signals"""
    reasoning = []
    
    # Weight the signals based on their confidence
    weighted_scores = []
    total_confidence = 0.0
    
    for signal in ai_signals:
        if signal.confidence > 0:
            # Convert signal type to numeric score
            score_map = {
                "STRONG_BUY": 1.0,
                "BUY": 0.5,
                "HOLD": 0.0,
                "SELL": -0.5,
                "STRONG_SELL": -1.0
            }
            score = score_map.get(signal.signal_type, 0.0)
            weighted_scores.append(score * signal.confidence)
            total_confidence += signal.confidence
            reasoning.append(f"{signal.signal_type} (confidence: {signal.confidence:.2f})")
    
    if not weighted_scores or total_confidence == 0:
        return AISignal(
            signal_type="HOLD",
            confidence=0.0,
            reasoning=["Insufficient data for AI analysis"],
            generated_at=timestamp
        )
    
    # Calculate weighted average
    overall_score = sum(weighted_scores) / total_confidence
    
    # Determine final signal type
    if overall_score >= 0.7:
        signal_type = "STRONG_BUY"
    elif overall_score >= 0.3:
        signal_type = "BUY"
    elif overall_score <= -0.7:
        signal_type = "STRONG_SELL"
    elif overall_score <= -0.3:
        signal_type = "SELL"
    else:
        signal_type = "HOLD"
    
    # Calculate overall confidence
    overall_confidence = min(abs(overall_score) * total_confidence / len(ai_signals), 1.0)
    
    reasoning.insert(0, f"AI Analysis Summary: {len(ai_signals)} signals analyzed")
    reasoning.append(f"Overall AI Score: {overall_score:.2f}")
    
    return AISignal(
        signal_type=signal_type,
        confidence=overall_confidence,
        reasoning=reasoning,
        generated_at=timestamp
    )

def calculate_signal_confidence(signals: List[str], reasoning: List[str]) -> float:
    """Calculate confidence score based on signal consistency"""
    if not signals:
        return 0.0
    
    # Count signal types
    signal_counts = {}
    for signal in signals:
        signal_counts[signal] = signal_counts.get(signal, 0) + 1
    
    # Calculate consistency (higher when signals agree)
    total_signals = len(signals)
    max_count = max(signal_counts.values())
    consistency = max_count / total_signals
    
    # Base confidence on consistency and number of signals
    base_confidence = consistency * 0.8
    signal_bonus = min(len(signals) * 0.05, 0.2)
    
    return min(base_confidence + signal_bonus, 1.0)

def get_signal_strength(signal_type: str) -> float:
    """Get numeric strength of signal type"""
    strength_map = {
        "STRONG_BUY": 1.0,
        "BUY": 0.5,
        "HOLD": 0.0,
        "SELL": -0.5,
        "STRONG_SELL": -1.0
    }
    return strength_map.get(signal_type, 0.0)