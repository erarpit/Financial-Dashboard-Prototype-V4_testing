import React, { useState, useEffect } from 'react';
import { getCurrencyRate, convertCurrency, formatCurrency } from '../api';
import { CurrencyRate, CurrencyConvert, CurrencyFormat } from '../types';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface CurrencyPanelProps {
  onClose: () => void;
}

const CurrencyPanel: React.FC<CurrencyPanelProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<'rate' | 'convert' | 'format'>('rate');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);
  const [convertAmount, setConvertAmount] = useState<number>(100);
  const [formatAmount, setFormatAmount] = useState<number>(1000);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let result;
      switch (activeTab) {
        case 'rate':
          result = await getCurrencyRate();
          break;
        case 'convert':
          result = await convertCurrency(convertAmount);
          break;
        case 'format':
          result = await formatCurrency(formatAmount);
          break;
        default:
          result = await getCurrencyRate();
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
  }, [activeTab, convertAmount, formatAmount]);

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

  const renderRateData = (rate: CurrencyRate) => (
    <div className="space-y-4">
      <div className="bg-blue-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Current Exchange Rate</h3>
        <p className="text-3xl font-bold text-blue-900">
          {formatPrice(rate.usd_to_inr_rate)}
        </p>
        <p className="text-sm text-blue-700">1 USD = {formatPrice(rate.usd_to_inr_rate)} INR</p>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Cache Duration</h3>
          <p className="text-lg font-semibold text-gray-900">{rate.cache_duration_seconds} seconds</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">API Key Status</h3>
          <p className={`text-lg font-semibold ${rate.api_key_configured ? 'text-green-600' : 'text-red-600'}`}>
            {rate.api_key_configured ? 'Configured' : 'Not Configured'}
          </p>
        </div>
      </div>
      
      <div className="text-sm text-gray-500">
        <p>Last Updated: {new Date(rate.last_updated).toLocaleString()}</p>
      </div>
    </div>
  );

  const renderConvertData = (convert: CurrencyConvert) => (
    <div className="space-y-4">
      <div className="bg-green-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-green-900 mb-2">Currency Conversion</h3>
        <div className="text-center">
          <p className="text-2xl font-bold text-green-900">
            {formatNumber(convert.original_amount)} {convert.original_currency} = {formatPrice(convert.converted_amount)}
          </p>
          <p className="text-sm text-green-700">Exchange Rate: {convert.exchange_rate.toFixed(4)}</p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Original Amount</h3>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(convert.original_amount)} {convert.original_currency}
          </p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Converted Amount</h3>
          <p className="text-lg font-semibold text-gray-900">
            {formatNumber(convert.converted_amount)} {convert.converted_currency}
          </p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Formatted Amount</h3>
          <p className="text-lg font-semibold text-gray-900">{convert.formatted_amount}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Exchange Rate</h3>
          <p className="text-lg font-semibold text-gray-900">{convert.exchange_rate.toFixed(4)}</p>
        </div>
      </div>
      
      <div className="text-sm text-gray-500">
        <p>Last Updated: {new Date(convert.last_updated).toLocaleString()}</p>
      </div>
    </div>
  );

  const renderFormatData = (format: CurrencyFormat) => (
    <div className="space-y-4">
      <div className="bg-purple-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-purple-900 mb-2">Currency Formatting</h3>
        <div className="text-center">
          <p className="text-2xl font-bold text-purple-900">{format.formatted}</p>
          <p className="text-sm text-purple-700">
            {formatNumber(format.amount)} {format.currency} formatted with {format.decimals} decimals
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Original Amount</h3>
          <p className="text-lg font-semibold text-gray-900">{formatNumber(format.amount)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Currency</h3>
          <p className="text-lg font-semibold text-gray-900">{format.currency}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Formatted</h3>
          <p className="text-lg font-semibold text-gray-900">{format.formatted}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Decimals</h3>
          <p className="text-lg font-semibold text-gray-900">{format.decimals}</p>
        </div>
      </div>
    </div>
  );

  const renderData = () => {
    if (!data) return null;

    switch (activeTab) {
      case 'rate':
        return renderRateData(data as CurrencyRate);
      case 'convert':
        return renderConvertData(data as CurrencyConvert);
      case 'format':
        return renderFormatData(data as CurrencyFormat);
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Currency Tools</h2>
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
              { key: 'rate', label: 'Exchange Rate' },
              { key: 'convert', label: 'Convert' },
              { key: 'format', label: 'Format' }
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

          {activeTab === 'convert' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount to Convert (USD)
              </label>
              <input
                type="number"
                value={convertAmount}
                onChange={(e) => setConvertAmount(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                step="0.01"
              />
            </div>
          )}

          {activeTab === 'format' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount to Format (INR)
              </label>
              <input
                type="number"
                value={formatAmount}
                onChange={(e) => setFormatAmount(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                step="0.01"
              />
            </div>
          )}

          {loading && <LoadingSpinner />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && renderData()}
        </div>
      </div>
    </div>
  );
};

export default CurrencyPanel;
