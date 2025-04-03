import json
import os
from pathlib import Path
import pandas as pd

# Thư mục lưu trữ dữ liệu
DATA_DIR = Path(__file__).parent / "data"

def save_stock_data(symbol, data):
    """
    Lưu dữ liệu cổ phiếu đơn giản vào file JSON
    
    Args:
        symbol: Mã cổ phiếu
        data: Dữ liệu cần lưu
    """
    # Đảm bảo thư mục tồn tại
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Tên file đơn giản
    file_path = DATA_DIR / f"{symbol}_data.json"
    
    try:
        # Xử lý dữ liệu để đảm bảo có thể serialize
        if isinstance(data, pd.DataFrame):
            # Xử lý DataFrame để chuyển đổi sang dict
            # Đặc biệt xử lý MultiIndex nếu có
            data_to_save = {
                "columns": [str(col) if not isinstance(col, tuple) else '_'.join(str(c) for c in col) for col in data.columns],
                "index": [str(idx) for idx in data.index],
                "data": data.reset_index().to_dict('records')
            }
        elif isinstance(data, dict) and any(isinstance(v, pd.DataFrame) for v in data.values()):
            # Xử lý dict chứa DataFrame
            data_to_save = {}
            for key, value in data.items():
                if isinstance(value, pd.DataFrame):
                    data_to_save[key] = {
                        "columns": [str(col) if not isinstance(col, tuple) else '_'.join(str(c) for c in col) for col in value.columns],
                        "index": [str(idx) for idx in value.index],
                        "data": value.reset_index().to_dict('records')
                    }
                else:
                    data_to_save[key] = value
        else:
            # Với dict, list và các kiểu dữ liệu khác
            data_to_save = data
            
        # Lưu dữ liệu
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2, default=str)
            
        print(f"Đã lưu dữ liệu cho {symbol} tại {file_path}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu cho {symbol}: {str(e)}")
        return False 

# Tạo các alias cho các hàm cũ để tương thích với code hiện tại
def save_page1_data(symbol, data):
    """Alias của save_stock_data cho dữ liệu page1"""
    return save_stock_data(f"{symbol}_page1", data)

def save_page2_data(symbol, data):
    """Alias của save_stock_data cho dữ liệu page2"""
    return save_stock_data(f"{symbol}_page2", data)

def save_result_dataset(symbol, data):
    """Alias của save_stock_data cho dữ liệu phân tích"""
    return save_stock_data(f"{symbol}_analysis", data) 