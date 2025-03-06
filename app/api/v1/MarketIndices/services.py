from datetime import datetime, timedelta
from fastapi import Depends, APIRouter, HTTPException
from typing import Dict, List, Any
import pandas as pd
from vnstock import Vnstock
import random
import traceback
import json
import time

# Biến toàn cục để cache
_global_cache = {}
_global_cache_time = {}
_global_cache_expiry = 600  # Cache expiry in seconds (10 minutes)

# Khởi tạo Vnstock một lần duy nhất
_vnstock_instance = None

def get_vnstock_instance():
    global _vnstock_instance
    if _vnstock_instance is None:
        _vnstock_instance = Vnstock().stock(source='VCI')
    return _vnstock_instance

class Market_indices:
    def __init__(self):
        # Sử dụng cache toàn cục thay vì tạo mới mỗi lần
        self.cache = _global_cache
        self.cache_time = _global_cache_time
        self.cache_expiry = _global_cache_expiry
    
    def get_market_indices(self, index_code: str = "VNINDEX", top: int = 90) -> List[Dict[str, Any]]:
        try:
            current_time = time.time()  # Use time.time() instead of datetime.now().timestamp()
            cache_key = f"{index_code}_{top}"
            
            # Check if we have cached data that's not expired
            if cache_key in self.cache and current_time - self.cache_time.get(cache_key, 0) < self.cache_expiry:
                print(f"Using cached data for {index_code}")
                return self.cache[cache_key]
            try:
                # Lấy dữ liệu thời gian
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')

                # Sử dụng instance đã tạo sẵn
                stock = get_vnstock_instance()
                
                # Đo thời gian lấy dữ liệu
                start_time = time.time()
                data = stock.quote.history(symbol=index_code, start=start_date, end=end_date, interval='1m')
                fetch_time = time.time() - start_time
                print(f"Fetched {index_code} data in {fetch_time:.2f} seconds")
                
                # Convert to list for API response
                if isinstance(data, pd.DataFrame) and not data.empty:
                    # Tối ưu hóa xử lý DataFrame
                    if 'time' in data.columns and 'open' in data.columns:
                        # Chỉ lấy 2 cột cần thiết ngay từ đầu để tránh copy dữ liệu
                        top_data = data[['time', 'open']].tail(top).copy()
                    else:
                        # Map lại tên cột nếu cần
                        time_col = data.columns[0]  # giả sử cột đầu tiên là thời gian
                        close_col = [col for col in data.columns if 'open' in col.lower() or 'close' in col.lower()][0]
                        top_data = data[[time_col, close_col]].tail(top).copy()
                        top_data.columns = ['time', 'open']  # đổi tên cột
                    
                    # Xử lý Timestamp trước khi chuyển thành dict
                    # Chuyển cột time từ Timestamp sang string khi có Timestamp
                    if pd.api.types.is_datetime64_any_dtype(top_data['time']):
                        top_data['time'] = top_data['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Chuyển thành dict - chỉ làm một lần
                    result = top_data.to_dict(orient='records')
                    
                    # Cache kết quả
                    self.cache[cache_key] = result
                    self.cache_time[cache_key] = current_time
                    
                    return result
                else:
                    # Nếu không có dữ liệu, trả về danh sách trống
                    print(f"No data returned for {index_code} or data is empty")
                    return []
            except Exception as e:
                print(f"Error fetching {index_code} data: {e}")
                print(traceback.format_exc())
                # Trả về danh sách trống khi có lỗi
                return []
                
        except Exception as e:
            # Log lỗi đầy đủ
            print(f"Unhandled error in get_market_indices for {index_code}: {e}")
            print(traceback.format_exc())
            
            # Trả về danh sách trống khi có lỗi
            return []