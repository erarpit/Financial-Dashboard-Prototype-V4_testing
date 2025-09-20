import React from 'react';

interface TopCompany {
  symbol: string;
  name: string;
  rating?: string;
  market_weight?: number;
}

interface DomainOverview {
  companies_count?: number;
  market_cap?: number;
  description?: string;
  industries_count?: number;
  market_weight?: number;
  employee_count?: number;
}

interface DomainCardProps {
  key: string;
  name: string;
  symbol: string;
  overview: DomainOverview;
  top_companies: TopCompany[];
  research_reports: Array<{
    title: string;
    url: string;
    date: string;
  }>;
  last_updated: string;
  type: 'sector' | 'industry';
}

const DomainCard: React.FC<DomainCardProps> = ({
  key,
  name,
  symbol,
  overview,
  top_companies,
  research_reports,
  last_updated,
  type
}) => {
  const formatMarketCap = (value?: number) => {
    if (!value) return 'N/A';
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    return `$${value.toFixed(0)}`;
  };

  const formatNumber = (value?: number) => {
    if (!value) return 'N/A';
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
    return value.toFixed(0);
  };

  const getRatingColor = (rating?: string) => {
    switch (rating?.toUpperCase()) {
      case 'BUY': return 'text-green-600 bg-green-100';
      case 'HOLD': return 'text-yellow-600 bg-yellow-100';
      case 'SELL': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{name}</h3>
          <p className="text-sm text-gray-500 uppercase tracking-wide">{symbol}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          type === 'sector' 
            ? 'bg-blue-100 text-blue-800' 
            : 'bg-purple-100 text-purple-800'
        }`}>
          {type}
        </span>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Companies</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(overview.companies_count)}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Market Cap</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatMarketCap(overview.market_cap)}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Market Weight</p>
          <p className="text-lg font-semibold text-gray-900">
            {overview.market_weight ? `${overview.market_weight}%` : 'N/A'}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">Employees</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(overview.employee_count)}
          </p>
        </div>
      </div>

      {/* Description */}
      {overview.description && (
        <div className="mb-6">
          <p className="text-sm text-gray-700 leading-relaxed">
            {overview.description}
          </p>
        </div>
      )}

      {/* Top Companies */}
      {top_companies && top_companies.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Top Companies</h4>
          <div className="space-y-2">
            {top_companies.slice(0, 5).map((company, index) => (
              <div key={index} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{company.name}</p>
                  <p className="text-xs text-gray-500">{company.symbol}</p>
                </div>
                <div className="flex items-center space-x-2">
                  {company.market_weight && (
                    <span className="text-xs text-gray-600">
                      {company.market_weight}%
                    </span>
                  )}
                  {company.rating && (
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getRatingColor(company.rating)}`}>
                      {company.rating}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Research Reports */}
      {research_reports && research_reports.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Research Reports</h4>
          <div className="space-y-2">
            {research_reports.slice(0, 3).map((report, index) => (
              <div key={index} className="flex items-center justify-between py-2 px-3 bg-blue-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900">{report.title}</p>
                  <p className="text-xs text-blue-600">{report.date}</p>
                </div>
                <a 
                  href={report.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                >
                  View →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Last updated: {new Date(last_updated).toLocaleString()}
        </p>
      </div>
    </div>
  );
};

export default DomainCard;
