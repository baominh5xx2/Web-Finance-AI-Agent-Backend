from vnstock import Vnstock
from datetime import datetime, timedelta

class TreemapColorService:
    def __init__(self):
        self.vnstock = Vnstock
    def get_data_cp(self,symbol):
        stock = self.vnstock().stock(symbol=symbol, source='VCI')
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')  # Fix parentheses placement
        df = stock.quote.history(start=start_date, end=end_date, interval='1D')
        difference = df['close'].iloc[-1] - df['close'].iloc[-2]
        percentage_change = (difference / df['close'].iloc[-2]) * 100
        return difference, percentage_change
