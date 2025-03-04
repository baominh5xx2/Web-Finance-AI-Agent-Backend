from datetime import datetime, timedelta
from fastapi import Depends, APIRouter, HTTPException
from typing import Dict, List, Any
import pandas as pd
from vnstock import Vnstock

class Market_indices:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_expiry = 600  # Cache expiry in seconds (10 minutes)
    
    def get_market_indices(self, index_code: str = "VNINDEX", top: int = 30) -> List[Dict[str, Any]]:
        """
        Get market index data using vnstock and return the last entries
        
        Args:
            index_code: The market index code (default: VNINDEX)
                Options: VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALL, VN100, VNALL, etc.
            top: Number of entries to return (default: 30)
        
        Returns:
            List of dictionaries containing market index data (last entries)
        """
        current_time = datetime.now().timestamp()
        cache_key = f"{index_code}_{top}"
        
        # Check if we have cached data that's not expired
        if cache_key in self.cache and current_time - self.cache_time.get(cache_key, 0) < self.cache_expiry:
            print(f"Using cached data for {index_code}")
            return self.cache[cache_key]
        
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            print(end_date)
            start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

            stock = Vnstock().stock(source='VCI')
            data = stock.quote.history(symbol=index_code, start=start_date, end=end_date, interval='1m')
            
            # Convert to list for API response
            if isinstance(data, pd.DataFrame):
                # Ensure we return only the last N entries and only 'time' and 'close' columns
                # If your DataFrame doesn't have these exact column names, adjust accordingly
                if 'time' in data.columns and 'open' in data.columns:
                    # Modified to get the last 'top' rows instead of the first
                    top_data = data[['time', 'open']].tail(top)
                else:
                    # If column names are different, map them - adjust to your actual column names
                    time_col = data.columns[0]  # assuming first column is date/time
                    close_col = [col for col in data.columns if 'open' in col.lower()][0]  # find close column
                    # Modified to get the last 'top' rows instead of the first
                    top_data = data[[time_col, close_col]].tail(top)
                    top_data.columns = ['time', 'open']  # rename columns
                
                result = top_data.to_dict(orient='records')
            else:
                # If data is not a DataFrame, try to get last entries if it's a list
                if isinstance(data, list) and len(data) > top:
                    result = data[-top:]  # Get the last 'top' items
                else:
                    result = data
                
            # Cache the result
            self.cache[cache_key] = result
            self.cache_time[cache_key] = current_time
            
            return result
        except Exception as e:
            print(f"Error fetching market index data: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")