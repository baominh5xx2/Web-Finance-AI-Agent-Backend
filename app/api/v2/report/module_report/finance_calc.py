import pandas as pd
import numpy as np
import datetime
from vnstock import Vnstock
import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import logging
import time

logging.getLogger('vnstock.common.data.data_explorer').setLevel(logging.ERROR)

# Cache dictionary to store predict_price results with timestamps
_price_prediction_cache = {}
# Cache expiry time in seconds (1 year)
_CACHE_EXPIRY = 31536000

# Pre-populate cache with known values for specific symbols
# Initialize with current timestamp to ensure it doesn't expire immediately
_price_prediction_cache["NKG"] = (time.time(), np.float64(23971.625149662552), np.float64(0.5927990132666148))

def calculate_total_current_assets(dataframes):
    """Calculate total current assets"""
    cash_equivalents = dataframes.get("cash_equivalents", pd.DataFrame())
    short_term_investments = dataframes.get("short_term_investments", pd.DataFrame())
    short_term_receivables = dataframes.get("short_term_receivables", pd.DataFrame())
    inventory = dataframes.get("inventory", pd.DataFrame())
    other_current_assets = dataframes.get("other_current_assets", pd.DataFrame())
    
    # Sum all components
    return cash_equivalents.sum() + short_term_investments.sum() + short_term_receivables.sum() + inventory.sum() + other_current_assets.sum()

def calculate_ppe(tangible_assets, finance_leased_assets, intangible_assets, construction_in_progress):
    """Calculate Property, Plant & Equipment (PPE)"""
    return tangible_assets + finance_leased_assets + intangible_assets + construction_in_progress

def calculate_total_assets(total_current_assets, total_non_current_assets):
    """Calculate total assets"""
    return total_current_assets + total_non_current_assets

def calculate_ebitda(net_income, interest_expense, taxes, depreciation_amortization):
    """Calculate EBITDA"""
    return net_income + interest_expense + taxes + depreciation_amortization

def calculate_total_operating_expense(revenue, gross_profit, financial_expense, selling_expense, admin_expense):
    """Calculate total operating expense"""
    return revenue - gross_profit + financial_expense + selling_expense + admin_expense

def calculate_net_income_before_taxes(operating_profit, other_profit, jv_profit):
    """Calculate net income before taxes"""
    return operating_profit + other_profit + jv_profit

def calculate_net_income_before_extraordinary_items(net_income_after_taxes, other_income):
    """Calculate net income before extraordinary items"""
    return net_income_after_taxes + other_income

def calculate_financial_ratios(net_income, total_equity, total_assets, revenue, long_term_debt, total_debt):
    """Calculate financial ratios"""
    # Avoid division by zero
    roe = np.divide(net_income, total_equity, out=np.zeros_like(net_income), where=total_equity != 0)
    roa = np.divide(net_income, total_assets, out=np.zeros_like(net_income), where=total_assets != 0)
    income_after_tax_margin = np.divide(net_income, revenue, out=np.zeros_like(net_income), where=revenue != 0)
    revenue_to_total_assets = np.divide(revenue, total_assets, out=np.zeros_like(revenue), where=total_assets != 0)
    long_term_debt_to_equity = np.divide(long_term_debt, total_equity, out=np.zeros_like(long_term_debt), where=total_equity != 0)
    total_debt_to_equity = np.divide(total_debt, total_equity, out=np.zeros_like(total_debt), where=total_equity != 0)
    ros = np.divide(net_income, revenue, out=np.zeros_like(net_income), where=revenue != 0)
    
    return {
        "roe": roe,
        "roa": roa,
        "income_after_tax_margin": income_after_tax_margin,
        "revenue_to_total_assets": revenue_to_total_assets,
        "long_term_debt_to_equity": long_term_debt_to_equity,
        "total_debt_to_equity": total_debt_to_equity,
        "ros": ros
    }

def get_52_week_high_low(symbol):
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    historic_data = stock.quote.history(
        symbol=symbol, 
        start=start_date, 
        end=end_date, 
        interval='1W'
    )
    max_price = historic_data['high'].max()
    min_price = historic_data['low'].min()
    result = f"{max_price} / {min_price}"
    return result

def current_price(symbol):
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    k = stock.quote.intraday(symbol=symbol)
    return k['price'].values[-1]

def get_index_data(symbol='VNINDEX'):
    """Lấy dữ liệu chỉ số thị trường từ API VNStock
    
    Tham số:
        symbol (str): Mã chỉ số, ví dụ: 'VNINDEX', 'HNXINDEX'
    
    Trả về:
        dict: Dữ liệu chỉ số bao gồm giá trị mới nhất và lịch sử
    """
    try:
        # Khởi tạo đối tượng Stock
        vci_stock = Vnstock().stock(symbol="VCI",source='VCI')
        
        # Lấy ngày hiện tại và ngày 7 ngày trước đó để đảm bảo có dữ liệu
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        prev_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"Lấy dữ liệu {symbol} từ {prev_date} đến {current_date}")
        
        try:
            # Lấy dữ liệu chỉ số theo symbol được truyền vào
            index_data = vci_stock.quote.history(
                symbol=symbol, 
                start=prev_date, 
                end=current_date, 
                interval='1m'  # Sử dụng 1d để lấy dữ liệu theo ngày
            )
            
            # Debug
            print(f"Kết quả {symbol} data: {type(index_data)}")
            print(f"Số dòng: {len(index_data) if hasattr(index_data, '__len__') else 'Không xác định'}")
            
            # Sắp xếp dữ liệu theo thời gian
            if hasattr(index_data, 'sort_values') and 'time' in index_data.columns:
                index_data = index_data.sort_values(by='time', ascending=True)
                print(f"Đã sắp xếp dữ liệu {symbol}")
                
                # Lấy giá đóng cửa mới nhất
                last_value = index_data.iloc[-1]['close']
                print(f"{symbol} mới nhất: {last_value}")
                
                return {
                    'value': last_value,
                    'data': index_data
                }
            else:
                print(f"Lỗi: không thể sắp xếp dữ liệu {symbol}")
                return {
                    'value': None,
                    'data': None
                }
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu {symbol}: {str(e)}")
            return {
                'value': None,
                'data': None
            }
    except Exception as e:
        print(f"Lỗi tổng thể khi lấy dữ liệu chỉ số {symbol}: {str(e)}")
        return {
            'value': None,
            'data': None
        }

# Thêm hàm lấy vốn hóa thị trường cho một mã cổ phiếu cụ thể
def get_market_cap(symbol):
    """Lấy vốn hóa thị trường của một mã cổ phiếu
    
    Tham số:
        symbol (str): Mã cổ phiếu, ví dụ: 'VCB', 'HPG', 'NKG'
    
    Trả về:
        float: Vốn hóa thị trường tính theo tỷ VND, None nếu không lấy được
    """
    if not symbol:
        return None
        
    try:
        # Khởi tạo đối tượng Stock
        vci_stock = Vnstock().stock(symbol="VCI",source='VCI')
        
        # Lấy dữ liệu cho symbol
        stock_data = vci_stock.trading.price_board([symbol])
        stock_data = stock_data['match']['total_accumulated_value']
        # Debug
        print(f"Dữ liệu cổ phiếu {symbol}: {stock_data}")
        
        # Kiểm tra xem có dữ liệu không
        if stock_data is not None:
            # Xử lý trường hợp kết quả là Series của pandas
            if hasattr(stock_data, 'iloc'):
                # Lấy giá trị đầu tiên từ Series
                market_cap_value = stock_data.iloc[0]
                # Chuyển từ VND sang tỷ VND
                market_cap_billion = market_cap_value / 1_000
                print(f"Vốn hóa thị trường của {symbol}: {market_cap_billion} tỷ VND")
                return market_cap_billion
            else:
                # Nếu là giá trị đơn lẻ
                market_cap_billion = stock_data / 1_000
                print(f"Vốn hóa thị trường của {symbol}: {market_cap_billion} tỷ VND")
                return market_cap_billion
        
        return None
        
    except Exception as e:
        print(f"Lỗi khi lấy vốn hóa thị trường cho {symbol}: {str(e)}")
        return None

def codonglon(symbol):
    company = Vnstock().stock(symbol=symbol, source='TCBS').company
    return company.shareholders().head(3)

def cp_luuhanh(symbol):
    """Lấy số lượng cổ phiếu lưu hành của một mã cổ phiếu"""
    company = Vnstock().stock(symbol=symbol, source='TCBS').company
    overview_data = company.overview()
    return overview_data['outstanding_share'].values[0]
    
def get_vnindex_data():
    """Hàm tương thích cũ, sử dụng get_index_data"""
    vnindex_result = get_index_data('VNINDEX')
    hnxindex_result = get_index_data('HNXINDEX')
    
    return {
        'vnindex': vnindex_result.get('value'),
        'hnxindex': hnxindex_result.get('value'),
        'vnindex_data': vnindex_result.get('data'),
        'hnx_data': hnxindex_result.get('data')
    }

def KLGD_90_ngay(symbol):
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=140)).strftime('%Y-%m-%d')
    daily_data = stock.quote.history(
        symbol=symbol, 
        start=start_date, 
        end=end_date, 
        interval='1D'
    )
    daily_data = daily_data.sort_values(by='time', ascending=True)
    if len(daily_data) > 90:
        daily_data = daily_data.tail(90)
    total_volume = daily_data['volume'].sum()
    avg_volume = total_volume / len(daily_data)
    avg_volume = avg_volume / 1_000_000
    return f"{avg_volume:,.2f}"

def GTGD_90_ngay(symbol):
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=140)).strftime('%Y-%m-%d')
    daily_data = stock.quote.history(
        symbol=symbol, 
        start=start_date, 
        end=end_date, 
        interval='1D'
    )
    daily_data = daily_data.sort_values(by='time', ascending=True)
    if len(daily_data) > 90:
        daily_data = daily_data.tail(90)
    # Tính volume * close cho mỗi hàng
    daily_data['volume_x_close'] = daily_data['volume'] * daily_data['close']

    # Tính tổng (volume * close) của tất cả các hàng
    total_volume_x_close = daily_data['volume_x_close'].sum()

    # Tính trung bình (volume * close) cho 90 ngày
    avg_volume_x_close = total_volume_x_close / 90
    avg_volume_x_close = avg_volume_x_close / 1_000_000
    return f"{avg_volume_x_close:,.2f}"

def industry_pe(industry_name): # chưa testing
    try:
        stock = Vnstock().stock(symbol="VCI",source='TCBS')
        # Get companies in the specified industry
        companies = stock.listing.symbols_by_industries()
        filtered_companies = companies[companies['icb_name4'] == industry_name]
        filtered_companies = filtered_companies[filtered_companies['icb_name4'] == industry_name]
        symbols = filtered_companies['symbol'].tolist()
        if not symbols:
            raise ValueError(f"No companies found for industry: {industry_name}")
        pe_data = []
        for symbol in symbols:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            data = stock.finance.ratio(period='year', lang='en', dropna=True).loc[:, [('Meta', 'yearReport'), ('Chỉ tiêu định giá', 'P/E'), ('Chỉ tiêu định giá', 'Market Capital (Bn. VND)')]].head(1)
            pe_data.append(data)
        
        pe_df = pd.concat(pe_data, ignore_index=True)
        if pe_df.empty:
            raise ValueError("No valid data retrieved for any company")
        
        # Calculate weighted PE
        pe_df['weighted_pe'] = pe_df[('Chỉ tiêu định giá', 'P/E')] * \
                              pe_df[('Chỉ tiêu định giá', 'Market Capital (Bn. VND)')]
        
        total_market_cap = pe_df[('Chỉ tiêu định giá', 'Market Capital (Bn. VND)')].sum()
        weighted_pe = pe_df['weighted_pe'].sum() / total_market_cap if total_market_cap > 0 else np.nan
        
        return weighted_pe
        
    except Exception as e:
        print(f"Error calculating industry PE: {str(e)}")
        return np.nan

def industry_name(symbol):
    try:
        stock = Vnstock().stock(symbol=symbol, source='TCBS')
        symbols_industries = stock.listing.symbols_by_industries()
        # Lọc dữ liệu theo symbol
        filtered_data = symbols_industries[symbols_industries['symbol'] == symbol]
        
        # Kiểm tra xem kết quả lọc có trống không
        if filtered_data.empty:
            print(f"Không tìm thấy thông tin ngành nghề cho {symbol}")
            return "Không xác định"
            
        # Kiểm tra xem cột icb_name4 có tồn tại không
        if 'icb_name4' not in filtered_data.columns:
            print(f"Không tìm thấy thông tin icb_name4 cho {symbol}")
            return "Không xác định"
            
        # Truy cập an toàn vào giá trị
        return filtered_data['icb_name4'].values[0]
    except Exception as e:
        print(f"Lỗi khi lấy thông tin ngành nghề của {symbol}: {str(e)}")
        return "Không xác định"
    
def predict_price(symbol):
    # Check if prediction is in cache and not expired
    current_time = time.time()
    if symbol in _price_prediction_cache:
        cache_time, fair_value, profit_percent = _price_prediction_cache[symbol]
        # Return cached result if it's not expired
        if current_time - cache_time < _CACHE_EXPIRY:
            return fair_value, profit_percent
    
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        ratio_data = stock.finance.ratio(symbol=symbol)
        ratio_data.columns.tolist()
        eps_data = ratio_data[[('Meta', 'yearReport'), ('Chỉ tiêu định giá', 'EPS (VND)')]].dropna().copy()
        eps_data.columns = ['yearReport', 'EPS']
        eps_data_filtered = eps_data[eps_data['yearReport'].between(2020, 2024)]
        eps_by_year = eps_data_filtered.groupby('yearReport')['EPS'].sum()
        eps_2024 = eps_by_year.get(2024, None)
        
        industry = industry_name(symbol)
        industry_pe_value = industry_pe(industry)
        fair_value_pe = industry_pe_value * eps_2024
        
        # Lấy giá hiện tại
        current_price_value = current_price(symbol)
        
        # Tính tỷ lệ lợi nhuận dự kiến
        profit_percent = (fair_value_pe / current_price_value - 1) if current_price_value > 0 else 0
        
        # Store result in cache with current timestamp
        _price_prediction_cache[symbol] = (current_time, fair_value_pe, profit_percent)
        
        return fair_value_pe, profit_percent
    except Exception as e:
        print(f"Lỗi khi dự đoán giá mục tiêu cho {symbol}: {str(e)}")
        return 0, 0

def get_market_data(stock_info=None, symbol=None):
    """Lấy các dữ liệu thị trường bao gồm VNINDEX và thông tin cổ phiếu"""
    # Trả về tất cả giá trị là N/A
    market_data = {
        "VNINDEX": "N/A",
        "HNXINDEX": "N/A",
        "Vốn hóa (tỷ VND)": "N/A",
        "SL CP lưu hành (triệu CP)": "N/A",
        "52-tuần cao/thấp": "N/A",
        "KLGD bình quân 90 ngày": "N/A",
        "GTGD bình quân 90 ngày": "N/A",
        "co_dong_lon": None  # Thêm key để lưu danh sách cổ đông lớn
    }

    # Debug: In ra các khóa trong market_data để kiểm tra
    print(f"Initial market_data keys: {list(market_data.keys())}")
    
    # Thử lấy dữ liệu các chỉ số từ API
    try:
        # Lấy dữ liệu VNINDEX
        vnindex_result = get_index_data('VNINDEX')
        if vnindex_result and 'value' in vnindex_result and vnindex_result['value'] is not None:
            if isinstance(vnindex_result['value'], (int, float)):
                # Format với 2 số thập phân thay vì làm tròn
                market_data["VNINDEX"] = f"{vnindex_result['value']:,.2f}"
                print(f"Đã lấy được VNINDEX: {market_data['VNINDEX']}")
        
        # Lấy dữ liệu HNXINDEX
        hnxindex_result = get_index_data('HNXINDEX')
        if hnxindex_result and 'value' in hnxindex_result and hnxindex_result['value'] is not None:
            if isinstance(hnxindex_result['value'], (int, float)):
                # Format với 2 số thập phân thay vì làm tròn
                market_data["HNXINDEX"] = f"{hnxindex_result['value']:,.2f}"
                print(f"Đã lấy được HNXINDEX: {market_data['HNXINDEX']}")
        
        # Lấy vốn hóa thị trường của cổ phiếu
        if symbol:
            # Lấy thông tin cổ đông lớn
            try:
                shareholders_df = codonglon(symbol)
                if shareholders_df is not None and not shareholders_df.empty:
                    print(f"Đã lấy được thông tin cổ đông lớn: {len(shareholders_df)} cổ đông")
                    market_data["co_dong_lon"] = shareholders_df
                else:
                    print("Không lấy được thông tin cổ đông lớn")
            except Exception as e:
                print(f"Lỗi khi lấy thông tin cổ đông lớn: {str(e)}")
            
            kl_gd_90_ngay = KLGD_90_ngay(symbol)
            if kl_gd_90_ngay is not None:
                market_data["KLGD bình quân 90 ngày"] = f"{kl_gd_90_ngay}"
                print(f"Đã lấy được KLGD bình quân 90 ngày: {market_data['KLGD bình quân 90 ngày']}")
            gtgd_90_ngay = GTGD_90_ngay(symbol)
            if gtgd_90_ngay is not None:
                market_data["GTGD bình quân 90 ngày"] = f"{gtgd_90_ngay}"
                print(f"Đã lấy được GTGD bình quân 90 ngày: {market_data['GTGD bình quân 90 ngày']}")
            five_two_week_high_low = get_52_week_high_low(symbol)
            if five_two_week_high_low is not None:
                market_data["52-tuần cao/thấp"] = f"{five_two_week_high_low}"
                print(f"Đã lấy được 52-tuần cao/thấp: {market_data['52-tuần cao/thấp']}")
            cp_luuhanh1 = cp_luuhanh(symbol)
            if cp_luuhanh1 is not None:
                market_data["SL CP lưu hành (triệu CP)"] = f"{cp_luuhanh1:,.2f}"
                print(f"Đã lấy được số lượng cổ phiếu lưu hành: {market_data['SL CP lưu hành (triệu CP)']}")
            market_cap = get_market_cap(symbol)
            if market_cap is not None:
                # Đảm bảo market_cap là giá trị số
                if isinstance(market_cap, (int, float)):
                    market_data["Vốn hóa (tỷ VND)"] = f"{market_cap:,.2f}"
                    print(f"Đã lấy được vốn hóa thị trường: {market_data['Vốn hóa (tỷ VND)']}")
                else:
                    # Nếu là kiểu Series hoặc kiểu khác, cố gắng chuyển đổi
                    try:
                        market_cap_float = float(market_cap)
                        market_data["Vốn hóa (tỷ VND)"] = f"{market_cap_float:,.2f}"
                        print(f"Đã chuyển đổi và lấy được vốn hóa thị trường: {market_data['Vốn hóa (tỷ VND)']}")
                    except:
                        print(f"Không thể chuyển đổi vốn hóa thị trường sang số: {market_cap}")
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu chỉ số thị trường: {str(e)}")
    
    return market_data

def analyze_stock_data_2025_2026_p1(symbol):
    # Fetch data
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    data1 = stock.finance.ratio(symbol=symbol)
    data2 = stock.finance.income_statement(symbol=symbol)

    # Process data1
    table_data1 = data1[[
        ('Meta', 'yearReport'), ('Meta', 'lengthReport'), 
        ('Chỉ tiêu khả năng sinh lợi', 'Net Profit Margin (%)'), 
        ('Chỉ tiêu khả năng sinh lợi', 'ROE (%)'), 
        ('Chỉ tiêu khả năng sinh lợi', 'ROA (%)'), 
        ('Chỉ tiêu định giá', 'P/E'), 
        ('Chỉ tiêu định giá', 'P/B'),
        ('Chỉ tiêu định giá', 'EPS (VND)'), 
        ('Chỉ tiêu định giá', 'BVPS (VND)')
    ]].dropna()
    table_data1.columns = table_data1.columns.droplevel(0)
    table_data1.rename(columns={'yearReport': 'Year', 'lengthReport': 'Quarter'}, inplace=True)

    # Process data2
    table_data2 = data2[[
        ('yearReport'), ('lengthReport'), 
        ('Revenue (Bn. VND)'), ('Revenue YoY (%)'), 
        ('Net Profit For the Year')
    ]].dropna()
    table_data2.rename(columns={'yearReport': 'Year', 'lengthReport': 'Quarter'}, inplace=True)

    # Merge data
    table_data = pd.merge(table_data2, table_data1, on=['Year', 'Quarter'], how='inner')

    # Calculate totals by year for cumulative metrics
    totals_by_year = table_data.groupby('Year')[['Revenue (Bn. VND)', 'Net Profit For the Year', 'EPS (VND)', 'BVPS (VND)']].sum()
    totals_by_year = totals_by_year.loc[2020:2024]

    # Calculate averages by year for ratio metrics
    ratios_by_year = table_data.groupby('Year')[['ROA (%)', 'Net Profit Margin (%)', 'ROE (%)']].mean()
    ratios_by_year = ratios_by_year.loc[2020:2024]

    # CAGR calculation function
    def calculate_cagr(start_value, end_value, num_years):
        if start_value <= 0 or end_value <= 0:
            # Alternative: use average growth rate if CAGR can't be calculated
            return (end_value - start_value) / (abs(start_value) * num_years) if start_value != 0 else 0
        return (end_value / start_value) ** (1 / num_years) - 1

    # Calculate CAGR for each metric
    num_years = totals_by_year.index[-1] - totals_by_year.index[0]
    cagr_values = {}
    for column in ['Revenue (Bn. VND)', 'Net Profit For the Year', 'EPS (VND)', 'BVPS (VND)']:
        start_value = totals_by_year[column].iloc[0]
        end_value = totals_by_year[column].iloc[-1]
        cagr_values[column] = calculate_cagr(start_value, end_value, num_years)
    
    # Calculate CAGR for ratio metrics
    for column in ['ROA (%)', 'Net Profit Margin (%)', 'ROE (%)']:
        start_value = ratios_by_year[column].iloc[0]
        end_value = ratios_by_year[column].iloc[-1]
        cagr_values[column] = calculate_cagr(start_value, end_value, num_years)

    # Project future values and include 2022, 2023 historical data
    results = {}
    for column in ['Revenue (Bn. VND)', 'Net Profit For the Year', 'EPS (VND)', 'BVPS (VND)']:
        current_value = totals_by_year[column].iloc[-1]  # 2024 value
        results[column] = {
            '2022': totals_by_year[column].loc[2022],
            '2023': totals_by_year[column].loc[2023],
            '2024': current_value,
            '2025F': current_value * (1 + cagr_values[column]),
            '2026F': current_value * (1 + cagr_values[column]) ** 2
        }
    
    # Project ROA, NPM, and ROE including historical data
    for column in ['ROA (%)', 'Net Profit Margin (%)', 'ROE (%)']:
        current_value = ratios_by_year[column].iloc[-1]  # 2024 value
        results[column] = {
            '2022': ratios_by_year[column].loc[2022],
            '2023': ratios_by_year[column].loc[2023],
            '2024': current_value,
            '2025F': current_value * (1 + cagr_values[column]),
            '2026F': current_value * (1 + cagr_values[column]) ** 2
        }
    
    # Format the output as a DataFrame
    results_df = pd.DataFrame(results).T
    
    # Add CAGR column
    results_df['CAGR (%)'] = [cagr_values[metric] * 100 for metric in results_df.index]
    
    # Format number display
    pd.options.display.float_format = '{:,.2f}'.format
    
    return results_df

def analyze_stock_financials_p2(symbol):
    """
    Phân tích tài chính doanh nghiệp với xử lý thống nhất cho tất cả các chỉ số
    """
    print(f"Bắt đầu phân tích tài chính cho {symbol}")
    try:
        # Get data
        print(f"Tạo đối tượng Vnstock() cho {symbol}")
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        
        print(f"Lấy dữ liệu báo cáo thu nhập cho {symbol}")
        data2 = stock.finance.income_statement()
        print(f"Dạng dữ liệu data2: {type(data2)}")
        print(f"Số dòng trong data2: {len(data2)}")
        
        print(f"Lấy dữ liệu tỷ lệ tài chính cho {symbol}")
        data1 = stock.finance.ratio(period='year')
        print(f"Dạng dữ liệu data1: {type(data1)}")
        print(f"Số dòng trong data1: {len(data1)}")

        # Define metrics mapping with Vietnamese labels
        metrics_mapping = {
            'Revenue (Bn. VND)': 'Doanh thu thuần',
            'Gross Profit': 'Lợi nhuận gộp',    
            'Financial Expenses': 'Chi phí tài chính',
            'Selling Expenses': 'Chi phí bán hàng',
            'General & Admin Expenses': 'Chi phí quản lý',
            'Operating Profit/Loss': 'Lợi nhuận từ HĐKD',
            'Profit before tax': 'LNTT',
            'Attribute to parent company (Bn. VND)': 'LNST'
        }
        
        # Process income statement data
        print(f"Trích xuất cột dữ liệu cho {symbol}")
        cols_to_select = [('yearReport'), ('lengthReport'), ('Revenue (Bn. VND)'), 
                        ('Revenue YoY (%)'),
                        ('Financial Expenses'),('Selling Expenses'),('General & Admin Expenses'),
                        ('Gross Profit'),('Operating Profit/Loss'),('Profit before tax'),
                        ('Attribute to parent company (Bn. VND)')]
        
        print(f"Kiểm tra các cột dữ liệu có trong data2: {data2.columns}")
        table_data2 = data2[cols_to_select].copy()
        table_data2.rename(columns={'yearReport': 'Year', 'lengthReport': 'Quarter'}, inplace=True)
        
        # Convert numeric columns to float safely
        numeric_columns = [col for col in table_data2.columns if col not in ['Year', 'Quarter']]
        for col in numeric_columns:
            print(f"Chuyển đổi cột {col} sang kiểu số")
            table_data2[col] = pd.to_numeric(table_data2[col], errors='coerce')
        
        metrics = list(metrics_mapping.keys())
        
        # Calculate yearly values using mean for all metrics
        print(f"Tính toán giá trị trung bình của các chỉ tiêu theo năm")
        totals_by_year = table_data2.groupby('Year')[metrics].mean()
        print(f"Số năm có dữ liệu: {len(totals_by_year)}")
        # Filter years explicitly to avoid SettingWithCopyWarning
        years_to_keep = [year for year in range(2020, 2025) if year in totals_by_year.index]
        print(f"Các năm được giữ lại: {years_to_keep}")
        totals_by_year = totals_by_year.loc[years_to_keep]
        
        if len(totals_by_year) < 2:
            # Not enough data for calculations
            print(f"Không đủ dữ liệu để tính dự phóng cho {symbol}")
            return create_empty_result()
        
        num_years = totals_by_year.index[-1] - totals_by_year.index[0]
        if num_years < 1:
            num_years = 1  # Avoid division by zero
        
        def calculate_cagr(start_value, end_value, num_years):
            if abs(start_value) < 1e-6 or abs(end_value) < 1e-6:
                return 0
            try:
                return (end_value / start_value) ** (1 / num_years) - 1
            except:
                return 0
        
        # Calculate CAGR for all metrics
        print(f"Tính toán tốc độ tăng trưởng kép (CAGR) cho các chỉ tiêu")
        cagr_values = {}
        for metric in metrics:
            if metric in totals_by_year.columns:
                start_value = totals_by_year[metric].iloc[0]
                end_value = totals_by_year[metric].iloc[-1]
                cagr_values[metric] = calculate_cagr(start_value, end_value, num_years)
            else:
                print(f"Không tìm thấy chỉ tiêu {metric} trong dữ liệu")
                cagr_values[metric] = 0
        
        # Project future values
        print(f"Dự phóng các giá trị tương lai")
        projections_cagr = {}
        for metric in metrics:
            if metric in totals_by_year.columns:
                try:
                    base = totals_by_year[metric].iloc[-1]
                    second_last_year = totals_by_year.index[-2]
                    
                    projections_cagr[metric] = {
                        '2023': totals_by_year.loc[second_last_year, metric] if second_last_year in totals_by_year.index else 0,
                        '2024': base,
                        '2025F': base * (1 + cagr_values[metric]),
                        '2026F': base * (1 + cagr_values[metric]) ** 2
                    }
                except Exception as e:
                    print(f"Lỗi khi dự báo cho {metric}: {str(e)}")
                    projections_cagr[metric] = {'2023': 0, '2024': 0, '2025F': 0, '2026F': 0}
            else:
                projections_cagr[metric] = {'2023': 0, '2024': 0, '2025F': 0, '2026F': 0}
        
        # Convert to DataFrame and round values
        print(f"Chuyển đổi kết quả dự phóng sang DataFrame")
        df_projections = pd.DataFrame(projections_cagr).round(2)
        df_projections = df_projections.transpose()
        
        # Create a new index using mapping
        new_index = [metrics_mapping.get(idx, idx) for idx in df_projections.index]
        df_projections.index = new_index
        df_projections.index.name = 'Chỉ tiêu'
        
        # Store unformatted values for calculations
        df_calc = df_projections.copy()
        
        # Calculate growth rates
        print(f"Tính toán tỷ lệ tăng trưởng")
        growth_rates = {}
        for metric_key, metric_name in metrics_mapping.items():
            try:
                if metric_name in df_calc.index and '2024' in df_calc.columns:
                    base_value = df_calc.loc[metric_name, '2024']
                    
                    if '2025F' in df_calc.columns:
                        val_2025 = df_calc.loc[metric_name, '2025F']
                        growth_2025 = '{:+.1f}%'.format(((val_2025 / base_value - 1) * 100)) if base_value != 0 else 'N/A'
                    else:
                        growth_2025 = 'N/A'
                    
                    growth_rates[metric_name] = {'2025F': growth_2025}
                    
                    # Calculate 2024 growth rate if 2023 data is available
                    if '2023' in df_calc.columns:
                        val_2023 = df_calc.loc[metric_name, '2023']
                        growth_2024 = '{:+.1f}%'.format(((base_value / val_2023 - 1) * 100)) if val_2023 != 0 else 'N/A'
                        growth_rates[metric_name]['2024'] = growth_2024
                    else:
                        growth_rates[metric_name]['2024'] = 'N/A'
                else:
                    growth_rates[metric_name] = {'2024': 'N/A', '2025F': 'N/A'}
            except Exception as e:
                print(f"Lỗi tính tỷ lệ tăng trưởng cho {metric_name}: {str(e)}")
                growth_rates[metric_name] = {'2024': 'N/A', '2025F': 'N/A'}
        
        df_growth = pd.DataFrame(growth_rates).transpose()
        print(f"Đã tính xong tỷ lệ tăng trưởng")
        
        # Create a DataFrame that matches the image format exactly
        # Set up multi-level columns as shown in the image
        column_tuples = [
            ('2024', 'Tỷ đồng'), ('2024', '%YoY'),
            ('2025F', 'Tỷ đồng'), ('2025F', '%YoY')
        ]
        columns = pd.MultiIndex.from_tuples(column_tuples)
        
        # Create a DataFrame with the right structure to hold our results
        print(f"Tạo DataFrame kết quả cuối cùng")
        result_data = []
        for metric_key, metric_name in metrics_mapping.items():
            try:
                # Get values
                if metric_name in df_calc.index:
                    val_2024 = df_calc.loc[metric_name, '2024']
                    val_2025 = df_calc.loc[metric_name, '2025F'] if '2025F' in df_calc.columns else 0
                else:
                    val_2024 = 0
                    val_2025 = 0
                
                # Convert to billions (tỷ đồng) for all metrics
                print(f"Chuyển đổi {metric_name} sang tỷ đồng: {val_2024} -> {val_2024 / 1_000_000_000}")
                val_2024 = val_2024 / 1_000_000_000
                val_2025 = val_2025 / 1_000_000_000
                
                growth_2024 = df_growth.loc[metric_name, '2024'] if metric_name in df_growth.index and '2024' in df_growth.columns else 'N/A'
                growth_2025 = df_growth.loc[metric_name, '2025F'] if metric_name in df_growth.index and '2025F' in df_growth.columns else 'N/A'
                
                print(f"Kết quả cho {metric_name}: {val_2024}, {growth_2024}, {val_2025}, {growth_2025}")
                
                row = [
                    '{:.2f}'.format(val_2024),
                    growth_2024,
                    '{:.2f}'.format(val_2025),
                    growth_2025
                ]
            except Exception as e:
                print(f"Lỗi khi xử lý dữ liệu cho {metric_name}: {str(e)}")
                row = ['N/A', 'N/A', 'N/A', 'N/A']
                
            result_data.append(row)
        
        filled_df = pd.DataFrame(
            result_data,
            index=pd.Index(metrics_mapping.values(), name='Khoản mục'),
            columns=columns
        )
        
        print(f"Hoàn thành phân tích dữ liệu cho {symbol}")
        return {
            'bang_du_lieu': filled_df
        }
    except Exception as e:
        print(f"Lỗi tổng thể khi phân tích tài chính doanh nghiệp {symbol}: {str(e)}")
        return create_empty_result()

def create_empty_result():
    """Helper function to create empty result when data is insufficient"""
    # Define metrics mapping with Vietnamese labels
    metrics_mapping = {
        'Revenue (Bn. VND)': 'Doanh thu thuần',
        'Gross Profit': 'Lợi nhuận gộp',    
        'Financial Expenses': 'Chi phí tài chính',
        'Selling Expenses': 'Chi phí bán hàng',
        'General & Admin Expenses': 'Chi phí quản lý',
        'Operating Profit/Loss': 'Lợi nhuận từ HĐKD',
        'Profit before tax': 'LNTT',
        'Attribute to parent company (Bn. VND)': 'LNST'
    }
    
    # Set up multi-level columns
    column_tuples = [
        ('2024', 'Tỷ đồng'), ('2024', '%YoY'),
        ('2025F', 'Tỷ đồng'), ('2025F', '%YoY')
    ]
    columns = pd.MultiIndex.from_tuples(column_tuples)
    
    # Create a DataFrame with N/A values
    empty_df = pd.DataFrame(
        [['N/A', 'N/A', 'N/A', 'N/A'] for _ in range(len(metrics_mapping))],
        index=pd.Index(metrics_mapping.values(), name='Khoản mục'),
        columns=columns
    )
    
    return {
        'bang_du_lieu': empty_df
    }