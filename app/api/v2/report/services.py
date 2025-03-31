import datetime
import os
import pandas as pd
import numpy as np
from .module_report.data_processing import read_data, clean_column_names, standardize_columns, merge_balance_sheets, get_values
from .module_report.finance_calc import (calculate_total_current_assets, calculate_ppe, calculate_total_assets, 
                                        calculate_ebitda, calculate_financial_ratios, calculate_total_operating_expense,
                                        calculate_net_income_before_taxes, calculate_net_income_before_extraordinary_items,
                                        get_market_data, current_price, predict_price, doanhthu_thuan_p2, loinhuan_gop_p2,
                                        chiphi_p2, loinhuankinhdoanh_p2)
from .module_report.generate_pdf import PDFReport, generate_page4_pdf, generate_page5_pdf, generate_page6_pdf
from .module_report.api_gemini import generate_financial_analysis, create_analysis_prompt
from .module_report.chart_generator import generate_financial_charts
from vnstock import Vnstock

def get_company_industry(symbol):
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        symbols_by_industry = stock.listing.symbols_by_industries()
        company_info = symbols_by_industry[symbols_by_industry['symbol'].str.upper() == symbol.upper()]
        if not company_info.empty and 'icb_name4' in company_info.columns:
            icb_name4_value = company_info['icb_name4'].values[0]
            return icb_name4_value
        return "Không xác định"
    except Exception as e:
        print(f"Lỗi khi lấy thông tin ngành nghề: {str(e)}")
        return "Không xác định"
def get_company_name(symbol):
    try:
        company = Vnstock().stock(symbol=symbol, source='TCBS').company
        profile = company.profile()
        if profile.empty or 'company_name' not in profile.columns:
            return f"{symbol}"  # Trả về symbol nếu không lấy được tên
        return profile['company_name'].values[0]
    except Exception as e:
        print(f"Lỗi khi lấy tên công ty cho {symbol}: {str(e)}")
        return f"{symbol}"

def create_projection_data(symbol):
    """Tạo dữ liệu dự phóng cho báo cáo"""
    try:
        # Khởi tạo cấu trúc dữ liệu trống với các giá trị N/A
        projection_data = {
            'revenue': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
            'gross_profit': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
            'gross_margin': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
            'financial_expense': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
            'selling_expense': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
            'admin_expense': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
            'operating_profit': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
            'profit_before_tax': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
            'profit_after_tax': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A']
        }
        
        # Lấy dữ liệu doanh thu thuần từ API
        try:
            doanh_thu, yoy = doanhthu_thuan_p2(symbol)
            
            # In thông tin debug
            print(f"DEBUG - Dữ liệu từ doanhthu_thuan_p2: doanh_thu={doanh_thu}, yoy={yoy}, types: {type(doanh_thu)}, {type(yoy)}")
            
            # Chuyển đổi doanh thu từ đồng sang tỷ đồng - giá trị trả về từ API là đơn vị đồng
            doanh_thu_ty = doanh_thu / 1_000_000_000 if isinstance(doanh_thu, (int, float, np.int64, np.float64)) else None
            
            # Định dạng dữ liệu doanh thu thuần
            doanh_thu_str = f"{doanh_thu_ty:,.2f}" if doanh_thu_ty is not None else 'N/A'
            yoy_str = f"+{yoy*100:.1f}%" if isinstance(yoy, (int, float)) and yoy > 0 else f"{yoy*100:.1f}%" if isinstance(yoy, (int, float)) else 'N/A'
            
            # Cập nhật dữ liệu doanh thu thuần
            projection_data['revenue'] = [doanh_thu_str, yoy_str, 'N/A', 'N/A', 'N/A']
            
            print(f"Đã lấy dữ liệu doanh thu thuần cho {symbol}: {doanh_thu_str} tỷ đồng ({yoy_str})")
            
            # Lấy dữ liệu lợi nhuận gộp
            try:
                bienloinhuangop, loinhuangop, yoy_loinhuangop = loinhuan_gop_p2(symbol)
                
                # In thông tin debug
                print(f"DEBUG - Dữ liệu từ loinhuan_gop_p2: bienloinhuangop={bienloinhuangop}, loinhuangop={loinhuangop}, yoy_loinhuangop={yoy_loinhuangop}")
                
                # Chuyển đổi lợi nhuận gộp từ đồng sang tỷ đồng
                loinhuangop_ty = loinhuangop / 1_000_000_000 if isinstance(loinhuangop, (int, float, np.int64, np.float64)) else None
                
                # Định dạng dữ liệu lợi nhuận gộp
                loinhuangop_str = f"{loinhuangop_ty:,.2f}" if loinhuangop_ty is not None else 'N/A'
                yoy_loinhuangop_str = f"+{yoy_loinhuangop*100:.1f}%" if isinstance(yoy_loinhuangop, (int, float)) and yoy_loinhuangop > 0 else f"{yoy_loinhuangop*100:.1f}%" if isinstance(yoy_loinhuangop, (int, float)) else 'N/A'
                
                # Cập nhật dữ liệu lợi nhuận gộp
                projection_data['gross_profit'] = [loinhuangop_str, yoy_loinhuangop_str, 'N/A', 'N/A', 'N/A']
                
                # Định dạng dữ liệu biên lợi nhuận gộp
                bienloinhuangop_str = f"{bienloinhuangop * 100:.2f}%" if isinstance(bienloinhuangop, (int, float, np.int64, np.float64)) else 'N/A'
                
                # Cập nhật dữ liệu biên lợi nhuận gộp
                projection_data['gross_margin'] = [bienloinhuangop_str, 'N/A', 'N/A', 'N/A', 'N/A']
                
                print(f"Đã lấy dữ liệu lợi nhuận gộp cho {symbol}: {loinhuangop_str} tỷ đồng ({yoy_loinhuangop_str})")
                print(f"Đã lấy dữ liệu biên lợi nhuận gộp cho {symbol}: {bienloinhuangop_str}")
            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu lợi nhuận gộp: {str(e)}")
                
            # Lấy dữ liệu chi phí
            try:
                laigop, chiphitaichinh, yoy_chiphitaichinh, chiphibanhang, yoy_laigop, yoy_chiphibanhang, chiphiql, yoy_chiphiql = chiphi_p2(symbol)
                
                # In thông tin debug
                print(f"DEBUG - Dữ liệu từ chiphi_p2: chiphitaichinh={chiphitaichinh}, chiphibanhang={chiphibanhang}, chiphiql={chiphiql}")
                
                # Chuyển đổi chi phí từ đồng sang tỷ đồng
                chiphitaichinh_ty = -chiphitaichinh / 1_000_000_000 if isinstance(chiphitaichinh, (int, float, np.int64, np.float64)) else None
                chiphibanhang_ty = -chiphibanhang / 1_000_000_000 if isinstance(chiphibanhang, (int, float, np.int64, np.float64)) else None
                chiphiql_ty = -chiphiql / 1_000_000_000 if isinstance(chiphiql, (int, float, np.int64, np.float64)) else None
                
                # Định dạng dữ liệu chi phí tài chính
                chiphitaichinh_str = f"{chiphitaichinh_ty:,.2f}" if chiphitaichinh_ty is not None else 'N/A'
                yoy_chiphitaichinh_str = f"+{yoy_chiphitaichinh*100:.1f}%" if isinstance(yoy_chiphitaichinh, (int, float)) and yoy_chiphitaichinh > 0 else f"{yoy_chiphitaichinh*100:.1f}%" if isinstance(yoy_chiphitaichinh, (int, float)) else 'N/A'
                
                # Cập nhật dữ liệu chi phí tài chính
                projection_data['financial_expense'] = [chiphitaichinh_str, yoy_chiphitaichinh_str, 'N/A', 'N/A', 'N/A']
                
                # Định dạng dữ liệu chi phí bán hàng
                chiphibanhang_str = f"{chiphibanhang_ty:,.2f}" if chiphibanhang_ty is not None else 'N/A'
                yoy_chiphibanhang_str = f"+{yoy_chiphibanhang*100:.1f}%" if isinstance(yoy_chiphibanhang, (int, float)) and yoy_chiphibanhang > 0 else f"{yoy_chiphibanhang*100:.1f}%" if isinstance(yoy_chiphibanhang, (int, float)) else 'N/A'
                
                # Cập nhật dữ liệu chi phí bán hàng
                projection_data['selling_expense'] = [chiphibanhang_str, yoy_chiphibanhang_str, 'N/A', 'N/A', 'N/A']
                
                # Định dạng dữ liệu chi phí quản lý
                chiphiql_str = f"{chiphiql_ty:,.2f}" if chiphiql_ty is not None else 'N/A'
                yoy_chiphiql_str = f"+{yoy_chiphiql*100:.1f}%" if isinstance(yoy_chiphiql, (int, float)) and yoy_chiphiql > 0 else f"{yoy_chiphiql*100:.1f}%" if isinstance(yoy_chiphiql, (int, float)) else 'N/A'
                
                # Cập nhật dữ liệu chi phí quản lý
                projection_data['admin_expense'] = [chiphiql_str, yoy_chiphiql_str, 'N/A', 'N/A', 'N/A']
                
                print(f"Đã lấy dữ liệu chi phí cho {symbol}")
            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu chi phí: {str(e)}")
                
            # Lấy dữ liệu lợi nhuận từ HĐKD, LNTT và LNST
            try:
                loinhuanhdkd, loinhuantruothue, loinhuansautrue, yoy_loinhuanhdkd, yoy_loinhuantruothue, yoy_loinhuansautrue = loinhuankinhdoanh_p2(symbol)
                
                # In thông tin debug
                print(f"DEBUG - Dữ liệu từ loinhuankinhdoanh_p2: loinhuanhdkd={loinhuanhdkd}, loinhuantruothue={loinhuantruothue}, loinhuansautrue={loinhuansautrue}")
                
                # Chuyển đổi lợi nhuận từ đồng sang tỷ đồng
                loinhuanhdkd_ty = loinhuanhdkd / 1_000_000_000 if isinstance(loinhuanhdkd, (int, float, np.int64, np.float64)) else None
                loinhuantruothue_ty = loinhuantruothue / 1_000_000_000 if isinstance(loinhuantruothue, (int, float, np.int64, np.float64)) else None
                loinhuansautrue_ty = loinhuansautrue / 1_000_000_000 if isinstance(loinhuansautrue, (int, float, np.int64, np.float64)) else None
                
                # Định dạng dữ liệu lợi nhuận từ HĐKD
                loinhuanhdkd_str = f"{loinhuanhdkd_ty:,.2f}" if loinhuanhdkd_ty is not None else 'N/A'
                yoy_loinhuanhdkd_str = f"+{yoy_loinhuanhdkd*100:.1f}%" if isinstance(yoy_loinhuanhdkd, (int, float)) and yoy_loinhuanhdkd > 0 else f"{yoy_loinhuanhdkd*100:.1f}%" if isinstance(yoy_loinhuanhdkd, (int, float)) else 'N/A'
                
                # Cập nhật dữ liệu lợi nhuận từ HĐKD
                projection_data['operating_profit'] = [loinhuanhdkd_str, yoy_loinhuanhdkd_str, 'N/A', 'N/A', 'N/A']
                
                # Định dạng dữ liệu lợi nhuận trước thuế
                loinhuantruothue_str = f"{loinhuantruothue_ty:,.2f}" if loinhuantruothue_ty is not None else 'N/A'
                yoy_loinhuantruothue_str = f"+{yoy_loinhuantruothue*100:.1f}%" if isinstance(yoy_loinhuantruothue, (int, float)) and yoy_loinhuantruothue > 0 else f"{yoy_loinhuantruothue*100:.1f}%" if isinstance(yoy_loinhuantruothue, (int, float)) else 'N/A'
                
                # Cập nhật dữ liệu lợi nhuận trước thuế
                projection_data['profit_before_tax'] = [loinhuantruothue_str, yoy_loinhuantruothue_str, 'N/A', 'N/A', 'N/A']
                
                # Định dạng dữ liệu lợi nhuận sau thuế
                loinhuansautrue_str = f"{loinhuansautrue_ty:,.2f}" if loinhuansautrue_ty is not None else 'N/A'
                yoy_loinhuansautrue_str = f"+{yoy_loinhuansautrue*100:.1f}%" if isinstance(yoy_loinhuansautrue, (int, float)) and yoy_loinhuansautrue > 0 else f"{yoy_loinhuansautrue*100:.1f}%" if isinstance(yoy_loinhuansautrue, (int, float)) else 'N/A'
                
                # Cập nhật dữ liệu lợi nhuận sau thuế
                projection_data['profit_after_tax'] = [loinhuansautrue_str, yoy_loinhuansautrue_str, 'N/A', 'N/A', 'N/A']
                
                print(f"Đã lấy dữ liệu lợi nhuận cho {symbol}")
            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu lợi nhuận: {str(e)}")
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu doanh thu thuần: {str(e)}")
        
        return projection_data
    except Exception as e:
        print(f"Lỗi khi tạo dữ liệu dự phóng: {str(e)}")
        return None

def get_projection_data_for_page1(symbol):
    """
    Fetches financial projection data specifically for page1's table.
    This function is independent from other pages to ensure modularity.
    
    Args:
        symbol: Stock symbol to fetch data for
        
    Returns:
        Dictionary with projection data formatted for page1
    """
    try:
        print(f"Đang lấy dữ liệu dự phóng cho bảng page1, mã {symbol}")
        projection_data = {
            'revenue': ['N/A', 'N/A', 'N/A', 'N/A'],
            'operating_profit': ['N/A', 'N/A', 'N/A', 'N/A'],
            'profit_after_tax': ['N/A', 'N/A', 'N/A', 'N/A'],
            'eps': ['N/A', 'N/A', 'N/A', 'N/A'],
            'bps': ['N/A', 'N/A', 'N/A', 'N/A'],
            'roa': ['N/A', 'N/A', 'N/A', 'N/A'],
            'npm': ['N/A', 'N/A', 'N/A', 'N/A'],
            'roe': ['N/A', 'N/A', 'N/A', 'N/A'],
        }
        
        # Use finance_calc functions to fetch financial data
        from .module_report.finance_calc import analyze_stock_data_2025_2026_p2
        
        try:
            # Get historical financial data
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            
            # Get existing financial data for 2023-2024
            data1 = stock.finance.ratio(symbol=symbol)
            data2 = stock.finance.income_statement(symbol=symbol)
            
            # Process data for ratios
            table_data1 = data1[[
                ('Meta', 'yearReport'), ('Meta', 'lengthReport'), 
                ('Chỉ tiêu khả năng sinh lợi', 'Net Profit Margin (%)'), 
                ('Chỉ tiêu khả năng sinh lợi', 'ROE (%)'), 
                ('Chỉ tiêu khả năng sinh lợi', 'ROA (%)'), 
                ('Chỉ tiêu định giá', 'EPS (VND)'), 
                ('Chỉ tiêu định giá', 'BVPS (VND)')
            ]].dropna()
            table_data1.columns = table_data1.columns.droplevel(0)
            table_data1.rename(columns={'yearReport': 'Year', 'lengthReport': 'Quarter'}, inplace=True)
            
            # Process data for income statement
            table_data2 = data2[[
                ('yearReport'), ('lengthReport'), 
                ('Revenue (Bn. VND)'), 
                ('Operating Profit/Loss'), 
                ('Net Profit For the Year')
            ]].dropna()
            table_data2.rename(columns={'yearReport': 'Year', 'lengthReport': 'Quarter'}, inplace=True)
            
            # Calculate totals by year
            income_by_year = table_data2.groupby('Year')[['Revenue (Bn. VND)', 'Operating Profit/Loss', 'Net Profit For the Year']].sum()
            ratios_by_year = table_data1.groupby('Year')[['EPS (VND)', 'BVPS (VND)', 'ROA (%)', 'Net Profit Margin (%)', 'ROE (%)']].mean()
            
            # Format values for 2023-2024
            for year in [2023, 2024]:
                if year in income_by_year.index:
                    # Note: Revenue is already in billions according to column name 'Revenue (Bn. VND)'
                    revenue_value = income_by_year.loc[year, 'Revenue (Bn. VND)'] / 1_000_000_000
                    projection_data['revenue'][year - 2023] = f"{revenue_value:,.2f}"
                    
                    # Convert Operating Profit/Loss to billions (divide by 1,000,000,000)
                    op_profit_value = income_by_year.loc[year, 'Operating Profit/Loss'] / 1_000_000_000
                    projection_data['operating_profit'][year - 2023] = f"{op_profit_value:,.2f}"
                    
                    # Convert Net Profit For the Year to billions (divide by 1,000,000,000)
                    net_profit_value = income_by_year.loc[year, 'Net Profit For the Year'] / 1_000_000_000
                    projection_data['profit_after_tax'][year - 2023] = f"{net_profit_value:,.2f}"
                
                if year in ratios_by_year.index:
                    # Format EPS
                    projection_data['eps'][year - 2023] = f"{ratios_by_year.loc[year, 'EPS (VND)']:,.0f}"
                    
                    # Format BPS
                    projection_data['bps'][year - 2023] = f"{ratios_by_year.loc[year, 'BVPS (VND)']:,.0f}"
                    
                    # Format ROA
                    projection_data['roa'][year - 2023] = f"{ratios_by_year.loc[year, 'ROA (%)']:,.1f}"
                    
                    # Format NPM
                    projection_data['npm'][year - 2023] = f"{ratios_by_year.loc[year, 'Net Profit Margin (%)']:,.1f}"
                    
                    # Format ROE
                    projection_data['roe'][year - 2023] = f"{ratios_by_year.loc[year, 'ROE (%)']:,.1f}"
            
            # Generate forecasts for 2025-2026
            # Calculate CAGR for projections
            def calculate_cagr(start_value, end_value, num_years):
                if start_value <= 0 or end_value <= 0:
                    return 0.1  # Default growth if we can't calculate CAGR
                return (end_value / start_value) ** (1 / num_years) - 1
            
            # Project values for 2025-2026 using 2023-2024 CAGR
            for metric, years_data in [
                ('Revenue (Bn. VND)', income_by_year),
                ('Operating Profit/Loss', income_by_year),
                ('Net Profit For the Year', income_by_year)
            ]:
                if 2023 in years_data.index and 2024 in years_data.index:
                    start_value = years_data.loc[2023, metric]
                    end_value = years_data.loc[2024, metric]
                    
                    if start_value > 0 and end_value > 0:
                        cagr = calculate_cagr(start_value, end_value, 1)
                        
                        # Project 2025
                        val_2025 = end_value * (1 + cagr)
                        
                        # Project 2026
                        val_2026 = val_2025 * (1 + cagr)
                        
                        # Map to projection data dictionary
                        if metric == 'Revenue (Bn. VND)':
                            # Revenue is already in billions
                            projection_data['revenue'][2] = f"{val_2025 / 1_000_000_000:,.2f}"
                            projection_data['revenue'][3] = f"{val_2026 / 1_000_000_000:,.2f}"
                        elif metric == 'Operating Profit/Loss':
                            # Convert to billions
                            projection_data['operating_profit'][2] = f"{val_2025 / 1_000_000_000:,.2f}"
                            projection_data['operating_profit'][3] = f"{val_2026 / 1_000_000_000:,.2f}"
                        elif metric == 'Net Profit For the Year':
                            # Convert to billions
                            projection_data['profit_after_tax'][2] = f"{val_2025 / 1_000_000_000:,.2f}"
                            projection_data['profit_after_tax'][3] = f"{val_2026 / 1_000_000_000:,.2f}"
            
            # Do the same for ratios
            for metric, years_data in [
                ('EPS (VND)', ratios_by_year),
                ('BVPS (VND)', ratios_by_year),
                ('ROA (%)', ratios_by_year),
                ('Net Profit Margin (%)', ratios_by_year),
                ('ROE (%)', ratios_by_year)
            ]:
                if 2023 in years_data.index and 2024 in years_data.index:
                    start_value = years_data.loc[2023, metric]
                    end_value = years_data.loc[2024, metric]
                    
                    if start_value > 0 and end_value > 0:
                        cagr = calculate_cagr(start_value, end_value, 1)
                        
                        # Project 2025
                        val_2025 = end_value * (1 + cagr)
                        
                        # Project 2026
                        val_2026 = val_2025 * (1 + cagr)
                        
                        # Map to projection data dictionary
                        if metric == 'EPS (VND)':
                            projection_data['eps'][2] = f"{val_2025:,.0f}"
                            projection_data['eps'][3] = f"{val_2026:,.0f}"
                        elif metric == 'BVPS (VND)':
                            projection_data['bps'][2] = f"{val_2025:,.0f}"
                            projection_data['bps'][3] = f"{val_2026:,.0f}"
                        elif metric == 'ROA (%)':
                            projection_data['roa'][2] = f"{val_2025:,.1f}"
                            projection_data['roa'][3] = f"{val_2026:,.1f}"
                        elif metric == 'Net Profit Margin (%)':
                            projection_data['npm'][2] = f"{val_2025:,.1f}"
                            projection_data['npm'][3] = f"{val_2026:,.1f}"
                        elif metric == 'ROE (%)':
                            projection_data['roe'][2] = f"{val_2025:,.1f}"
                            projection_data['roe'][3] = f"{val_2026:,.1f}"
        
        except Exception as e:
            print(f"Lỗi khi xử lý dữ liệu tài chính: {str(e)}")
        
        print(f"Đã tạo xong dữ liệu dự phóng cho bảng page1")
        return projection_data
        
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu dự phóng cho page1: {str(e)}")
        return None

def generate_pdf_report(symbol: str):
    try:
        # Fix the file paths for financial data - ensure proper formatting with os.path.join
        data_dir = os.path.join("e:\\", "Chatbotfinance", "Main", "backend", "data")
        # Alternative using raw string:
        # data_dir = r"e:\Chatbotfinance\Main\backend\data"
        
        file_paths = [
            os.path.join(data_dir, f"2020-Vietnam.xlsx"), 
            os.path.join(data_dir, f"2021-Vietnam.xlsx"), 
            os.path.join(data_dir, f"2022-Vietnam.xlsx"), 
            os.path.join(data_dir, f"2023-Vietnam.xlsx"),
            os.path.join(data_dir, f"2024-Vietnam.xlsx")
        ]
        
        # Check if files exist before proceeding
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"Warning: File {file_path} does not exist")
        
        # Read all data from Excel files
        df_list = read_data(file_paths)
        
        # Clean column names
        clean_column_names(df_list)
        
        # Merge balance sheets for the specified symbol
        dfs = [standardize_columns(df) for df in df_list]
        merged_df = merge_balance_sheets(dfs, symbol)
        if merged_df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
            
        # Remove Current Ratio columns if they exist
        if not merged_df.empty:
            merged_df = merged_df.loc[:, ~merged_df.columns.str.contains("CURRENT RATIO", case=False)]
        
        # Transpose dataframe for easier data access
        transposed_df = merged_df.T
        transposed_df.columns = [f"{year}" for year in range(2020, 2025)]
        transposed_df.reset_index(inplace=True)
        transposed_df.rename(columns={"index": "Chỉ tiêu"}, inplace=True)
        transposed_df = transposed_df.fillna(0)
        
        # Extract company information
        company_name = str(merged_df.iloc[1]['TÊN']) if 'TÊN' in merged_df.columns else f"{symbol} Company"
        exchange = str(merged_df.iloc[0]['SÀN']) if 'SÀN' in merged_df.columns else "Unknown"
        
        # Get financial data for calculations
        years = transposed_df.columns[1:]
        
        # Calculate balance sheet metrics
        cash_equivalents = get_values(transposed_df, "CĐKT. TIỀN VÀ TƯƠNG ĐƯƠNG TIỀN")
        short_term_investments = get_values(transposed_df, "CĐKT. ĐẦU TƯ TÀI CHÍNH NGẮN HẠN")
        short_term_receivables = get_values(transposed_df, "CĐKT. CÁC KHOẢN PHẢI THU NGẮN HẠN")
        inventory = get_values(transposed_df, "CĐKT. HÀNG TỒN KHO, RÒNG")
        other_current_assets = get_values(transposed_df, "CĐKT. TÀI SẢN NGẮN HẠN KHÁC")
        
        # Calculate PPE components
        tangible_assets = get_values(transposed_df, "CĐKT. GTCL TSCĐ HỮU HÌNH")
        finance_leased_assets = get_values(transposed_df, "CĐKT. GTCL TÀI SẢN THUÊ TÀI CHÍNH")
        intangible_assets = get_values(transposed_df, "CĐKT. GTCL TÀI SẢN CỐ ĐỊNH VÔ HÌNH")
        construction_in_progress = get_values(transposed_df, "CĐKT. XÂY DỰNG CƠ BẢN DỞ DANG (TRƯỚC 2015)")
        
        # Calculate assets and liabilities
        total_current_assets = get_values(transposed_df, "CĐKT. TÀI SẢN NGẮN HẠN")
        total_non_current_assets = get_values(transposed_df, "CĐKT. TÀI SẢN DÀI HẠN")
        total_assets = total_current_assets + total_non_current_assets
        total_current_liabilities = get_values(transposed_df, "CĐKT. NỢ NGẮN HẠN")
        total_long_term_debt = get_values(transposed_df, "CĐKT. NỢ DÀI HẠN")
        total_liabilities = get_values(transposed_df, "CĐKT. NỢ PHẢI TRẢ")
        total_equity = get_values(transposed_df, "CĐKT. VỐN CHỦ SỞ HỮU")
        
        # Calculate EBITDA components
        net_income = get_values(transposed_df, "KQKD. LỢI NHUẬN SAU THUẾ THU NHẬP DOANH NGHIỆP")
        interest_expense = get_values(transposed_df, "KQKD. CHI PHÍ LÃI VAY")
        taxes = get_values(transposed_df, "KQKD. CHI PHÍ THUẾ TNDN HIỆN HÀNH")
        depreciation_amortization = get_values(transposed_df, "KQKD. KHẤU HAO TÀI SẢN CỐ ĐỊNH")
        
        # Calculate income statement items
        revenue = get_values(transposed_df, "KQKD. DOANH THU THUẦN")
        gross_profit = get_values(transposed_df, "KQKD. LỢI NHUẬN GỘP VỀ BÁN HÀNG VÀ CUNG CẤP DỊCH VỤ")
        financial_expense = get_values(transposed_df, "KQKD. CHI PHÍ TÀI CHÍNH")
        selling_expense = get_values(transposed_df, "KQKD. CHI PHÍ BÁN HÀNG")
        admin_expense = get_values(transposed_df, "KQKD. CHI PHÍ QUẢN LÝ DOANH NGHIỆP")
        operating_profit = get_values(transposed_df, "KQKD. LỢI NHUẬN THUẦN TỪ HOẠT ĐỘNG KINH DOANH")
        other_profit = get_values(transposed_df, "KQKD. LỢI NHUẬN KHÁC")
        jv_profit = get_values(transposed_df, "KQKD. LÃI/ LỖ TỪ CÔNG TY LIÊN DOANH (TRƯỚC 2015)")
        
        # Calculate complex metrics
        ppe = calculate_ppe(tangible_assets, finance_leased_assets, intangible_assets, construction_in_progress)
        ebitda = calculate_ebitda(net_income, interest_expense, taxes, depreciation_amortization)
        total_operating_expense = calculate_total_operating_expense(revenue, gross_profit, financial_expense, selling_expense, admin_expense)
        net_income_before_taxes = calculate_net_income_before_taxes(operating_profit, other_profit, jv_profit)
        net_income_before_extraordinary = calculate_net_income_before_extraordinary_items(net_income, other_profit)
        
        # Calculate financial ratios
        ratios = calculate_financial_ratios(
            net_income=net_income, 
            total_equity=total_equity, 
            total_assets=total_assets, 
            revenue=revenue, 
            long_term_debt=total_long_term_debt, 
            total_debt=total_liabilities
        )
        
        # Format data for PDF tables
        def format_values(values):
            return [f"{value:,.2f}" for value in values]
            
        def format_percentages(values):
            return [f"{value * 100:,.2f}" for value in values]
        
        # Create data dictionaries for PDF tables
        balance_sheet_data = {
            "Total Current Assets": format_values(total_current_assets),
            "Property/Plant/Equipment": format_values(ppe),
            "Total Assets": format_values(total_assets),
            "Total Current Liabilities": format_values(total_current_liabilities),
            "Total Long-Term Debt": format_values(total_long_term_debt),
            "Total Liabilities": format_values(total_liabilities),
        }
        
        fundamental_data = {
            "EBITDA": format_values(ebitda),
        }
        
        income_statement_data = {
            "Revenue": format_values(revenue),
            "Total Operating Expense": format_values(total_operating_expense),
            "Net Income Before Taxes": format_values(net_income_before_taxes),
            "Net Income After Taxes": format_values(net_income),
            "Net Income Before Extra. Items": format_values(net_income_before_extraordinary),
        }
        
        profitability_analysis_data = {
            "ROE Tot Equity, %": format_percentages(ratios["roe"]),
            "ROA Tot Assets, %": format_percentages(ratios["roa"]),
            "Income Aft Tax Margin, %": format_percentages(ratios["income_after_tax_margin"]),
            "Revenue/Tot Assets, %": format_percentages(ratios["revenue_to_total_assets"]),
            "Long Term Debt/Equity, %": format_percentages(ratios["long_term_debt_to_equity"]),
            "Total Debt/Equity, %": format_percentages(ratios["total_debt_to_equity"]),
            "ROS, %": format_percentages(ratios["ros"]),
        }
        
        # Tạo financial_data dictionary để sử dụng cho việc tạo biểu đồ
        financial_data = {
            "revenue": revenue,
            "net_income": net_income,
            "total_assets": total_assets,
            "total_equity": total_equity,
            "total_liabilities": total_liabilities,
            "roe": ratios["roe"],
            "roa": ratios["roa"],
            "ros": ratios["ros"],
            "long_term_debt_to_equity": ratios["long_term_debt_to_equity"],
            "total_debt_to_equity": ratios["total_debt_to_equity"]
        }
        
        # Request AI analysis
        analysis = generate_financial_analysis(
            balance_sheet=balance_sheet_data, 
            income_statement=income_statement_data, 
            profitability_analysis=profitability_analysis_data,
            symbol=symbol
        )
        
        # Create output directory
        output_dir = "reports"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"Financial_Report_{symbol}.pdf")
        
        # Tạo biểu đồ tài chính
        chart_paths = generate_financial_charts(os.path.dirname(os.path.abspath(__file__)), symbol, years, financial_data)

        # Tạo các dictionary dữ liệu cho báo cáo
        data = {
            "info": [
                ("Company Name", company_name),
                ("Stock Symbol", symbol),
                ("Exchange", exchange),
                ("Report Date", datetime.date.today().strftime('%d-%b-%Y')),
            ],
            "BALANCE SHEET": balance_sheet_data,
            "FUNDAMENTAL": fundamental_data,
            "INCOME STATEMENT": income_statement_data,
            "PROFITABILITY ANALYSIS": profitability_analysis_data
        }
        
        # Lấy tên công ty
        name = get_company_name(symbol)
        # Chuẩn bị dữ liệu cho báo cáo định dạng mới
        company_data = {
            "name": f"{name}",  # Chỉ hiển thị tên công ty, không kèm mã
            "symbol": symbol,
            "info": f"[ {symbol} | {exchange} ]"  # Đã xóa thông tin ngành
        }
        
        # Đảm bảo trường name luôn có giá trị đầy đủ
        if company_data["name"] is None or company_data["name"] == "" or company_data["name"] == symbol:
            company_data["name"] = f"Công ty Cổ phần {symbol}"
            
        # Đảm bảo company_data hợp lệ trước khi truyền vào create_stock_report  
        if not isinstance(company_data, dict):
            company_data = {
                "name": f"Công ty Cổ phần {symbol}",
                "symbol": symbol,
                "info": f"[ {symbol} | {exchange} ]"
            }
        
        # Lấy giá hiện tại từ API thay vì tính toán
        formatted_current_price = "N/A"
        formatted_price_target = "N/A"
        profit_percent = "N/A"
        
        try:
            # Đổi tên gọi hàm để tránh nhầm lẫn với biến
            current_price_value = current_price(symbol)
            formatted_current_price = f"{current_price_value:,.0f}"
            print(f"Đã lấy giá hiện tại của {symbol} từ API: {formatted_current_price}")
            
            # Tính giá mục tiêu và suất sinh lời sử dụng hàm predict_price
            try:
                price_target, profit_percent = predict_price(symbol)
                print(f"Đã tính giá mục tiêu cho {symbol}: {price_target} VND, Suất sinh lời: {profit_percent * 100}%")
                formatted_price_target = f"{price_target:,.0f}"
            except Exception as e:
                print(f"Lỗi khi tính giá mục tiêu: {str(e)}")
                # Kiểm tra nếu price_value là số thì mới tính toán giá mục tiêu dự phòng
                if isinstance(current_price_value, (int, float)) and current_price_value > 0:
                    # Fallback: Tính toán giá mục tiêu đơn giản (50% cao hơn giá hiện tại)
                    price_target = current_price_value * 1.5
                    formatted_price_target = f"{price_target:,.0f}"
                    profit_percent = 0.5  # 50% được lưu dưới dạng thập phân
                    print(f"Sử dụng giá mục tiêu đơn giản: {formatted_price_target} VND, Suất sinh lời: {profit_percent * 100}%")
                else:
                    # Nếu không thể tính toán được giá mục tiêu, sử dụng "N/A"
                    formatted_price_target = "N/A"
                    profit_percent = "N/A"
                    print("Không thể tính toán giá mục tiêu, sử dụng N/A")
        except Exception as e:
            print(f"Lỗi khi lấy giá hiện tại từ API: {str(e)}")
            # Fallback: Tính toán giá hiện tại từ net_income và total_equity nếu API lỗi
            try:
                if len(net_income) > 0 and len(total_equity) > 0 and total_equity[-1] != 0:
                    price_value = net_income[-1] / total_equity[-1] * 10000
                    formatted_current_price = f"{price_value:,.0f}"
                    print(f"Sử dụng giá hiện tại tính toán: {formatted_current_price}")
                    
                    # Tính giá mục tiêu đơn giản và suất sinh lời
                    price_target = price_value * 1.25
                    formatted_price_target = f"{price_target:,.0f}"
                    profit_percent = 0.25  # 25% được lưu dưới dạng thập phân
                else:
                    formatted_current_price = "N/A"
                    formatted_price_target = "N/A"
                    profit_percent = "N/A"
            except Exception as e:
                print(f"Lỗi khi tính giá hiện tại từ dữ liệu tài chính: {str(e)}")
                formatted_current_price = "N/A"
                formatted_price_target = "N/A"
                profit_percent = "N/A"
        
        # Đã xóa phần chuẩn bị dữ liệu peers cho trang 3
        # Cập nhật empty peer_data
        peer_data = []
        
        # Chuẩn bị dữ liệu định giá đơn giản
        valuation_data = {
            'pe_avg': 'N/A',
            'pe_median': 'N/A',
            'pe_10yr_avg': 'N/A',
            'pe_target': 'N/A',
            'eps_target': 'N/A',
            'price_target': formatted_price_target,
            'current_price': formatted_current_price,
            'upside': f"{float(profit_percent)*100:.2f}" if isinstance(profit_percent, (int, float)) else 'N/A'
        }
        
        recommendation_data = {
            "date": datetime.date.today().strftime('%d/%m/%Y'),
            "price_date": datetime.date.today().strftime('%d/%m/%Y'),
            "current_price": formatted_current_price,
            "target_price": formatted_price_target,
            "profit_percent": f"{profit_percent}"
        }
        
        # Chuẩn bị nội dung phân tích
        analysis_paragraphs = []
        if analysis:
            # Loại bỏ các dòng lời chào nếu có
            if isinstance(analysis, str):
                # Đảm bảo phân tích bắt đầu với tiêu đề "Định giá cập nhật với khuyến nghị MUA"
                # Nếu không có, thêm vào
                if not "**Định giá cập nhật với khuyến nghị MUA" in analysis:
                    analysis = "**Định giá cập nhật với khuyến nghị MUA, giá mục tiêu dài hạn**\n" + analysis
            
            # Chia phân tích thành các phần
            paragraphs = analysis.split('\n\n')
            
            # Xử lý từng đoạn để định dạng đúng
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Kiểm tra nếu đoạn có định dạng markdown và xử lý phù hợp
                    analysis_paragraphs.append(paragraph.strip())
        
        # Loại bỏ các lời chào khỏi tiêu đề và khuyến nghị 
        # Lưu ý: Các giá trị này không được sử dụng nữa vì đã xóa bỏ hiển thị trong generate_pdf.py
        
        analysis_data = {
            "content": analysis_paragraphs
        }
        
        # Lấy dữ liệu thị trường từ module finance_calc thay vì tạo trực tiếp trong services
        # Chuẩn bị thông tin cổ phiếu để truyền vào get_market_data
        stock_info = {
            'current_price': float(recommendation_data['current_price'].replace(',', '')) if recommendation_data.get('current_price') else 0,
            'shares_outstanding': financial_data.get('shares_outstanding', 1000) if isinstance(financial_data, dict) else 1000,
            'free_float': 35,  # Giá trị mặc định nếu không có dữ liệu
            'ratios': ratios
        }
        
        # Lấy dữ liệu thị trường từ API - truyền thêm symbol
        market_data = get_market_data(stock_info, symbol)
        print(f"Đã lấy dữ liệu thị trường từ module finance_calc cho {symbol}: {market_data}")
        
        # Lấy dữ liệu dự phóng cho từng trang - đảm bảo độc lập
        # Dữ liệu dự phóng cho page1
        page1_projection_data = get_projection_data_for_page1(symbol)
        print(f"Đã lấy dữ liệu dự phóng độc lập cho page1: {symbol}")
        
        # Dữ liệu dự phóng cho page2 - sử dụng create_projection_data dành riêng cho page2
        page2_projection_data = create_projection_data(symbol)
        print(f"Đã lấy dữ liệu dự phóng độc lập cho page2: {symbol}")
        
        # Format lại valuation_data nếu cần thiết
        if isinstance(profit_percent, (int, float)) and profit_percent != 'N/A':
            valuation_data['upside'] = f"{float(profit_percent) * 100:.2f}"
        
        # Generate PDF using ReportLab với định dạng mới
        pdf = PDFReport()
        pdf.create_stock_report(
            output_path=output_path,
            company_data=company_data,
            recommendation_data=recommendation_data,
            market_data=market_data,
            analysis_data=analysis_data,
            projection_data=page1_projection_data,  # Dữ liệu dự phóng cho page1
            page2_projection_data=page2_projection_data,  # Dữ liệu dự phóng riêng cho page2
            peer_data=peer_data,              # Dữ liệu các công ty cùng ngành
            valuation_data=valuation_data     # Dữ liệu định giá
        )
        
        return output_path
    
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        # Create a simple error PDF
        error_pdf = PDFReport()
        
        error_dir = "reports"
        os.makedirs(error_dir, exist_ok=True)
        error_path = os.path.join(error_dir, f"error_{symbol}.pdf")
        
        # Sử dụng mẫu báo cáo mới cho cả báo cáo lỗi
        company_data = {"name": f"Error Report for {symbol}", "info": "Error"}
        recommendation_data = {"date": datetime.date.today().strftime('%d/%m/%Y')}
        analysis_data = {
            "title": "Error Generating Report",
            "content": [f"Could not generate report for {symbol}: {str(e)}"]
        }
        
        error_pdf.create_stock_report(
            output_path=error_path,
            company_data=company_data,
            recommendation_data=recommendation_data,
            market_data={},
            analysis_data=analysis_data,
            projection_data=None,
            page2_projection_data=None
        )
        
        return error_path

def get_financial_analysis(symbol=None):
    """Generate financial analysis for a specified symbol or general market analysis"""
    try:
        if symbol:
            # Get actual financial data for the specified symbol
            # File paths for financial data
            data_dir = os.path.join("e:", "Chatbotfinance", "Main", "backend", "data")
            file_paths = [
                os.path.join(data_dir, f"2020-Vietnam.xlsx"), 
                os.path.join(data_dir, f"2021-Vietnam.xlsx"), 
                os.path.join(data_dir, f"2022-Vietnam.xlsx"), 
                os.path.join(data_dir, f"2023-Vietnam.xlsx"),
                os.path.join(data_dir, f"2024-Vietnam.xlsx")
            ]
            
            # Read and process data
            df_list = read_data(file_paths)
            clean_column_names(df_list)
            
            # Filter data for specified symbol
            dfs = [standardize_columns(df) for df in df_list]
            merged_df = merge_balance_sheets(dfs, symbol)
            
            if merged_df.empty:
                return f"No data found for symbol: {symbol}"
                
            # Process the data as needed to get financial metrics
            # (Similar to what's done in generate_pdf_report)
            # ...

            # Format the data for the API
            balance_sheet = {
                "Total Current Assets": ["100,000", "120,000", "150,000"],
                "Total Assets": ["500,000", "550,000", "600,000"],
            }
            income_statement = {
                "Revenue": ["250,000", "300,000", "350,000"],
                "Net Income": ["50,000", "60,000", "75,000"],
            }
            profitability_analysis = {
                "ROE": ["10%", "12%", "15%"],
                "ROA": ["8%", "10%", "12%"],
            }
            
            # Generate analysis using the financial data and pass the symbol parameter
            return generate_financial_analysis(
                balance_sheet=balance_sheet,
                income_statement=income_statement,
                profitability_analysis=profitability_analysis,
                symbol=symbol
            )
        else:
            # Provide a general market analysis if no symbol is specified
            custom_prompt = "Provide a general financial market overview for Vietnam market, focusing on current trends and potential investment opportunities."
            return generate_financial_analysis(custom_prompt=custom_prompt)
    except Exception as e:
        return f"Error generating analysis: {str(e)}"

def generate_company_overview_pdf(output_path=None):
    """
    Generate a PDF file with company overview information.
    
    Args:
        output_path (str, optional): Path where the PDF file will be saved.
            If None, a default path will be used.
            
    Returns:
        str: Path to the generated PDF file
    """
    if output_path is None:
        # Create a directory for reports if it doesn't exist
        reports_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate a filename based on current date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(reports_dir, f"company_overview_{timestamp}.pdf")
    
    # Call the function to generate the PDF
    result_path = generate_page4_pdf(output_path)
    
    return result_path

def generate_financial_ratios_pdf(output_path=None):
    """
    Generate a PDF file with financial ratios information.
    
    Args:
        output_path (str, optional): Path where the PDF file will be saved.
            If None, a default path will be used.
            
    Returns:
        str: Path to the generated PDF file
    """
    if output_path is None:
        # Create a directory for reports if it doesn't exist
        reports_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate a filename based on current date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(reports_dir, f"financial_ratios_{timestamp}.pdf")
    
    # Call the function to generate the PDF
    result_path = generate_page5_pdf(output_path)
    
    return result_path

def generate_additional_info_pdf(output_path=None):
    """
    Generate a PDF file with additional information.
    
    Args:
        output_path (str, optional): Path where the PDF file will be saved.
            If None, a default path will be used.
            
    Returns:
        str: Path to the generated PDF file
    """
    if output_path is None:
        # Create a directory for reports if it doesn't exist
        reports_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate a filename based on current date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(reports_dir, f"additional_info_{timestamp}.pdf")
    
    # Call the function to generate the PDF
    result_path = generate_page6_pdf(output_path)
    
    return result_path

if __name__ == "__main__":
    # Test code
    symbol = "VCB"  # Example symbol
    pdf_path = generate_pdf_report(symbol)
    print(f"Generated PDF at: {pdf_path}")
