import datetime
import os
import pandas as pd
import numpy as np
from .module_report.data_processing import read_data, clean_column_names, standardize_columns, merge_balance_sheets, get_values
from .module_report.finance_calc import (calculate_total_current_assets, calculate_ppe, calculate_total_assets, 
                                        calculate_ebitda, calculate_financial_ratios, calculate_total_operating_expense,
                                        calculate_net_income_before_taxes, calculate_net_income_before_extraordinary_items,
                                        get_market_data, current_price, predict_price)
from .module_report.generate_pdf import PDFReport
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
    company = Vnstock().stock(symbol=symbol, source='TCBS').company
    return company.profile()['company_name'].values[0]

# Thêm hàm để tạo dữ liệu dự phóng
def create_projection_data(symbol):
    """Tạo dữ liệu dự phóng cho báo cáo"""
    try:
        # Dữ liệu dự phóng mẫu - trong thực tế sẽ lấy từ database hoặc API
        projection_data = {
            'revenue': ['20,609', '+11%', '25,266', '+23%', 'Doanh thu thuần năm 2024 ghi nhận tăng 11% YoY. Đóng góp chủ yếu đến từ sản lượng tăng (+10.1 triệu tấn, +18% YoY), đặc biệt là ở kênh xuất khẩu (620 nghìn tấn, +21% YoY). Trong năm 2025, chúng tôi kỳ vọng sản lượng tiếp tục tăng trưởng 14% YoY, giá tôn mạ và ống thép trong nước tăng trưởng 10% YoY, từ đó đóng góp cho sự tăng trưởng doanh thu.'],
            'volume': ['882', '20%', '1,014', '15%', 'Sản lượng tôn mạ tăng 20% YoY và đóng lực từ các kênh nội địa và xuất khẩu. Chúng tôi kỳ vọng sản lượng bán hàng tiếp tục tăng trưởng 15% trong năm 2025 do kỳ vọng nhu cầu hồi phục đặc biệt tại thị trường nội địa, nhờ (1) Thị trường BĐS ấm lên; (2) Chính phủ đẩy mạnh giải ngân đầu tư công.'],
            'coated_steel': ['882', '20%', '1,014', '15%', ''],
            'steel_pipe': ['130', '-5%', '137', '5%', 'Sản phẩm ống thép của Nam Kim chủ yếu được tiêu thụ tại thị trường nội địa. Năm 2024, sản lượng giảm nhẹ 5% do nhu cầu ống thép xây dựng miền Nam chưa khởi sắc, trong khi hệ thống phân phối của Nam Kim chủ yếu tại khu vực này. Chúng tôi kỳ vọng sản lượng ống thép sẽ tăng 5% trong năm 2025 nhờ hoạt động xây dựng hồi phục, đặc biệt là đối với các dự án tại miền Nam được khởi động phát triển.'],
            'gross_profit': ['1,832', '66%', '2,653', '45%', 'Trong 2024, giá HRC đã giảm 10.7% khiến biên lợi nhuận gộp của NKG tăng mạnh (do giá HRC giảm đầu vào giá bán đầu ra thường được điều chỉnh trễ hơn với giá HRC giao ngay). Trong năm 2025, chúng tôi cho rằng xu hướng hồi phục của giá thép HRC, kết hợp với chiến lược quản lý hàng tồn kho linh hoạt sẽ giúp Nam Kim cải thiện biên lợi nhuận gộp.'],
            'gross_margin': ['8.9%', '', '10.5%', '', ''],
            'sga': ['1,138', '54%', '1,337', '17.4%', 'Năm 2024, giá cước vận chuyển tăng đột biến khiến chi phí bán hàng của NKG tăng đột biến. Chúng tôi kỳ vọng giá cước vận chuyển sẽ quay lại mức ổn định trong năm 2025.'],
            'operating_profit': ['557', '215%', '1,021', '83%', ''],
            'profit_before_tax': ['558', '215%', '1,023', '83%', ''],
            'profit_after_tax': ['453', '286%', '829', '83%', '']
        }
        return projection_data
    except Exception as e:
        print(f"Lỗi khi tạo dữ liệu dự phóng: {str(e)}")
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
            custom_prompt=f"Analyze financial performance of {symbol} based on: Balance Sheet: {balance_sheet_data}, Income Statement: {income_statement_data}, Profitability Analysis: {profitability_analysis_data}"
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
        
        # Lấy thông tin ngành nghề của công ty
        industry = get_company_industry(symbol)
        print(f"Đã lấy thông tin ngành nghề của {symbol}: {industry}")
        name = get_company_name(symbol)
        # Chuẩn bị dữ liệu cho báo cáo định dạng mới
        company_data = {
            "name": f"{name}",  # Chỉ hiển thị tên công ty, không kèm mã
            "symbol": symbol,
            "info": f"[ {symbol} | {exchange} | Ngành: {industry} ]"  # Thêm thông tin ngành
        }
        
        # Lấy giá hiện tại từ API thay vì tính toán
        try:
            price_value = current_price(symbol)
            formatted_current_price = f"{price_value:,.0f}"
            print(f"Đã lấy giá hiện tại của {symbol} từ API: {formatted_current_price}")
            
            # Tính giá mục tiêu và suất sinh lời sử dụng hàm predict_price
            try:
                price_target, profit_percent = predict_price(symbol)
                print(f"Đã tính giá mục tiêu cho {symbol}: {price_target} VND, Suất sinh lời: {profit_percent * 100}%")
                formatted_price_target = f"{price_target:,.0f}"
            except Exception as e:
                print(f"Lỗi khi tính giá mục tiêu: {str(e)}")
                # Kiểm tra nếu price_value là số thì mới tính toán giá mục tiêu dự phòng
                if isinstance(price_value, (int, float)) and price_value > 0:
                    # Fallback: Tính toán giá mục tiêu đơn giản (50% cao hơn giá hiện tại)
                    price_target = price_value * 1.5
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
            except:
                formatted_current_price = "N/A"
                formatted_price_target = "N/A"
                profit_percent = "N/A"
        
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
                # Loại bỏ các dòng lời chào đầu tiên
                lines = analysis.split('\n')
                clean_lines = []
                skip_intro = True
                for line in lines:
                    # Bỏ qua các dòng cho đến khi gặp tiêu đề đầu tiên
                    if skip_intro and not line.startswith('**Định giá cập nhật với khuyến nghị MUA**'):
                        continue
                    skip_intro = False
                    clean_lines.append(line)
                
                analysis = '\n'.join(clean_lines)
            
            # Tạo tiêu đề cho các phần phân tích chính
            analysis_sections = [
                "**Định giá cập nhật với khuyến nghị MUA**",
                "**TÌNH HÌNH TÀI CHÍNH HIỆN NAY**"
            ]
            
            # Chia phân tích thành các phần
            paragraphs = analysis.split('\n\n')
            
            # Kiểm tra xem phân tích đã có tiêu đề Markdown hay chưa
            if paragraphs and not any(p.startswith('**') for p in paragraphs):
                # Không có tiêu đề Markdown, thêm tiêu đề vào nội dung
                formatted_paragraphs = []
                section_idx = 0
                paragraphs_per_section = max(1, len(paragraphs) // len(analysis_sections))
                
                for i, para in enumerate(paragraphs):
                    if i % paragraphs_per_section == 0 and section_idx < len(analysis_sections):
                        # Thêm tiêu đề kết hợp với đoạn đầu tiên của phần
                        formatted_paragraphs.append(f"{analysis_sections[section_idx]} {para}")
                        section_idx += 1
                    else:
                        # Thêm đoạn thông thường
                        formatted_paragraphs.append(para)
                
                # Đảm bảo sử dụng tất cả các tiêu đề
                while section_idx < len(analysis_sections):
                    formatted_paragraphs.append(analysis_sections[section_idx])
                    section_idx += 1
                
                analysis_paragraphs = formatted_paragraphs
            else:
                # Đã có tiêu đề Markdown, giữ nguyên định dạng
                analysis_paragraphs = paragraphs
        
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
        
        # Tạo dữ liệu dự phóng
        projection_data = create_projection_data(symbol)
        
        # Generate PDF using ReportLab với định dạng mới
        pdf = PDFReport()
        pdf.create_stock_report(
            output_path=output_path,
            company_data=company_data,
            recommendation_data=recommendation_data,
            market_data=market_data,
            analysis_data=analysis_data,
            projection_data=projection_data  # Thêm dữ liệu dự phóng
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
            analysis_data=analysis_data
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
            
            # Generate analysis using the financial data
            return generate_financial_analysis(
                balance_sheet=balance_sheet,
                income_statement=income_statement,
                profitability_analysis=profitability_analysis
            )
        else:
            # Provide a general market analysis if no symbol is specified
            custom_prompt = "Provide a general financial market overview for Vietnam market, focusing on current trends and potential investment opportunities."
            return generate_financial_analysis(custom_prompt=custom_prompt)
    except Exception as e:
        return f"Error generating analysis: {str(e)}"

if __name__ == "__main__":
    # Test code
    symbol = "VCB"  # Example symbol
    pdf_path = generate_pdf_report(symbol)
    print(f"Generated PDF at: {pdf_path}")
