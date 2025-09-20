```tsx
import React from 'react';
import { Signal } from '../types';

interface AISignalCardProps {
  signal: Signal;
}

export const AISignalCard: React.FC<AISignalCardProps> = ({ signal }) => {
  const getSignalColor = (signalType: string) => {
    switch (signalType.toUpperCase()) {
      case 'BUY':
        return {
          bg: 'bg-green-100',
          text: 'text-green-800',
          border: 'border-green-200',
          icon: '↗️'
        };
      case 'SELL':
        return {
          bg: 'bg-red-100',
          text: 'text-red-800',
          border: 'border-red-200',
          icon: '↘️'
        };
      case 'HOLD':
        return {
          bg: 'bg-yellow-100',
          text: 'text-yellow-800',
          border: 'border-yellow-200',
          icon: '➖'
        };
      default:
        return {
          bg: 'bg-gray-100',
          text: 'text-gray-800',
          border: 'border-gray-200',
          icon: '❓'
        };
    }
  };

  const signalStyle = getSignalColor(signal.signal);

  return (
    <div className={`rounded-lg border-2 ${signalStyle.border} ${signalStyle.bg} p-4 mb-4`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {signal.ticker}
          </h3>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${signalStyle.bg} ${signalStyle.text} mt-1`}>
            <span className="mr-1">{signalStyle.icon}</span>
            {signal.signal.toUpperCase()}
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">AI Generated</p>
          <p className="text-xs text-gray-400">
            {new Date(signal.generated_at).toLocaleTimeString()}
          </p>
        </div>
      </div>

      {/* Signals List */}
      {signal.signals && signal.signals.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Technical Signals:
          </h4>
          <div className="flex flex-wrap gap-1">
            {signal.signals.map((sig, index) => (
              <span
                key={index}
                className="inline-block px-2 py-1 bg-white rounded text-xs text-gray-600 border"
              >
                {sig}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* AI Reasoning */}
      {signal.reasoning && signal.reasoning.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            🤖 AI Analysis:
          </h4>
          <div className="space-y-2">
            {signal.reasoning.map((reason, index) => (
              <div key={index} className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-sm text-gray-700">{reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Confidence Indicator */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-500">AI Confidence</span>
          <div className="flex items-center space-x-2">
            <div className="w-16 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  signal.signal.toUpperCase() === 'BUY' ? 'bg-green-500' :
                  signal.signal.toUpperCase() === 'SELL' ? 'bg-red-500' :
                  'bg-yellow-500'
                }`}
                style={{ width: '75%' }} // You can make this dynamic based on actual confidence
              ></div>
            </div>
            <span className="text-xs font-medium text-gray-700">High</span>
          </div>
        </div>
      </div>
    </div>
  );
};
```