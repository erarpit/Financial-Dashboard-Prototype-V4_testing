import React from 'react';

interface QuoteCardProps {
  data: {
    symbol: string;
    info: Record<string, any>;
    last_updated: string;
  };
}

const QuoteCard: React.FC<QuoteCardProps> = ({ data }) => {
  const formatNumber = (value?: any) => {
    if (value === undefined || value === null) return 'N/A';
    if (typeof value === 'number') {
      if (value >= 1e12) return `₹${(value / 1e12).toFixed(2)}T`;
      if (value >= 1e9) return `₹${(value / 1e9).toFixed(2)}B`;
      if (value >= 1e6) return `₹${(value / 1e6).toFixed(2)}M`;
      if (value >= 1e3) return `₹${(value / 1e3).toFixed(2)}K`;
      return `₹${value.toFixed(2)}`;
    }
    return String(value);
  };

  const formatPercentage = (value?: any) => {
    if (value === undefined || value === null) return 'N/A';
    if (typeof value === 'number') {
      return `${(value * 100).toFixed(2)}%`;
    }
    return String(value);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            {data.symbol} - Company Info
          </h3>
          <p className="text-sm text-gray-500">
            {data.info.longName || data.info.shortName || 'Company Information'}
          </p>
        </div>
        <span className="text-xs text-gray-500">
          {new Date(data.last_updated).toLocaleString()}
        </span>
      </div>

      {/* Basic Info */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Sector</p>
          <p className="text-lg font-semibold text-gray-900">
            {data.info.sector || 'N/A'}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Industry</p>
          <p className="text-lg font-semibold text-gray-900">
            {data.info.industry || 'N/A'}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Market Cap</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(data.info.marketCap)}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Employees</p>
          <p className="text-lg font-semibold text-gray-900">
            {data.info.fullTimeEmployees ? data.info.fullTimeEmployees.toLocaleString() : 'N/A'}
          </p>
        </div>
      </div>

      {/* Financial Metrics */}
      {data.info.financialData && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">Financial Data</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 p-3 rounded-lg">
              <p className="text-sm text-green-600">Total Revenue</p>
              <p className="text-lg font-semibold text-green-900">
                {formatNumber(data.info.financialData.totalRevenue)}
              </p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <p className="text-sm text-green-600">Net Income</p>
              <p className="text-lg font-semibold text-green-900">
                {formatNumber(data.info.financialData.netIncomeToCommon)}
              </p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <p className="text-sm text-green-600">ROE</p>
              <p className="text-lg font-semibold text-green-900">
                {formatPercentage(data.info.financialData.returnOnEquity)}
              </p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <p className="text-sm text-green-600">ROA</p>
              <p className="text-lg font-semibold text-green-900">
                {formatPercentage(data.info.financialData.returnOnAssets)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Company Description */}
      {data.info.longBusinessSummary && (
        <div className="mb-4">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">About</h4>
          <p className="text-sm text-gray-700 leading-relaxed">
            {data.info.longBusinessSummary.substring(0, 300)}
            {data.info.longBusinessSummary.length > 300 && '...'}
          </p>
        </div>
      )}

      {/* Website */}
      {data.info.website && (
        <div className="pt-4 border-t border-gray-200">
          <a 
            href={data.info.website} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Visit Company Website →
          </a>
        </div>
      )}
    </div>
  );
};

export default QuoteCard;
