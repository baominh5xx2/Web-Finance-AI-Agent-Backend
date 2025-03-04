from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional

# Fix relative import
from .services import Market_indices
from .schemas import MarketIndexResponse

router = APIRouter(tags=["Market Indices"])

# Instantiate the class
market_indices = Market_indices()

@router.get("/indices/{index_code}", response_model=MarketIndexResponse)
async def get_market_indices(index_code: str = "VNINDEX", top: int = 30):
    """
    Get market index data (top entries)
    """
    result = market_indices.get_market_indices(index_code, top)
    return {
        "success": True,
        "message": f"Top {top} market index entries for {index_code}",
        "data": result
    }

@router.get("/indices", response_model=MarketIndexResponse)
async def get_default_indices(top: int = 30):
    """
    Get VNINDEX data (top entries) - default endpoint
    """
    result = market_indices.get_market_indices("VNINDEX", top)
    return {
        "success": True,
        "message": f"Top {top} market index entries for VNINDEX",
        "data": result
    }