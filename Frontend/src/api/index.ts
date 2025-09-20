import axios from 'axios';
// Type declarations moved to vite-env.d.ts

/**
 * The base URL for API requests.
 *
 * This constant retrieves the API base URL from the environment variable `VITE_API_BASE`.
 * If the environment variable is not set, it defaults to `'http://localhost:8000'`.
 *
 * @remarks
 * This allows the frontend to dynamically target different backend endpoints
 * depending on the deployment environment (development, staging, production, etc.).
 */
const API_BASE =
  typeof import.meta !== 'undefined' &&
  typeof (import.meta as any).env !== 'undefined' &&
  (import.meta as any).env.VITE_API_BASE
    ? (import.meta as any).env.VITE_API_BASE
    : 'http://localhost:8000';

/**
 * Sanitizes ticker strings by removing extra quotes and whitespace,
 * and converts to uppercase.
 *
 * @param ticker - The ticker string to sanitize.
 * @returns The cleaned ticker string.
 */
export const cleanTicker = (ticker: string): string =>
  ticker.replace(/^['"]+|['"]+$/g, '').toUpperCase();

/**
 * Fetches dashboard data for the specified stock tickers.
 *
 * Sends a GET request to the `/dashboard` endpoint with the provided tickers as a comma-separated list.
 *
 * @param tickers - An array of stock ticker symbols to retrieve dashboard data for.
 * @returns A promise that resolves to the dashboard data returned by the API.
 */
export const getDashboardData = async (tickers: string[]) => {
  console.log('API_BASE:', API_BASE);
  console.log('Requesting tickers:', tickers.join(','));
  const response = await axios.get(`${API_BASE}/dashboard`, {
    params: { tickers: tickers.join(',') }
  });
  console.log('API Response:', response.data);
  return response.data;
};

/**
 * Fetches individual stock data for a given ticker.
 *
 * @param ticker - The stock ticker symbol.
 * @returns A promise that resolves to the stock data returned by the API.
 */
export const getStockData = async (ticker: string) => {
  const cleanSymbol = cleanTicker(ticker);
  const response = await axios.get(`${API_BASE}/stocks/${cleanSymbol}`);
  return response.data;
};

/**
 * Fetches news items with an optional limit.
 *
 * @param limit - Number of news items to fetch (default is 10).
 * @returns A promise that resolves to the news data returned by the API.
 */
export const getNews = async (limit: number = 10) => {
  const response = await axios.get(`${API_BASE}/news`, {
    params: { limit }
  });
  return response.data;
};

/**
 * Fetches trading signals for a given ticker.
 *
 * @param ticker - The stock ticker symbol.
 * @returns A promise that resolves to the signals data returned by the API.
 */
export const getSignals = async (ticker: string) => {
  const cleanSymbol = cleanTicker(ticker);
  const response = await axios.get(`${API_BASE}/signals/${cleanSymbol}`);
  return response.data;
};

/**
 * Performs a health check on the backend API.
 *
 * @returns A promise that resolves to the health check data.
 */
export const healthCheck = async () => {
  const response = await axios.get(`${API_BASE}/health`);
  return response.data;
};

// ============= ALPHA VANTAGE API FUNCTIONS =============

/**
 * Fetches Alpha Vantage quote data for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @returns A promise that resolves to the quote data.
 */
export const getAlphaVantageQuote = async (symbol: string) => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/alpha-vantage/quote/${cleanSymbol}`);
  return response.data;
};

/**
 * Fetches Alpha Vantage daily data for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @param outputsize - 'compact' or 'full' (default: 'compact').
 * @returns A promise that resolves to the daily data.
 */
export const getAlphaVantageDaily = async (symbol: string, outputsize: string = 'compact') => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/alpha-vantage/daily/${cleanSymbol}`, {
    params: { outputsize }
  });
  return response.data;
};

/**
 * Fetches Alpha Vantage intraday data for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @param interval - Time interval (default: '5min').
 * @param outputsize - 'compact' or 'full' (default: 'compact').
 * @returns A promise that resolves to the intraday data.
 */
export const getAlphaVantageIntraday = async (symbol: string, interval: string = '5min', outputsize: string = 'compact') => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/alpha-vantage/intraday/${cleanSymbol}`, {
    params: { interval, outputsize }
  });
  return response.data;
};

/**
 * Fetches Alpha Vantage technical indicators for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @param function - Indicator function (default: 'SMA').
 * @param interval - Time interval (default: 'daily').
 * @param time_period - Number of data points (default: 20).
 * @param series_type - Series type (default: 'close').
 * @returns A promise that resolves to the indicators data.
 */
export const getAlphaVantageIndicators = async (
  symbol: string, 
  function: string = 'SMA', 
  interval: string = 'daily', 
  time_period: number = 20, 
  series_type: string = 'close'
) => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/alpha-vantage/indicators/${cleanSymbol}`, {
    params: { function, interval, time_period, series_type }
  });
  return response.data;
};

/**
 * Fetches Alpha Vantage company overview for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @returns A promise that resolves to the overview data.
 */
export const getAlphaVantageOverview = async (symbol: string) => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/alpha-vantage/overview/${cleanSymbol}`);
  return response.data;
};

/**
 * Fetches Alpha Vantage earnings data for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @returns A promise that resolves to the earnings data.
 */
export const getAlphaVantageEarnings = async (symbol: string) => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/alpha-vantage/earnings/${cleanSymbol}`);
  return response.data;
};

/**
 * Fetches Alpha Vantage news sentiment for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @param limit - Number of news items (default: 50).
 * @returns A promise that resolves to the news data.
 */
export const getAlphaVantageNews = async (symbol: string, limit: number = 50) => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/alpha-vantage/news/${cleanSymbol}`, {
    params: { limit }
  });
  return response.data;
};

// ============= CURRENCY CONVERSION API FUNCTIONS =============

/**
 * Fetches current USD to INR exchange rate.
 *
 * @returns A promise that resolves to the exchange rate data.
 */
export const getCurrencyRate = async () => {
  const response = await axios.get(`${API_BASE}/currency/rate`);
  return response.data;
};

/**
 * Converts currency amount from USD to INR.
 *
 * @param amount - Amount to convert (default: 100).
 * @returns A promise that resolves to the conversion data.
 */
export const convertCurrency = async (amount: number = 100) => {
  const response = await axios.get(`${API_BASE}/currency/convert`, {
    params: { amount }
  });
  return response.data;
};

/**
 * Formats currency amount in INR.
 *
 * @param amount - Amount to format (default: 1000).
 * @returns A promise that resolves to the formatted currency data.
 */
export const formatCurrency = async (amount: number = 1000) => {
  const response = await axios.get(`${API_BASE}/currency/format`, {
    params: { amount }
  });
  return response.data;
};

// ============= ANGEL ONE API FUNCTIONS =============

/**
 * Fetches Angel One service status.
 *
 * @returns A promise that resolves to the status data.
 */
export const getAngelOneStatus = async () => {
  const response = await axios.get(`${API_BASE}/angel-one/status`);
  return response.data;
};

/**
 * Fetches Angel One quote data for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @returns A promise that resolves to the quote data.
 */
export const getAngelOneQuote = async (symbol: string) => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/angel-one/quote/${cleanSymbol}`);
  return response.data;
};

/**
 * Fetches Angel One historical data for a given symbol.
 *
 * @param symbol - The stock symbol.
 * @param interval - Time interval (default: '1d').
 * @param period - Time period (default: '1mo').
 * @returns A promise that resolves to the historical data.
 */
export const getAngelOneHistorical = async (symbol: string, interval: string = '1d', period: string = '1mo') => {
  const cleanSymbol = cleanTicker(symbol);
  const response = await axios.get(`${API_BASE}/angel-one/historical/${cleanSymbol}`, {
    params: { interval, period }
  });
  return response.data;
};

/**
 * Fetches Angel One indices data.
 *
 * @returns A promise that resolves to the indices data.
 */
export const getAngelOneIndices = async () => {
  const response = await axios.get(`${API_BASE}/angel-one/indices`);
  return response.data;
};

/**
 * Fetches Angel One market status.
 *
 * @returns A promise that resolves to the market status data.
 */
export const getAngelOneMarketStatus = async () => {
  const response = await axios.get(`${API_BASE}/angel-one/market-status`);
  return response.data;
};
