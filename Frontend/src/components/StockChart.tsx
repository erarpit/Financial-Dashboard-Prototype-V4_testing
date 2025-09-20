import React from 'react'
import Plot from 'react-plotly.js'
import { StockData } from '../types'

interface StockChartProps {
  ticker: string
  data: StockData | undefined
}

const StockChart: React.FC<StockChartProps> = ({ ticker, data }) => {
  if (!data) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">{ticker}</h2>
        <div className="text-gray-500">No data available</div>
      </div>
    )
  }

  const priceColor = data.price_change_1d >= 0 ? 'text-green-600' : 'text-red-600'
  const changeSign = data.price_change_1d >= 0 ? '+' : ''

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-lg font-semibold">{data.ticker}</h2>
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold">₹{data.price.toFixed(2)}</span>
            <span className={`text-sm ${priceColor}`}>
              {changeSign}{data.price_change_1d.toFixed(2)}%
            </span>
          </div>
        </div>
        <div className="text-right">
          <span className={`px-2 py-1 rounded text-xs ${
            data.trend === 'BULLISH' ? 'bg-green-100 text-green-800' :
            data.trend === 'BEARISH' ? 'bg-red-100 text-red-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {data.trend}
          </span>
          <div className="mt-1 text-xs text-gray-500">
            RSI: {data.rsi.toFixed(1)} ({data.rsi_status})
          </div>
        </div>
      </div>

      <div className="h-64">
        <Plot
          data={[
            {
              x: [1, 2, 3, 4, 5],
              y: [data.price * 0.95, data.price * 0.97, data.price, data.price * 1.02, data.price * 1.05],
              type: 'scatter',
              mode: 'lines',
              line: { color: priceColor.replace('text-', '').replace('-600', '') }
            }
          ]}
          layout={{
            title: `${ticker} Price Trend`,
            showlegend: false,
            height: 250,
            margin: { t: 30, b: 30, l: 40, r: 10 },
            xaxis: { showticklabels: false },
            yaxis: { title: 'Price' }
          }}
          config={{ responsive: true, displayModeBar: false }}
        />
      </div>

      <div className="grid grid-cols-3 gap-2 mt-4 text-xs">
        <div className="text-center">
          <div className="text-gray-500">MACD</div>
          <div className="font-semibold">{data.macd.toFixed(3)}</div>
        </div>
        <div className="text-center">
          <div className="text-gray-500">EMA 20</div>
          <div className="font-semibold">₹{data.ema20.toFixed(2)}</div>
        </div>
        <div className="text-center">
          <div className="text-gray-500">Volume</div>
          <div className="font-semibold">{(data.volume / 1000).toFixed(0)}K</div>
        </div>
      </div>
    </div>
  )
}

export default StockChart