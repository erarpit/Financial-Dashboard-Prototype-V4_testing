import React, { useState } from 'react';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface EnhancedDownloaderProps {
  onDataReceived?: (data: any) => void;
}

interface DownloadResult {
  tickers: string[];
  data: any[];
  columns: string[];
  shape: [number, number];
  timestamp: string;
}

const EnhancedDownloader: React.FC<EnhancedDownloaderProps> = ({ onDataReceived }) => {
  const [tickers, setTickers] = useState<string>('RELIANCE.NS,TCS.NS,HDFCBANK.NS');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [period, setPeriod] = useState<string>('1mo');
  const [interval, setInterval] = useState<string>('1d');
  const [includeIndicators, setIncludeIndicators] = useState<boolean>(true);
  const [includeSentiment, setIncludeSentiment] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DownloadResult | null>(null);

  const handleDownload = async () => {
    try {
      setLoading(true);
      setError(null);

      const tickerList = tickers.split(',').map(t => t.trim()).filter(t => t);
      if (tickerList.length === 0) {
        throw new Error('Please enter at least one ticker symbol');
      }

      const params = new URLSearchParams({
        tickers: tickerList.join(','),
        period,
        interval,
        include_indicators: includeIndicators.toString(),
        include_sentiment: includeSentiment.toString(),
        threads: 'true',
        timeout: '30'
      });

      if (startDate) params.append('start', startDate);
      if (endDate) params.append('end', endDate);

      const response = await fetch(`http://localhost:8000/enhanced-download?${params}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      onDataReceived?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
    return `$${value.toFixed(2)}`;
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Enhanced Data Downloader</h2>
        <div className="text-sm text-gray-500">
          Powered by Enhanced YFinance
        </div>
      </div>

      {/* Configuration Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Download Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Tickers */}
          <div className="lg:col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ticker Symbols (comma-separated)
            </label>
            <input
              type="text"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              placeholder="RELIANCE.NS,TCS.NS,HDFCBANK.NS"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date (Optional)
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Date (Optional)
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Period */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Period
            </label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="1d">1 Day</option>
              <option value="5d">5 Days</option>
              <option value="1mo">1 Month</option>
              <option value="3mo">3 Months</option>
              <option value="6mo">6 Months</option>
              <option value="1y">1 Year</option>
              <option value="2y">2 Years</option>
              <option value="5y">5 Years</option>
              <option value="10y">10 Years</option>
              <option value="ytd">Year to Date</option>
              <option value="max">Max</option>
            </select>
          </div>

          {/* Interval */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Interval
            </label>
            <select
              value={interval}
              onChange={(e) => setInterval(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="1m">1 Minute</option>
              <option value="2m">2 Minutes</option>
              <option value="5m">5 Minutes</option>
              <option value="15m">15 Minutes</option>
              <option value="30m">30 Minutes</option>
              <option value="60m">1 Hour</option>
              <option value="90m">90 Minutes</option>
              <option value="1h">1 Hour</option>
              <option value="1d">1 Day</option>
              <option value="5d">5 Days</option>
              <option value="1wk">1 Week</option>
              <option value="1mo">1 Month</option>
              <option value="3mo">3 Months</option>
            </select>
          </div>

          {/* Options */}
          <div className="lg:col-span-3">
            <div className="flex items-center space-x-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeIndicators}
                  onChange={(e) => setIncludeIndicators(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Include Technical Indicators</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeSentiment}
                  onChange={(e) => setIncludeSentiment(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Include Sentiment Analysis</span>
              </label>
            </div>
          </div>
        </div>

        {/* Download Button */}
        <div className="mt-6">
          <button
            onClick={handleDownload}
            disabled={loading || tickers.trim() === ''}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <LoadingSpinner size="small" />
                <span className="ml-2">Downloading...</span>
              </>
            ) : (
              'Download Enhanced Data'
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <ErrorMessage message={error} />
      )}

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Download Results
            </h3>
            <div className="mt-2 text-sm text-gray-600">
              <span className="font-medium">{result.tickers.length}</span> tickers • 
              <span className="font-medium"> {result.shape[0]}</span> rows • 
              <span className="font-medium"> {result.shape[1]}</span> columns
            </div>
          </div>
          
          <div className="p-6">
            <div className="mb-4">
              <h4 className="text-md font-medium text-gray-900 mb-2">Available Columns:</h4>
              <div className="flex flex-wrap gap-2">
                {result.columns.map((column, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                  >
                    {column}
                  </span>
                ))}
              </div>
            </div>

            {/* Data Preview */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    {result.columns.slice(0, 6).map((column, index) => (
                      <th key={index} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {result.data.slice(0, 10).map((row: any, index: number) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {row.Date || 'N/A'}
                      </td>
                      {result.columns.slice(0, 6).map((column, colIndex) => (
                        <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {typeof row[column] === 'number' 
                            ? row[column].toFixed(2) 
                            : row[column] || 'N/A'
                          }
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {result.data.length > 10 && (
              <div className="mt-4 text-sm text-gray-500 text-center">
                Showing first 10 rows of {result.data.length} total rows
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedDownloader;
