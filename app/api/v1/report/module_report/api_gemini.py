import os
import google.generativeai as genai
from dotenv import load_dotenv

def configure_api():
    """Configure and authenticate the API"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API Key is not set. Please check the .env file.")
    genai.configure(api_key=api_key)

def create_analysis_prompt(symbol,finacne_data_tttc):
    """Create the prompt for financial analysis"""
    return f""" 
Bạn là một chuyên gia phân tích tài chính chuyên về phân tích cơ bản cổ phiếu về công ty Thép Nam Kim với mã chứng khoán là NKG. Hãy đánh giá rủi ro và triển vọng đầu tư của mã cổ phiếu dựa trên các chỉ số tài chính và thông tin sau.
Giữ văn phong chuyên nghiệp và báo cáo dưới 300 từ.
- Tìm số liệu trên mạng để nói
Cho các dữ liệu báo cáo tài chính sau: 
- viết sao cho chuyên nghiệp như là một nhà phân tích tài chính chuyên nghiệp.

Yêu cầu phân tích:

- GIỚI THIỆU VỀ CÔNG TY:
Một đoạn văn dưới 200 từ, giới thiệu tổng quan về công ty, ngành nghề kinh doanh, vị thế trong ngành, và những điểm nổi bật về mô hình kinh doanh của công ty Thép Nam Kim. Hãy viết đoạn văn này thật chuyên nghiệp.

- TÌNH HÌNH TÀI CHÍNH HIỆN NAY:
+ Không quá 200 từ
+ Đưa ra được ([+/-]% YoY, [+/-]% QoQ) cho người dùng
+ Đoạn văn dưới 200 từ, phân tích tình hình tài chính hiện tại của công ty, tập trung vào các số liệu cụ thể theo định dạng sau:
+ Trong quý gần nhất, [tên công ty] ghi nhận doanh thu thuần đạt [X] tỷ đồng ([+/-]% YoY, [+/-]% QoQ) do [lý do]. Sản lượng [sản phẩm chính] đạt [X] tấn/đơn vị ([+/-]% QoQ). LNST đạt [X] tỷ đồng ([+/-]% YoY, [+/-]% QoQ) do [lý do, đặc biệt là ảnh hưởng của chi phí tài chính, chi phí lãi vay, biến động tỷ giá...].
+ Tính cả năm [năm gần nhất], [tên công ty] đạt doanh thu thuần [X] tỷ đồng ([+/-]% YoY), sản lượng [sản phẩm chính] đạt [X] đơn vị ([+/-]% YoY). Biên lợi nhuận gộp tăng/giảm từ [X]% lên/xuống [Y]% YoY, LNST đạt [X] tỷ đồng ([+/-]% YoY), [so sánh với kế hoạch năm]. Tập trung vào các chỉ số này, bắt buộc phải đưa chỉ số này ra cho người dùng.

Đánh giá tình hình nợ vay và khả năng thanh toán của công ty, cũng như triển vọng tăng trưởng trong thời gian tới.

Định dạng đầu ra mong muốn: 
- Đoạn văn nhận xét súc tích, logic (khoảng bé hơn 300 từ)
- Có kết luận rõ ràng về tiềm năng đầu tư của mã cổ phiếu.
- TUYỆT ĐỐI PHẢI TIẾT KIỆM SỐ TRANG SỬ DỤNG. HÃY GHI CÁC NỘI DUNG GẦN VỚI NHAU NHẤT CÓ THỂ, TRÁNH TÌNH TRẠNG VIẾT NỘI DUNG VÀO FILE MÀ MỖI CÁC NỘI DUNG DÙNG 1 TRẠNG. TIẾT KIỆM NHẤT CÓ THỂ NHÉ.
- KHÔNG ĐƯỢC XUỐNG DÒNG 2 LẦN TRONG MỌI TÌNH HUỐNG.
- PHẢI SỬ DỤNG 2 TIÊU ĐỀ MARKDOWN: **GIỚI THIỆU VỀ CÔNG TY** và **TÌNH HÌNH TÀI CHÍNH HIỆN NAY** trong nội dung phân tích, không được thay đổi.
"""
def create_analysis_prompt_NKG_page1(symbol,finacne_data_tttc):
    """Create the prompt for financial analysis"""
    return f""" 
Bạn là một chuyên gia phân tích tài chính chuyên về phân tích cơ bản cổ phiếu về công ty Thép Nam Kim với mã chứng khoán là NKG. Hãy đánh giá rủi ro và triển vọng đầu tư của mã cổ phiếu dựa trên các chỉ số tài chính và thông tin sau.
Cho các dữ liệu báo cáo tài chính sau: 
- viết sao cho chuyên nghiệp như là một nhà phân tích tài chính chuyên nghiệp.

Yêu cầu phân tích:

- Định giá cập nhật với khuyến nghị MUA:
+ Dựa vào thông tin sau đây giới thiệu về công ty Thép Nam Kim không quá 3 câu: CTCP Thép Nam Kim (NKG) là top 3 doanh nghiệp lớn nhất trong lĩnh vực tôn mạ (chiếm 11% thị phần
trong nước) và xuất khẩu đến hơn 50 quốc gia trên toàn cầu (chủ yếu tại khu vực Bắc Mỹ và Châu Âu). 

- TÌNH HÌNH TÀI CHÍNH HIỆN NAY:
+ Không quá 150 từ
+ Đưa ra được ([+/-]% YoY, [+/-]% QoQ) cho người dùng
+ Đoạn văn dưới 200 từ, phân tích tình hình tài chính hiện tại của công ty, tập trung vào các số liệu cụ thể theo định dạng sau:
+ Trong quý gần nhất, [tên công ty] ghi nhận doanh thu thuần đạt [X] tỷ đồng ([+/-]% YoY, [+/-]% QoQ) do [lý do]. Sản lượng [sản phẩm chính] đạt [X] tấn/đơn vị ([+/-]% QoQ). LNST đạt [X] tỷ đồng ([+/-]% YoY, [+/-]% QoQ) do [lý do, đặc biệt là ảnh hưởng của chi phí tài chính, chi phí lãi vay, biến động tỷ giá...].
+ Tính cả năm [năm gần nhất], [tên công ty] đạt doanh thu thuần [X] tỷ đồng ([+/-]% YoY), sản lượng [sản phẩm chính] đạt [X] đơn vị ([+/-]% YoY). Biên lợi nhuận gộp tăng/giảm từ [X]% lên/xuống [Y]% YoY, LNST đạt [X] tỷ đồng ([+/-]% YoY), [so sánh với kế hoạch năm]. Tập trung vào các chỉ số này, bắt buộc phải đưa chỉ số này ra cho người dùng.

Đánh giá tình hình nợ vay và khả năng thanh toán của công ty, cũng như triển vọng tăng trưởng trong thời gian tới.

Định dạng đầu ra mong muốn: 
- Đoạn văn nhận xét súc tích, logic (khoảng bé hơn 300 từ)
- Có kết luận rõ ràng về tiềm năng đầu tư của mã cổ phiếu.
- TUYỆT ĐỐI PHẢI TIẾT KIỆM SỐ TRANG SỬ DỤNG. HÃY GHI CÁC NỘI DUNG GẦN VỚI NHAU NHẤT CÓ THỂ, TRÁNH TÌNH TRẠNG VIẾT NỘI DUNG VÀO FILE MÀ MỖI CÁC NỘI DUNG DÙNG 1 TRẠNG. TIẾT KIỆM NHẤT CÓ THỂ NHÉ.
- KHÔNG ĐƯỢC XUỐNG DÒNG 2 LẦN TRONG MỌI TÌNH HUỐNG.
- PHẢI SỬ DỤNG 2 TIÊU ĐỀ MARKDOWN: **GIỚI THIỆU VỀ CÔNG TY** và **TÌNH HÌNH TÀI CHÍNH HIỆN NAY** trong nội dung phân tích, không được thay đổi.
"""
def generate_financial_analysis(symbol,finacne_data_tttc):
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
        system_instruction="Bạn là một chuyên gia phân tích chứng khoán viết báo cáo phân tích cổ phiếu. KHÔNG BAO GIỜ bắt đầu với lời chào như 'Chào bạn' hoặc 'Tôi là chuyên gia phân tích'. KHÔNG BAO GIỜ giới thiệu bản thân hoặc nói về việc bạn đang phân tích. Phản hồi của bạn phải bắt đầu trực tiếp bằng tiêu đề '**GIỚI THIỆU VỀ CÔNG TY**' và sau đó là nội dung phân tích. TUYỆT ĐỐI KHÔNG có bất kỳ đoạn văn nào trước tiêu đề đầu tiên."
    )

    try:
        if finacne_data_tttc and symbol:
            prompt = create_analysis_prompt_NKG_page1(symbol,finacne_data_tttc)
        else:
            prompt = "Provide a general financial market analysis and investment recommendations."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API error: {str(e)}")
        return f"Error generating analysis: {str(e)}"
