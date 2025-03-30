import os
import google.generativeai as genai
from dotenv import load_dotenv
from .finance_calc import current_price
def configure_api():
    """Configure and authenticate the API"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API Key is not set. Please check the .env file.")
    genai.configure(api_key=api_key)

def create_analysis_prompt(balance_sheet, income_statement, profitability_analysis):
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

def create_nkg_analysis_prompt(balance_sheet, income_statement, profitability_analysis, current_price, profit_data=None):
    """Create the prompt specifically for NKG stock analysis"""
    
    # Extract profit indicators if provided
    profit_indicators = ""
    if profit_data and len(profit_data) >= 6:
        loinhuanhdkd, loinhuantruothue, loinhuansautrue, yoy_loinhuanhdkd, yoy_loinhuantruothue, yoy_loinhuansautrue = profit_data
        profit_indicators = f"""
Chi tiết chỉ số lợi nhuận:
- Lợi nhuận từ hoạt động kinh doanh: {loinhuanhdkd:,.0f} đồng (YoY: {yoy_loinhuanhdkd:.2%})
- Lợi nhuận trước thuế: {loinhuantruothue:,.0f} đồng (YoY: {yoy_loinhuantruothue:.2%})
- Lợi nhuận sau thuế của cổ đông công ty mẹ: {loinhuansautrue:,.0f} đồng (YoY: {yoy_loinhuansautrue:.2%})
"""
    
    return f""" 
Bạn là một chuyên gia phân tích tài chính chuyên về phân tích cơ bản cổ phiếu ngành thép. Hãy đánh giá rủi ro và triển vọng đầu tư của Công ty Cổ phần Thép Nam Kim (mã cổ phiếu: NKG) dựa trên thông tin ngành thép và vị thế của công ty.
Giữ văn phong chuyên nghiệp và báo cáo dưới 300 từ.

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

Yêu cầu phân tích:

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

Định dạng đầu ra cần tuân thủ:
1. Bắt đầu phân tích với tiêu đề "**Định giá cập nhật với khuyến nghị MUA, giá mục tiêu dài hạn**"
2. Nội dung phải súc tích, logic, tổng cộng không quá 300 từ
3. Có kết luận rõ ràng về tiềm năng đầu tư cổ phiếu NKG
4. TUYỆT ĐỐI PHẢI TIẾT KIỆM SỐ TRANG SỬ DỤNG. Viết các nội dung gần với nhau nhất có thể.
5. KHÔNG ĐƯỢC XUỐNG DÒNG 2 LẦN TRONG MỌI TÌNH HUỐNG.
6. Tuyệt đối không bắt đầu các mục với ký hiệu "**" và "*".
7. Viết phải thật sự chuyên nghiệp giống như một người phân tích tài chính chuyên nghiệp.
"""

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
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction="Chatbot này sẽ hoạt động như một broker chứng khoán chuyên nghiệp..."
    )

    try:
        # Use custom prompt if provided, otherwise check for NKG-specific prompt
        if custom_prompt:
            prompt = custom_prompt
        elif symbol == "NKG" and balance_sheet and income_statement and profitability_analysis:
            # Import loinhuankinhdoanh_p2 here to avoid circular imports
            from .finance_calc import loinhuankinhdoanh_p2, current_price
            
            # Get profit data for NKG
            try:
                profit_data = loinhuankinhdoanh_p2("NKG")
                prompt = create_nkg_analysis_prompt(
                    balance_sheet, 
                    income_statement, 
                    profitability_analysis,
                    current_price("NKG"),
                    profit_data
                )
            except Exception as e:
                print(f"Error getting profit data for NKG: {str(e)}")
                # Fallback to the original function without profit data
                prompt = create_nkg_analysis_prompt(
                    balance_sheet, 
                    income_statement, 
                    profitability_analysis,
                    current_price("NKG")
                )
        elif balance_sheet and income_statement and profitability_analysis:
            prompt = create_analysis_prompt(balance_sheet, income_statement, profitability_analysis)
        else:
            prompt = "Provide a general financial market analysis and investment recommendations."
            
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API error: {str(e)}")
        return f"Error generating analysis: {str(e)}"
