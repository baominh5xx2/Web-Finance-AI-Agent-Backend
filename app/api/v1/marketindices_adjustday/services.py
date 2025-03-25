from vnstock import Vnstock
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketIndicesAdjustDayService: 
    def get_adjusted_data(self, symbol, time) -> List[Dict[str, str]]:
        logger.info(f"Getting adjusted data for symbol: {symbol}, time: {time}")
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            if time == "1D":
                start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                interval = '1m'
            elif time == "3M":
                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                interval = '1H'
            elif time == "6M":
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
                interval = '1H'
            elif time == "1Y":
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                interval = '1D'
            elif time == "2Y":
                start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
                interval = '1D'
                
            logger.info(f"Date range: {start_date} to {end_date}, interval: {interval}")
            
            # Create stock instance properly
            logger.info(f"Creating VnStock instance for {symbol}")
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            
            # Get historical data
            logger.info(f"Fetching historical data")
            df = stock.quote.history(start=start_date, end=end_date, interval=interval)
            
            if df is not None and not df.empty:
                logger.info(f"Got {len(df)} data points")
                
                # Convert dates to string format
                dates = df['time'].dt.strftime('%Y-%m-%d').tolist()
                
                # Get close prices
                close_prices = df['close'].tolist() if 'close' in df.columns else []
                
                # Create pairs of close prices and dates
                price_date_pairs = []
                for price, date in zip(close_prices, dates):
                    price_date_pairs.append({
                        "price": float(price),  # Ensure it's a float
                        "date": date
                    })
                
                logger.info(f"Returning {len(price_date_pairs)} price-date pairs")
                return price_date_pairs
            else:
                logger.warning(f"Empty dataframe or None returned for {symbol}")
                return []
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}", exc_info=True)
            return []