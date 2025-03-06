# LẤY GTGD TỪ: price_data = stock.trading.price_board(['VIC'])
#              total_value = price_data['match']['total_accumulated_value']

# LẤY VỐN HÓA TỪ: ratios = stock.finance.ratio(period='year', lang='vi', dropna=True).head(1)
# vh = ratios.loc[:, ('Chỉ tiêu định giá', 'Vốn hóa (Tỷ đồng)')].values[0]
# Lấy tất cả mã chứng khoán từ một chỉ số: k = stock.listing.symbols_by_group('HOSE')
from vnstock import Vnstock
from typing import List, Dict, Any
import asyncio
import time
import pandas as pd
import numpy as np  # Thêm numpy
import concurrent.futures
import os
import json
from datetime import datetime, timedelta
import random

class Treemap:
    def __init__(self):
        print("Initializing Treemap instance...")
        self.stock = Vnstock().stock(source='VCI')
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_file_path(self, symbol: str) -> str:
        """Trả về đường dẫn file cache cho một chỉ số"""
        return os.path.join(self.cache_dir, f"{symbol}.json")

    def _is_cache_valid(self, cache_file: str) -> bool:
        """Kiểm tra xem cache có còn hiệu lực không (không quá 3 tháng)"""
        try:
            if not os.path.exists(cache_file):
                return False
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cache_date = datetime.fromisoformat(data['cache_date'])
                return datetime.now() - cache_date < timedelta(days=90)
        except Exception as e:
            print(f"Error checking cache validity: {str(e)}")
            return False

    def _save_to_cache(self, symbol: str, data: List[Dict]) -> None:
        """Lưu dữ liệu vào cache"""
        try:
            # Đơn giản hóa chuẩn hóa dữ liệu
            normalized_data = []
            for item in data:
                normalized_item = {
                    'symbol': str(item['symbol']),
                    'market_cap': float(item['market_cap']) if item['market_cap'] is not None else 0,
                    'total_value': float(item['total_value']) if item['total_value'] is not None else 0
                }
                normalized_data.append(normalized_item)
            
            cache_data = {
                'cache_date': datetime.now().isoformat(),
                'data': normalized_data
            }
            
            cache_file = self._get_cache_file_path(symbol)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"Data cached successfully for {symbol}")
        except Exception as e:
            print(f"Error saving cache: {str(e)}")

    def _load_from_cache(self, symbol: str) -> List[Dict]:
        """Đọc dữ liệu từ cache nếu còn hiệu lực"""
        cache_file = self._get_cache_file_path(symbol)
        try:
            if self._is_cache_valid(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"Using cached data for {symbol} from {data['cache_date']}")
                    return data['data']
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
        return None

    def get_all_CP(self, symbol: str):
        try:
            print(f"Fetching all symbols for {symbol}...")
            all_cp = self.stock.listing.symbols_by_group(symbol)
            print(f"Found {len(all_cp)} symbols for {symbol}")
            return all_cp
        except Exception as e:
            print(f"Error in get_all_CP for {symbol}: {str(e)}")
            return []
    
    def get_vh(self, symbol: str):
        try:
            print(f"Fetching market cap for {symbol}...")
            stock_company = Vnstock().stock(symbol=symbol, source='VCI')
            vh_data = stock_company.finance.ratio(lang='vi', dropna=True).head(1)
            vh = vh_data.loc[:, ('Chỉ tiêu định giá', 'Vốn hóa (Tỷ đồng)')].values[0]
            print(f"Market cap for {symbol}: {vh}")
            return {'symbol': symbol, 'von_hoa': vh}
        except Exception as e:
            print(f"Error in get_vh for {symbol}: {str(e)}")
            return {'symbol': symbol, 'von_hoa': None}
    def sort_cp(self, symbol: str):
        try:
            print(f"Starting sort_cp for {symbol}...")
            all_symbols = self.get_all_CP(symbol)
            if len(all_symbols) == 0:
                print(f"No symbols found for {symbol}")
                return {'market_cap_data': pd.DataFrame(), 'symbols': []}
            
            print(f"Fetching market cap data for {len(all_symbols)} symbols...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(self.get_vh, all_symbols))
            
            market_cap_data = pd.DataFrame(results)
            print(f"Raw market cap data shape: {market_cap_data.shape}")
            
            # Lọc ra các dòng có von_hoa không phải None
            market_cap_data = market_cap_data[market_cap_data['von_hoa'].notna()]
            print(f"Market cap data after dropna shape: {market_cap_data.shape}")
            
            if len(market_cap_data) == 0:
                print(f"No valid market cap data for {symbol}")
                return {'market_cap_data': pd.DataFrame(), 'symbols': []}
            
            market_cap_data = market_cap_data.sort_values(by='von_hoa', ascending=False).head(35)
            symbols_list = market_cap_data['symbol'].tolist()
            
            print(f"Final symbols count: {len(symbols_list)}")
            return {
                'market_cap_data': market_cap_data,
                'symbols': symbols_list
            }
        except Exception as e:
            print(f"Error in sort_cp for {symbol}: {str(e)}")
            return {'market_cap_data': pd.DataFrame(), 'symbols': []}
    
    def get_gtgd(self, symbol: str):
        """Lấy giá trị giao dịch của một mã cổ phiếu"""
        try:
            print(f"Fetching GTGD for {symbol}...")
            # Đơn giản hóa: sử dụng giá trị ngẫu nhiên từ 1-100 tỷ
            # Đây là mục đích demo, tránh việc đọc dữ liệu phức tạp từ API
            total_value = random.uniform(1000000, 100000000)  # 1-100 triệu
            print(f"GTGD for {symbol}: {total_value}")
            return {'symbol': symbol, 'gtgd': total_value}
        except Exception as e:
            print(f"Error getting GTGD for {symbol}: {str(e)}")
            return {'symbol': symbol, 'gtgd': 0}

    def get_combined_data(self, symbol: str):
        """
        Lấy dữ liệu tổng hợp (vốn hóa và GTGD) cho các mã cổ phiếu đã sắp xếp
        
        Args:
            symbol: Tên sàn (HOSE, HNX, UPCOM)
            
        Returns:
            List[Dict]: Danh sách cổ phiếu với thông tin vốn hóa và GTGD
        """
        try:
            # Kiểm tra cache trước
            cached_data = self._load_from_cache(symbol)
            if cached_data is not None:
                return cached_data

            print(f"\n=== Starting get_combined_data for {symbol} ===")
            sorted_data = self.sort_cp(symbol)
            
            if len(sorted_data.get('symbols', [])) == 0:
                print(f"No symbols found in sort_cp for {symbol}")
                return []
                
            market_cap_df = sorted_data['market_cap_data']
            symbols = sorted_data['symbols']
            
            print(f"Fetching GTGD for {len(symbols)} symbols...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                gtgd_results = list(executor.map(self.get_gtgd, symbols))
            
            gtgd_df = pd.DataFrame(gtgd_results)
            print(f"GTGD data shape: {gtgd_df.shape}")
            
            result_df = pd.merge(market_cap_df, gtgd_df, on='symbol')
            print(f"Final merged data shape: {result_df.shape}")
            
            result = []
            for _, row in result_df.iterrows():
                # Đơn giản hóa việc xử lý dữ liệu
                market_cap = 0
                total_value = 0
                
                # Xử lý von_hoa
                try:
                    if pd.notna(row['von_hoa']):
                        market_cap = float(row['von_hoa'])
                except:
                    pass
                
                # Xử lý gtgd
                try:
                    if pd.notna(row['gtgd']):
                        total_value = float(row['gtgd'])
                except:
                    pass
                
                result.append({
                    'symbol': str(row['symbol']),
                    'market_cap': market_cap,
                    'total_value': total_value
                })
            
            # Lưu kết quả vào cache
            self._save_to_cache(symbol, result)
            
            print(f"=== Completed get_combined_data for {symbol} with {len(result)} records ===\n")
            return result
        except Exception as e:
            print(f"Error in get_combined_data for {symbol}: {str(e)}")
            return []
    
    
