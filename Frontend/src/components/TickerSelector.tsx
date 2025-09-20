import React from 'react'

interface TickerSelectorProps {
  selectedTickers: string[]
  onTickersChange: (tickers: string[]) => void
}

const TickerSelector: React.FC<TickerSelectorProps> = ({
  selectedTickers,
  onTickersChange
}) => {
  const popularTickers = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
    'META', 'NVDA', 'NFLX', 'BABA', 'JPM'
  ]

  const handleTickerChange = (ticker: string) => {
    if (selectedTickers.includes(ticker)) {
      onTickersChange(selectedTickers.filter(t => t !== ticker))
    } else {
      onTickersChange([...selectedTickers, ticker])
    }
  }

  const handleCustomTicker = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      const input = event.currentTarget as HTMLInputElement
      const newTicker = input.value.trim().toUpperCase()
      
      if (newTicker && !selectedTickers.includes(newTicker)) {
        onTickersChange([...selectedTickers, newTicker])
        input.value = ''
      }
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm font-medium text-gray-700">Stocks:</span>
      
      {popularTickers.map(ticker => (
        <label key={ticker} className="flex items-center text-sm">
          <input
            type="checkbox"
            checked={selectedTickers.includes(ticker)}
            onChange={() => handleTickerChange(ticker)}
            className="mr-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          {ticker}
        </label>
      ))}
      
      <input
        type="text"
        placeholder="Add ticker..."
        onKeyPress={handleCustomTicker}
        className="text-sm border border-gray-300 rounded px-2 py-1 w-24 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
    </div>
  )
}

export default TickerSelector