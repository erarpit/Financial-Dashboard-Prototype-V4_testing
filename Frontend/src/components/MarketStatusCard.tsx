import React from 'react';

interface MarketStatusProps {
  market: string;
  is_open: boolean;
  open_time?: string;
  close_time?: string;
  timezone?: string;
  last_updated: string;
}

const MarketStatusCard: React.FC<MarketStatusProps> = ({
  market,
  is_open,
  open_time,
  close_time,
  timezone,
  last_updated
}) => {
  const formatTime = (timeString?: string) => {
    if (!timeString) return 'N/A';
    try {
      return new Date(timeString).toLocaleTimeString();
    } catch {
      return timeString;
    }
  };

  const getStatusColor = (isOpen: boolean) => {
    return isOpen 
      ? 'text-green-600 bg-green-100' 
      : 'text-red-600 bg-red-100';
  };

  const getStatusText = (isOpen: boolean) => {
    return isOpen ? 'OPEN' : 'CLOSED';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900 capitalize">
          {market} Market
        </h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(is_open)}`}>
          {getStatusText(is_open)}
        </span>
      </div>

      {/* Market Hours */}
      <div className="space-y-3">
        <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
          <span className="text-sm font-medium text-gray-600">Open Time</span>
          <span className="text-sm text-gray-900">{formatTime(open_time)}</span>
        </div>
        
        <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
          <span className="text-sm font-medium text-gray-600">Close Time</span>
          <span className="text-sm text-gray-900">{formatTime(close_time)}</span>
        </div>
        
        {timezone && (
          <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-600">Timezone</span>
            <span className="text-sm text-gray-900">{timezone}</span>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="pt-4 border-t border-gray-200 mt-4">
        <p className="text-xs text-gray-500">
          Last updated: {new Date(last_updated).toLocaleString()}
        </p>
      </div>
    </div>
  );
};

export default MarketStatusCard;
