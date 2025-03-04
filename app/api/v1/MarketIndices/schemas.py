from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class MarketIndexEntry(BaseModel):
    time: str = Field(..., description="Date/time of the market data")
    close: float = Field(..., description="Closing price")

class MarketIndexResponse(BaseModel):
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
