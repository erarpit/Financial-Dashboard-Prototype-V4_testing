import React from 'react';
import StockCard from './StockCard';
import { StockData } from '../types';

interface StockGridProps {
  stocks: StockData[];
  onSelect: (ticker: string) => void;
}

const StockGrid: React.FC<StockGridProps> = ({ stocks, onSelect }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {stocks.map((stock) => (
        <StockCard
          key={stock.ticker}
          stock={stock}
          onClick={() => onSelect(stock.ticker)}
        />
      ))}
    </div>
  );
};

export default StockGrid;
