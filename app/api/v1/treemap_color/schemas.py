from pydantic import BaseModel
from typing import Optional, Any

class StockChangeResponse(BaseModel):
    symbol: str
    difference: float
    percentage_change: float
    status: str
