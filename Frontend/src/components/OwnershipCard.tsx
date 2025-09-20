import React from 'react';

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

interface OwnershipCardProps {
  data: OwnershipData;
}

const OwnershipCard: React.FC<OwnershipCardProps> = ({ data }) => {
  const formatNumber = (value: number) => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
    return value.toFixed(0);
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">
          Ownership Analysis - {data.symbol}
        </h3>
        <span className="text-sm text-gray-500">
          {new Date(data.last_updated).toLocaleString()}
        </span>
      </div>

      {/* Major Holders Breakdown */}
      {Object.keys(data.major_holders_breakdown).length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">Major Holders Breakdown</h4>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(data.major_holders_breakdown).map(([key, value]) => (
              <div key={key} className="bg-gray-50 p-3 rounded-lg">
                <p className="text-sm text-gray-600 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</p>
                <p className="text-lg font-semibold text-gray-900">
                  {typeof value === 'number' ? formatNumber(value) : value}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Institutional Holders */}
      {data.institutional_holders.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">Top Institutional Holders</h4>
          <div className="space-y-2">
            {data.institutional_holders.slice(0, 5).map((holder, index) => (
              <div key={index} className="flex items-center justify-between py-2 px-3 bg-blue-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900">{holder.Holder}</p>
                  <p className="text-xs text-blue-600">{formatDate(holder['Date Reported'])}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-blue-900">{formatNumber(holder.Shares)} shares</p>
                  <p className="text-xs text-blue-600">${formatNumber(holder.Value)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insider Transactions */}
      {data.insider_transactions.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">Recent Insider Transactions</h4>
          <div className="space-y-2">
            {data.insider_transactions.slice(0, 5).map((transaction, index) => (
              <div key={index} className="flex items-center justify-between py-2 px-3 bg-yellow-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-yellow-900">{transaction.Insider}</p>
                  <p className="text-xs text-yellow-600">{transaction.Position}</p>
                  <p className="text-xs text-yellow-600">{formatDate(transaction['Start Date'])}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-yellow-900">{transaction.Transaction}</p>
                  {transaction.Shares && (
                    <p className="text-xs text-yellow-600">{formatNumber(transaction.Shares)} shares</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insider Roster */}
      {data.insider_roster.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">Key Insiders</h4>
          <div className="space-y-2">
            {data.insider_roster.slice(0, 5).map((insider, index) => (
              <div key={index} className="flex items-center justify-between py-2 px-3 bg-green-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-900">{insider.Name}</p>
                  <p className="text-xs text-green-600">{insider.Position}</p>
                  <p className="text-xs text-green-600">{insider['Most Recent Transaction']}</p>
                </div>
                <div className="text-right">
                  {insider['Shares Owned Directly'] && (
                    <p className="text-sm font-medium text-green-900">
                      {formatNumber(insider['Shares Owned Directly'])} direct
                    </p>
                  )}
                  {insider['Shares Owned Indirectly'] && (
                    <p className="text-xs text-green-600">
                      {formatNumber(insider['Shares Owned Indirectly'])} indirect
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Mutual Fund Holders */}
      {data.mutual_fund_holders.length > 0 && (
        <div className="mb-4">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">Top Mutual Fund Holders</h4>
          <div className="space-y-2">
            {data.mutual_fund_holders.slice(0, 3).map((fund, index) => (
              <div key={index} className="flex items-center justify-between py-2 px-3 bg-purple-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-purple-900">{fund.Holder}</p>
                  <p className="text-xs text-purple-600">{formatDate(fund['Date Reported'])}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-purple-900">{formatNumber(fund.Shares)} shares</p>
                  <p className="text-xs text-purple-600">${formatNumber(fund.Value)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OwnershipCard;
