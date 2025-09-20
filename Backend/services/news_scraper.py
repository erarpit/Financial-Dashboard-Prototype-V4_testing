import aiohttp
from bs4 import BeautifulSoup  # pyright: ignore[reportMissingModuleSource]
from datetime import datetime
import logging
from typing import List
from models.schemas import NewsItem
from services.sentiment_analysis import analyze_sentiment

logger = logging.getLogger(__name__)

async def get_financial_news(limit: int = 10) -> List[NewsItem]:
    """Get financial news from various sources"""
    news_items = []
    
    try:

        # Scrape from Financial Express
        try:
            fe_news = await scrape_financial_express(limit // 2)
            if fe_news:
                news_items.extend(fe_news)
        except Exception as e:
            logger.warning(f"Financial Express scraping failed: {str(e)}")
        
        # Scrape from Moneycontrol (if needed)
        if len(news_items) < limit:
            try:
                mc_news = await scrape_moneycontrol(limit - len(news_items))
                if mc_news:
                    news_items.extend(mc_news)
            except Exception as e:
                logger.warning(f"Moneycontrol scraping failed: {str(e)}")
        
        # If no news was scraped, return empty list
        if not news_items:
            logger.warning("No news could be scraped from any source")
            return []
            
    except Exception as e:
        logger.error(f"Error scraping news: {str(e)}")
        return []
    
    # Ensure we don't exceed the limit
    return news_items[:limit]

async def scrape_financial_express(limit: int = 5) -> List[NewsItem]:
    """Scrape news from Financial Express"""
    news_items = []
    try:
        url = "https://www.financialexpress.com/market/"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article', class_='article-list')[:limit]
        
        for article in articles:
            try:
                title_elem = article.find('h3', class_='title')
                link_elem = article.find('a')
                date_elem = article.find('time')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href')
                    if not link.startswith('http'):
                        link = f'https://www.financialexpress.com{link}'
                    
                    # Parse date or use current time
                    published_at = datetime.now()
                    if date_elem and date_elem.get('datetime'):
                        try:
                            datetime_str = date_elem['datetime'].replace('Z', '+00:00')
                            published_at = datetime.fromisoformat(datetime_str)
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Failed to parse date: {e}")
                            pass
                    
                    # Analyze sentiment
                    sentiment, confidence = analyze_sentiment(title)
                    
                    news_item = NewsItem(
                        title=title,
                        url=link,
                        source="Financial Express",
                        published_at=published_at.isoformat(),
                        content="",  # Would be fetched in detail view
                        sentiment=sentiment,
                        confidence=confidence
                    )
                    news_items.append(news_item)
            except Exception as e:
                logger.error(f"Error parsing article: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping Financial Express: {e}")
    
    return news_items

async def scrape_moneycontrol(limit: int = 5) -> List[NewsItem]:
    """Scrape news from Moneycontrol"""
    news_items = []
    try:
        url = "https://www.moneycontrol.com/news/business/markets/"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.select('li.clearfix')[:limit]
        
        for article in articles:
            try:
                title_elem = article.select_one('h2')
                link_elem = article.select_one('a')
                date_elem = article.select_one('span')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href')
                    if link and not link.startswith('http'):
                        link = f'https://www.moneycontrol.com{link}'
                    
                    # Parse date or use current time
                    published_at = datetime.now()
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        # Simple date parsing logic
                        if 'min' in date_text or 'hour' in date_text:
                            published_at = datetime.now()
                    
                    # Analyze sentiment
                    sentiment, confidence = analyze_sentiment(title)
                    
                    news_item = NewsItem(
                        title=title,
                        url=link or "#",
                        source="Moneycontrol",
                        published_at=published_at.isoformat(),
                        content="",
                        sentiment=sentiment,
                        confidence=confidence
                    )
                    news_items.append(news_item)
            except Exception as e:
                logger.error(f"Error parsing Moneycontrol article: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping Moneycontrol: {e}")
    
    return news_items