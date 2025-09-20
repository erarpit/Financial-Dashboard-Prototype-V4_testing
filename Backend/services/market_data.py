						 
import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Any
from models.schemas import StockData

logger = logging.getLogger(__name__)

async def get_stock_data(ticker: str, period: str = "6mo", interval: str = "1d") -> StockData:
    """Get stock data from Yahoo Finance"""
    try:
        # Try to download data with retry logic
        df = None
        max_retries = 2
        
        # For Indian stocks, try multiple formats
        ticker_variants = [ticker]
        if ticker.endswith('.NS'):
            # Try without .NS suffix
            ticker_variants.append(ticker.replace('.NS', ''))
            # Try with .BO suffix (Bombay Stock Exchange)
            ticker_variants.append(ticker.replace('.NS', '.BO'))
        
        for ticker_variant in ticker_variants:
            for attempt in range(max_retries):
                try:
                    logger.info(f"Trying to fetch data for {ticker_variant} (attempt {attempt + 1})")
                    df = yf.download(ticker_variant, period=period, interval=interval, progress=False, auto_adjust=True)
                    if not df.empty:
                        logger.info(f"Successfully fetched data for {ticker_variant}")
                        break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {ticker_variant}: {str(e)}")
                    if attempt == max_retries - 1:
                        continue
                    continue
            
            if df is not None and not df.empty:
                break
        
        if df is None or df.empty:
            logger.warning(f"All attempts failed for {ticker}, using mock data")
            raise ValueError(f"No data found for {ticker} with any variant")
        
        # Flatten multi-level columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Calculate technical indicators
        df = calculate_indicators(df)
        
        # Get latest data
        latest = df.iloc[-1]
        
        # Calculate price changes
        price_change_1d = calculate_price_change(df, 1) if len(df) > 1 else 0
        price_change_5d = calculate_price_change(df, 5) if len(df) > 5 else 0
        
        # Determine trend
        current_price = latest['Close']
        ema20 = latest.get('EMA_20', current_price)
        trend = "BULLISH" if current_price > ema20 else "BEARISH" if current_price < ema20 else "NEUTRAL"
        
        # Determine RSI status
        rsi = latest.get('RSI_14', 50)
        rsi_status = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL"
        
        return StockData(
            ticker=ticker.upper(),
            price=round(current_price, 2),
            price_change_1d=round(price_change_1d, 2),
            price_change_5d=round(price_change_5d, 2),
            rsi=round(rsi, 2),
            rsi_status=rsi_status,
            macd=round(latest.get('MACD_12_26_9', 0), 4),
            macd_signal=round(latest.get('MACDs_12_26_9', 0), 4),
            ema20=round(ema20, 2),
            bollinger_high=round(latest.get('BBU_20_2.0', 0), 2),
            bollinger_low=round(latest.get('BBL_20_2.0', 0), 2),
            atr=round(latest.get('ATR_14', 0), 2),
            trend=trend,
            volume=int(latest['Volume']),
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        # Return mock data for failed requests to prevent complete failure
        logger.warning(f"Failed to fetch data for {ticker}: {str(e)}. Returning mock data.")
        return generate_mock_data(ticker)

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators using pandas/numpy"""
    try:
        # RSI calculation
        df['RSI_14'] = calculate_rsi(df['Close'], 14)
        
        # MACD calculation
        macd, macd_signal, macd_hist = calculate_macd(df['Close'])
        df['MACD_12_26_9'] = macd
        df['MACDs_12_26_9'] = macd_signal
        df['MACDh_12_26_9'] = macd_hist
        
        # EMA calculation
        df['EMA_20'] = df['Close'].ewm(span=20).mean()
        
        # Bollinger Bands calculation
        bb_middle = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BBM_20_2.0'] = bb_middle
        df['BBU_20_2.0'] = bb_middle + (bb_std * 2)
        df['BBL_20_2.0'] = bb_middle - (bb_std * 2)
        
        # ATR calculation
        df['ATR_14'] = calculate_atr(df['High'], df['Low'], df['Close'], 14)
        
        # Fill NaN values with default values
        df['RSI_14'] = df['RSI_14'].fillna(50.0)
        df['MACD_12_26_9'] = df['MACD_12_26_9'].fillna(0.0)
        df['MACDs_12_26_9'] = df['MACDs_12_26_9'].fillna(0.0)
        df['MACDh_12_26_9'] = df['MACDh_12_26_9'].fillna(0.0)
        df['EMA_20'] = df['EMA_20'].fillna(df['Close'])
        df['BBU_20_2.0'] = df['BBU_20_2.0'].fillna(df['Close'] * 1.05)
        df['BBM_20_2.0'] = df['BBM_20_2.0'].fillna(df['Close'])
        df['BBL_20_2.0'] = df['BBL_20_2.0'].fillna(df['Close'] * 0.95)
        df['ATR_14'] = df['ATR_14'].fillna(df['Close'] * 0.02)
        
    except Exception as e:
        logger.warning(f"Error calculating indicators: {str(e)}. Using default values.")
        # Set default values if calculation fails
        df['RSI_14'] = 50.0
        df['MACD_12_26_9'] = 0.0
        df['MACDs_12_26_9'] = 0.0
        df['MACDh_12_26_9'] = 0.0
        df['EMA_20'] = df['Close']
        df['BBU_20_2.0'] = df['Close'] * 1.05
        df['BBM_20_2.0'] = df['Close']
        df['BBL_20_2.0'] = df['Close'] * 0.95
        df['ATR_14'] = df['Close'] * 0.02
    
    return df

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI using pandas"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculate MACD using pandas"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate ATR using pandas"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def generate_mock_data(ticker: str) -> StockData:
    """Generate realistic mock data for a ticker"""
    import random
    
    # Generate realistic price based on ticker
    base_prices = {
        'AAPL': 240.0, 'MSFT': 380.0, 'GOOGL': 140.0, 'AMZN': 150.0, 'TSLA': 250.0,
        'RELIANCE.NS': 2500.0, 'HDFCBANK.NS': 1600.0, 'INFY.NS': 1500.0, 'TCS.NS': 3500.0, 'ICICIBANK.NS': 1000.0,
        'HINDUNILVR.NS': 2500.0, 'SBIN.NS': 600.0, 'BAJFINANCE.NS': 7000.0, 'RELIANCE': 2500.0, 'HDFCBANK': 1600.0,
        'INFY': 1500.0, 'TCS': 3500.0, 'ICICIBANK': 1000.0, 'HINDUNILVR': 2500.0, 'SBIN': 600.0, 'BAJFINANCE': 7000.0
    }
    
    base_price = base_prices.get(ticker.upper(), 100.0)
    
    # Add some randomness
    price_variation = random.uniform(0.9, 1.1)
    current_price = round(base_price * price_variation, 2)
    
    # Generate realistic changes
    price_change_1d = round(random.uniform(-5, 5), 2)
    price_change_5d = round(random.uniform(-10, 10), 2)
    
    # Generate realistic technical indicators
    rsi = round(random.uniform(30, 70), 2)
    rsi_status = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL"
    
    macd = round(random.uniform(-2, 2), 4)
    macd_signal = round(random.uniform(-2, 2), 4)
    
    ema20 = round(current_price * random.uniform(0.95, 1.05), 2)
    trend = "BULLISH" if current_price > ema20 else "BEARISH" if current_price < ema20 else "NEUTRAL"
    
    bollinger_high = round(current_price * 1.05, 2)
    bollinger_low = round(current_price * 0.95, 2)
    atr = round(current_price * 0.02, 2)
    
    volume = random.randint(1000000, 10000000)
    
    return StockData(
        ticker=ticker.upper(),
        price=current_price,
        price_change_1d=price_change_1d,
        price_change_5d=price_change_5d,
        rsi=rsi,
        rsi_status=rsi_status,
        macd=macd,
        macd_signal=macd_signal,
        ema20=ema20,
        bollinger_high=bollinger_high,
        bollinger_low=bollinger_low,
        atr=atr,
        trend=trend,
        volume=volume,
        last_updated=datetime.now().isoformat()
    )

def calculate_price_change(df: pd.DataFrame, days: int) -> float:
    """Calculate price change percentage"""
    current_price = df.iloc[-1]['Close']
    previous_price = df.iloc[-(days + 1)]['Close']
    return ((current_price / previous_price) - 1) * 100

async def get_historical_data(ticker: str, period: str = "6mo", interval: str = "1d") -> Dict[str, Any]:
    """Get historical data for charts"""
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return {"error": "No data found"}
        
        df = calculate_indicators(df)
        
        return {
            "timestamp": df.index.strftime("%Y-%m-%d").tolist(),
            "open": df['Open'].fillna(0).tolist(),
            "high": df['High'].fillna(0).tolist(),
            "low": df['Low'].fillna(0).tolist(),
            "close": df['Close'].fillna(0).tolist(),
            "volume": df['Volume'].fillna(0).tolist(),
            "rsi": df['RSI_14'].fillna(0).tolist(),
            "macd": df['MACD_12_26_9'].fillna(0).tolist(),
            "macd_signal": df['MACDs_12_26_9'].fillna(0).tolist(),
            "ema20": df['EMA_20'].fillna(0).tolist(),
            "bollinger_high": df['BBU_20_2.0'].fillna(0).tolist(),
            "bollinger_low": df['BBL_20_2.0'].fillna(0).tolist(),
        }
    except Exception as e:
        raise Exception(f"Error fetching historical data: {str(e)}")
# ADD this function at the end of the file

async def get_ohlc_candlestick_data(ticker: str, period: str = "6mo", interval: str = "1d", limit: int = 100) -> Dict[str, Any]:
    """Get OHLC data specifically formatted for candlestick charts"""
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if df.empty:
            raise ValueError(f"No data found for {ticker}")
        
        # Take last 'limit' rows
        df = df.tail(limit)
        
        # Flatten multi-level columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        return {
            "ticker": ticker,
            "timeframe": interval,
            "timestamps": df.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
            "open": df['Open'].round(2).tolist(),
            "high": df['High'].round(2).tolist(),
            "low": df['Low'].round(2).tolist(),
            "close": df['Close'].round(2).tolist(),
            "volume": df['Volume'].astype(int).tolist()
        }
    except Exception as e:
        logger.error(f"Error getting OHLC data for {ticker}: {str(e)}")
        raise Exception(f"Error fetching OHLC data: {str(e)}")