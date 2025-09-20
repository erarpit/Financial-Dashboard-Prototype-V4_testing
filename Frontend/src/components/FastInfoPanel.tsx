import React, { useState, useEffect } from 'react';
import FastInfoCard from './FastInfoCard';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface FastInfoData {
  symbol: string;
  currency?: string;
  quote_type?: string;
  exchange?: string;
  timezone?: string;
  shares?: number;
  market_cap?: number;
  last_price?: number;
  previous_close?: number;
  open_price?: number;
  day_high?: number;
  day_low?: number;
  regular_market_previous_close?: number;
  last_volume?: number;
  fifty_day_average?: number;
  two_hundred_day_average?: number;
  ten_day_average_volume?: number;
  three_month_average_volume?: number;
  year_high?: number;
  year_low?: number;
  year_change?: number;
  last_updated: string;
}

const FastInfoPanel: React.FC = () => {
  const [ticker, setTicker] = useState('RELIANCE.NS');
  const [fastInfoData, setFastInfoData] = useState<FastInfoData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTickerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTicker(e.target.value);
  };

  const fetchFastInfo = async () => {
    if (!ticker.trim()) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/fastinfo/${ticker}`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`No fast info found for ${ticker}`);
        }
        throw new Error('Failed to fetch fast info');
      }
      
      const data = await response.json();
      setFastInfoData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setFastInfoData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchFastInfo();
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Enhanced Stock Information
        </h2>
        <p className="text-gray-600">
          Get comprehensive stock data including price, volume, technical indicators, and market metrics
        </p>
      </div>

      {/* Search Form */}
      <div className="mb-6">
        <form onSubmit={handleSubmit} className="flex gap-4 items-end">
          <div className="flex-1">
            <label htmlFor="ticker" className="block text-sm font-medium text-gray-700 mb-2">
              Stock Ticker
            </label>
            <input
              type="text"
              id="ticker"
              value={ticker}
              onChange={handleTickerChange}
              placeholder="Enter ticker symbol (e.g., RELIANCE.NS, AAPL)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !ticker.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Loading...' : 'Get Info'}
          </button>
        </form>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="mb-6">
          <ErrorMessage message={error} />
          <button
            onClick={fetchFastInfo}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* FastInfo Data */}
      {fastInfoData && !loading && (
        <FastInfoCard data={fastInfoData} />
      )}

      {/* No Data State */}
      {!fastInfoData && !loading && !error && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Enter a ticker symbol</h3>
          <p className="text-gray-500">
            Search for enhanced stock information by entering a stock ticker symbol above
          </p>
        </div>
      )}
    </div>
  );
};

export default FastInfoPanel;
