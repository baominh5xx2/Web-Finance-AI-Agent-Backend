from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from .services import TreemapColorService
from .schemas import StockChangeResponse

router = APIRouter(
    prefix="/treemap-color",
    tags=["treemap-color"]
)

@router.get("/stock-change/{symbol}", response_model=StockChangeResponse)
async def get_stock_change(symbol: str) -> Dict[str, Any]:
    """
    Get the price difference and percentage change for a given stock symbol.
    
    Parameters:
    - symbol: Stock symbol to query
    
    Returns:
    - Dictionary containing price difference and percentage change
    """
    try:
        service = TreemapColorService()
        difference, percentage_change = service.get_data_cp(symbol)
        
        return {
            "symbol": symbol,
            "difference": float(difference),
            "percentage_change": float(percentage_change),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")