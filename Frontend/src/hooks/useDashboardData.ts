// src/hooks/useDashboardData.ts

import { useState, useEffect } from 'react';
import { getDashboardData } from '../api';
import { DashboardData } from '../types';

export const useDashboardData = (tickers: string[], refreshInterval = 60000) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        const dashboardData = await getDashboardData(tickers);
        if (isMounted) {
          setData(dashboardData);
          setError(null);
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to fetch data');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    if (tickers.length > 0) {
      fetchData();
      const interval = setInterval(fetchData, refreshInterval);
      return () => {
        isMounted = false;
        clearInterval(interval);
      };
    } else {
      setData(null);
      setLoading(false);
      setError(null);
    }
  }, [tickers, refreshInterval]);

  return { data, loading, error };
};
