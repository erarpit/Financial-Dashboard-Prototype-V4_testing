// src/hooks/useNews.ts
import { useState, useEffect } from 'react';
import { getNews } from '../api';
import { NewsItem } from '../types';

export const useNews = (limit: number = 10) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getNews(limit);
        setNews(data.news || data); // Handle both response formats
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch news');
      } finally {
        setLoading(false);
      }
    };

    fetchNews();

    // Refresh news every 5 minutes
    const interval = setInterval(fetchNews, 300000);
    return () => clearInterval(interval);
  }, [limit]);

  return { news, loading, error };
};
export default useNews;