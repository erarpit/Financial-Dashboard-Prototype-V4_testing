# pipelines/news.py

import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NewsProvider:
    def __init__(self):
        self.sources = {
            "moneycontrol": "https://www.moneycontrol.com/rss/business.xml",
            "economic_times": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            "business_standard": "https://www.business-standard.com/rss/markets-106.rss",
            "livemint": "https://www.livemint.com/rss/markets"
        }
        
        # Stock-specific news mapping
        self.stock_keywords = {
            "RELIANCE.NS": ["reliance", "ril", "mukesh ambani", "jio", "retail"],
            "TCS.NS": ["tcs", "tata consultancy", "it services"],
            "HDFCBANK.NS": ["hdfc bank", "banking", "private bank"],
            "INFY.NS": ["infosys", "it services", "tech"],
            "HINDUNILVR.NS": ["hindustan unilever", "hul", "fmcg"],
            "ITC.NS": ["itc", "cigarette", "fmcg"],
            "SBIN.NS": ["sbi", "state bank", "public bank"],
            "BHARTIARTL.NS": ["bharti airtel", "telecom", "5g"],
            "KOTAKBANK.NS": ["kotak", "private bank"],
            "LT.NS": ["larsen toubro", "engineering", "infrastructure"]
        }

    def get_rss_news(self, source_url: str, limit: int = 10) -> List[Dict]:
        """Fetch news from RSS feed."""
        try:
            feed = feedparser.parse(source_url)
            news_items = []
            
            for entry in feed.entries[:limit]:
                item = {
                    "title": entry.get('title', ''),
                    "url": entry.get('link', ''),
                    "content": entry.get('summary', ''),
                    "published_at": self._parse_date(entry.get('published', '')),
                    "source": feed.feed.get('title', 'Unknown')
                }
                news_items.append(item)
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching RSS from {source_url}: {str(e)}")
            return []

    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats from RSS feeds."""
        try:
            # Try common RSS date formats
            for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%dT%H:%M:%S%z', '%a, %d %b %Y %H:%M:%S']:
                try:
                    return datetime.strptime(date_str, fmt).isoformat()
                except ValueError:
                    continue
            
            # If parsing fails, return current time
            return datetime.now().isoformat()
            
        except Exception:
            return datetime.now().isoformat()

    def get_recent_news(self, limit: int = 20) -> List[Dict]:
        """Get recent financial news from all sources."""
        all_news = []
        
        for source_name, source_url in self.sources.items():
            try:
                news_items = self.get_rss_news(source_url, limit // len(self.sources))
                for item in news_items:
                    item['source_name'] = source_name
                all_news.extend(news_items)
                
            except Exception as e:
                logger.error(f"Error fetching from {source_name}: {str(e)}")
        
        # Sort by published date (most recent first)
        all_news.sort(key=lambda x: x['published_at'], reverse=True)
        
        return all_news[:limit]

    def get_stock_specific_news(self, ticker: str, limit: int = 5) -> List[Dict]:
        """Get news specific to a stock ticker."""
        keywords = self.stock_keywords.get(ticker, [ticker.replace('.NS', '').replace('.BO', '')])
        all_news = self.get_recent_news(limit * 3)  # Get more to filter
        
        relevant_news = []
        
        for item in all_news:
            title_lower = item['title'].lower()
            content_lower = item['content'].lower()
            
            # Check if any keyword appears in title or content
            if any(keyword.lower() in title_lower or keyword.lower() in content_lower 
                   for keyword in keywords):
                relevant_news.append(item)
                
                if len(relevant_news) >= limit:
                    break
        
        return relevant_news

    def get_market_news(self, limit: int = 10) -> List[Dict]:
        """Get general market news."""
        market_keywords = ['sensex', 'nifty', 'market', 'stock', 'trading', 'bse', 'nse']
        all_news = self.get_recent_news(limit * 2)
        
        market_news = []
        
        for item in all_news:
            title_lower = item['title'].lower()
            
            if any(keyword in title_lower for keyword in market_keywords):
                market_news.append(item)
                
                if len(market_news) >= limit:
                    break
        
        return market_news

# Global instance
news_provider = NewsProvider()

def get_recent_news(ticker: str = None, limit: int = 10) -> List[Dict]:
    """
    Get recent news - either stock-specific or general market news.
    """
    try:
        if ticker:
            # Get stock-specific news
            stock_news = news_provider.get_stock_specific_news(ticker, limit // 2)
            market_news = news_provider.get_market_news(limit // 2)
            
            # Combine and deduplicate
            all_news = stock_news + market_news
            seen_titles = set()
            unique_news = []
            
            for item in all_news:
                if item['title'] not in seen_titles:
                    seen_titles.add(item['title'])
                    unique_news.append(item)
            
            return unique_news[:limit]
        else:
            return news_provider.get_recent_news(limit)
            
    except Exception as e:
        logger.error(f"Error in get_recent_news: {str(e)}")
        return _get_fallback_news()

def _get_fallback_news() -> List[Dict]:
    """Fallback news when API fails."""
    return [
        {
            "title": "Market News Unavailable",
            "url": "#",
            "content": "Unable to fetch latest market news. Please check your internet connection.",
            "published_at": datetime.now().isoformat(),
            "source": "System",
            "source_name": "fallback"
        }
    ]

# Sample news data for testing
SAMPLE_NEWS = {
    "RELIANCE.NS": [
        {
            "title": "Reliance Industries Q2 results: Net profit rises 12% YoY",
            "url": "#",
            "content": "Reliance Industries reported strong quarterly results with increased profits from retail and telecom segments.",
            "published_at": datetime.now().isoformat(),
            "source": "Sample News"
        },
        {
            "title": "Jio announces new 5G expansion plans across India",
            "url": "#", 
            "content": "Reliance Jio plans to expand 5G coverage to 200 more cities by end of fiscal year.",
            "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "source": "Sample News"
        }
    ],
    "HDFCBANK.NS": [
        {
            "title": "HDFC Bank reports strong loan growth in Q2",
            "url": "#",
            "content": "Private sector lender shows robust credit growth amid economic recovery.",
            "published_at": datetime.now().isoformat(),
            "source": "Sample News"
        },
        {
            "title": "RBI policy supports private banking sector",
            "url": "#",
            "content": "Reserve Bank's monetary policy stance benefits private sector banks like HDFC Bank.",
            "published_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "source": "Sample News"
        }
    ]
}

def get_sample_news(ticker: str = None) -> List[Dict]:
    """Get sample news for testing purposes."""
    if ticker and ticker in SAMPLE_NEWS:
        return SAMPLE_NEWS[ticker]
    else:
        # Return mixed sample news
        all_sample = []
        for stock_news in SAMPLE_NEWS.values():
            all_sample.extend(stock_news)
        return all_sample[:5]