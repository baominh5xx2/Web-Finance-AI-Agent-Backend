# API treemap just for the developer to use
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
        except Exception as e:
            print(f"Error saving cache: {str(e)}")

    def _load_from_cache(self, symbol: str) -> List[Dict]:
        """Đọc dữ liệu từ cache nếu còn hiệu lực"""
        cache_file = self._get_cache_file_path(symbol)
        try:
            if self._is_cache_valid(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data['data']
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
        return None

    def get_all_CP(self, symbol: str):
        try:
            stock = Vnstock().stock(symbol="VCI", source='VCI')
            all_cp = stock.listing.symbols_by_group(symbol)
            return all_cp
        except Exception as e:
            return []
    
    def get_vh(self, symbol: str):
        try:
            stock_company = Vnstock().stock(symbol=symbol, source='VCI')
            vh_data = stock_company.finance.ratio(lang='vi', dropna=True).head(1)
            vh = vh_data.loc[:, ('Chỉ tiêu định giá', 'Vốn hóa (Tỷ đồng)')].values[0]
            return {'symbol': symbol, 'von_hoa': vh}
        except Exception as e:
            return {'symbol': symbol, 'von_hoa': None}

    def sort_cp(self, symbol: str):
        try:
            print(f"Starting sort_cp for {symbol}...")
            
            # Check if we have valid cached data
            cached_data = self._load_from_cache(symbol)
            if cached_data:
                print(f"Using cached data for {symbol}")
                # Convert cache data to DataFrame
                market_cap_data = pd.DataFrame([
                    {'symbol': item['symbol'], 'von_hoa': item['market_cap']} 
                    for item in cached_data
                ])
                symbols_list = market_cap_data['symbol'].tolist()
                return {
                    'market_cap_data': market_cap_data,
                    'symbols': symbols_list
                }
            
            # If no valid cache, fetch fresh data
            all_symbols = self.get_all_CP(symbol)
            if len(all_symbols) == 0:
                print(f"No symbols found for {symbol}")
                return {'market_cap_data': pd.DataFrame(), 'symbols': []}
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(self.get_vh, all_symbols))
            
            market_cap_data = pd.DataFrame(results)
            # Filter out rows where von_hoa is None
            market_cap_data = market_cap_data[market_cap_data['von_hoa'].notna()]
            
            if len(market_cap_data) == 0:
                return {'market_cap_data': pd.DataFrame(), 'symbols': []}
            
            market_cap_data = market_cap_data.sort_values(by='von_hoa', ascending=False).head(35)
            symbols_list = market_cap_data['symbol'].tolist()
            
            # Save the results to cache
            cache_data = [
                {'symbol': row['symbol'], 'market_cap': row['von_hoa'], 'total_value': 0} 
                for _, row in market_cap_data.iterrows()
            ]
            self._save_to_cache(symbol, cache_data)
            
            return {
                'market_cap_data': market_cap_data,
                'symbols': symbols_list
            }
        except Exception as e:
            print(f"Error in sort_cp: {str(e)}")
            return {'market_cap_data': pd.DataFrame(), 'symbols': []}

