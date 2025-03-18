import pandas as pd
import numpy as np
import datetime
from vnstock import Vnstock
import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from functools import partial
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
        symbol='NKG', 
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
        vci_stock = Vnstock().stock(source='VCI')
        
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
        vci_stock = Vnstock().stock(source='VCI')
        
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
# Thêm hàm lấy dữ liệu thị trường dựa trên dữ liệu từ VNINDEX và các nguồn khác
'''def predict_price(symbol):
    # Eps expect 2025
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    eps = stock.finance.ratio(period='year',lang='en', dropna=True).head(5)
    eps_list = eps[('Chỉ tiêu định giá', 'EPS (VND)')].astype(float)  # Chuyển EPS về kiểu số
    years = eps[('Meta', 'yearReport')].astype(int)  # Chuyển năm về kiểu số nguyên
    eps_yearly = pd.DataFrame({"Year": years, "EPS": eps_list}).sort_values("Year")
    eps_yearly = eps_yearly[eps_yearly["EPS"] > 0]
    eps_yearly["growth_rate"] = eps_yearly["EPS"].pct_change()
    avg_growth = eps_yearly["growth_rate"].mean(skipna=True)
    eps_2025 = eps_yearly["EPS"].iloc[-1] * (1 + avg_growth)
    
    # P/E expect 2025
    ratio_data = stock.finance.ratio(symbol=symbol)
    industry_pe = ratio_data[('Chỉ tiêu định giá', 'P/E')].mean()  
    result = eps_2025 * industry_pe
    rounded_price_target = round(result / 100) * 100
    # current price
    kk = stock.quote.intraday(symbol=symbol)
    current_price = kk['price'].values[-1]
    profit = (rounded_price_target - current_price) / current_price
    
    return int(rounded_price_target), profit'''
def industry_pe(industry_name, max_workers=10, source='VCI'):
    def get_company_data(symbol, stock_client):
        try:
            data = stock_client.stock(symbol=symbol, source=source)\
                .finance.ratio(period='year', lang='en', dropna=True)\
                .loc[:, [
                    ('Meta', 'yearReport'),
                    ('Chỉ tiêu định giá', 'P/E'),
                    ('Chỉ tiêu định giá', 'Market Capital (Bn. VND)')
                ]].head(1)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None

    try:
        stock = Vnstock().stock(source='VCI')
        # Get companies in the specified industry
        companies = stock.listing.symbols_by_industries()
        filtered_companies = companies[companies['en_icb_name4'] == industry_name]
        symbols = filtered_companies['symbol'].tolist()
        
        if not symbols:
            raise ValueError(f"No companies found for industry: {industry_name}")
        
        # Initialize stock client
        stock_client = Vnstock()
        
        # Fetch data in parallel
        with ThreadPoolExecutor(max_workers=min(max_workers, len(symbols))) as executor:
            func = partial(get_company_data, stock_client=stock_client)
            results = list(executor.map(func, symbols))
        
        # Process results
        pe_df = pd.concat([r for r in results if r is not None], ignore_index=True)
        
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
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    industry_names = stock.listing.symbols_by_industries()['en_icb_name4'].values[0]
    industry_name = industry_names[industry_names['symbol'] == symbol]
    return industry_name['icb_name4'].values[0]
    
def current_price(symbol):
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    ratio_data = stock.finance.ratio(symbol=symbol)
    eps_data = ratio_data[[('Meta', 'yearReport'), ('Chỉ tiêu định giá', 'EPS (VND)')]].dropna()
    eps_data_filtered = eps_data[eps_data['yearReport'].between(2020, 2024)]
    eps_by_year = eps_data_filtered.groupby('yearReport')['EPS (VND)'].sum()
    eps_2024 = eps_by_year.get(2024, None)
    fair_value_pe = industry_pe(industry_name(symbol), 10, 'VCI') * eps_2024
    return fair_value_pe
    
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
