import React, { useState, useEffect } from 'react';
import QuoteCard from './QuoteCard';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface QuoteData {
  symbol: string;
  info: Record<string, any>;
  last_updated: string;
}

const QuotePanel: React.FC = () => {
  const [ticker, setTicker] = useState('RELIANCE.NS');
  const [quoteData, setQuoteData] = useState<QuoteData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTickerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTicker(e.target.value);
  };

  const fetchQuoteData = async () => {
    if (!ticker.trim()) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/quote/${ticker}`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`No quote data found for ${ticker}`);
        }
        throw new Error('Failed to fetch quote data');
      }
      
      const data = await response.json();
      setQuoteData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setQuoteData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchQuoteData();
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Company Information & Analysis
        </h2>
        <p className="text-gray-600">
          Get detailed company information, financial data, and fundamental analysis
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
            {loading ? 'Loading...' : 'Get Quote'}
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
            onClick={fetchQuoteData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Quote Data */}
      {quoteData && !loading && (
        <QuoteCard data={quoteData} />
      )}

      {/* No Data State */}
      {!quoteData && !loading && !error && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Enter a ticker symbol</h3>
          <p className="text-gray-500">
            Search for company information and fundamental analysis by entering a stock ticker symbol above
          </p>
        </div>
      )}
    </div>
  );
};

export default QuotePanel;
