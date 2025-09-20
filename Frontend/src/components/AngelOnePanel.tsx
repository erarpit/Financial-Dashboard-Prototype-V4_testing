import React, { useState, useEffect } from 'react';
import { 
  getAngelOneStatus, 
  getAngelOneQuote, 
  getAngelOneHistorical, 
  getAngelOneIndices,
  getAngelOneMarketStatus
} from '../api';
import { 
  AngelOneStatus, 
  AngelOneQuote, 
  AngelOneHistorical, 
  AngelOneIndices,
  AngelOneMarketStatus
} from '../types';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface AngelOnePanelProps {
  symbol?: string;
  onClose: () => void;
}

const AngelOnePanel: React.FC<AngelOnePanelProps> = ({ symbol, onClose }) => {
  const [activeTab, setActiveTab] = useState<'status' | 'quote' | 'historical' | 'indices' | 'market'>('status');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<string>(symbol || 'RELIANCE.NS');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let result;
      switch (activeTab) {
        case 'status':
          result = await getAngelOneStatus();
          break;
        case 'quote':
          result = await getAngelOneQuote(selectedSymbol);
          break;
        case 'historical':
          result = await getAngelOneHistorical(selectedSymbol);
          break;
        case 'indices':
          result = await getAngelOneIndices();
          break;
        case 'market':
          result = await getAngelOneMarketStatus();
          break;
        default:
          result = await getAngelOneStatus();
      }
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeTab, selectedSymbol]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-IN').format(num);
  };

  const formatPercentage = (num: number) => {
    return `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`;
  };

  const renderStatusData = (status: AngelOneStatus) => (
    <div className="space-y-4">
      <div className="bg-blue-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Angel One Service Status</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-900">
              {status.enabled ? '✅ Enabled' : '❌ Disabled'}
            </p>
            <p className="text-sm text-blue-700">Service Status</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-900">
              {status.api_configured ? '✅ Configured' : '❌ Not Configured'}
            </p>
            <p className="text-sm text-blue-700">API Configuration</p>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Client Configuration</h3>
          <p className={`text-lg font-semibold ${status.client_configured ? 'text-green-600' : 'text-red-600'}`}>
            {status.client_configured ? 'Configured' : 'Not Configured'}
          </p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Last Updated</h3>
          <p className="text-lg font-semibold text-gray-900">
            {new Date(status.last_updated).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );

  const renderQuoteData = (quote: AngelOneQuote) => (
    <div className="space-y-4">
      <div className="bg-green-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-green-900 mb-2">{quote.name}</h3>
        <div className="text-center">
          <p className="text-3xl font-bold text-green-900">{formatPrice(quote.price)}</p>
          <p className={`text-lg font-semibold ${quote.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatPrice(quote.change)} ({formatPercentage(quote.change_percent)})
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Symbol</h3>
          <p className="text-lg font-semibold text-gray-900">{quote.symbol}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Volume</h3>
          <p className="text-lg font-semibold text-gray-900">{formatNumber(quote.volume)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Source</h3>
          <p className="text-lg font-semibold text-gray-900">{quote.source}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Last Updated</h3>
          <p className="text-lg font-semibold text-gray-900">
            {new Date(quote.last_updated).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );

  const renderHistoricalData = (historical: AngelOneHistorical) => (
    <div className="space-y-4">
      <div className="text-sm text-gray-500">
        <p>Symbol: {historical.symbol}</p>
        <p>Interval: {historical.interval}</p>
        <p>Period: {historical.period}</p>
        <p>Data Points: {historical.data.length}</p>
        <p>Source: {historical.source}</p>
        <p>Last Updated: {new Date(historical.last_updated).toLocaleString()}</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Open</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">High</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Low</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Close</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Volume</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {historical.data.slice(0, 10).map((row, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(row.date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.open)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.high)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.low)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.close)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(row.volume)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderIndicesData = (indices: AngelOneIndices) => (
    <div className="space-y-4">
      <div className="text-sm text-gray-500">
        <p>Source: {indices.source}</p>
        <p>Last Updated: {new Date(indices.last_updated).toLocaleString()}</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(indices.indices).map(([key, index]) => (
          <div key={key} className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{index.symbol}</h3>
            <p className="text-2xl font-bold text-gray-900">{formatPrice(index.price)}</p>
            <p className={`text-sm font-semibold ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPrice(index.change)} ({formatPercentage(index.change_percent)})
            </p>
          </div>
        ))}
      </div>
    </div>
  );

  const renderMarketData = (market: AngelOneMarketStatus) => (
    <div className="space-y-4">
      <div className="text-sm text-gray-500">
        <p>Source: {market.source}</p>
        <p>Last Updated: {new Date(market.last_updated).toLocaleString()}</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">NSE (National Stock Exchange)</h3>
          <div className="text-center">
            <p className={`text-2xl font-bold ${market.nse.is_open ? 'text-green-600' : 'text-red-600'}`}>
              {market.nse.is_open ? '🟢 OPEN' : '🔴 CLOSED'}
            </p>
            <p className="text-sm text-gray-600">
              Last Updated: {new Date(market.nse.last_updated).toLocaleString()}
            </p>
          </div>
        </div>
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">BSE (Bombay Stock Exchange)</h3>
          <div className="text-center">
            <p className={`text-2xl font-bold ${market.bse.is_open ? 'text-green-600' : 'text-red-600'}`}>
              {market.bse.is_open ? '🟢 OPEN' : '🔴 CLOSED'}
            </p>
            <p className="text-sm text-gray-600">
              Last Updated: {new Date(market.bse.last_updated).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderData = () => {
    if (!data) return null;

    switch (activeTab) {
      case 'status':
        return renderStatusData(data as AngelOneStatus);
      case 'quote':
        return renderQuoteData(data as AngelOneQuote);
      case 'historical':
        return renderHistoricalData(data as AngelOneHistorical);
      case 'indices':
        return renderIndicesData(data as AngelOneIndices);
      case 'market':
        return renderMarketData(data as AngelOneMarketStatus);
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Angel One Data</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>
        
        <div className="p-6">
          <div className="flex space-x-1 mb-6 border-b border-gray-200">
            {[
              { key: 'status', label: 'Status' },
              { key: 'quote', label: 'Quote' },
              { key: 'historical', label: 'Historical' },
              { key: 'indices', label: 'Indices' },
              { key: 'market', label: 'Market' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-4 py-2 text-sm font-medium border-b-2 ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {(activeTab === 'quote' || activeTab === 'historical') && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Symbol
              </label>
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="RELIANCE.NS">RELIANCE.NS</option>
                <option value="TCS.NS">TCS.NS</option>
                <option value="HDFCBANK.NS">HDFCBANK.NS</option>
                <option value="INFY.NS">INFY.NS</option>
                <option value="HINDUNILVR.NS">HINDUNILVR.NS</option>
                <option value="ITC.NS">ITC.NS</option>
                <option value="SBIN.NS">SBIN.NS</option>
                <option value="BHARTIARTL.NS">BHARTIARTL.NS</option>
                <option value="KOTAKBANK.NS">KOTAKBANK.NS</option>
                <option value="LT.NS">LT.NS</option>
              </select>
            </div>
          )}

          {loading && <LoadingSpinner />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && renderData()}
        </div>
      </div>
    </div>
  );
};

export default AngelOnePanel;
