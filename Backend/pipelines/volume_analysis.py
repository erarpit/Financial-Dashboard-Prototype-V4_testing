# pipelines/volume_analysis.py

import pandas as pd
import numpy as np
from typing import Dict, Any

def analyze_volume(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive volume analysis for stock data.
    Input: DataFrame with ['Close', 'Volume', 'High', 'Low']
    Returns: Dictionary with volume insights
    """
    if df.empty or len(df) < 20:
        return {"error": "Insufficient data for volume analysis"}
    
    result = {}
    
    # Basic volume metrics
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    avg_vol_5 = df['Volume'].rolling(5).mean().iloc[-1]
    today_vol = df['Volume'].iloc[-1]
    yesterday_vol = df['Volume'].iloc[-2] if len(df) > 1 else today_vol
    
    # Volume trend detection
    if today_vol > yesterday_vol:
        result['trend'] = "Increasing"
        result['trend_strength'] = round(((today_vol - yesterday_vol) / yesterday_vol) * 100, 2)
    elif today_vol < yesterday_vol:
        result['trend'] = "Decreasing" 
        result['trend_strength'] = round(((yesterday_vol - today_vol) / yesterday_vol) * 100, 2)
    else:
        result['trend'] = "Flat"
        result['trend_strength'] = 0.0
    
    # Volume strength classification
    vol_ratio = today_vol / avg_vol_20
    if vol_ratio > 2.0:
        result['strength'] = "Extremely High"
        result['signal'] = "Strong breakout/breakdown potential"
    elif vol_ratio > 1.5:
        result['strength'] = "High"
        result['signal'] = "Above average activity"
    elif vol_ratio > 0.8:
        result['strength'] = "Normal"
        result['signal'] = "Average trading activity"
    else:
        result['strength'] = "Low"
        result['signal'] = "Below average interest"
    
    # Volume oscillator (short vs long term)
    vo = ((avg_vol_5 - avg_vol_20) / avg_vol_20) * 100
    result['volume_oscillator'] = round(vo, 2)
    
    if vo > 10:
        result['vo_signal'] = "Volume expanding rapidly"
    elif vo > 5:
        result['vo_signal'] = "Volume trending higher"
    elif vo < -10:
        result['vo_signal'] = "Volume drying up"
    elif vo < -5:
        result['vo_signal'] = "Volume declining"
    else:
        result['vo_signal'] = "Volume stable"
    
    # Price-Volume relationship
    price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
    
    if price_change > 0 and vol_ratio > 1.2:
        result['pv_relationship'] = "Bullish confirmation"
        result['conviction'] = "High"
    elif price_change > 0 and vol_ratio < 0.8:
        result['pv_relationship'] = "Weak rally"
        result['conviction'] = "Low"
    elif price_change < 0 and vol_ratio > 1.2:
        result['pv_relationship'] = "Bearish pressure"
        result['conviction'] = "High"
    elif price_change < 0 and vol_ratio < 0.8:
        result['pv_relationship'] = "Weak selling"
        result['conviction'] = "Low"
    else:
        result['pv_relationship'] = "Neutral"
        result['conviction'] = "Medium"
    
    # Additional metrics
    result['volume_ratio'] = round(vol_ratio, 2)
    result['avg_volume_20d'] = int(avg_vol_20)
    result['current_volume'] = int(today_vol)
    result['price_change_pct'] = round(price_change, 2)
    
    return result

def compute_volume_signal(df: pd.DataFrame) -> str:
    """
    Simple volume signal for quick reference.
    """
    analysis = analyze_volume(df)
    
    if 'error' in analysis:
        return "Insufficient data"
    
    strength = analysis.get('strength', 'Normal')
    trend = analysis.get('trend', 'Flat')
    
    if strength in ['High', 'Extremely High'] and trend == 'Increasing':
        return f"🚀 High volume breakout ({analysis['volume_ratio']}x avg)"
    elif strength == 'Low':
        return f"📉 Weak volume ({analysis['volume_ratio']}x avg)"
    else:
        return f"📊 {strength} volume, {trend.lower()} trend"

# On Balance Volume (OBV) calculation
def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """
    Calculate On Balance Volume indicator.
    """
    obv = pd.Series(index=df.index, dtype=float)
    obv.iloc[0] = df['Volume'].iloc[0]
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + df['Volume'].iloc[i]
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - df['Volume'].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv

# Volume Weighted Average Price (VWAP)
def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Calculate Volume Weighted Average Price.
    """
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    cumulative_tp_volume = (typical_price * df['Volume']).cumsum()
    cumulative_volume = df['Volume'].cumsum()
    
    return cumulative_tp_volume / cumulative_volume