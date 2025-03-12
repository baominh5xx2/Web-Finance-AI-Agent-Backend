from fastapi import APIRouter, HTTPException, Query
from .services import news
from .schemas import NewsResponse, NewsItem, TopNewsResponse
from typing import List

router = APIRouter()
news_service = news()

@router.get("/top/latest", response_model=TopNewsResponse)
async def get_top_stocks_news():
    """
    Get the latest 10 news from the top 5 stocks by market capitalization
    """
    try:
        news_data = news_service.get_top_stocks_news(limit=10)
        if not news_data:
            return TopNewsResponse(news=[])
        
        # Transform the data to match our schema
        news_items = [
            NewsItem(
                title=item.get('title', ''),
                publish_date=item.get('publish_date', ''),
                symbol=item.get('symbol', '')
            ) for item in news_data
        ]
        
        return TopNewsResponse(news=news_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top stocks news: {str(e)}")

@router.get("/{symbol}", response_model=NewsResponse)
async def get_stock_news(symbol: str):
    """
    Get news for a specific stock by its symbol
    """
    try:
        news_data = news_service.get_news(symbol)
        if not news_data:
            return NewsResponse(symbol=symbol, news=[])
        
        # Transform the data to match our schema
        news_items = [
            NewsItem(
                title=item.get('title', ''),
                publish_date=item.get('publish_date', ''),
                symbol=symbol
            ) for item in news_data
        ]
        
        return NewsResponse(symbol=symbol, news=news_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")
