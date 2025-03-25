from pydantic import BaseModel
from typing import List, Optional

class NewsItem(BaseModel):
    title: str
    publish_date: str
    symbol: Optional[str] = None
    
class NewsResponse(BaseModel):
    symbol: str
    news: List[NewsItem]
    
class TopNewsResponse(BaseModel):
    news: List[NewsItem]
