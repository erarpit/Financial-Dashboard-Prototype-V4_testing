// src/hooks/index.ts
import { useState, useEffect } from 'react';

export const useStocks = (tickers: string[]) => {
  const [stocks, setStocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Implement actual API call here
    const fetchStocks = async () => {
      try {
        setLoading(true);
        // Mock data - replace with actual API call
        const mockStocks = tickers.map(ticker => ({
          ticker,
          trend: Math.random() > 0.5 ? 'BULLISH' : 'BEARISH',
          rsi: Math.random() * 100,
          rsi_status: Math.random() > 0.5 ? 'OVERBOUGHT' : 'OVERSOLD'
        }));
        setStocks(mockStocks);
      } catch (err) {
        setError('Failed to fetch stocks');
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();
  }, [tickers]);

  return { stocks, loading, error };
};

export const useNews = (limit: number) => {
  const [news, setNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Implement actual news API call here
    const fetchNews = async () => {
      try {
        setLoading(true);
        // Mock data - replace with actual API call
        const mockNews = Array.from({ length: limit }, (_, i) => ({
          id: i,
          title: `News item ${i + 1}`,
          content: `Sample news content ${i + 1}`
        }));
        setNews(mockNews);
      } catch (err) {
        setError('Failed to fetch news');
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [limit]);

  return { news, loading, error };
};
