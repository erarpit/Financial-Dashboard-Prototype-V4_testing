// src/components/Dashboard.tsx

import React, { useState } from 'react';
import { useDashboardData } from '../hooks/useApi';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

// Lazy load components to avoid import errors if files are missing or to improve performance
const StockGrid = React.lazy(() => import('./StockGrid'));
const SignalsPanel = React.lazy(() => import('./SignalsPanel'));
const NewsPanel = React.lazy(() => import('./NewsPanel'));
const AIChat = React.lazy(() => import('./AIChat'));
const AlphaVantagePanel = React.lazy(() => import('./AlphaVantagePanel'));
const CurrencyPanel = React.lazy(() => import('./CurrencyPanel'));
const AngelOnePanel = React.lazy(() => import('./AngelOnePanel'));

interface DashboardProps {
  tickers: string[];
  onStockSelect: (ticker: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ tickers, onStockSelect }) => {
  const { data, loading, error } = useDashboardData(tickers);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [showAlphaVantage, setShowAlphaVantage] = useState(false);
  const [showCurrency, setShowCurrency] = useState(false);
  const [showAngelOne, setShowAngelOne] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <ErrorMessage message={error} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Data Available</h2>
          <p className="text-gray-600">Please check your connection and try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">AI Financial Dashboard</h1>
          <div className="flex items-center space-x-4">
            <div className="flex space-x-2">
              <button
                onClick={() => setShowAlphaVantage(true)}
                className="px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Alpha Vantage
              </button>
              <button
                onClick={() => setShowCurrency(true)}
                className="px-3 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Currency
              </button>
              <button
                onClick={() => setShowAngelOne(true)}
                className="px-3 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                Angel One
              </button>
            </div>
            <span className="text-sm text-gray-500">
              Last updated: {new Date(data.timestamp).toLocaleString()}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stock Grid */}
        <section className="lg:col-span-2 bg-white rounded-lg shadow p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Stock Portfolio</h2>
            <span className="text-sm text-gray-500">{data.stocks.length} stocks</span>
          </div>
          <StockGrid stocks={data.stocks} onSelect={(ticker) => {
            setSelectedSymbol(ticker);
            onStockSelect(ticker);
          }} />
        </section>

        {/* Side Panel */}
        <aside className="space-y-6">
          <section className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">AI Trading Signals</h2>
            <SignalsPanel signals={data.signals} />
          </section>
          <section className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">Market Sentiment</h2>
            <NewsPanel news={data.news} />
          </section>
          <section className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">AI Assistant</h2>
            <React.Suspense fallback={<LoadingSpinner />}>
              <AIChat />
            </React.Suspense>
          </section>
        </aside>
      </main>

      {/* API Panels */}
      {showAlphaVantage && (
        <React.Suspense fallback={<LoadingSpinner />}>
          <AlphaVantagePanel 
            symbol={selectedSymbol || 'RELIANCE.NS'} 
            onClose={() => setShowAlphaVantage(false)} 
          />
        </React.Suspense>
      )}
      
      {showCurrency && (
        <React.Suspense fallback={<LoadingSpinner />}>
          <CurrencyPanel onClose={() => setShowCurrency(false)} />
        </React.Suspense>
      )}
      
      {showAngelOne && (
        <React.Suspense fallback={<LoadingSpinner />}>
          <AngelOnePanel 
            symbol={selectedSymbol || 'RELIANCE.NS'} 
            onClose={() => setShowAngelOne(false)} 
          />
        </React.Suspense>
      )}
    </div>
  );
};

export default Dashboard;
