from vnstock import Vnstock
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Tuple, Dict

class MarketIndicesAdjustDayService:
    def __init__(self):
        self.vnstock = Vnstock
        
    def get_adjusted_data(self, symbol,time) -> List[Dict[str, str]]:
        # Fix method name to match what router is calling
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            if time == "3M":
                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                interval = '1D'
            elif time == "6M":
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
                interval = '1D'
            elif time == "1Y":
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                interval = '1M'
            elif time == "2Y":
                start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
                interval = '1M'
            # Create stock instance properly
            stock = self.vnstock().stock(symbol=symbol, source='VCI')
            
            # Get historical data
            df = stock.quote.history(start=start_date, end=end_date, interval=interval)
            
            if df is not None and not df.empty:
                # Convert dates to string format
                dates = df['time'].dt.strftime('%Y-%m-%d').tolist()
                
                # Get close prices
                close_prices = df['close'].tolist() if 'close' in df.columns else []
                
                # Create pairs of close prices and dates
                price_date_pairs = []
                for price, date in zip(close_prices, dates):
                    price_date_pairs.append({
                        "price": price,
                        "date": date
                    })
                
                return price_date_pairs
            else:
                return []
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return []