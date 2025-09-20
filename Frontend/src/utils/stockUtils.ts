import axios from 'axios';

const YAHOO_BASE_URL = 'https://query1.finance.yahoo.com/v7/finance/quote';

// Full Nifty 50 Tickers List
const NIFTY_50_TICKERS = [
  'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'KOTAKBANK', 'LT',
  'AXISBANK', 'SBIN', 'HDFC', 'ITC', 'BAJFINANCE', 'BHARTIARTL', 'HCLTECH',
  'ASIANPAINT', 'MARUTI', 'WIPRO', 'ULTRACEMCO', 'TITAN', 'SUNPHARMA',
  'POWERGRID', 'JSWSTEEL', 'ONGC', 'DIVISLAB', 'NESTLEIND', 'TECHM', 'GRASIM',
  'DRREDDY', 'HEROMOTOCO', 'HINDUNILVR', 'ADANIGREEN', 'BAJAJ-AUTO', 'IOC',
  'COALINDIA', 'ADANIPORTS', 'EICHERMOT', 'SBILIFE', 'CIPLA', 'BRITANNIA',
  'TATASTEEL', 'TATAMOTORS', 'SHREECEM', 'INDUSINDBK', 'TATACONSUM', 'HINDALCO',
  'DLF', 'UPL', 'BPCL', 'M&M', 'ICICIPRULI'
];

// Sanitize ticker string by removing quotes and whitespace
const cleanTicker = (ticker: string): string =>
  ticker.replace(/^['"]+|['"]+$/g, '').toUpperCase();

// Map sanitized ticker to Yahoo Finance symbol (append .NS for NSE)
const mapTickerToYahooSymbol = (ticker: string): string => {
  const symbol = cleanTicker(ticker);
  if (NIFTY_50_TICKERS.includes(symbol)) {
    return `${symbol}.NS`;
  }
  return symbol;
};

export const getStockData = async (ticker: string) => {
  const symbol = mapTickerToYahooSymbol(ticker);
  try {
    const response = await axios.get(YAHOO_BASE_URL, { params: { symbols: symbol } });
    const quote = response.data?.quoteResponse?.result?.[0];
    if (!quote) {
      throw new Error(`No data for symbol: ${symbol}`);
    }
    return {
      ticker: cleanTicker(ticker),
      price: quote.regularMarketPrice ?? 0,
      price_change_1d: quote.regularMarketChangePercent ?? 0,
      price_change_5d: 0,  // Optionally extend this with historical data fetch
      rsi: 0,
      rsi_status: 'NEUTRAL',
      macd: 0,
      macd_signal: 0,
      ema20: 0,
      bollinger_high: 0,
      bollinger_low: 0,
      atr: 0,
      trend: (quote.regularMarketChangePercent ?? 0) > 0 ? 'BULLISH' : 'BEARISH',
      volume: quote.regularMarketVolume ?? 0,
      last_updated: new Date((quote.regularMarketTime ?? 0) * 1000).toISOString()
    };
  } catch (error) {
    console.error(`Error fetching data for ${ticker}:`, error);
    throw error;
  }
};

export const getDashboardData = async (tickers: string[]) => {
  const stocks: any[] = [];
  for (const ticker of tickers.length ? tickers : NIFTY_50_TICKERS) {
    try {
      const stockData = await getStockData(ticker);
      stocks.push(stockData);
    } catch (error) {
      console.error(`Failed to fetch data for ${ticker}:`, error);
    }
  }
  // For demo, use empty arrays or implement news & signals fetching
  return {
    stocks,
    news: [],
    signals: [],
    timestamp: new Date().toISOString()
  };
};
