from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StockData(BaseModel):
    """Schema cho dữ liệu của một cổ phiếu"""
    symbol: str = Field(..., description="Mã cổ phiếu")
    total_value: float = Field(..., description="Giá trị giao dịch")
    market_cap: float = Field(..., description="Vốn hóa thị trường (tỷ đồng)")

class TreemapResponse(BaseModel):
    """Schema cho response của API treemap"""
    success: bool = Field(..., description="Trạng thái thành công của request")
    message: str = Field(..., description="Thông báo")
    data: Optional[List[StockData]] = Field(None, description="Danh sách dữ liệu cổ phiếu")
