from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
import time

from .services import Treemap
from .schemas import TreemapResponse, StockData

router = APIRouter(tags=["Treemap"])

# Sử dụng một instance duy nhất cho toàn bộ ứng dụng
treemap_instance = Treemap()

@router.get("/{index_name}", response_model=TreemapResponse)
async def get_stocks_by_index(index_name: str):
    """
    Lấy danh sách cổ phiếu của một chỉ số cụ thể với thông tin vốn hóa và GTGD
    
    Args:
        index_name: Tên chỉ số (HOSE, HNX, UPCOM)
        
    Returns:
        TreemapResponse: Danh sách cổ phiếu với thông tin
    """
    try:
        print(f"Starting to fetch stock data for {index_name}...")
        start_time = time.time()
        
        # Lấy dữ liệu cổ phiếu với vốn hóa và GTGD
        result = treemap_instance.sort_cp(index_name)
        
        # Extract the DataFrame and convert to records
        if isinstance(result, dict) and 'market_cap_data' in result:
            # Convert DataFrame to list of dictionaries
            market_cap_df = result['market_cap_data']
            stocks_data = market_cap_df.to_dict('records')
            
            # Chuyển đổi dữ liệu sang định dạng phù hợp với schema
            formatted_data = [
                StockData(
                    symbol=stock["symbol"],
                    market_cap=float(stock["von_hoa"])  # Use 'von_hoa' instead of 'market_cap'
                ) for stock in stocks_data
            ]
        else:
            formatted_data = []
        
        elapsed = time.time() - start_time
        print(f"Fetched {len(formatted_data)} stocks from {index_name} in {elapsed:.2f} seconds")
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"Successfully fetched {len(formatted_data)} stocks from {index_name}",
                "data": [stock.dict() for stock in formatted_data]
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
    except Exception as e:
        print(f"Error in get_stocks_by_index: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to fetch stock data from {index_name}: {str(e)}",
                "data": None
            }
        )
