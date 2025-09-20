import React from 'react';
import { StockData } from '../types';

interface StockCardProps {
  stock: StockData;
  onClick?: () => void;
}

const StockCard: React.FC<StockCardProps> = ({ stock, onClick }) => {
  const isPositive = stock.price_change_1d >= 0;
  
  return (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {stock.ticker}
          </h3>
          <p className="text-2xl font-bold text-gray-900">
            ${stock.price.toFixed(2)}
          </p>
        </div>
        <div className={`px-2 py-1 rounded text-xs font-medium ${
          isPositive ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
        }`}>
          {isPositive ? '+' : ''}{stock.price_change_1d.toFixed(2)}%
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500">1D Change</p>
          <p className={`text-sm font-medium ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            {isPositive ? '+' : ''}{stock.price_change_1d.toFixed(2)}%
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Volume</p>
          <p className="text-sm font-medium">
            {(stock.volume / 1000000).toFixed(1)}M
          </p>
        </div>
      </div>

      <div className="text-xs text-gray-400">
        RSI: {stock.rsi.toFixed(1)} | Trend: {stock.trend}
      </div>
    </div>
  );
};

export default StockCard;