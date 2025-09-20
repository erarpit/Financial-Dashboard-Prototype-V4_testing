import React, { useState, useEffect } from 'react';
import { 
  getAlphaVantageQuote, 
  getAlphaVantageDaily, 
  getAlphaVantageIntraday, 
  getAlphaVantageIndicators,
  getAlphaVantageOverview,
  getAlphaVantageEarnings,
  getAlphaVantageNews
} from '../api';
import { 
  AlphaVantageQuote, 
  AlphaVantageDailyData, 
  AlphaVantageIntradayData, 
  AlphaVantageIndicators,
  AlphaVantageOverview,
  AlphaVantageEarnings,
  AlphaVantageNews
} from '../types';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface AlphaVantagePanelProps {
  symbol: string;
  onClose: () => void;
}

const AlphaVantagePanel: React.FC<AlphaVantagePanelProps> = ({ symbol, onClose }) => {
  const [activeTab, setActiveTab] = useState<'quote' | 'daily' | 'intraday' | 'indicators' | 'overview' | 'earnings' | 'news'>('quote');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let result;
      switch (activeTab) {
        case 'quote':
          result = await getAlphaVantageQuote(symbol);
          break;
        case 'daily':
          result = await getAlphaVantageDaily(symbol);
          break;
        case 'intraday':
          result = await getAlphaVantageIntraday(symbol);
          break;
        case 'indicators':
          result = await getAlphaVantageIndicators(symbol);
          break;
        case 'overview':
          result = await getAlphaVantageOverview(symbol);
          break;
        case 'earnings':
          result = await getAlphaVantageEarnings(symbol);
          break;
        case 'news':
          result = await getAlphaVantageNews(symbol);
          break;
        default:
          result = await getAlphaVantageQuote(symbol);
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
  }, [activeTab, symbol]);

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

  const renderQuoteData = (quote: AlphaVantageQuote) => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Current Price</h3>
          <p className="text-2xl font-bold text-gray-900">{formatPrice(quote.price)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Change</h3>
          <p className={`text-xl font-semibold ${quote.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatPrice(quote.change)} ({formatPercentage(quote.change_percent)})
          </p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Volume</h3>
          <p className="text-lg font-semibold text-gray-900">{formatNumber(quote.volume)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Market Cap</h3>
          <p className="text-lg font-semibold text-gray-900">
            {quote.market_cap ? formatPrice(quote.market_cap) : 'N/A'}
          </p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Day High</h3>
          <p className="text-lg font-semibold text-gray-900">{formatPrice(quote.high)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Day Low</h3>
          <p className="text-lg font-semibold text-gray-900">{formatPrice(quote.low)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Open</h3>
          <p className="text-lg font-semibold text-gray-900">{formatPrice(quote.open)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Previous Close</h3>
          <p className="text-lg font-semibold text-gray-900">{formatPrice(quote.previous_close)}</p>
        </div>
      </div>
      <div className="text-sm text-gray-500">
        <p>Source: {quote.source}</p>
        <p>Last Updated: {new Date(quote.last_updated).toLocaleString()}</p>
      </div>
    </div>
  );

  const renderDailyData = (daily: AlphaVantageDailyData) => (
    <div className="space-y-4">
      <div className="text-sm text-gray-500">
        <p>Data Points: {daily.count}</p>
        <p>Source: {daily.source}</p>
        <p>Last Updated: {new Date(daily.last_updated).toLocaleString()}</p>
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
            {daily.data.slice(0, 10).map((row, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(row.Date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.Open)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.High)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.Low)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.Close)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(row.Volume)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderIndicatorsData = (indicators: AlphaVantageIndicators) => (
    <div className="space-y-4">
      <div className="text-sm text-gray-500">
        <p>Function: {indicators.function}</p>
        <p>Interval: {indicators.interval}</p>
        <p>Time Period: {indicators.time_period}</p>
        <p>Series Type: {indicators.series_type}</p>
        <p>Source: {indicators.source}</p>
        <p>Last Updated: {new Date(indicators.last_updated).toLocaleString()}</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              {Object.keys(indicators.data[0] || {}).filter(key => key !== 'Date').map(key => (
                <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {indicators.data.slice(0, 10).map((row, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(row.Date).toLocaleDateString()}
                </td>
                {Object.entries(row).filter(([key]) => key !== 'Date').map(([key, value]) => (
                  <td key={key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {typeof value === 'number' ? value.toFixed(4) : value}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderOverviewData = (overview: AlphaVantageOverview) => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Company Name</h3>
          <p className="text-lg font-semibold text-gray-900">{overview.name}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Sector</h3>
          <p className="text-lg font-semibold text-gray-900">{overview.sector}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Industry</h3>
          <p className="text-lg font-semibold text-gray-900">{overview.industry}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Market Cap</h3>
          <p className="text-lg font-semibold text-gray-900">{formatPrice(overview.market_cap)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">P/E Ratio</h3>
          <p className="text-lg font-semibold text-gray-900">{overview.pe_ratio?.toFixed(2) || 'N/A'}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">EPS</h3>
          <p className="text-lg font-semibold text-gray-900">{overview.eps?.toFixed(2) || 'N/A'}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Dividend Yield</h3>
          <p className="text-lg font-semibold text-gray-900">{overview.dividend_yield?.toFixed(2) || 'N/A'}%</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Beta</h3>
          <p className="text-lg font-semibold text-gray-900">{overview.beta?.toFixed(2) || 'N/A'}</p>
        </div>
      </div>
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-sm font-medium text-gray-500 mb-2">Description</h3>
        <p className="text-sm text-gray-700">{overview.description}</p>
      </div>
      <div className="text-sm text-gray-500">
        <p>Source: {overview.source}</p>
        <p>Last Updated: {new Date(overview.last_updated).toLocaleString()}</p>
      </div>
    </div>
  );

  const renderEarningsData = (earnings: AlphaVantageEarnings) => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Next Earnings Date</h3>
          <p className="text-lg font-semibold text-gray-900">{earnings.next_earnings_date}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Estimated EPS</h3>
          <p className="text-lg font-semibold text-gray-900">{earnings.estimated_eps?.toFixed(2) || 'N/A'}</p>
        </div>
      </div>
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-sm font-medium text-gray-500 mb-2">Earnings History</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quarter</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">EPS</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {earnings.earnings_history.map((row, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.quarter}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.eps.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatPrice(row.revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="text-sm text-gray-500">
        <p>Source: {earnings.source}</p>
        <p>Last Updated: {new Date(earnings.last_updated).toLocaleString()}</p>
      </div>
    </div>
  );

  const renderNewsData = (news: AlphaVantageNews) => (
    <div className="space-y-4">
      <div className="text-sm text-gray-500">
        <p>News Items: {news.news_items.length}</p>
        <p>Source: {news.source}</p>
        <p>Last Updated: {new Date(news.last_updated).toLocaleString()}</p>
      </div>
      <div className="space-y-4">
        {news.news_items.slice(0, 5).map((item, index) => (
          <div key={index} className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h3>
            <p className="text-sm text-gray-600 mb-2">{item.summary}</p>
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{item.source} • {new Date(item.time_published).toLocaleDateString()}</span>
              <span className={`px-2 py-1 rounded ${
                item.overall_sentiment_label === 'Bullish' ? 'bg-green-100 text-green-800' :
                item.overall_sentiment_label === 'Bearish' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {item.overall_sentiment_label}
              </span>
            </div>
            <a 
              href={item.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Read more →
            </a>
          </div>
        ))}
      </div>
    </div>
  );

  const renderData = () => {
    if (!data) return null;

    switch (activeTab) {
      case 'quote':
        return renderQuoteData(data as AlphaVantageQuote);
      case 'daily':
        return renderDailyData(data as AlphaVantageDailyData);
      case 'intraday':
        return renderDailyData(data as AlphaVantageIntradayData); // Similar structure
      case 'indicators':
        return renderIndicatorsData(data as AlphaVantageIndicators);
      case 'overview':
        return renderOverviewData(data as AlphaVantageOverview);
      case 'earnings':
        return renderEarningsData(data as AlphaVantageEarnings);
      case 'news':
        return renderNewsData(data as AlphaVantageNews);
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Alpha Vantage Data - {symbol}</h2>
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
              { key: 'quote', label: 'Quote' },
              { key: 'daily', label: 'Daily' },
              { key: 'intraday', label: 'Intraday' },
              { key: 'indicators', label: 'Indicators' },
              { key: 'overview', label: 'Overview' },
              { key: 'earnings', label: 'Earnings' },
              { key: 'news', label: 'News' }
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

          {loading && <LoadingSpinner />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && renderData()}
        </div>
      </div>
    </div>
  );
};

export default AlphaVantagePanel;
