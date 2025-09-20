export interface StockData {
  ticker: string
  price: number
  price_change_1d: number
  price_change_5d: number
  rsi: number
  rsi_status: string
  macd: number
  macd_signal: number
  ema20: number
  bollinger_high: number
  bollinger_low: number
  atr: number
  trend: string
  volume: number
  last_updated: string
}

export interface NewsItem {
  title: string
  url: string
  source: string
  published_at: string
  content: string
  sentiment: string
  confidence: number
}

export interface Signal {
  ticker: string
  signal: string
  signals: string[]
  reasoning: string[]
  generated_at: string
}

export interface DashboardData {
  stocks: StockData[]
  news: NewsItem[]
  signals: Signal[]
  timestamp: string
}

// ============= ALPHA VANTAGE TYPES =============

export interface AlphaVantageQuote {
  symbol: string
  price: number
  change: number
  change_percent: number
  volume: number
  high: number
  low: number
  open: number
  previous_close: number
  market_cap?: number
  currency: string
  last_updated: string
  source: string
  alpha_vantage_symbol?: string
}

export interface AlphaVantageDailyData {
  symbol: string
  data: Array<{
    Date: string
    Open: number
    High: number
    Low: number
    Close: number
    Volume: number
  }>
  count: number
  last_updated: string
  source: string
}

export interface AlphaVantageIntradayData {
  symbol: string
  interval: string
  data: Array<{
    Datetime: string
    Open: number
    High: number
    Low: number
    Close: number
    Volume: number
  }>
  last_updated: string
  source: string
}

export interface AlphaVantageIndicators {
  symbol: string
  function: string
  interval: string
  time_period: number
  series_type: string
  data: Array<{
    Date: string
    [key: string]: any // For various indicator values
  }>
  last_updated: string
  source: string
}

export interface AlphaVantageOverview {
  symbol: string
  name: string
  description: string
  sector: string
  industry: string
  market_cap: number
  pe_ratio: number
  eps: number
  dividend_yield: number
  beta: number
  last_updated: string
  source: string
}

export interface AlphaVantageEarnings {
  symbol: string
  earnings_history: Array<{
    quarter: string
    eps: number
    revenue: number
  }>
  next_earnings_date: string
  estimated_eps: number
  last_updated: string
  source: string
}

export interface AlphaVantageNews {
  symbol: string
  news_items: Array<{
    title: string
    url: string
    time_published: string
    authors: string[]
    summary: string
    banner_image: string
    source: string
    category_within_source: string
    source_domain: string
    topics: Array<{
      topic: string
      relevance_score: string
    }>
    overall_sentiment_score: number
    overall_sentiment_label: string
    ticker_sentiment: Array<{
      ticker: string
      relevance_score: string
      ticker_sentiment_score: string
      ticker_sentiment_label: string
    }>
  }>
  last_updated: string
  source: string
}

// ============= CURRENCY TYPES =============

export interface CurrencyRate {
  usd_to_inr_rate: number
  last_updated: string
  cache_duration_seconds: number
  api_key_configured: boolean
}

export interface CurrencyConvert {
  original_amount: number
  original_currency: string
  converted_amount: number
  converted_currency: string
  formatted_amount: string
  exchange_rate: number
  last_updated: string
}

export interface CurrencyFormat {
  amount: number
  currency: string
  formatted: string
  decimals: number
}

// ============= ANGEL ONE TYPES =============

export interface AngelOneStatus {
  enabled: boolean
  api_configured: boolean
  client_configured: boolean
  last_updated: string
}

export interface AngelOneQuote {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  last_updated: string
  source: string
}

export interface AngelOneHistorical {
  symbol: string
  data: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>
  interval: string
  period: string
  last_updated: string
  source: string
}

export interface AngelOneIndices {
  indices: {
    [key: string]: {
      symbol: string
      price: number
      change: number
      change_percent: number
    }
  }
  last_updated: string
  source: string
}

export interface AngelOneMarketStatus {
  nse: {
    is_open: boolean
    last_updated: string
  }
  bse: {
    is_open: boolean
    last_updated: string
  }
  last_updated: string
  source: string
}