from datetime import datetime, timedelta
from fastapi import Depends, APIRouter, HTTPException
from typing import Dict, List, Any
import pandas as pd
from vnstock import Vnstock
import random
import traceback
import json
import time
import os

# Biến toàn cục để cache
_global_cache = {}
_global_cache_time = {}
_global_cache_expiry = 600  # Cache expiry in seconds (10 minutes)

# Khởi tạo Vnstock một lần duy nhất
_vnstock_instance = None

# Đọc dữ liệu ngày nghỉ lễ từ file holiday.json
_holidays = {}

def load_holidays():
    global _holidays
    try:
        # Lấy đường dẫn tới file holiday.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        holiday_file = os.path.join(current_dir, 'holiday.json')
        
        # Đọc file holiday.json
        with open(holiday_file, 'r') as f:
            _holidays = json.load(f)
        print(f"Loaded holidays for years: {', '.join(_holidays.keys())}")
    except Exception as e:
        print(f"Error loading holidays: {e}")
        _holidays = {}

# Hàm kiểm tra xem một ngày có phải là ngày nghỉ lễ không
def is_holiday(date):
    # Nếu chưa load dữ liệu ngày nghỉ, load ngay
    if not _holidays:
        load_holidays()
    
    # Lấy năm của ngày cần kiểm tra
    year = str(date.year)
    
    # Kiểm tra xem năm có trong dữ liệu ngày nghỉ không
    if year not in _holidays:
        print(f"Warning: No holiday data for year {year}")
        return False
    
    # Kiểm tra xem ngày có trong danh sách ngày nghỉ của năm đó không
    date_str = date.strftime('%Y-%m-%d')
    return date_str in _holidays[year]

def get_vnstock_instance():
    global _vnstock_instance
    if _vnstock_instance is None:
        _vnstock_instance = Vnstock().stock(source='VCI')
    return _vnstock_instance

# Load holidays khi module được import
load_holidays()

class Market_indices:
    def __init__(self):
        # Sử dụng cache toàn cục thay vì tạo mới mỗi lần
        self.cache = _global_cache
        self.cache_time = _global_cache_time
        self.cache_expiry = _global_cache_expiry
    
    def get_market_indices(self, index_code: str = "VNINDEX", top: int = None) -> List[Dict[str, Any]]:
        try:
            current_time = time.time()
            today = datetime.now()
            
            # Định nghĩa thời gian giao dịch
            market_open_time = today.replace(hour=9, minute=0, second=0, microsecond=0)
            market_close_time = today.replace(hour=15, minute=0, second=0, microsecond=0)
            start_time_data = today.replace(hour=8, minute=59, second=0, microsecond=0)
            
            # Kiểm tra xem hôm nay có phải là cuối tuần không (thứ 7 hoặc chủ nhật)
            is_weekend = today.weekday() >= 5  # 5 = Saturday, 6 = Sunday
            
            # Kiểm tra xem hôm nay có phải là ngày nghỉ lễ không
            is_holiday_today = is_holiday(today)
            
            # Xác định xem hiện tại có trong giờ giao dịch không (chỉ áp dụng cho ngày làm việc)
            is_trading_hours = (not is_weekend) and (not is_holiday_today) and (market_open_time <= today <= market_close_time)
            
            # Xác định thời gian bắt đầu và kết thúc dựa vào quy tắc
            if is_weekend or is_holiday_today:
                # Cuối tuần hoặc ngày lễ: Lấy dữ liệu từ 9:00 đến 15:00 của ngày làm việc gần nhất trước đó
                
                # Tìm ngày làm việc gần nhất trước đó
                previous_working_day = today
                days_back = 1
                
                while days_back <= 10:  # Giới hạn tìm kiếm 10 ngày để tránh vòng lặp vô hạn
                    previous_working_day = today - timedelta(days=days_back)
                    # Kiểm tra xem ngày này có phải là ngày làm việc không
                    if previous_working_day.weekday() < 5 and not is_holiday(previous_working_day):
                        break
                    days_back += 1
                
                start_time = previous_working_day.replace(hour=9, minute=0, second=0, microsecond=0)
                end_time = previous_working_day.replace(hour=15, minute=0, second=0, microsecond=0)
                
                if is_weekend:
                    print(f"Weekend: Getting data from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} (previous working day)")
                else:
                    print(f"Holiday: Getting data from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} (previous working day)")
            elif is_trading_hours:
                # Trong giờ giao dịch: Lấy từ 8:59 sáng đến hiện tại
                start_time = start_time_data
                end_time = today
                print(f"Trading hours: Getting data from {start_time.strftime('%H:%M')} to current time {end_time.strftime('%H:%M')}")
            else:
                # Ngoài giờ giao dịch (nhưng vẫn trong ngày làm việc)
                if today > market_close_time:
                    # Sau 15:00: Lấy dữ liệu từ 9:00 đến 15:00 của ngày hôm nay
                    start_time = market_open_time
                    end_time = market_close_time
                    print(f"After market close: Getting data from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')} today")
                else:
                    # Trước 9:00 sáng: Lấy dữ liệu từ 9:00 đến 15:00 của ngày làm việc gần nhất trước đó
                    
                    # Tìm ngày làm việc gần nhất trước đó
                    previous_working_day = today - timedelta(days=1)
                    days_back = 1
                    
                    while days_back <= 10:  # Giới hạn tìm kiếm 10 ngày để tránh vòng lặp vô hạn
                        previous_working_day = today - timedelta(days=days_back)
                        # Kiểm tra xem ngày này có phải là ngày làm việc không
                        if previous_working_day.weekday() < 5 and not is_holiday(previous_working_day):
                            break
                        days_back += 1
                    
                    start_time = previous_working_day.replace(hour=9, minute=0, second=0, microsecond=0)
                    end_time = previous_working_day.replace(hour=15, minute=0, second=0, microsecond=0)
                    print(f"Before market open: Getting data from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
            
            # Format thời gian cho API (vẫn giữ nhiều ngày để đảm bảo có dữ liệu)
            # Mở rộng range để đảm bảo lấy được dữ liệu cuối tuần trước nếu cần
            api_start_date = (today - timedelta(days=10)).strftime('%Y-%m-%d')  # Tăng lên 10 ngày để đảm bảo có dữ liệu cho các kỳ nghỉ lễ dài
            api_end_date = today.strftime('%Y-%m-%d')
            
            # Tạo cache key mới bao gồm thời gian bắt đầu và kết thúc
            cache_key = f"{index_code}_{start_time.strftime('%Y-%m-%d_%H:%M')}_{end_time.strftime('%H:%M')}"
            
            # Check if we have cached data that's not expired
            if cache_key in self.cache and current_time - self.cache_time.get(cache_key, 0) < self.cache_expiry:
                print(f"Using cached data for {index_code} from {cache_key}")
                return self.cache[cache_key]
            
            try:
                # Sử dụng instance đã tạo sẵn
                stock = Vnstock().stock(symbol="VCI", source='VCI')
                
                # Đo thời gian lấy dữ liệu
                start_fetch_time = time.time()
                data = stock.quote.history(symbol=index_code, start=api_start_date, end=api_end_date, interval='1m')
                fetch_time = time.time() - start_fetch_time
                print(f"Fetched {index_code} data in {fetch_time:.2f} seconds")
                
                # Convert to list for API response
                if isinstance(data, pd.DataFrame) and not data.empty:
                    # Chuyển cột time sang datetime nếu chưa phải
                    if not pd.api.types.is_datetime64_any_dtype(data['time']):
                        data['time'] = pd.to_datetime(data['time'])
                    
                    # Áp dụng logic lọc theo thời gian
                    filter_start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    filter_end_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Filtering data from {filter_start_str} to {filter_end_str}")
                    
                    # Lọc dữ liệu từ thời điểm bắt đầu đến kết thúc
                    filtered_data = data[(data['time'] >= start_time) & (data['time'] <= end_time)].copy()
                    
                    print(f"Found {len(filtered_data)} records from {filter_start_str} to {filter_end_str}")
                    
                    # Tối ưu hóa xử lý DataFrame
                    if 'time' in filtered_data.columns and 'open' in filtered_data.columns:
                        # Chỉ lấy 2 cột cần thiết
                        result_data = filtered_data[['time', 'open']].copy()
                    else:
                        # Map lại tên cột nếu cần
                        time_col = filtered_data.columns[0]  # giả sử cột đầu tiên là thời gian
                        close_col = [col for col in filtered_data.columns if 'open' in col.lower() or 'close' in col.lower()][0]
                        result_data = filtered_data[[time_col, close_col]].copy()
                        result_data.columns = ['time', 'open']  # đổi tên cột
                    
                    # Xử lý Timestamp trước khi chuyển thành dict
                    if pd.api.types.is_datetime64_any_dtype(result_data['time']):
                        result_data['time'] = result_data['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Chuyển thành dict
                    result = result_data.to_dict(orient='records')
                    
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