from vnstock import Vnstock
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import heapq

class news():
    def __init__(self):
        self.company = Vnstock()
        self.cp = Vnstock().stock(symbol="VCI",source='VCI')
        self.cache_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent.parent / 'api' / 'v1' / 'treemap' / 'cache'
    
    def get_top_symbols_from_cache(self, limit=5):
        """Get top symbols from cache files based on market cap"""
        all_symbols = []
        
        # List of cache files to read
        cache_files = ['VN30.json', 'HOSE.json', 'HNX30.json', 'UPCOM.json']
        
        for file_name in cache_files:
            file_path = self.cache_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        cache_data = json.load(f)
                        
                    # Extract symbols and sort by market_cap (already sorted in most cache files)
                    symbols = [item["symbol"] for item in cache_data.get("data", [])]
                    
                    # Add symbols to the list (avoid duplicates)
                    for symbol in symbols[:limit]:
                        if symbol not in all_symbols:
                            all_symbols.append(symbol)
                            
                except Exception as e:
                    print(f"Error reading {file_name}: {str(e)}")
        
        # Return the top unique symbols
        return all_symbols[:limit]
    
    def get_cp(self, index_name: str):
        all_cp = self.stock.listing.symbols_by_group(index_name)
        return all_cp
    
    def get_news(self, symbol: str, limit=10):
        try:
            company = self.company.stock(symbol=symbol, source='TCBS').company
            news_data = company.news().head(limit)        
            
            # Check the structure of the returned data
            if isinstance(news_data, pd.DataFrame):
                # Convert DataFrame to a list of dictionaries
                news_list = []
                for index, row in news_data.iterrows():
                    news_item = {
                        'title': row.get('title', ''),
                        'publish_date': str(row.get('publish_date', '')),
                        'symbol': symbol  # Add symbol for tracking source
                    }
                    news_list.append(news_item)
                return news_list
            else:
                # If it's not a DataFrame, return an empty list
                print(f"Unexpected data type: {type(news_data)}")
                return []
        except Exception as e:
            print(f"Error getting news for {symbol}: {str(e)}")
            return []
    
    def get_top_stocks_news(self, limit=10):
        """Get news for top stocks and return the most recent ones"""
        # Get top symbols from cache
        top_symbols = self.get_top_symbols_from_cache(5)
        all_news = []
        
        # Get news for each symbol
        for symbol in top_symbols:
            symbol_news = self.get_news(symbol)
            all_news.extend(symbol_news)
        
        # Sort by publish_date (newest first)
        try:
            all_news.sort(key=lambda x: datetime.strptime(x['publish_date'], '%Y-%m-%d %H:%M:%S'), reverse=True)
        except ValueError:
            # Handle different date formats if needed
            try:
                all_news.sort(key=lambda x: datetime.strptime(x['publish_date'], '%Y-%m-%d'), reverse=True)
            except:
                pass
        
        # Return only the top 'limit' news items
        return all_news[:limit]
