import React, { useState, useEffect } from 'react';
import OwnershipCard from './OwnershipCard';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface OwnershipData {
  symbol: string;
  institutional_holders: Array<{
    'Date Reported': string;
    'Holder': string;
    'Shares': number;
    'Value': number;
  }>;
  mutual_fund_holders: Array<{
    'Date Reported': string;
    'Holder': string;
    'Shares': number;
    'Value': number;
  }>;
  major_holders_breakdown: Record<string, any>;
  insider_transactions: Array<{
    'Start Date': string;
    'Insider': string;
    'Position': string;
    'Transaction': string;
    'Shares': number;
    'Value': number;
  }>;
  insider_roster: Array<{
    'Name': string;
    'Position': string;
    'Most Recent Transaction': string;
    'Shares Owned Directly': number;
    'Shares Owned Indirectly': number;
  }>;
  insider_purchases: Record<string, any>;
  last_updated: string;
}

const OwnershipPanel: React.FC = () => {
  const [ticker, setTicker] = useState('RELIANCE.NS');
  const [ownershipData, setOwnershipData] = useState<OwnershipData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTickerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTicker(e.target.value);
  };

  const fetchOwnershipData = async () => {
    if (!ticker.trim()) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/ownership/${ticker}`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`No ownership data found for ${ticker}`);
        }
        throw new Error('Failed to fetch ownership data');
      }
      
      const data = await response.json();
      setOwnershipData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setOwnershipData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchOwnershipData();
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Ownership Analysis
        </h2>
        <p className="text-gray-600">
          Analyze institutional ownership, insider transactions, and major holders
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
            {loading ? 'Loading...' : 'Analyze'}
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
            onClick={fetchOwnershipData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Ownership Data */}
      {ownershipData && !loading && (
        <OwnershipCard data={ownershipData} />
      )}

      {/* No Data State */}
      {!ownershipData && !loading && !error && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Enter a ticker symbol</h3>
          <p className="text-gray-500">
            Search for ownership data by entering a stock ticker symbol above
          </p>
        </div>
      )}
    </div>
  );
};

export default OwnershipPanel;
