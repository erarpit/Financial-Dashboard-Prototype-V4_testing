import React from 'react';
import { Signal } from '../types';

interface SignalsPanelProps {
  signals: Signal[];
}

const SignalsPanel: React.FC<SignalsPanelProps> = ({ signals }) => {
  const getSignalColor = (type: string) => {
    switch (type) {
      case 'buy': return 'text-green-600 bg-green-50';
      case 'sell': return 'text-red-600 bg-red-50';
      case 'hold': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="space-y-3">
      {signals.length === 0 ? (
        <p className="text-gray-500 text-sm">No signals available</p>
      ) : (
        signals.map((signal, index) => (
          <div key={index} className="p-3 border rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <span className="font-medium text-sm">{signal.ticker}</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getSignalColor(signal.signal)}`}>
                {signal.signal.toUpperCase()}
              </span>
            </div>
            <p className="text-xs text-gray-600 mb-2">{signal.reasoning.join(', ')}</p>
            <div className="flex justify-between items-center text-xs text-gray-500">
              <span>Signals: {signal.signals.join(', ')}</span>
              <span>{new Date(signal.generated_at).toLocaleTimeString()}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default SignalsPanel;
