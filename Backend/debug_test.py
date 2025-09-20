#!/usr/bin/env python3
"""Debug script to test individual components"""

import asyncio
import sys
import traceback

async def test_components():
    try:
        print("Testing market data...")
        from services.market_data import get_stock_data
        stock_data = await get_stock_data('AAPL')
        print(f"✅ Stock data: {stock_data.ticker} - ${stock_data.price}")
        
        print("Testing news scraper...")
        from services.news_scraper import get_financial_news
        news = await get_financial_news(3)
        print(f"✅ News count: {len(news)}")
        
        print("Testing signals...")
        from services.signals import generate_signals
        signal = generate_signals('AAPL', stock_data, news)
        print(f"✅ Signal: {signal.signal}")
        
        print("All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_components())
