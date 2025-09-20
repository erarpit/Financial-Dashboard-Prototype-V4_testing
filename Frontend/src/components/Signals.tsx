import React from 'react'
import { Signal as SignalType } from '../types'

interface SignalsProps {
  signals: SignalType[]
}

const Signals: React.FC<SignalsProps> = ({ signals }) => {
  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'STRONG_BUY':
        return 'bg-green-100 border-green-400 text-green-800'
      case 'BUY':
        return 'bg-green-50 border-green-300 text-green-700'
      case 'STRONG_SELL':
        return 'bg-red-100 border-red-400 text-red-800'
      case 'SELL':
        return 'bg-red-50 border-red-300 text-red-700'
      default:
        return 'bg-gray-100 border-gray-300 text-gray-700'
    }
  }

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'STRONG_BUY':
      case 'BUY':
        return '📈'
      case 'STRONG_SELL':
      case 'SELL':
        return '📉'
      default:
        return '📊'
    }
  }

  if (!signals || signals.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Trading Signals</h2>
        <div className="text-gray-500">No signals available</div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h2 className="text-lg font-semibold mb-4">Trading Signals</h2>
      <div className="space-y-3">
        {signals.map((signal, index) => (
          <div key={index} className={`border-2 rounded-lg p-3 ${getSignalColor(signal.signal)}`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                <span className="text-xl mr-2">{getSignalIcon(signal.signal)}</span>
                <h3 className="font-semibold">{signal.ticker}</h3>
              </div>
              <span className="font-bold">{signal.signal}</span>
            </div>
            
            {signal.reasoning.length > 0 && (
              <div className="text-sm">
                <p className="font-medium mb-1">Reasoning:</p>
                <ul className="list-disc list-inside space-y-1">
                  {signal.reasoning.map((reason, i) => (
                    <li key={i} className="text-xs">{reason}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Signals