from datetime import datetime
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import asyncio
import time

# Fix relative import
from .services import Market_indices
from .schemas import MarketIndexResponse

router = APIRouter(tags=["Market Indices"])

# Sử dụng một instance duy nhất cho toàn bộ ứng dụng
market_indices_instance = Market_indices()

@router.get("/indices/{index_code}", response_model=MarketIndexResponse)
async def get_market_indices(index_code: str = "VNINDEX", top: int = 90):
    """
    Get market index data
    """
    try:
        # Sử dụng instance toàn cục thay vì tạo mới
        start_time = time.time()
        market_indices_data = market_indices_instance.get_market_indices(index_code, top)
        elapsed = time.time() - start_time
        print(f"Retrieved {index_code} data in {elapsed:.2f} seconds")
        
        # Nếu mảng dữ liệu trống, đánh dấu đây là dữ liệu không khả dụng (N/A)
        is_na = len(market_indices_data) == 0
        
        return JSONResponse(
            content={
                "data": market_indices_data,
                "is_na": is_na  # Thêm flag để frontend biết đây là N/A
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
    except Exception as e:
        print(f"Error in get_market_indices API: {e}")
        # Return N/A flag when error
        return JSONResponse(
            status_code=200,
            content={"data": [], "is_na": True, "error": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )

# Hàm async để tải một chỉ số
async def fetch_index_data(index_code: str, top: int = 90):
    return index_code, market_indices_instance.get_market_indices(index_code, top)

@router.get("/indices", response_model=MarketIndexResponse)
async def get_default_indices(top: int = 90):
    """
    Get default market indices (VNINDEX, HNXINDEX, UPCOMINDEX, VN30, HNX30)
    """
    try:
        print("Starting to fetch all indices data...")
        total_start_time = time.time()
        
        vnindex_future = asyncio.create_task(fetch_index_data("VNINDEX", top))
        vn30_future = asyncio.create_task(fetch_index_data("VN30", top))
        hnxindex_future = asyncio.create_task(fetch_index_data("HNXINDEX", top))
        upcomindex_future = asyncio.create_task(fetch_index_data("UPCOMINDEX", top))
        hnx30_future = asyncio.create_task(fetch_index_data("HNX30", top))
        
        # Xử lý kết quả khi tất cả các tasks hoàn thành
        results = {}
        results_status = {}
        
        # Chờ và xử lý kết quả cho TẤT CẢ các chỉ số (thay vì chỉ VNINDEX và VN30)
        for future in [await vnindex_future, await vn30_future, await hnxindex_future, await upcomindex_future, await hnx30_future]:
            index_code, data = future
            results[index_code] = data
            results_status[index_code] = len(data) == 0
        
        total_elapsed = time.time() - total_start_time
        print(f"Fetched all indices data in {total_elapsed:.2f} seconds")
        
        return JSONResponse(
            content={
                "data": {
                    "VNINDEX": results.get("VNINDEX", []),
                    "HNXINDEX": results.get("HNXINDEX", []),
                    "UPCOMINDEX": results.get("UPCOMINDEX", []),
                    "VN30": results.get("VN30", []),
                    "HNX30": results.get("HNX30", [])
                },
                "is_na": results_status
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
    except Exception as e:
        print(f"Error in get_default_indices API: {e}")
        # Tất cả các chỉ số đều không khả dụng khi có lỗi
        return JSONResponse(
            status_code=200,
            content={
                "data": {
                    "VNINDEX": [],
                    "HNXINDEX": [],
                    "UPCOMINDEX": [],
                    "VN30": [],
                    "HNX30": []
                },
                "is_na": {
                    "VNINDEX": True,
                    "HNXINDEX": True,
                    "UPCOMINDEX": True,
                    "VN30": True,
                    "HNX30": True
                },
                "error": str(e)
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )

# Add OPTIONS method for CORS preflight requests
@router.options("/indices/{index_code}")
@router.options("/indices")
async def options_route():
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response