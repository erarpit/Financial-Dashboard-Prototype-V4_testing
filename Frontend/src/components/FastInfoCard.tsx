import React from 'react';

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

interface FastInfoCardProps {
  data: FastInfoData;
}

const FastInfoCard: React.FC<FastInfoCardProps> = ({ data }) => {
  const formatNumber = (value?: number) => {
    if (value === undefined || value === null) return 'N/A';
    if (value >= 1e12) return `₹${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `₹${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `₹${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `₹${(value / 1e3).toFixed(2)}K`;
    return `₹${value.toFixed(2)}`;
  };

  const formatVolume = (value?: number) => {
    if (value === undefined || value === null) return 'N/A';
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value.toLocaleString();
  };

  const formatPercentage = (value?: number) => {
    if (value === undefined || value === null) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  const getPriceChangeColor = (current?: number, previous?: number) => {
    if (!current || !previous) return 'text-gray-600';
    return current > previous ? 'text-green-600' : current < previous ? 'text-red-600' : 'text-gray-600';
  };

  const getPriceChangeIcon = (current?: number, previous?: number) => {
    if (!current || !previous) return '→';
    return current > previous ? '↗' : current < previous ? '↘' : '→';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            {data.symbol}
          </h3>
          <p className="text-sm text-gray-500">
            {data.exchange} • {data.currency} • {data.quote_type}
          </p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">
            {formatNumber(data.last_price)}
          </p>
          <div className={`flex items-center text-sm ${getPriceChangeColor(data.last_price, data.previous_close)}`}>
            <span className="mr-1">{getPriceChangeIcon(data.last_price, data.previous_close)}</span>
            <span>
              {data.last_price && data.previous_close 
                ? `${((data.last_price - data.previous_close) / data.previous_close * 100).toFixed(2)}%`
                : 'N/A'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Price Information */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Previous Close</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(data.previous_close)}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Open</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(data.open_price)}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Day High</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(data.day_high)}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Day Low</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(data.day_low)}
          </p>
        </div>
      </div>

      {/* Volume Information */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-3">Volume & Trading</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm text-blue-600">Last Volume</p>
            <p className="text-lg font-semibold text-blue-900">
              {formatVolume(data.last_volume)}
            </p>
          </div>
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm text-blue-600">10-Day Avg Volume</p>
            <p className="text-lg font-semibold text-blue-900">
              {formatVolume(data.ten_day_average_volume)}
            </p>
          </div>
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm text-blue-600">3-Month Avg Volume</p>
            <p className="text-lg font-semibold text-blue-900">
              {formatVolume(data.three_month_average_volume)}
            </p>
          </div>
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm text-blue-600">Market Cap</p>
            <p className="text-lg font-semibold text-blue-900">
              {formatNumber(data.market_cap)}
            </p>
          </div>
        </div>
      </div>

      {/* Technical Indicators */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-3">Technical Indicators</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-green-50 p-3 rounded-lg">
            <p className="text-sm text-green-600">50-Day Average</p>
            <p className="text-lg font-semibold text-green-900">
              {formatNumber(data.fifty_day_average)}
            </p>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <p className="text-sm text-green-600">200-Day Average</p>
            <p className="text-lg font-semibold text-green-900">
              {formatNumber(data.two_hundred_day_average)}
            </p>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <p className="text-sm text-green-600">52-Week High</p>
            <p className="text-lg font-semibold text-green-900">
              {formatNumber(data.year_high)}
            </p>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <p className="text-sm text-green-600">52-Week Low</p>
            <p className="text-lg font-semibold text-green-900">
              {formatNumber(data.year_low)}
            </p>
          </div>
        </div>
      </div>

      {/* Year Change */}
      {data.year_change !== undefined && data.year_change !== null && (
        <div className="mb-4">
          <div className="bg-purple-50 p-3 rounded-lg">
            <p className="text-sm text-purple-600">Year Change</p>
            <p className={`text-lg font-semibold ${data.year_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercentage(data.year_change)}
            </p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>Shares: {data.shares ? data.shares.toLocaleString() : 'N/A'}</span>
          <span>Last updated: {new Date(data.last_updated).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};

export default FastInfoCard;
