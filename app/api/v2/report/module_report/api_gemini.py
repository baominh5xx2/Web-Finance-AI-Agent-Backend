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

Thông tin ngành thép: Ngành thép Việt Nam chịu ảnh hưởng bởi giá nguyên liệu đầu vào (quặng sắt, thép phế), chi phí năng lượng, biến động tỷ giá và cạnh tranh từ thép Trung Quốc. 
Nam Kim là một trong những nhà sản xuất tôn mạ hàng đầu Việt Nam, có thế mạnh về thép mạ màu và thép mạ kẽm, đồng thời có hoạt động xuất khẩu sang các thị trường như Bắc Mỹ, châu Âu và Đông Nam Á. 
Việc Bộ Công Thương gia hạn thuế tôn mạ nhập khẩu từ Hàn Quốc và Trung Quốc đến T10/2029 sẽ giảm bớt áp lực cạnh tranh, giúp doanh nghiệpmởrộng thịphần nội địa trong bối cảnh: (1) Thịtrường Bất động 
sản ấm lên, (2) Chính phủ đẩy mạnh giải ngân đầu tư công, (3) Chính phủ tạo điều kiện cho vay với lãi suất thấp để thúc đẩy nền kinh tế.

Cho các dữ liệu báo cáo tài chính của NKG (Nam Kim Steel):  
Bảng cân đối kế toán (Balance Sheet):
{balance_sheet}  
Báo cáo thu nhập (Income Statement):
{income_statement}  
Phân tích khả năng sinh lời (Profitability Analysis):
{profitability_analysis} 
{profit_indicators}


Yêu cầu phân tích 4 PHẦN LỚN SAU:

**TÌNH HÌNH TÀI CHÍNH HIỆN NAY**
Phân tích ngắn gọn và cố gắng cập nhật và so sánh năm 2024 và 2023 về:
- Bắt buộc phải tham khảo chỉ số YoY của công ty thép nam kim từ các dữ liệu báo cáo tài chính và chỉ số lợi nhuận được cung cấp.
- Tập trung phân tích biến động lợi nhuận từ hoạt động kinh doanh, lợi nhuận trước thuế và lợi nhuận sau thuế theo số liệu YoY đã cung cấp.
- Doanh thu và lợi nhuận: Biến động và triển vọng phục hồi
- Biên lợi nhuận: Yếu tố ảnh hưởng từ giá nguyên liệu và giá bán thép
- Tình hình thanh khoản: Đánh giá khả năng thanh toán ngắn hạn
- Hiệu quả hoạt động và quản trị chi phí: Đánh giá khả năng kiểm soát chi phí
- Phải đưa ra được số liệu cụ thể.
- Bình luận các chỉ số dựa trên hiểu biết của bạn và các chỉ số đã cung cấp.
- Không quá 200 từ

**THÔNG TIN GIAO DỊCH CÔNG TY THÉP NAM KIM**
- Đây là thông tin mới nhất về công ty thép nam kim: {news}.
- Có thể tìm các tin tức mới nhất trên google để nói về công ty thép nam kim.
- Hãy viết về một đoạn văn giới thiệu thông tin mới nhất về công ty thép nam kim với mã cổ phiếu là NKG. Tìm các chỉ số mới nhất để đánh giá tình hình hiện tại của công ty. không quá 300 từ

**RỦI RO VÀ TRIỂN VỌNG ĐẦU TƯ**
Hãy đánh giá rủi ro và triển vọng đầu tư của mã cổ phiếu NKG, tập trung vào các yếu tố sau:
- Vị thế doanh nghiệp trong ngành thép mạ Việt Nam
- Hiệu quả vận hành nhà máy và chi phí sản xuất
- Tỷ suất lợi nhuận so với các đối thủ cùng ngành
- Khả năng chống chịu biến động giá nguyên liệu đầu vào
- Tiềm năng tăng trưởng từ xuất khẩu thép. Có thể tham khảo thêm thông tin như sau để đánh giá : (1) Chính sách bảo hộ ngành tôn mạ được gia hạn trong bối cảnh nhu cầu nội địa hồi phục; (2) Giá thép hồi phục giúp BLN cải thiện; (3)Nam Kim Phú Mỹ là động lực dài hạn

**ĐÁNH GIÁ TÁC ĐỘNG CỦA THUẾ LÊN NKG**
Tôi cung cấp cho bạn các thông tin sau:
- Thuế CBPG HRC của Việt Nam áp lên thép nhập khẩu từ Trung Quốc
  Ngày 21/2/2025, Bộ Công Thương đã áp dụng thuế CBPG tạm thời đối với sản phẩm HRC nhập 
khẩu từ Trung Quốc, với mức thuế dao động từ 19.38% đến 27.83%, có hiệu lực sau 15 ngày kể
từ ngày ban hành và kéo dài trong 120 ngày. 
  Hiện nay, NKG phụ thuộc phần lớn nguồn cung HRC từ Trung Quốc, phần còn lại là mua từ HPG 
hoặc Formosa. Việc thuế này được áp dụng có thể khiến chi phí nguyên vật liệu đầu vào của 
NKG tăng lên. Song, chúng tôi kỳ vọng doanh nghiệp sẽ tối ưu hóa chi phí, đa dạng hóa nguồn 
cung HRC và điều chỉnh giá đầu ra linh hoạt để bảo vệ được biên lợi nhuận trong thời gian tới.
- Thuế nhập khẩu của Mỹ đối với thép và nhôm 
  Vào ngày 10/2/2025, Tổng thống Mỹ Donald Trump đã ký sắc lệnh áp thuế 25% đối với tất
cả các mặt hàng thép và nhôm nhập khẩu vào Mỹ, không có ngoại lệ hay miễn trừ. Mức thuế
này sẽ có hiệu lực từ ngày 4/3/2025. 
  Đối với Việt Nam, mặt hàng thép nhập khẩu vào Mỹ đã bị đánh thuế 25% theo Mục 232 kể từ
tháng 3/2018. Trong khi đó, các đồng minh của Mỹ được miễn trừ thuế này bao gồm Argentina, 
Brazil, Canada, EU, Hàn Quốc, Nhật Bản và Vương quốc Anh. Hiện tại, tất cả đối tác xuất khẩu 
thép vào Mỹ đều phải đối mặt với cùng một mức thuế. Trong năm 2024, tỷ trọng thép Việt Nam 
xuất khẩu đi Mỹ chỉ chiếm tỷ trọng 14% tổng sản lượng. Với riêng NKG, tỷ trọng thép xuất khẩu 
sang Mỹ chiếm đến 15% tổng sản lượng tiêu thụ. Chúng tôi cho rằng chính sách thuế mới này sẽ
tạo cơ hội gia tăng sản lượng xuất khẩu sang Mỹ cho NKG khi cạnh tranh trở nên công bằng hơn 
giữa các nước. 
- Thuế chống trợ cấp của Mỹ đối với sản phẩm tôn mạ chống ăn mòn 
Vào ngày 25/09/2024, Bộ Thương mại Mỹ (DOC) đã chính thức tiến hành các cuộc điều tra để
áp thuế chống trợ cấp đối với sản phẩm tôn mạ chống ăn mòn (CORE) nhập khẩu từ Việt Nam
(cũng như từ Brazil, Canada và Mexico). Kết quả cuối cùng sẽ được công bố vào ngày 17/06/2025, 
quyết định sẽ được đưa ra vào ngày 01/08/2025 và lệnh có hiệu lực từ ngày 08/08/20225. Trong 
trường hợp bị đánh thêm thuế chống trợ cấp, các doanh nghiệp xuất khẩu vào Mỹ lớn như NKG 
sẽ bị tác động.
Hãy viết đoạn văn khoảng 200 từ, tóm gọn lại các thông tin trên và đánh giá tác động của thuế lên NKG.

Định dạng đầu ra cần tuân thủ:
0. Không cần viết kết luận cuối.
1. Bắt đầu phân tích với tiêu đề "**Định giá cập nhật với khuyến nghị MUA, giá mục tiêu dài hạn**"
2. Nội dung phải súc tích, logic, tổng cộng không quá 600 từ và viết thành các đoạn văn liền mạch nhau.
3. Có kết luận rõ ràng về tiềm năng đầu tư cổ phiếu NKG
4. TUYỆT ĐỐI PHẢI TIẾT KIỆM SỐ TRANG SỬ DỤNG. Viết các nội dung gần với nhau nhất có thể.
5. KHÔNG ĐƯỢC XUỐNG DÒNG 2 LẦN TRONG MỌI TÌNH HUỐNG.
6. Tuyệt đối không bắt đầu các mục với ký hiệu "**" và "*". Không bắt đầu đoạn văn với cụm từ "Dựa trên dữ liệu đưa ra", đi thẳng vào nội dung phân tích luôn.
7. Viết phải thật sự chuyên nghiệp giống như một người phân tích tài chính chuyên nghiệp.
8. Phải có số liệu cụ thể trong các phân tích.  
"""

def create_revenue_commentary_prompt(revenue_data):
    data = {
  "doanh_thu_thuan": "20707.52",
  "yoy_doanh_thu": "+11.2%",
  "doanh_thu_thuan_2025F": "23928.46",
  "yoy_doanh_thu_2025F": "+15.6%",
  "loi_nhuan_gop": "1831.77",
  "yoy_loi_nhuan_gop": "+64.7%",
  "loi_nhuan_gop_2025F": "2207.03",
  "yoy_loi_nhuan_gop_2025F": "+20.5%",
  "chi_phi_tai_chinh": "-477.10",
  "yoy_chi_phi_tai_chinh": "+12.0%",
  "chi_phi_tai_chinh_2025F": "-544.48",
  "yoy_chi_phi_tai_chinh_2025F": "+14.1%",
  "chi_phi_ban_hang": "-1017.60",
  "yoy_chi_phi_ban_hang": "+67.1%",
  "chi_phi_ban_hang_2025F": "-1420.55",
  "yoy_chi_phi_ban_hang_2025F": "+39.6%",
  "chi_phi_quan_ly": "-120.24",
  "yoy_chi_phi_quan_ly": "-7.7%",
  "chi_phi_quan_ly_2025F": "-128.60",
  "yoy_chi_phi_quan_ly_2025F": "+6.9%",
  "loi_nhuan_hdkd": "557.45",
  "yoy_loi_nhuan_hdkd": "+214.8%",
  "loi_nhuan_hdkd_2025F": "641.85",
  "yoy_loi_nhuan_hdkd_2025F": "+15.1%",
  "loi_nhuan_truoc_thue": "558.17",
  "yoy_loi_nhuan_truoc_thue": "+214.8%",
  "loi_nhuan_truoc_thue_2025F": "641.06",
  "yoy_loi_nhuan_truoc_thue_2025F": "+14.8%",
  "loi_nhuan_sau_thue": "453.01",
  "yoy_loi_nhuan_sau_thue": "+285.8%",
  "loi_nhuan_sau_thue_2025F": "504.17",
  "yoy_loi_nhuan_sau_thue_2025F": "+11.3%",
}
    """Create a prompt for revenue commentary"""
    return f"""
Bạn là một chuyên gia phân tích tài chính. 
Cho dữ liệu tài chính đã tính toán sẵn
{data}
Hãy viết bình luận chi tiết về DOANH THU của công ty dựa trên dữ liệu sau:
- Doanh thu thuần: {data.get("doanh_thu_thuan", 'N/A')} tỷ VND
- Tăng trưởng doanh thu so với năm trước: {data.get("yoy_doanh_thu", 'N/A')}
- Doanh thu dự kiến năm tới: {data.get("doanh_thu_thuan_2025F", 'N/A')} tỷ VND
- Tăng trưởng dự kiến năm tới: {data.get("yoy_doanh_thu_2025F", 'N/A')}

Hãy viết một đoạn văn ngắn gọn (3-4 câu) đánh giá sâu về tình hình doanh thu của công ty, tập trung vào phân tích doanh thu của công ty thép NKG trong kỳ báo cáo này. Doanh thu có tăng trưởng so với cùng kỳ năm trước không? Nếu có, hãy xác định nguyên nhân (tăng giá bán, tăng sản lượng tiêu thụ hay yếu tố khác). Nếu giảm, hãy chỉ ra các nguyên nhân chính.
Yêu cầu:
- Không giới thiệu, chỉ trả lời trực tiếp
- Không dùng từ "theo dữ liệu" hoặc "dựa trên thông tin được cung cấp"
- Viết với giọng điệu tự tin, chuyên nghiệp của một chuyên gia phân tích tài chính

"""

def create_gross_profit_commentary_prompt(gross_profit_data):
    """Create a prompt for gross profit commentary, focusing only on gross profit margin"""
    data = {
      "doanh_thu_thuan": "20707.52",
      "yoy_doanh_thu": "+11.2%",
      "doanh_thu_thuan_2025F": "23928.46",
      "yoy_doanh_thu_2025F": "+15.6%",
      "loi_nhuan_gop": "1831.77",
      "yoy_loi_nhuan_gop": "+64.7%",
      "loi_nhuan_gop_2025F": "2207.03",
      "yoy_loi_nhuan_gop_2025F": "+20.5%",
      "loi_nhuan_hdkd": "557.45",
      "yoy_loi_nhuan_hdkd": "+214.8%",
      "loi_nhuan_hdkd_2025F": "641.85",
      "yoy_loi_nhuan_hdkd_2025F": "+15.1%",
      "loi_nhuan_truoc_thue": "558.17",
      "yoy_loi_nhuan_truoc_thue": "+214.8%",
      "loi_nhuan_truoc_thue_2025F": "641.06",
      "yoy_loi_nhuan_truoc_thue_2025F": "+14.8%",
      "loi_nhuan_sau_thue": "453.01",
      "yoy_loi_nhuan_sau_thue": "+285.8%",
      "loi_nhuan_sau_thue_2025F": "504.17",
      "yoy_loi_nhuan_sau_thue_2025F": "+11.3%",
    }
    
    # Tính biên lợi nhuận gộp nếu có dữ liệu doanh thu và lợi nhuận gộp
    gross_margin = ""
    try:
        doanh_thu = float(data.get("doanh_thu_thuan", "0").replace(",", ""))
        loi_nhuan_gop = float(data.get("loi_nhuan_gop", "0").replace(",", ""))
        if doanh_thu > 0:
            gross_margin = f"Biên lợi nhuận gộp năm 2024: {(loi_nhuan_gop/doanh_thu)*100:.2f}%"
    except:
        gross_margin = ""
    
    return f"""
Bạn là một chuyên gia phân tích tài chính. 
Cho dữ liệu tài chính đã tính toán sẵn:
- Lợi nhuận gộp: {data.get("loi_nhuan_gop", 'N/A')} tỷ VND
- Tăng trưởng lợi nhuận gộp so với năm trước: {data.get("yoy_loi_nhuan_gop", 'N/A')}
- Lợi nhuận gộp dự kiến năm tới: {data.get("loi_nhuan_gop_2025F", 'N/A')} tỷ VND
- Tăng trưởng lợi nhuận gộp dự kiến năm tới: {data.get("yoy_loi_nhuan_gop_2025F", 'N/A')}
- Doanh thu thuần: {data.get("doanh_thu_thuan", 'N/A')} tỷ VND
- Tăng trưởng doanh thu so với năm trước: {data.get("yoy_doanh_thu", 'N/A')}
{gross_margin}

Hãy viết một đoạn văn ngắn gọn (3-4 câu) đánh giá sâu về tình hình lợi nhuận gộp của công ty thép NKG trong năm 2024. Phân tích:
1. Lợi nhuận gộp có xu hướng tăng hay giảm so với năm trước
2. Biên lợi nhuận gộp (tỷ lệ lợi nhuận gộp/doanh thu) là bao nhiêu và thay đổi ra sao
3. Các yếu tố ảnh hưởng đến sự thay đổi lợi nhuận gộp (giá nguyên vật liệu, giá bán, cơ cấu sản phẩm, hiệu quả sản xuất)
4. Đưa ra nhận định về triển vọng lợi nhuận gộp năm 2025

Yêu cầu quan trọng:
- TUYỆT ĐỐI KHÔNG NHẮC ĐẾN CHI PHÍ TÀI CHÍNH, CHI PHÍ BÁN HÀNG HOẶC CHI PHÍ QUẢN LÝ
- CHỈ TẬP TRUNG VÀO LỢI NHUẬN GỘP, BIÊN LỢI NHUẬN GỘP VÀ NGUYÊN NHÂN BIẾN ĐỘNG
- Không giới thiệu, chỉ trả lời trực tiếp
- Không dùng từ "theo dữ liệu" hoặc "dựa trên thông tin được cung cấp"
- Viết với giọng điệu tự tin, chuyên nghiệp của một chuyên gia phân tích tài chính
- Tuyệt đối không viết quá 100 từ
"""

def create_operating_profit_commentary_prompt(operating_profit_data):
    """Create a prompt for operating profit and net profit commentary"""
    data = {
      "doanh_thu_thuan": "20707.52",
      "yoy_doanh_thu": "+11.2%",
      "doanh_thu_thuan_2025F": "23928.46",
      "yoy_doanh_thu_2025F": "+15.6%",
      "loi_nhuan_gop": "1831.77",
      "yoy_loi_nhuan_gop": "+64.7%",
      "loi_nhuan_gop_2025F": "2207.03",
      "yoy_loi_nhuan_gop_2025F": "+20.5%",
      "chi_phi_tai_chinh": "-477.10",
      "yoy_chi_phi_tai_chinh": "+12.0%",
      "chi_phi_tai_chinh_2025F": "-544.48",
      "yoy_chi_phi_tai_chinh_2025F": "+14.1%",
      "chi_phi_ban_hang": "-1017.60",
      "yoy_chi_phi_ban_hang": "+67.1%",
      "chi_phi_ban_hang_2025F": "-1420.55",
      "yoy_chi_phi_ban_hang_2025F": "+39.6%",
      "chi_phi_quan_ly": "-120.24",
      "yoy_chi_phi_quan_ly": "-7.7%",
      "chi_phi_quan_ly_2025F": "-128.60",
      "yoy_chi_phi_quan_ly_2025F": "+6.9%",
      "loi_nhuan_hdkd": "557.45",
      "yoy_loi_nhuan_hdkd": "+214.8%",
      "loi_nhuan_hdkd_2025F": "641.85",
      "yoy_loi_nhuan_hdkd_2025F": "+15.1%",
      "loi_nhuan_truoc_thue": "558.17",
      "yoy_loi_nhuan_truoc_thue": "+214.8%",
      "loi_nhuan_truoc_thue_2025F": "641.06",
      "yoy_loi_nhuan_truoc_thue_2025F": "+14.8%",
      "loi_nhuan_sau_thue": "453.01",
      "yoy_loi_nhuan_sau_thue": "+285.8%",
      "loi_nhuan_sau_thue_2025F": "504.17",
      "yoy_loi_nhuan_sau_thue_2025F": "+11.3%",
    }
    
    # Tính biên lợi nhuận hoạt động kinh doanh nếu có dữ liệu
    operating_margin = ""
    try:
        doanh_thu = float(data.get("doanh_thu_thuan", "0").replace(",", ""))
        loi_nhuan_hdkd = float(data.get("loi_nhuan_hdkd", "0").replace(",", ""))
        if doanh_thu > 0:
            operating_margin = f"Biên lợi nhuận hoạt động kinh doanh năm 2024: {(loi_nhuan_hdkd/doanh_thu)*100:.2f}%"
    except:
        operating_margin = ""
    
    return f"""
Bạn là một chuyên gia phân tích tài chính. 
Cho dữ liệu tài chính đã tính toán sẵn:
- Lợi nhuận hoạt động kinh doanh: {data.get("loi_nhuan_hdkd", 'N/A')} tỷ VND
- Tăng trưởng lợi nhuận HĐKD so với năm trước: {data.get("yoy_loi_nhuan_hdkd", 'N/A')}
- Lợi nhuận HĐKD dự kiến năm tới: {data.get("loi_nhuan_hdkd_2025F", 'N/A')} tỷ VND
- Tăng trưởng lợi nhuận HĐKD dự kiến năm tới: {data.get("yoy_loi_nhuan_hdkd_2025F", 'N/A')}
- Lợi nhuận trước thuế: {data.get("loi_nhuan_truoc_thue", 'N/A')} tỷ VND
- Tăng trưởng lợi nhuận trước thuế so với năm trước: {data.get("yoy_loi_nhuan_truoc_thue", 'N/A')}
- Lợi nhuận sau thuế: {data.get("loi_nhuan_sau_thue", 'N/A')} tỷ VND
- Tăng trưởng lợi nhuận sau thuế so với năm trước: {data.get("yoy_loi_nhuan_sau_thue", 'N/A')}
{operating_margin}

Hãy viết một đoạn văn ngắn gọn (3-4 câu) đánh giá sâu về tình hình lợi nhuận hoạt động kinh doanh của công ty thép NKG trong năm 2024. Phân tích:
1. Lợi nhuận HĐKD có xu hướng tăng hay giảm so với năm trước, mức tăng/giảm đáng kể không
2. Biên lợi nhuận HĐKD (tỷ lệ lợi nhuận HĐKD/doanh thu) thay đổi ra sao
3. Mối quan hệ giữa lợi nhuận HĐKD, lợi nhuận trước thuế và lợi nhuận sau thuế
4. Đưa ra nhận định về triển vọng lợi nhuận hoạt động kinh doanh năm 2025

Yêu cầu quan trọng:
- CHỈ TẬP TRUNG VÀO LỢI NHUẬN HOẠT ĐỘNG KINH DOANH VÀ BIÊN LỢI NHUẬN HOẠT ĐỘNG
- Không giới thiệu, chỉ trả lời trực tiếp
- Không dùng từ "theo dữ liệu" hoặc "dựa trên thông tin được cung cấp"
- Viết với giọng điệu tự tin, chuyên nghiệp của một chuyên gia phân tích tài chính
"""

def create_cost_of_goods_sold_commentary_prompt(data):
    datta = {
  "doanh_thu_thuan": "20707.52",
  "yoy_doanh_thu": "+11.2%",
  "doanh_thu_thuan_2025F": "23928.46",
  "yoy_doanh_thu_2025F": "+15.6%",
  "loi_nhuan_gop": "1831.77",
  "yoy_loi_nhuan_gop": "+64.7%",
  "loi_nhuan_gop_2025F": "2207.03",
  "yoy_loi_nhuan_gop_2025F": "+20.5%",
  "chi_phi_tai_chinh": "-477.10",
  "yoy_chi_phi_tai_chinh": "+12.0%",
  "chi_phi_tai_chinh_2025F": "-544.48",
  "yoy_chi_phi_tai_chinh_2025F": "+14.1%",
  "chi_phi_ban_hang": "-1017.60",
  "yoy_chi_phi_ban_hang": "+67.1%",
  "chi_phi_ban_hang_2025F": "-1420.55",
  "yoy_chi_phi_ban_hang_2025F": "+39.6%",
  "chi_phi_quan_ly": "-120.24",
  "yoy_chi_phi_quan_ly": "-7.7%",
  "chi_phi_quan_ly_2025F": "-128.60",
  "yoy_chi_phi_quan_ly_2025F": "+6.9%",
  "loi_nhuan_hdkd": "557.45",
  "yoy_loi_nhuan_hdkd": "+214.8%",
  "loi_nhuan_hdkd_2025F": "641.85",
  "yoy_loi_nhuan_hdkd_2025F": "+15.1%",
  "loi_nhuan_truoc_thue": "558.17",
  "yoy_loi_nhuan_truoc_thue": "+214.8%",
  "loi_nhuan_truoc_thue_2025F": "641.06",
  "yoy_loi_nhuan_truoc_thue_2025F": "+14.8%",
  "loi_nhuan_sau_thue": "453.01",
  "yoy_loi_nhuan_sau_thue": "+285.8%",
  "loi_nhuan_sau_thue_2025F": "504.17",
  "yoy_loi_nhuan_sau_thue_2025F": "+11.3%",
}
    """Create a prompt for cost of goods sold commentary"""
    return f"""
Bạn là một chuyên gia phân tích tài chính. Hãy viết bình luận ngắn gọn về giá vốn hàng bán của công ty dựa trên dữ liệu sau:

- Doanh thu thuần: {datta.get('doanh_thu_thuan', 'N/A')} tỷ VND
- Lợi nhuận gộp: {datta.get('loi_nhuan_gop', 'N/A')} tỷ VND
- Tăng trưởng doanh thu so với năm trước: {datta.get('yoy_doanh_thu', 'N/A')}
- Tăng trưởng lợi nhuận gộp so với năm trước: {datta.get('yoy_loi_nhuan_gop', 'N/A')}

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
                "Lợi nhuận gộp": "biên lợi nhuận gộp, nguyên nhân thay đổi, và triển vọng. CHỈ NÓI VỀ LỢI NHUẬN GỘP, không nói đến chi phí bán hàng, chi phí quản lý, chi phí tài chính",
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

def generate_valuation_commentary(company_code, valuation_data, peer_data=None):
    """Generate commentary for valuation section based on provided data"""
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
        data1 = {
            "Công ty": [
                "Công ty Cổ phần Thép Nam Kim (Hiện tại)",
                "Tổng Công ty Thép Việt Nam - Công ty Cổ phần",
                "Công ty Cổ phần Tôn Đông Á",
                "Công ty Cổ phần Quốc tế Sơn Hà",
                "Công ty Cổ phần Ống thép Việt - Đức VG PIPE"
            ],
            "P/E": [10.77, 20.00, 8.26, 30.38, 14.92],
            "Vốn hóa (tỷ)": [0.20, 0.24, 0.12, 0.10, 0.07],
            "Tăng trưởng Doanh thu (%)": [11.20, 19.78, 9.69, 16.76, -2.85],
            "Tăng trưởng EPS (%)": [221.53, -211.16, 20.55, 375.86, 80.18],
            "ROA (%)": [3.52, 1.18, 2.79, 0.92, 4.60],
            "ROE (%)": [8.02, 3.49, 9.20, 4.41, 10.64]
        }
        data2 = {
            "P/E mục tiêu": [15.59],
            "EPS mục tiêu": [1537.53],
            "Giá mục tiêu (VND)": [23972],
            "Giá hiện tại (VND)": [15200],
            "Tiềm năng tăng giảm giá(%)": [59.28],
        }

        # Format peer data if available
        peers_info = ""
        if peer_data and len(peer_data) > 0:
            peers_info = "Thông tin doanh nghiệp cùng ngành:\n"
            for peer in peer_data:
                peers_info += f"- {peer.get('company_name', 'N/A')}: P/E {peer.get('pe', 'N/A')}, Vốn hóa {peer.get('market_cap', 'N/A')} tỷ\n"
        
        # Format data1 and data2 as tables for better presentation
        data1_str = "Dữ liệu các công ty ngành thép:\n"
        # Add header row
        headers = list(data1.keys())
        for h in headers:
            data1_str += f"{h:<25}"
        data1_str += "\n"
        # Add data rows
        for i in range(len(data1["Công ty"])):
            for h in headers:
                data1_str += f"{data1[h][i]:<25}"
            data1_str += "\n"
        
        data2_str = "Dữ liệu mục tiêu và định giá:\n"
        # Add data in key-value format
        for k, v in data2.items():
            data2_str += f"{k}: {v[0]}\n"
        
        # Create prompt template
        valuation_prompt = """Bạn là một chuyên gia phân tích tài chính.
        Có các dữ liệu như sau:
        1. Dữ liệu các công ty ngành thép:
        {data1}
        2. Dữ liệu mục tiêu và định giá:
        {data2}
        3. Thông tin doanh nghiệp cùng ngành:
        {peers_info}
        Hãy viết một đoạn văn khoảng 200 từ :
        - Tóm tắt các chỉ số tài chính của các công ty ngành thép
        - So sánh các chỉ số tài chính của công ty NKG với các công ty khác trong ngành
        - Đưa ra nhận định về tiềm năng tăng trưởng của cổ phiếu NKG trong tương lai
        - Viết với giọng điệu tự tin, chuyên nghiệp của một chuyên gia phân tích tài chính
        """
        
        # Format the prompt with actual data
        formatted_prompt = valuation_prompt.format(
            data1=data1_str,
            data2=data2_str,
            peers_info=peers_info
        )
        
        # Generate commentary using the formatted prompt
        response = model.generate_content(formatted_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating valuation commentary: {str(e)}")
        return "Không thể tạo bình luận về định giá."

def create_valuation_commentary_prompt(company_code, valuation_data, peer_data=None):
    """Create prompt template for valuation commentary"""
    # This function returns an empty prompt template as requested
    # The user can fill this in later
    return """"""
