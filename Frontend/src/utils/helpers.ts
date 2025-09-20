export const formatPrice = (price: number): string => {
  if (price >= 1000) {
    return `₹${price.toFixed(0)}`
  } else if (price >= 100) {
    return `₹${price.toFixed(1)}`
  } else {
    return `₹${price.toFixed(2)}`
  }
}

export const formatCurrency = (amount: number, currency: string = 'INR'): string => {
  if (amount >= 1e12) {
    return `₹${(amount / 1e12).toFixed(2)}T`
  } else if (amount >= 1e9) {
    return `₹${(amount / 1e9).toFixed(2)}B`
  } else if (amount >= 1e6) {
    return `₹${(amount / 1e6).toFixed(2)}M`
  } else if (amount >= 1e3) {
    return `₹${(amount / 1e3).toFixed(2)}K`
  } else {
    return `₹${amount.toFixed(2)}`
  }
}

export const formatVolume = (volume: number): string => {
  if (volume >= 1e9) {
    return `${(volume / 1e9).toFixed(2)}B`
  } else if (volume >= 1e6) {
    return `${(volume / 1e6).toFixed(2)}M`
  } else if (volume >= 1e3) {
    return `${(volume / 1e3).toFixed(2)}K`
  } else {
    return volume.toLocaleString()
  }
}

export const formatPercentage = (change: number): string => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  } else {
    return num.toString()
  }
}

export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}