import os
import google.generativeai as genai
from dotenv import load_dotenv
from .finance_calc import current_price
import json

def configure_api():
    """Configure and authenticate the API"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API Key is not set. Please check the .env file.")
    genai.configure(api_key=api_key)

def create_analysis_prompt_page1(balance_sheet, income_statement, profitability_analysis):
    """Create the prompt for financial analysis"""
    return f""" 
Bạn là một chuyên gia phân tích tài chính chuyên về phân tích cơ bản cổ phiếu. Hãy đánh giá rủi ro và triển vọng đầu tư của mã cổ phiếu dựa trên các chỉ số tài chính và thông tin sausau.
Giữ văn phong chuyên nghiệp và báo cáo dưới 300 từ.

Cho các dữ liệu báo cáo tài chính sau:  
Bảng cân đối kế toán (Balance Sheet):
{balance_sheet}  
Báo cáo thu nhập (Income Statement):
{income_statement}  
Phân tích khả năng sinh lời (Profitability Analysis):
{profitability_analysis} 
Hãy lấy các chỉ số tài chính từ các dữ liệu trên và đánh giá rủi ro và triển vọng đầu tư của mã cổ phiếu. kkhi đưa ra so sánh hoặc đánh giá nên trích dẫn số liệu cụ thể.
Nhận xét với văn phong và từ ngữ nên được tham khảo sau đây, khi đưa ra so sánh hoặc đánh giá nên trích dẫn số liệu cụ thể lấy từ dữ liệu đã chocho:
Yêu cầu phân tích:

- PHÂN TÍCH TÀI CHÍNH:
Một đoạn văn dưới 200 từ, phân tích các chỉ số tài chính quan trọng sau:
Doanh thu và Lợi nhuận ròng: Xu hướng tăng trưởng qua các năm.
Biên lợi nhuận gộp (Gross Margin), biên lợi nhuận ròng (Net Profit Margin): So sánh với trung bình ngành.
Tỷ lệ giá trên thu nhập (P/E): Tỷ lệ này đo lường mối quan hệ giữa giá cổ phiếu và thu nhập của công ty. P/E càng cao thì cổ phiếu càng được định giá cao.
Tỷ lệ giá trên giá trị sổ sách (P/B): Tỷ lệ này đo lường mối quan hệ giữa giá cổ phiếu và giá trị sổ sách của công ty. P/B càng thấp thì cổ phiếu càng được định giá thấp.
Tỷ lệ lợi nhuận trên vốn chủ sở hữu (ROE): Tỷ lệ này đo lường khả năng sinh lời của công ty trên vốn chủ sở hữu. ROE càng cao thì công ty càng có khả năng tạo ra lợi nhuận.
Tỷ lệ lợi nhuận trên tài sản (ROA): Tỷ lệ này đo lường khả năng sinh lời của công ty trên tổng tài sản. ROA càng cao thì công ty càng có khả năng tạo ra lợi nhuận từ tài sản của mình.
Tỷ lệ nợ trên vốn chủ sở hữu (D/E): Tỷ lệ này đo lường mức độ đòn bẩy tài chính của công ty. D/E càng cao thì công ty càng phụ thuộc vào nợ vay.
EBITDA: EBITDA là chỉ số đo lường lợi nhuận trước thuế, lãi vay, khấu hao và chi phí khấu hao.
Hãy đưa ra nhận xét ngắn gọn về tình hình tài chính.

- PHÂN TÍCH RỦI RO:
Đoạn văn dưới 200 từ đánh giá được rủi ro tài chính (nợ vay, thanh khoản, dòng tiền).

- ĐÁNH GIÁ TRIỂN VỌNG ĐẦU TƯ:
Đoạn văn ngắn đánh giá ttiềm năng tăng trưởng lợi nhuận và biên lợi nhuận.

Định dạng đầu ra mong muốn: Đoạn văn nhận xét súc tích, logic (khoảng bé hơn 300 từ)
Có kết luận rõ ràng về tiềm năng đầu tư của mã cổ phiếu.
- TUYỆT ĐỐI PHẢI TIẾT KIỆM SỐ TRANG SỬ DỤNG. HÃY GHI CÁC NỘI DUNG GẦN VỚI NHAU NHẤT CÓ THỂ, TRÁNH TÌNH TRẠNG VIẾT NỘI DUNG VÀO FILE MÀ MỖI CÁC NỘI DUNG DÙNG 1 TRẠNG. TIẾT KIỆM NHẤT CÓ THỂ NHÉ.
- KHÔNG ĐƯỢC XUỐNG DÒNG 2 LẦN TRONG MỌI TÌNH HUỐNG.
"""

def create_nkg_analysis_prompt_page1(balance_sheet, income_statement, profitability_analysis, current_price, profit_data=None, news=None):
    """Create the prompt specifically for NKG stock analysis"""
    
    # Set default profit indicators - all N/A since profit_data function was removed
    profit_indicators = """
Chi tiết chỉ số lợi nhuận:
- Lợi nhuận từ hoạt động kinh doanh: N/A
- Lợi nhuận trước thuế: N/A
- Lợi nhuận sau thuế của cổ đông công ty mẹ: N/A
"""
    
    return f""" 
Bạn là một chuyên gia phân tích tài chính chuyên về phân tích cơ bản cổ phiếu ngành thép. Hãy đánh giá rủi ro và triển vọng đầu tư của Công ty Cổ phần Thép Nam Kim (mã cổ phiếu: NKG) dựa trên thông tin ngành thép và vị thế của công ty.
Giữ văn phong chuyên nghiệp.

Thông tin ngành thép: Ngành thép Việt Nam chịu ảnh hưởng bởi giá nguyên liệu đầu vào (quặng sắt, thép phế), chi phí năng lượng, biến động tỷ giá và cạnh tranh từ thép Trung Quốc. Nam Kim là một trong những nhà sản xuất tôn mạ hàng đầu Việt Nam, có thế mạnh về thép mạ màu và thép mạ kẽm, đồng thời có hoạt động xuất khẩu sang các thị trường như Bắc Mỹ, châu Âu và Đông Nam Á.

Cho các dữ liệu báo cáo tài chính của NKG (Nam Kim Steel):  
Bảng cân đối kế toán (Balance Sheet):
{balance_sheet}  
Báo cáo thu nhập (Income Statement):
{income_statement}  
Phân tích khả năng sinh lời (Profitability Analysis):
{profitability_analysis} 
{profit_indicators}

Hãy đánh giá rủi ro và triển vọng đầu tư của mã cổ phiếu NKG, tập trung vào các yếu tố sau:
1. Vị thế doanh nghiệp trong ngành thép mạ Việt Nam
2. Hiệu quả vận hành nhà máy và chi phí sản xuất
3. Tỷ suất lợi nhuận so với các đối thủ cùng ngành
4. Khả năng chống chịu biến động giá nguyên liệu đầu vào
5. Tiềm năng tăng trưởng từ xuất khẩu thép

Yêu cầu phân tích 3 PHẦN LỚN SAU:

**Định giá cập nhật với khuyến nghị MUA, giá mục tiêu dài hạn**
- Hãy viết về một đoạn văn giới thiệu thông tin mới nhất về công ty thép nam kim với mã cổ phiếu là NKG. Tìm các chỉ số mới nhất như là giá hiện tại: {current_price}, giá mục tiêu là 23,972 VND,... để đánh giá tình hình hiện tại của công ty. không quá 300 từ

**TÌNH HÌNH TÀI CHÍNH HIỆN NAY**
Phân tích ngắn gọn về:
- Bắt buộc phải tham khảo chỉ số YoY của công ty thép nam kim từ các dữ liệu báo cáo tài chính và chỉ số lợi nhuận được cung cấp.
- Tập trung phân tích biến động lợi nhuận từ hoạt động kinh doanh, lợi nhuận trước thuế và lợi nhuận sau thuế theo số liệu YoY đã cung cấp.
- Doanh thu và lợi nhuận: Biến động và triển vọng phục hồi
- Biên lợi nhuận: Yếu tố ảnh hưởng từ giá nguyên liệu và giá bán thép
- Tỷ lệ nợ và khả năng trả nợ: Đánh giá rủi ro tài chính
- Tỷ lệ ROE/ROA của Nam Kim Steel so với các công ty cùng ngành
- Hiệu quả hoạt động và quản trị chi phí
- Tập trung bình luận chỉ số
- Phải đưa ra được số liệu cụ thể.
- Bình luận các chỉ số dựa trên hiểu biết của bạn và các chỉ số đã cung cấp.
- Không quá 200 từ

**CÁC TIN TỨC VỀ CÔNG TY THÉP NAM KIM**
- Đây là thông tin mới nhất về công ty thép nam kim: {news}.
- Có thể tìm các tin tức mới nhất trên google để nói về công ty thép nam kim.
- Hãy viết về một đoạn văn giới thiệu thông tin mới nhất về công ty thép nam kim với mã cổ phiếu là NKG. Tìm các chỉ số mới nhất như là giá hiện tại: {current_price}, giá mục tiêu là 23,972 VND,... để đánh giá tình hình hiện tại của công ty. không quá 300 từ
Định dạng đầu ra cần tuân thủ:
0. Không cần viết kết luận cuối.
1. Bắt đầu phân tích với tiêu đề "**Định giá cập nhật với khuyến nghị MUA, giá mục tiêu dài hạn**"
2. Nội dung phải súc tích, logic, tổng cộng không quá 600 từ
3. Có kết luận rõ ràng về tiềm năng đầu tư cổ phiếu NKG
4. TUYỆT ĐỐI PHẢI TIẾT KIỆM SỐ TRANG SỬ DỤNG. Viết các nội dung gần với nhau nhất có thể.
5. KHÔNG ĐƯỢC XUỐNG DÒNG 2 LẦN TRONG MỌI TÌNH HUỐNG.
6. Tuyệt đối không bắt đầu các mục với ký hiệu "**" và "*".
7. Viết phải thật sự chuyên nghiệp giống như một người phân tích tài chính chuyên nghiệp.
"""

def create_revenue_commentary_prompt(revenue_data):
    """Create a prompt for revenue commentary"""
    return f"""
Bạn là một chuyên gia phân tích tài chính. Hãy viết bình luận chi tiết về DOANH THU của công ty dựa trên dữ liệu sau:

- Doanh thu thuần: {revenue_data.get('revenue', 'N/A')} tỷ VND
- Tăng trưởng doanh thu so với năm trước: {revenue_data.get('yoy_growth', 'N/A')}
- Doanh thu dự kiến năm tới: {revenue_data.get('projected_revenue', 'N/A')} tỷ VND
- Tăng trưởng dự kiến năm tới: {revenue_data.get('projected_growth', 'N/A')}
- Tăng trưởng trung bình ngành: {revenue_data.get('sector_growth', 'N/A')}
- Thị phần: {revenue_data.get('market_share', 'N/A')}

Hãy viết một đoạn văn ngắn gọn (3-4 câu) đánh giá sâu về tình hình doanh thu của công ty, tập trung vào:
1. Mức tăng trưởng doanh thu hiện tại và đánh giá chất lượng tăng trưởng (so với ngành)
2. Các yếu tố chính đóng góp vào kết quả doanh thu (như mở rộng thị trường, cải thiện sản phẩm)
3. Triển vọng tăng trưởng doanh thu trong năm tới dựa trên dự phóng
4. Đánh giá tính bền vững của chiến lược tăng trưởng doanh thu

Chú ý: Hãy cụ thể, có tham chiếu đến các con số thực tế từ dữ liệu. Bình luận phải súc tích, chuyên nghiệp và có giá trị phân tích cao.

Yêu cầu:
- Không giới thiệu, chỉ trả lời trực tiếp
- Không dùng từ "theo dữ liệu" hoặc "dựa trên thông tin được cung cấp"
- Viết với giọng điệu tự tin, chuyên nghiệp của một chuyên gia phân tích tài chính
"""

def create_gross_profit_commentary_prompt(gross_profit_data):
    """Create a prompt for gross profit and expenses commentary"""
    return f"""
Bạn là một chuyên gia phân tích tài chính. Hãy viết bình luận chi tiết về LỢI NHUẬN GỘP và CƠ CẤU CHI PHÍ của công ty dựa trên dữ liệu sau:

- Lợi nhuận gộp: {gross_profit_data.get('gross_profit', 'N/A')} tỷ VND
- Tăng trưởng lợi nhuận gộp so với năm trước: {gross_profit_data.get('yoy_growth', 'N/A')}
- Biên lợi nhuận gộp hiện tại: {gross_profit_data.get('gross_margin', 'N/A')}
- Biên lợi nhuận gộp năm trước: {gross_profit_data.get('prev_gross_margin', 'N/A')}
- Chi phí tài chính: {gross_profit_data.get('financial_expense', 'N/A')} tỷ VND (YoY: {gross_profit_data.get('financial_expense_yoy', 'N/A')})
- Chi phí bán hàng: {gross_profit_data.get('selling_expense', 'N/A')} tỷ VND (YoY: {gross_profit_data.get('selling_expense_yoy', 'N/A')})
- Chi phí quản lý: {gross_profit_data.get('admin_expense', 'N/A')} tỷ VND (YoY: {gross_profit_data.get('admin_expense_yoy', 'N/A')})
- Tỷ lệ chi phí trên doanh thu: {gross_profit_data.get('expense_ratio', 'N/A')}

Hãy viết một đoạn văn chi tiết (4-5 câu) phân tích biên lợi nhuận gộp và cơ cấu chi phí của công ty, tập trung vào:
1. Biên lợi nhuận gộp cải thiện/suy giảm và các yếu tố ảnh hưởng chính
2. Đánh giá hiệu quả kiểm soát chi phí tài chính và chiến lược quản lý nợ
3. Phân tích xu hướng chi phí bán hàng và hiệu quả của hoạt động marketing
4. Nhận xét về chi phí quản lý doanh nghiệp và nỗ lực tối ưu hóa bộ máy quản lý
5. Đánh giá tổng thể về khả năng quản lý chi phí của doanh nghiệp

Chú ý: Hãy cụ thể, có tham chiếu đến các con số thực tế từ dữ liệu. Bình luận phải súc tích, chuyên nghiệp và có giá trị phân tích cao.

Yêu cầu:
- Không giới thiệu, chỉ trả lời trực tiếp
- Không dùng từ "theo dữ liệu" hoặc "dựa trên thông tin được cung cấp"
- Tập trung phân tích cả lợi nhuận gộp VÀ các loại chi phí chính
- Viết với giọng điệu tự tin, chuyên nghiệp của một chuyên gia phân tích tài chính
"""

def create_operating_profit_commentary_prompt(operating_profit_data):
    """Create a prompt for operating profit and net profit commentary"""
    return f"""
Bạn là một chuyên gia phân tích tài chính. Hãy viết bình luận chi tiết về CÁC CHỈ SỐ LỢI NHUẬN CHÍNH của công ty dựa trên dữ liệu sau:

- Lợi nhuận từ hoạt động kinh doanh: {operating_profit_data.get('operating_profit', 'N/A')} tỷ VND
- Tăng trưởng LNHĐKD so với năm trước: {operating_profit_data.get('yoy_growth', 'N/A')}
- Lợi nhuận trước thuế: {operating_profit_data.get('profit_before_tax', 'N/A')} tỷ VND
- Tăng trưởng LNTT so với năm trước: {operating_profit_data.get('pbt_yoy_growth', 'N/A')}
- Lợi nhuận sau thuế: {operating_profit_data.get('profit_after_tax', 'N/A')} tỷ VND
- Tăng trưởng LNST so với năm trước: {operating_profit_data.get('pat_yoy_growth', 'N/A')}
- Biên lợi nhuận hoạt động: {operating_profit_data.get('operating_margin', 'N/A')}
- Thuế suất thực tế: {operating_profit_data.get('effective_tax_rate', 'N/A')}

Hãy viết một đoạn văn chi tiết (4-5 câu) phân tích sâu về hiệu quả hoạt động kinh doanh của công ty, tập trung vào:
1. Phân tích mức tăng trưởng của lợi nhuận từ hoạt động kinh doanh và nguyên nhân chính
2. So sánh tỷ lệ lợi nhuận trước thuế và lợi nhuận từ hoạt động kinh doanh để đánh giá tác động của các hoạt động tài chính/khác
3. Phân tích hiệu quả quản lý thuế thông qua chênh lệch giữa lợi nhuận trước thuế và sau thuế
4. Đánh giá tổng thể về khả năng sinh lời của doanh nghiệp 
5. Nhận xét về khả năng tạo ra giá trị dài hạn cho cổ đông

Chú ý: Hãy cụ thể, có tham chiếu đến các con số thực tế từ dữ liệu. Bình luận phải súc tích, chuyên nghiệp và có giá trị phân tích cao.

Yêu cầu:
- Không giới thiệu, chỉ trả lời trực tiếp
- Không dùng từ "theo dữ liệu" hoặc "dựa trên thông tin được cung cấp"
- Tập trung phân tích sâu về hiệu quả chung của hoạt động kinh doanh
- Viết với giọng điệu tự tin, chuyên nghiệp của một chuyên gia phân tích tài chính
"""

def create_cost_of_goods_sold_commentary_prompt(data):
    """Create a prompt for cost of goods sold commentary"""
    return f"""
Bạn là một chuyên gia phân tích tài chính. Hãy viết bình luận ngắn gọn về giá vốn hàng bán của công ty dựa trên dữ liệu sau:

- Doanh thu thuần: {data.get('doanh_thu_thuan', 'N/A')} tỷ VND
- Lợi nhuận gộp: {data.get('loi_nhuan_gop', 'N/A')} tỷ VND
- Tăng trưởng doanh thu so với năm trước: {data.get('yoy_doanh_thu', 'N/A')}
- Tăng trưởng lợi nhuận gộp so với năm trước: {data.get('yoy_loi_nhuan_gop', 'N/A')}

Hãy viết một đoạn văn ngắn (không quá 2 câu) để diễn giải về tình hình giá vốn hàng bán của công ty. Tập trung vào việc tối ưu hóa quy trình sản xuất, kiểm soát chi phí nguyên vật liệu, và cải thiện hiệu quả hoạt động.

Yêu cầu:
- Trả lời ngắn gọn, súc tích (tối đa 2 câu)
- Không giới thiệu, chỉ trả lời trực tiếp
- Không dùng từ "theo dữ liệu" hoặc "dựa trên thông tin được cung cấp"
"""

def generate_financial_commentary(company_code, page2_data):
    """
    Tạo chú thích tài chính cho 4 mục chính:
    - Doanh thu thuần
    - Lợi nhuận gộp
    - Chi phí (chung cho chi phí tài chính, chi phí bán hàng, chi phí quản lý)
    - Lợi nhuận từ HĐKD
    
    Args:
        company_code: Mã công ty (ví dụ: "NKG")
        page2_data: Dictionary chứa các chỉ số tài chính
        
    Returns:
        Dictionary các chú thích cho các mục chính
    """
    # Kiểm tra xem API key có được cấu hình đúng không
    try:
        # Chuẩn bị các chú thích trống
        default_comments = {
            'Doanh thu thuần': '',
            'Lợi nhuận gộp': '',
            'Chi phí': '',
            'Lợi nhuận từ HĐKD': ''
        }
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ Không tìm thấy GOOGLE_API_KEY trong biến môi trường")
            try:
                # Tải từ config.json nếu có
                with open("config.json", "r") as f:
                    config = json.load(f)
                    api_key = config.get("GOOGLE_API_KEY")
                    if api_key:
                        print("✅ Loaded API key from config.json")
                    else:
                        print("⚠️ Không tìm thấy GOOGLE_API_KEY trong config.json")
            except:
                print("⚠️ Không thể tải config.json")
                
        if not api_key:
            print("❌ Không có GOOGLE_API_KEY, trả về chú thích trống")
            return default_comments
            
        # Setup model với safety settings phù hợp
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.2,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
                "response_mime_type": "text/plain"
            },
            safety_settings={
                "HARASSMENT": "BLOCK_NONE",
                "HATE": "BLOCK_NONE",
                "SEXUAL": "BLOCK_NONE",
                "DANGEROUS": "BLOCK_NONE"
            }
        )
        
        results = {}
        
        # Định nghĩa mapping chính xác cho từng mục
        section_mappings = {
            "Doanh thu thuần": {
                "required_fields": [
                    "doanh_thu_thuan", "doanh_thu_thuan_2025F", 
                    "yoy_doanh_thu", "yoy_doanh_thu_2025F"
                ]
            },
            "Lợi nhuận gộp": {
                "required_fields": [
                    "loi_nhuan_gop", "loi_nhuan_gop_2025F",
                    "yoy_loi_nhuan_gop", "yoy_loi_nhuan_gop_2025F",
                    "bien_loi_nhuan_gop", "bien_loi_nhuan_gop_2025F"
                ]
            },
            "Chi phí": {
                "required_fields": [
                    "chi_phi_tai_chinh", "chi_phi_tai_chinh_2025F",
                    "yoy_chi_phi_tai_chinh", "yoy_chi_phi_tai_chinh_2025F",
                    "chi_phi_ban_hang", "chi_phi_ban_hang_2025F",
                    "yoy_chi_phi_ban_hang", "yoy_chi_phi_ban_hang_2025F",
                    "chi_phi_quan_ly", "chi_phi_quan_ly_2025F",
                    "yoy_chi_phi_quan_ly", "yoy_chi_phi_quan_ly_2025F"
                ]
            },
            "Lợi nhuận từ HĐKD": {
                "required_fields": [
                    "loi_nhuan_hdkd", "loi_nhuan_hdkd_2025F",
                    "yoy_loi_nhuan_hdkd", "yoy_loi_nhuan_hdkd_2025F",
                    "bien_loi_nhuan_hdkd", "bien_loi_nhuan_hdkd_2025F"
                ]
            }
        }
        
        # Tạo chú thích cho 4 mục 
        for section_name, mapping in section_mappings.items():
            print(f"📝 Tạo chú thích cho {section_name}...")
            
            # Lọc dữ liệu chính xác theo danh sách required_fields
            relevant_data = {}
            for field in mapping["required_fields"]:
                # Chỉ lấy chính xác các trường cần thiết
                if field in page2_data:
                    relevant_data[field] = page2_data[field]
                # Thử các biến thể viết hoa nếu không tìm thấy
                elif field.upper() in page2_data:
                    relevant_data[field] = page2_data[field.upper()]
            
            # Chỉ tiếp tục nếu có ít nhất một số liệu liên quan
            if not relevant_data:
                print(f"⚠️ Không tìm thấy dữ liệu liên quan cho {section_name}")
                continue
            
            # Format dữ liệu cho prompt
            data_fields = ", ".join([f"{k}: {v}" for k, v in relevant_data.items()])
            
            # Tạo mô tả phân tích phù hợp với từng mục
            descriptions = {
                "Doanh thu thuần": "tăng trưởng doanh thu, so sánh với mức tăng trưởng năm trước và dự báo năm tới",
                "Lợi nhuận gộp": "biên lợi nhuận gộp, nguyên nhân thay đổi, và triển vọng. CHỈ NÓI VỀ LỢI NHUẬN GỘP, KHÔNG NHẮC ĐẾN CHI PHÍ",
                "Chi phí": "biến động của chi phí tài chính (lãi vay và tỷ giá), chi phí bán hàng (marketing), và chi phí quản lý (bộ máy quản trị)",
                "Lợi nhuận từ HĐKD": "hiệu quả hoạt động kinh doanh, kiểm soát chi phí và triển vọng"
            }
            
            # Tạo prompt cho mục hiện tại
            prompt = f"""
            Tạo chú thích chi tiết về {section_name} của công ty {company_code} dựa trên dữ liệu sau:
            {data_fields}
            
            Chú thích cần đánh giá về {descriptions[section_name]}.
            {"Phân tích riêng biến động của từng loại chi phí (tài chính, bán hàng, quản lý) qua các yếu tố như Nêu những lí do làm chi phí tăng, thị trường biến động ra sao giá nguyên vật liệu năm 2024, các chi phí về vận hành như thế nào." if section_name == "Chi phí" else ""}
            {"CHÚ Ý: Chỉ phân tích về lợi nhuận gộp và biên lợi nhuận gộp. Tuyệt đối không được nhắc đến chi phí tài chính, bán hàng, quản lý." if section_name == "Lợi nhuận gộp" else ""}
            
            Hãy trả lời bằng tiếng Việt, viết 3-4 câu ngắn gọn, súc tích. 
            Đừng bao gồm tiêu đề hay phần mở đầu, chỉ cần ghi nội dung chú thích.
            Tuyệt đối không dùng các ký tự: *, **, [, ]
            """
            
            try:
                response = model.generate_content(prompt).text.strip()
                if response:
                    results[section_name] = response
                    print(f"✅ Đã tạo chú thích {section_name}: {response[:50]}...")
                else:
                    results[section_name] = ""
                    print(f"⚠️ API trả về chú thích trống cho {section_name}")
            except Exception as e:
                print(f"❌ Lỗi khi tạo chú thích {section_name}: {str(e)}")
                results[section_name] = ""
        
        print(f"✅ Đã tạo xong chú thích với keys: {list(results.keys())}")
        return results
        
    except Exception as e:
        print(f"❌ Lỗi tổng thể khi gọi API Gemini: {str(e)}")
        # Nếu có lỗi, trả về chú thích trống
        return {
            'Doanh thu thuần': '',
            'Lợi nhuận gộp': '',
            'Chi phí': '',
            'Lợi nhuận từ HĐKD': ''
        }

def generate_financial_analysis(balance_sheet=None, income_statement=None, profitability_analysis=None, custom_prompt=None, symbol=None):
    """Generate financial analysis from the API"""
    # Configure API if not already done
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            configure_api()
    except:
        configure_api()
        
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction="Chatbot này sẽ hoạt động như một broker chứng khoán chuyên nghiệp nhé..."
    )

    try:
        # Use custom prompt if provided, otherwise check for NKG-specific prompt
        if custom_prompt:
            prompt = custom_prompt
        elif symbol == "NKG" and balance_sheet and income_statement and profitability_analysis:
            # For NKG, we'll use a default approach without the removed functions
            try:
                prompt = create_nkg_analysis_prompt_page1(
                    balance_sheet, 
                    income_statement, 
                    profitability_analysis,
                    current_price("NKG"),
                    None,  # No profit data
                    "N/A"  # No news data
                )
            except Exception as e:
                print(f"Error creating NKG analysis prompt: {str(e)}")
                # Fallback to the original function without profit data
                prompt = create_nkg_analysis_prompt_page1(
                    balance_sheet, 
                    income_statement, 
                    profitability_analysis,
                    current_price("NKG"),
                    None,
                    "N/A"
                )
        elif balance_sheet and income_statement and profitability_analysis:
            prompt = create_analysis_prompt_page1(balance_sheet, income_statement, profitability_analysis)
        else:
            prompt = "Provide a general financial market analysis and investment recommendations."
            
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API error: {str(e)}")
        return f"Error generating analysis: {str(e)}"

def generate_revenue_commentary(revenue_data):
    """Generate commentary for revenue section based on provided data"""
    try:
        # Configure API if not already done
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            configure_api()
            
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
            "response_mime_type": "text/plain",
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        
        # Create prompt for revenue commentary
        revenue_prompt = create_revenue_commentary_prompt(revenue_data)
        
        # Generate commentary
        response = model.generate_content(revenue_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating revenue commentary: {str(e)}")
        return "Doanh thu dự kiến tăng trưởng ổn định nhờ mở rộng thị trường và cải thiện sản phẩm."

def generate_gross_profit_commentary(gross_profit_data):
    """Generate commentary for gross profit and expenses section based on provided data"""
    try:
        # Configure API if not already done
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            configure_api()
            
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
            "response_mime_type": "text/plain",
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        
        # Create prompt for gross profit commentary
        gross_profit_prompt = create_gross_profit_commentary_prompt(gross_profit_data)
        
        # Generate commentary
        response = model.generate_content(gross_profit_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating gross profit commentary: {str(e)}")
        return ""

def generate_operating_profit_commentary(operating_profit_data):
    """Generate commentary for operating profit and net profit section based on provided data"""
    try:
        # Configure API if not already done
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            configure_api()
            
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
            "response_mime_type": "text/plain",
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        
        # Create prompt for operating profit commentary
        operating_profit_prompt = create_operating_profit_commentary_prompt(operating_profit_data)
        
        # Generate commentary
        response = model.generate_content(operating_profit_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating operating profit commentary: {str(e)}")
        return " "
