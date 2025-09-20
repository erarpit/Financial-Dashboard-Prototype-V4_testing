import axios from 'axios';

const API_BASE =
  typeof import.meta !== 'undefined' &&
  typeof (import.meta as any).env !== 'undefined' &&
  (import.meta as any).env.VITE_API_BASE
    ? (import.meta as any).env.VITE_API_BASE
    : 'http://localhost:8000';

// Clean ticker by removing any quotes and trimming whitespace
export const cleanTicker = (ticker: string): string =>
  ticker.replace(/^['"]+|['"]+$/g, '').toUpperCase();

/**
 * Fetches dashboard data for multiple tickers.
 * @param tickers Array of ticker strings.
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
 * Fetches data for a single ticker.
 * @param ticker The stock ticker symbol.
 */
export const getStockData = async (ticker: string) => {
  const cleanSymbol = cleanTicker(ticker);
  const response = await axios.get(`${API_BASE}/stocks/${cleanSymbol}`);
  return response.data;
};

/**
 * Fetches news items, with optional limit.
 * @param limit Number of news items to fetch.
 */
export const getNews = async (limit: number = 10) => {
  const response = await axios.get(`${API_BASE}/news`, {
    params: { limit }
  });
  return response.data;
};

/**
 * Fetches trading signals for a given ticker.
 * @param ticker The stock ticker symbol.
 */
export const getSignals = async (ticker: string) => {
  const cleanSymbol = cleanTicker(ticker);
  const response = await axios.get(`${API_BASE}/signals/${cleanSymbol}`);
  return response.data;
};

/**
 * Checks the health status of the backend.
 */
export const healthCheck = async () => {
  const response = await axios.get(`${API_BASE}/health`);
  return response.data;
};
