from vnstockk import Vnstock
import json
import os
import pandas as pd 
class Vnstockk:
    def get_data_info(self, symbol, time):
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        data = stock.finance.ratio(period=time, lang='vi', dropna=True)
        
        # Create a dedicated folder for storing data
        data_folder = "financial_data"
        os.makedirs(data_folder, exist_ok=True)
        
        # Create filename using symbol and time period
        filename = f"{symbol}_{time}_financial_ratio.json"
        filepath = os.path.join(data_folder, filename)
        
        data_flat = data.copy()
        if isinstance(data_flat.columns, pd.MultiIndex):
            # Convert tuple column names to strings
            data_flat.columns = [str(col) for col in data_flat.columns]
        
        # Convert data to JSON and save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_flat.to_dict(orient='records'), f, ensure_ascii=False, indent=4)
        
        # Print the output
        print(f"Financial data for {symbol} ({time}):")
        print(data)
        
        return data

    def process_df(self, df):
        # Implementation from your code
        if isinstance(df, pd.DataFrame):
            for col in df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
                df[col] = df[col].astype(str)
        return df
    
    def save_company_data(self, data, symbol, time, data_type):
        # Implementation from your code
        data_folder = "financial_data"
        os.makedirs(data_folder, exist_ok=True)
        filename = f"{symbol}_{time}_{data_type}.json"
        filepath = os.path.join(data_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return filepath
    
    # Add all the other methods from your Vnstockk class
    def get_company_overview(self, symbol, time):
        # Implementation
        company = Vnstock().stock(symbol=symbol, source='TCBS').company
        overview = company.overview()
        data = overview.to_dict(orient='records') if hasattr(overview, 'to_dict') else overview
        self.save_company_data(data, symbol, time, "company_overview")
        return data
    
    def get_company_profile(self, symbol, time):
        company = Vnstock().stock(symbol=symbol, source='TCBS').company
        profile = company.profile()
        data = profile.to_dict(orient='records') if hasattr(profile, 'to_dict') else profile
        self.save_company_data(data, symbol, time, "company_profile")
        return data
    
    def get_company_shareholders(self, symbol, time):
        company = Vnstock().stock(symbol=symbol, source='TCBS').company
        shareholders = company.shareholders()
        data = shareholders.to_dict(orient='records') if hasattr(shareholders, 'to_dict') else shareholders
        self.save_company_data(data, symbol, time, "company_shareholders")
        return data
    
    def get_company_insider_deals(self, symbol, time):
        company = Vnstock().stock(symbol=symbol, source='TCBS').company
        insider_deals = company.insider_deals()
        insider_deals = self.process_df(insider_deals)
        data = insider_deals.to_dict(orient='records') if hasattr(insider_deals, 'to_dict') else insider_deals
        self.save_company_data(data, symbol, time, "company_insider_deals")
        return data
    
    def get_company_subsidiaries(self, symbol, time):
        company = Vnstock().stock(symbol=symbol, source='TCBS').company
        subsidiaries = company.subsidiaries()
        subsidiaries = self.process_df(subsidiaries)
        data = subsidiaries.to_dict(orient='records') if hasattr(subsidiaries, 'to_dict') else subsidiaries
        self.save_company_data(data, symbol, time, "company_subsidiaries")
        return data
    
    def get_company_officers(self, symbol, time):
        company = Vnstock().stock(symbol=symbol, source='TCBS').company
        officers = company.officers()
        officers = self.process_df(officers)
        data = officers.to_dict(orient='records') if hasattr(officers, 'to_dict') else officers
        self.save_company_data(data, symbol, time, "company_officers")
        return data
    
    def get_company_news(self, symbol, time):
        company = Vnstock().stock(symbol=symbol, source='TCBS').company
        news = company.news()
        news = self.process_df(news)
        data = news.to_dict(orient='records') if hasattr(news, 'to_dict') else news
        self.save_company_data(data, symbol, time, "company_news")
        return data

    def company_info(self, symbol, time):
        # Implementation
        company_overview = self.get_company_overview(symbol, time)
        company_profile = self.get_company_profile(symbol, time)
        company_shareholders = self.get_company_shareholders(symbol, time)
        company_insider_deals = self.get_company_insider_deals(symbol, time)
        company_subsidiaries = self.get_company_subsidiaries(symbol, time)
        company_officers = self.get_company_officers(symbol, time)
        company_news = self.get_company_news(symbol, time)
        
        all_company_data = {
            "overview": company_overview,
            "profile": company_profile,
            "shareholders": company_shareholders,
            "insider_deals": company_insider_deals,
            "subsidiaries": company_subsidiaries,
            "officers": company_officers,
            "news": company_news
        }
        
        self.save_company_data(all_company_data, symbol, time, "company_info")
        return all_company_data

    def load_financial_data(self, symbol, time_period, data_type="financial_ratio"):
        data_folder = "financial_data"
        filename = f"{symbol}_{time_period}_{data_type}.json"
        filepath = os.path.join(data_folder, filename)
        
        if os.path.exists(filepath):
            try:
                print(f"Loading data from {filepath}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # If data is for financial ratios, convert to DataFrame for easier processing
                if data_type == "financial_ratio" and isinstance(data, list):
                    df = pd.DataFrame(data)
                    
                    # Convert column names to MultiIndex if they are string representations of tuples
                    if df.columns.str.contains(r'^\(.*\)$').any():
                        # Extract tuples from string representation
                        tuples = [eval(col) if col.startswith('(') else ('Other', col) for col in df.columns]
                        df.columns = pd.MultiIndex.from_tuples(tuples)
                    
                    return df
                    
                return data
            except Exception as e:
                print(f"Error loading data from {filepath}: {str(e)}")
                return None
        else:
            print(f"File not found: {filepath}")
            return None

    def load_company_data(self, symbol, time_period):
        """Load company information from saved JSON files"""
        data_type = "company_info"
        return self.load_financial_data(symbol, time_period, data_type)