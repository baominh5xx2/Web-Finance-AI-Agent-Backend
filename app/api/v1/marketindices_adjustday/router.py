from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from .services import MarketIndicesAdjustDayService
from .schemas import MarketIndicesResponse

router = APIRouter(
    prefix="/adjust-day",
    tags=["market-indices-adjust"]
)

@router.get("/{symbol}/{time}", response_model=MarketIndicesResponse)
async def get_adjusted_market_indices(symbol: str, time: str) -> Dict[str, Any]:
    """
    Get the adjusted market indices data for a given symbol and time period.
    
    Parameters:
    - symbol: Stock symbol to query (e.g., VNINDEX, HNX, UPCOM)
    - time: Time period (3M, 6M, 1Y, 2Y)
    
    Returns:
    - Market indices data with price-date pairs
    """
    try:
        service = MarketIndicesAdjustDayService()
        data = service.get_adjusted_data(symbol=symbol, time=time)
        
        if not data:
            return {
                "symbol": symbol,
                "time": time,
                "data": []
            }
            
        return {
            "symbol": symbol,
            "time": time,
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market indices data: {str(e)}")