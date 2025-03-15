import pandas as pd
import numpy as np
import datetime
from vnstock import Vnstock

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

# Thêm hàm lấy dữ liệu chỉ số thị trường
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

# Giữ lại hàm cũ với tên mới để đảm bảo tính tương thích
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

# Thêm hàm lấy dữ liệu thị trường dựa trên dữ liệu từ VNINDEX và các nguồn khác
def get_market_data(stock_info=None):
    """Lấy các dữ liệu thị trường bao gồm VNINDEX và thông tin cổ phiếu"""
    # Trả về tất cả giá trị là N/A
    market_data = {
        "VNINDEX": "N/A",
        "HNXINDEX": "N/A",
        "Vốn hóa (tỷ VND)": "N/A",
        "SL CP lưu hành (triệu CP)": "N/A",
        "Tỷ lệ giao dịch tự do (%)": "N/A",
        "52-tuần cao/thấp": "N/A",
        "KLGD bình quân 90 ngày": "N/A",
        "GTGD bình quân 90 ngày": "N/A"
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
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu chỉ số thị trường: {str(e)}")
    
    # Các trường thông tin khác vẫn giữ là N/A
    
    return market_data
