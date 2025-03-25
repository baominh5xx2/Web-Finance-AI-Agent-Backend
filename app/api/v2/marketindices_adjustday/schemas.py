from pydantic import BaseModel
from typing import List

class PriceDatePair(BaseModel):
    price: float
    date: str

class MarketIndicesResponse(BaseModel):
    symbol: str
    time: str
    data: List[PriceDatePair]