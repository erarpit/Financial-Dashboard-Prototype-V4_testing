import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import DomainPanel from './components/DomainPanel';
import MarketStatusPanel from './components/MarketStatusPanel';
import OwnershipPanel from './components/OwnershipPanel';
import FastInfoPanel from './components/FastInfoPanel';
import QuotePanel from './components/QuotePanel';
import QueryBuilder from './components/QueryBuilder';
import EnhancedDownloader from './components/EnhancedDownloader';
import StockModal from './components/StockModal';
import { getStockData } from './utils/stockUtils';

// Main App component with navigation
const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<'dashboard' | 'sectors' | 'industries' | 'market' | 'ownership' | 'fastinfo' | 'quote' | 'screener' | 'downloader'>('dashboard');
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [tickers, setTickers] = useState<string[]>(['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']);

  const handleStockSelect = (ticker: string) => {
    setSelectedStock(ticker);
  };

  const handleCloseModal = () => {
    setSelectedStock(null);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'sectors':
        return <DomainPanel type="sectors" />;
      case 'industries':
        return <DomainPanel type="industries" />;
      case 'market':
        return <MarketStatusPanel />;
      case 'ownership':
        return <OwnershipPanel />;
      case 'fastinfo':
        return <FastInfoPanel />;
      case 'quote':
        return <QuotePanel />;
      case 'screener':
        return <QueryBuilder />;
      case 'downloader':
        return <EnhancedDownloader />;
      case 'dashboard':
      default:
        return <Dashboard tickers={tickers} onStockSelect={handleStockSelect} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">AI Financial Dashboard</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'dashboard'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('sectors')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'sectors'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                Sectors
              </button>
              <button
                onClick={() => setCurrentView('industries')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'industries'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                Industries
              </button>
              <button
                onClick={() => setCurrentView('market')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'market'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                Market Status
              </button>
              <button
                onClick={() => setCurrentView('ownership')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'ownership'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                Ownership
              </button>
              <button
                onClick={() => setCurrentView('fastinfo')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'fastinfo'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                FastInfo
              </button>
              <button
                onClick={() => setCurrentView('quote')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'quote'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                Quote
              </button>
              <button
                onClick={() => setCurrentView('screener')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'screener'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                Stock Screener
              </button>
              <button
                onClick={() => setCurrentView('downloader')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'downloader'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                Enhanced Download
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        {renderCurrentView()}
      </main>

      {/* Stock Modal */}
      {selectedStock && (
        <StockModal
          ticker={selectedStock}
          isOpen={!!selectedStock}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default App;