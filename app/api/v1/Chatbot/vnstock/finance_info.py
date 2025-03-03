import json
import os
import pandas as pd
from .get_data import Vnstockk

class FinanceInfo:
    """Service for handling financial information and metrics"""
    
    def __init__(self):
        try:
            with open('labels.json', 'r', encoding='utf-8') as f:
                self.labels = json.load(f)
        except Exception as e:
            print(f"Error loading labels.json: {e}")
            self.labels = {}
            
        self.current_symbol = None
        self.stock_data = None
        self.time_period = "quarter"  # Default to quarterly data

    def get_stock_info(self, symbol):
        """Get stock information for a given symbol"""
        try:
            # Initialize current symbol
            self.current_symbol = symbol
            
            vnstock_instance = Vnstockk()
            
            # First try to load existing data
            existing_data = vnstock_instance.load_financial_data(symbol, self.time_period)
            
            if existing_data is not None and not existing_data.empty:
                self.stock_data = existing_data
                print(f"Using existing data for {symbol}")
            else:
                # If no existing data, fetch new data
                print(f"Fetching fresh data for {symbol}")
                self.stock_data = vnstock_instance.get_data_info(symbol, self.time_period)
            
            if self.stock_data is None or (isinstance(self.stock_data, pd.DataFrame) and self.stock_data.empty):
                return False, f"Không thể lấy dữ liệu cho {symbol}. Vui lòng thử lại sau."
            
            period_text = "Quý" if self.time_period == "quarter" else "Năm"
            return True, f"Đã tải dữ liệu {period_text} thành công cho {symbol}!\nVui lòng chọn loại chỉ số để xem:"
        except Exception as e:
            print(f"Error getting stock info: {e}")
            return False, f"Lỗi khi tải dữ liệu cho {symbol}: {str(e)}"

    def get_categories_menu(self):
        """Generate menu of available categories"""
        # Get actual categories from the financial data if available
        categories = []
        if self.stock_data is not None and isinstance(self.stock_data.columns, pd.MultiIndex):
            # Extract unique level 0 values (categories) from MultiIndex columns
            categories = [cat for cat in self.stock_data.columns.get_level_values(0).unique() 
                         if cat != "Meta"]  # Exclude Meta category
        
        # Use default categories if no data is available or if they don't have categories
        if not categories:
            categories = list(self.labels.keys())
            if "Meta" in categories:
                categories.remove("Meta")
        
        menu = "Chọn loại chỉ số bạn muốn xem:\n\n"
        for idx, category in enumerate(categories, 1):
            menu += f"{idx}. {category}\n"
        menu += "\nNhập /vnstock_get [số] hoặc /vnstock_get all để xem tất cả chỉ số."
        return menu

    def get_indicators(self, category_idx):
        """Get indicators for a specific category"""
        if not self.current_symbol or self.stock_data is None:
            return "Vui lòng nhập lệnh /search [mã cổ phiếu] trước!"

        try:
            # Check if stock_data has categories
            if isinstance(self.stock_data.columns, pd.MultiIndex):
                # Get all categories except Meta
                categories = [cat for cat in self.stock_data.columns.get_level_values(0).unique() 
                             if cat != "Meta"]
            else:
                # Try to categorize using labels from labels.json
                return f"Dữ liệu tài chính cho {self.current_symbol} không có cấu trúc phù hợp để phân loại."
            
            if not categories:
                return f"Không tìm thấy dữ liệu phân loại cho {self.current_symbol}."
            
            if category_idx == 'all':
                result = f"📊 Tất cả chỉ số cho {self.current_symbol}:\n\n"
                
                # Get years and quarters if available
                years = []
                quarters = []
                if ('Meta', 'Năm') in self.stock_data.columns:
                    years = self.stock_data[('Meta', 'Năm')].tolist()
                    if ('Meta', 'Kỳ') in self.stock_data.columns:
                        quarters = self.stock_data[('Meta', 'Kỳ')].tolist()
                
                # Get indices for the 3 most recent years
                if years:
                    # Find unique years and sort in descending order (newest first)
                    unique_years = sorted(set(years), reverse=True)
                    recent_years = unique_years[:3]  # Get 3 most recent years
                    
                    # Find indices of the most recent data points for each of these years
                    indices_to_show = []
                    for year in recent_years:
                        # Find all indices for this year
                        year_indices = [i for i, y in enumerate(years) if y == year]
                        if year_indices:
                            # For each year, add its most recent quarter
                            indices_to_show.append(max(year_indices))
                    
                    # Sort indices in reverse chronological order (newest to oldest)
                    indices_to_show.sort(reverse=True)
                    
                    for cat in categories:
                        result += f"=== {cat} ===\n"
                        # Get indicators for this category
                        indicators = [col[1] for col in self.stock_data.columns if col[0] == cat]
                        
                        for indicator in indicators:
                            if (cat, indicator) in self.stock_data.columns:
                                values = self.stock_data[(cat, indicator)].tolist()
                                if values and len(values) > 0:
                                    result += f"{indicator}:\n"
                                    
                                    # Display values for the 3 most recent years
                                    for i in indices_to_show:
                                        if i < len(values):
                                            # Format the time period based on data type
                                            if self.time_period == "yearly" or self.time_period == "year":
                                                time_period = f"{years[i]}"
                                            else:
                                                time_period = f"Q{quarters[i]}/{years[i]}" if i < len(quarters) else f"{years[i]}"
                                                
                                            if isinstance(values[i], (int, float)):
                                                result += f"  {time_period}: {values[i]:.2f}\n"
                                            else:
                                                result += f"  {time_period}: {values[i]}\n"
                                    result += "\n"
                        result += "\n"
                else:
                    # No year data available
                    result += "Không có dữ liệu về năm."
                
                return result

            try:
                # Try to parse as integer index
                category_idx = int(category_idx)
                if category_idx < 1 or category_idx > len(categories):
                    return f"Lựa chọn không hợp lệ! Vui lòng chọn từ 1 đến {len(categories)}"
                
                category_name = categories[category_idx - 1]
                
            except ValueError:
                # If not an integer, try to match by name
                matching_categories = [cat for cat in categories 
                                     if category_idx.lower() in cat.lower()]
                if not matching_categories:
                    return "Không tìm thấy chỉ tiêu phù hợp. Vui lòng thử lại."
                category_name = matching_categories[0]

            # Get results for the selected category
            result = f"📊 {category_name} cho {self.current_symbol}:\n\n"
            
            # Get indicators for this category
            indicators = [col[1] for col in self.stock_data.columns if col[0] == category_name]
            
            for indicator in indicators:
                if (category_name, indicator) in self.stock_data.columns:
                    values = self.stock_data[(category_name, indicator)].tolist()
                    if values and len(values) > 0:
                        latest_value = values[-1]  # Get most recent value
                        if isinstance(latest_value, (int, float)):
                            result += f"{indicator}: {latest_value:.2f}\n"
                        else:
                            result += f"{indicator}: {latest_value}\n"
            
            return result

        except Exception as e:
            print(f"Error getting indicators: {e}")
            return f"Lỗi khi truy xuất dữ liệu: {str(e)}"

    def _get_specific_category_indicators(self, category_name):
        """Get all indicators for a specific category"""
        if not self.current_symbol or self.stock_data is None:
            return "Vui lòng nhập lệnh /search [mã cổ phiếu] trước!"
            
        try:
            result = f"📊 {category_name} cho {self.current_symbol}:\n\n"
            
            # Get indicators for this category
            indicators = [col[1] for col in self.stock_data.columns if col[0] == category_name]
            
            # Get years and quarters if available
            years = []
            quarters = []
            if ('Meta', 'Năm') in self.stock_data.columns:
                years = self.stock_data[('Meta', 'Năm')].tolist()
                if ('Meta', 'Kỳ') in self.stock_data.columns:
                    quarters = self.stock_data[('Meta', 'Kỳ')].tolist()
            
            # Show data by year for all categories if years data is available
            if years:
                # Find unique years and sort in descending order (newest first)
                unique_years = sorted(set(years), reverse=True)
                recent_years = unique_years[:3]  # Get 3 most recent years
                
                # Find indices of the most recent data for each year
                indices_to_show = []
                for year in recent_years:
                    year_indices = [i for i, y in enumerate(years) if y == year]
                    if year_indices:
                        indices_to_show.append(max(year_indices))
                        
                # Sort indices in reverse chronological order
                indices_to_show.sort(reverse=True)
                
                # Show each indicator with values for recent years
                for indicator in indicators:
                    if (category_name, indicator) in self.stock_data.columns:
                        result += f"\n{indicator}:\n"
                        values = self.stock_data[(category_name, indicator)].tolist()
                        
                        # Show each period's value
                        for i in indices_to_show:
                            if i < len(values):
                                # Format time period based on data type
                                if self.time_period == "yearly" or self.time_period == "year":
                                    time_period = f"{years[i]}"
                                else:
                                    time_period = f"Q{quarters[i]}/{years[i]}" if i < len(quarters) else f"{years[i]}"
                                    
                                if isinstance(values[i], (int, float)):
                                    result += f"{time_period}: {values[i]:.2f}\n"
                                else:
                                    result += f"{time_period}: {values[i]}\n"
            else:
                # Fallback when no year data is available
                for indicator in indicators:
                    if (category_name, indicator) in self.stock_data.columns:
                        values = self.stock_data[(category_name, indicator)].tolist()
                        if values and len(values) > 0:
                            latest_value = values[-1]
                            if isinstance(latest_value, (int, float)):
                                result += f"{indicator}: {latest_value:.2f}\n"
                            else:
                                result += f"{indicator}: {latest_value}\n"
                
            return result
        except Exception as e:
            print(f"Error getting indicators: {e}")
            return f"Lỗi khi truy xuất dữ liệu: {str(e)}"

    def _get_specific_indicator(self, category_name, indicator_name):
        """Get data for a specific indicator"""
        if not self.current_symbol or self.stock_data is None:
            return "Vui lòng nhập lệnh /search [mã cổ phiếu] trước!"
            
        try:
            result = f"📊 {category_name} - {indicator_name} cho {self.current_symbol}:\n\n"
            
            if (category_name, indicator_name) in self.stock_data.columns:
                values = self.stock_data[(category_name, indicator_name)].tolist()
                
                # Get metadata (years/quarters) if available
                years = []
                quarters = []
                if ('Meta', 'Năm') in self.stock_data.columns and ('Meta', 'Kỳ') in self.stock_data.columns:
                    years = self.stock_data[('Meta', 'Năm')].tolist()
                    quarters = self.stock_data[('Meta', 'Kỳ')].tolist()
                
                # Display first 5 values with timeframe if available (changed from last 5)
                first_n = min(5, len(values))
                for i in range(first_n):
                    if years and i < len(years):
                        # Check if we're using yearly or quarterly data
                        if self.time_period == "yearly" or self.time_period == "year":
                            time_period = f"{years[i]}"
                        else:
                            # For quarterly data, show quarter and year
                            time_period = f"Q{quarters[i]}/{years[i]}" if i < len(quarters) else f"{years[i]}"
                            
                        if isinstance(values[i], (int, float)):
                            result += f"{time_period}: {values[i]:.2f}\n"
                        else:
                            result += f"{time_period}: {values[i]}\n"
                    else:
                        if isinstance(values[i], (int, float)):
                            result += f"Giá trị {i+1}: {values[i]:.2f}\n"
                        else:
                            result += f"Giá trị {i+1}: {values[i]}\n"
                
                # Add trend analysis
                if len(values) > 1 and all(isinstance(v, (int, float)) for v in values[-3:]):
                    trend = "tăng" if values[-1] > values[-2] else "giảm"
                    change = abs(values[-1] - values[-2])
                    percent = (change / abs(values[-2])) * 100 if values[-2] != 0 else 0
                    result += f"\nChỉ số đang {trend} {percent:.2f}% so với kỳ trước."
                    
                    if len(values) > 2:
                        prev_change = values[-2] - values[-3]
                        current_change = values[-1] - values[-2]
                        if (prev_change > 0 and current_change > 0) or (prev_change < 0 and current_change < 0):
                            result += f"\nChỉ số duy trì xu hướng {trend} trong 2 kỳ liên tiếp."
                
            else:
                result += "Không có dữ liệu cho chỉ số này."
                
            return result
        except Exception as e:
            print(f"Error getting specific indicator: {e}")
            return f"Lỗi khi truy xuất dữ liệu chỉ số: {str(e)}"

    def get_help(self):
        """Return a help message for financial functionality"""
        return (
            "Hướng dẫn sử dụng tìm kiếm thông tin tài chính:\n\n"
            "1. Sử dụng lệnh /search [mã cổ phiếu] để bắt đầu.\n"
            "2. Chọn 'Thông tin tài chính' để xem các chỉ số tài chính.\n"
            "3. Chọn loại chỉ số để xem chi tiết (ví dụ: Định giá, Thanh khoản...).\n"
            "4. Sử dụng lệnh /vnstock_get [chỉ tiêu] để lấy dữ liệu cụ thể.\n"
        )
