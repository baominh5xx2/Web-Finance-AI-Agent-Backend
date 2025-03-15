import os
import datetime
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, Frame, NextPageTemplate, PageTemplate, FrameBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen.canvas import Canvas
from .finance_calc import get_market_data, current_price
from vnstock import Vnstock

class PDFReport:
    def __init__(self):
        # Đăng ký font
        self.font_added = self._setup_fonts()
        self.styles = getSampleStyleSheet()
        
        # Sử dụng font DejaVuSans nếu đã đăng ký, nếu không thì dùng Helvetica
        title_font = 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'
        normal_font = 'DejaVuSans' if self.font_added else 'Helvetica'
        
        # Màu sắc chính
        self.blue_color = colors.HexColor('#0066CC')
        self.light_blue = colors.HexColor('#E6F0FA')
        self.grey_color = colors.HexColor('#F5F5F5')
        
        # Tạo style cho tiêu đề và nội dung
        self.styles.add(ParagraphStyle(
            name='TitleStyle',
            fontName=title_font,
            fontSize=14,
            textColor=colors.HexColor('#0A64F0'),
            alignment=TA_LEFT,
            spaceAfter=6*mm
        ))
        self.styles.add(ParagraphStyle(
            name='NormalVN',
            fontName=normal_font,
            fontSize=10,
            leading=12,
            alignment=TA_LEFT
        ))
        self.styles.add(ParagraphStyle(
            name='Header',
            fontName=title_font,
            fontSize=16,
            alignment=TA_RIGHT,
        ))
        
        # Styles theo mẫu báo cáo mới
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            fontName=title_font,
            fontSize=24,
            textColor=colors.white,
            alignment=TA_LEFT,
            leading=28
        ))
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            fontName=title_font,
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=6,
            leading=20,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName=title_font,
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            leading=16,
            spaceBefore=6,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name='PriceData',
            fontName=title_font,
            fontSize=16,
            alignment=TA_RIGHT,
        ))
        self.styles.add(ParagraphStyle(
            name='AnalysisTitle',
            fontName=title_font,
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=6,
        ))
        
        # Thêm style cho tiêu đề phân tích
        self.styles.add(ParagraphStyle(
            name='AnalysisHeading',
            fontName=title_font,
            fontSize=11,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=4,
            leading=14,
            borderWidth=0,
            backColor=None,
        ))
        
        # Thêm style cho giá hiện tại
        self.styles.add(ParagraphStyle(
            name='PriceRow',
            fontName=normal_font,
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
        ))
        
        # Style cho giá trị
        self.styles.add(ParagraphStyle(
            name='PriceValue',
            fontName=title_font,
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            leading=16,
        ))

        # Style cho toàn bộ cột bên trái
        self.styles.add(ParagraphStyle(
            name='LeftColumn',
            fontName=normal_font,
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
        ))
    
    def _process_markdown_content(self, text):
        """Xử lý nội dung markdown, phát hiện tiêu đề và nội dung"""
        if not text or not isinstance(text, str):
            return ("normal", text if text else "")
            
        # Kiểm tra chuỗi bắt đầu với **
        if text.startswith('**'):
            # Tìm vị trí kết thúc của dấu **
            end_pos = text.find('**', 2)
            if end_pos > 0:
                # Trích xuất tiêu đề
                heading_text = text[2:end_pos]
                # Lấy phần còn lại của văn bản (nếu có)
                remaining_text = text[end_pos+2:].strip()
                
                if remaining_text:
                    # Kết hợp tiêu đề và phần còn lại để không mất nội dung
                    return ("heading", heading_text + ": " + remaining_text)
                else:
                    return ("heading", heading_text)
        
        # Nếu không phải tiêu đề, hoặc định dạng không đúng
        return ("normal", text)
    
    def _setup_fonts(self):
        """Đăng ký font DejaVuSans có sẵn trong dự án"""
        try:
            # Tìm kiếm font DejaVuSans đã biết vị trí
            font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
            font_bold_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans-Bold.ttf')
            
            # Kiểm tra nếu file DejaVuSans.ttf tồn tại
            if os.path.exists(font_path):
                # Đăng ký font thường
                pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                print(f"Đã đăng ký font DejaVuSans từ {font_path}")
                
                # Nếu không có font đậm, tạo font đậm giả từ font thường
                if not os.path.exists(font_bold_path):
                    # Sử dụng font thường cho font đậm nếu không có font đậm
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path))
                    print("Sử dụng font thường cho font đậm vì không tìm thấy DejaVuSans-Bold.ttf")
                else:
                    # Đăng ký font đậm nếu có
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))
                    print(f"Đã đăng ký font DejaVuSans-Bold từ {font_bold_path}")
                
                # Đăng ký font family
                pdfmetrics.registerFontFamily(
                    'DejaVuSans',
                    normal='DejaVuSans',
                    bold='DejaVuSans-Bold'
                )
                
                return True
            else:
                print(f"Không tìm thấy file DejaVuSans.ttf tại {font_path}")
                return False
            
        except Exception as e:
            print(f"Lỗi khi đăng ký font: {str(e)}")
            return False
    
    def create_header(self, company_name, today=None):
        """Tạo header cho báo cáo"""
        if today is None:
            today = datetime.date.today()
        
        # Tạo các phần tử header
        elements = []
        elements.append(Paragraph(company_name, self.styles['Header']))
        elements.append(Paragraph(f"Document Date: {today.strftime('%d-%b-%Y')}", self.styles['NormalVN']))
        elements.append(Spacer(1, 10*mm))
        
        return elements

    def create_table(self, data):
        """Tạo bảng thông tin từ dữ liệu"""
        table_data = []
        for item in data:
            table_data.append([str(item[0]), str(item[1])])
            
        table = Table(table_data, colWidths=[5*cm, 14*cm])
        
        # Style cho bảng
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Màu nền xen kẽ
        for i in range(len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#E6F0FA'))
                
        table.setStyle(table_style)
        return table
    
    def create_financial_table(self, title, table_data, years):
        """Tạo bảng tài chính với dữ liệu"""
        elements = []
        
        # Thêm tiêu đề bảng
        elements.append(Paragraph(title, self.styles['TitleStyle']))
        elements.append(Spacer(1, 3*mm))
        
        if not table_data or len(table_data) == 0:
            return elements
        
        # Chuyển từ dictionary sang list cho bảng
        data = []
        try:
            # Thêm header với các năm
            header_row = ['Chỉ tiêu'] + [str(year) for year in years]
            data.append(header_row)
            
            # Thêm dữ liệu từng dòng
            for key, values in table_data.items():
                row = [key] + values
                data.append(row)
            
            # Tạo bảng
            table = Table(data, colWidths=[8*cm] + [4*cm] * len(years))
            
            # Style cho bảng - Sử dụng DejaVuSans nếu đã đăng ký thành công
            header_font = 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'
            content_font = 'DejaVuSans' if self.font_added else 'Helvetica'
            
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E6F0FA')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), header_font),
                ('FONTSIZE', (0, 0), (-1, 0), 4),
                ('FONTNAME', (0, 1), (-1, -1), content_font),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            # Thêm màu nền xen kẽ cho các dòng
            for row in range(1, len(data)):
                if row % 2 == 1:
                    table_style.add('BACKGROUND', (0, row), (-1, row), colors.HexColor('#F5F5F5'))
            
            table.setStyle(table_style)
            elements.append(table)
            elements.append(Spacer(1, 1*cm))
            
        except (StopIteration, ValueError, TypeError) as e:
            print(f"Lỗi khi tạo bảng: {str(e)}")
        
        return elements
    
    def create_market_data_table(self, market_data):
        """Tạo bảng dữ liệu thị trường cho phần sidebar"""
        if not market_data:
            return None
            
        # Thêm tiêu đề "Thị trường" ở đầu bảng
        self.styles.add(ParagraphStyle(
            name='MarketDataTitle',
            fontName='DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold',
            fontSize=12,  # Tăng kích thước tiêu đề từ 11 lên 12
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            leading=16,  # Tăng leading từ 14 lên 16
            leftIndent=0,
        ))
        
        title = Paragraph("Thị trường", self.styles['MarketDataTitle'])
        
        # Tạo Spacer trước bảng
        spacer = Spacer(1, 0.3*cm)  # Tăng từ 0.2cm lên 0.3cm
        
        # In ra để debug các khóa có trong market_data
        print(f"Keys in market_data: {list(market_data.keys())}")
        
        # Sắp xếp các chỉ số theo thứ tự trong ảnh
        ordered_keys = [
            "VNINDEX", "HNXINDEX", 
            "Vốn hóa (tỷ VND)", "SLCP lưu hành (triệu CP)",
            "52-tuần cao/thấp (VND)", "KLGD bình quân 90 ngày (triệu CP)", "GTGD bình quân 90 ngày (tỷ VND)"
        ]
        
        # Map keys từ market_data API sang keys trong giao diện hiển thị 
        # Đảm bảo tên khóa khớp chính xác với finance_calc.py
        key_mapping = {
            "VNINDEX": "VNINDEX",
            "HNXINDEX": "HNXINDEX",
            "Vốn hóa (tỷ VND)": "Vốn hóa (tỷ VND)",
            "SL CP lưu hành (triệu CP)": "SLCP lưu hành (triệu CP)",
            "52-tuần cao/thấp": "52-tuần cao/thấp (VND)",
            "KLGD bình quân 90 ngày": "KLGD bình quân 90 ngày (triệu CP)",
            "GTGD bình quân 90 ngày": "GTGD bình quân 90 ngày (tỷ VND)"
        }
        
        # Chuẩn bị dữ liệu cố định cho bảng - tất cả là N/A trước khi kiểm tra
        fixed_data = [
            ["VNINDEX", "N/A"],
            ["HNXINDEX", "N/A"],
            ["Vốn hóa (tỷ VND)", "N/A"],
            ["SLCP lưu hành (triệu CP)", "N/A"],
            ["52-tuần cao/thấp (VND)", "N/A"],
            ["KLGD bình quân 90 ngày (triệu CP)", "N/A"],
            ["GTGD bình quân 90 ngày (tỷ VND)", "N/A"]
        ]
        
        # Cập nhật giá trị từ market_data nếu có
        for i, row in enumerate(fixed_data):
            key_display = row[0]  # Khóa hiển thị
            # Tìm khóa tương ứng trong market_data
            key_in_data = next((k for k, v in key_mapping.items() if v == key_display), None)
            
            if key_in_data and key_in_data in market_data:
                fixed_data[i][1] = market_data[key_in_data]
        
        # Điều chỉnh kích thước cột để rộng hơn
        table = Table(fixed_data, colWidths=[3.6*cm, 2.2*cm], spaceBefore=3, spaceAfter=3)  # Tăng đáng kể chiều rộng của cả hai cột
        
        # Style mới cho bảng - đơn giản hơn, không có lưới
        table_style = TableStyle([
            # Căn lề
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            
            # Font
            ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),  # Kích thước font
            
            # Padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),  # Tăng padding dưới
            ('TOPPADDING', (0, 0), (-1, -1), 8),     # Tăng padding trên
            ('LEFTPADDING', (0, 0), (0, -1), 0),     # Giảm padding bên trái của cột đầu tiên
            ('RIGHTPADDING', (0, 0), (0, -1), 5),   # Tăng padding bên phải của cột đầu tiên
            ('LEFTPADDING', (1, 0), (1, -1), 5),    # Tăng padding bên trái của cột thứ hai
            ('RIGHTPADDING', (1, 0), (1, -1), 0),    # Giảm padding bên phải của cột thứ hai
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Đường viền trên và dưới
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#0066CC')),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor('#0066CC')),
        ])
        
        # Thêm màu nền cho các nhóm chỉ số
        # Chỉ số thị trường (2 dòng đầu)
        table_style.add('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#E6F0FA'))
        
        table.setStyle(table_style)
        
        # Tăng khoảng cách giữa các bảng
        middle_spacer = Spacer(1, 0.5*cm)  # Tăng từ 0.3cm lên 0.5cm
        
        # Tạo dữ liệu cho cổ đông lớn từ market_data thay vì dữ liệu cố định
        major_shareholders = []
        
        # Kiểm tra xem có dữ liệu cổ đông lớn không
        if "co_dong_lon" in market_data and market_data["co_dong_lon"] is not None:
            shareholders_df = market_data["co_dong_lon"]
            try:
                # In ra tên các cột trong DataFrame để debug
                print(f"Columns in shareholders_df: {list(shareholders_df.columns)}")
                
                # Đảm bảo DataFrame có cột cần thiết - kiểm tra bất kể tên cột
                if not shareholders_df.empty:
                    # Kiểm tra nếu tồn tại các cột cần thiết
                    share_holder_col = None
                    share_percent_col = None
                    
                    # Tìm cột chứa tên cổ đông
                    for col in shareholders_df.columns:
                        if 'hold' in str(col).lower() or 'name' in str(col).lower():
                            share_holder_col = col
                            break
                    
                    # Tìm cột chứa phần trăm sở hữu
                    for col in shareholders_df.columns:
                        if 'percent' in str(col).lower() or 'own' in str(col).lower() or 'ratio' in str(col).lower():
                            share_percent_col = col
                            break
                    
                    print(f"Found columns - holder: {share_holder_col}, percent: {share_percent_col}")
                    
                    if share_holder_col and share_percent_col:
                        # Tạo dòng tiêu đề
                        try:
                            ownership_ratio = float(shareholders_df.iloc[0][share_percent_col]) * 100
                            major_shareholders.append(["Cổ đông lớn (%)", str(shareholders_df.iloc[0][share_holder_col]), f"{ownership_ratio:.2f}%"])
                            
                            # Thêm các cổ đông còn lại
                            for i in range(1, min(3, len(shareholders_df))):
                                ownership_ratio = float(shareholders_df.iloc[i][share_percent_col]) * 100
                                major_shareholders.append(["", str(shareholders_df.iloc[i][share_holder_col]), f"{ownership_ratio:.2f}%"])
                            
                            print(f"Đã tạo bảng cổ đông lớn với {len(major_shareholders)} dòng")
                        except (ValueError, TypeError) as e:
                            print(f"Lỗi khi xử lý giá trị: {str(e)}")
                            # Vẫn tiếp tục thực hiện nếu có lỗi
                    else:
                        print(f"Không tìm thấy cột phù hợp cho tên cổ đông và tỷ lệ sở hữu")
                else:
                    print("DataFrame cổ đông rỗng")
            except Exception as e:
                print(f"Lỗi khi xử lý dữ liệu cổ đông lớn: {str(e)}")
                # Sử dụng dữ liệu mẫu khi có lỗi
                major_shareholders = [
                    ["Cổ đông lớn (%)", "Hồ Minh Quang", "14.20%"],
                    ["", "Unicoh Specialty Chemicals", "5.85%"]
                ]
        
        # Chuẩn bị dữ liệu cổ đông lớn dưới dạng có thể đọc được
        formatted_shareholders = []
        if len(major_shareholders) > 0:
            # Bỏ tiêu đề "Cổ đông lớn (%)" và chỉ giữ lại tên và phần trăm
            for i, shareholder in enumerate(major_shareholders):
                if i == 0 and len(shareholder) >= 3:
                    formatted_shareholders.append([shareholder[1], shareholder[2]])
                elif len(shareholder) >= 3:
                    formatted_shareholders.append([shareholder[1], shareholder[2]])
        
        # Tạo tiêu đề riêng cho bảng cổ đông lớn với style tương tự như tiêu đề "Thị trường"
        shareholder_title = Paragraph("Cổ đông lớn (%)", self.styles['MarketDataTitle'])
        
        # Thêm spacer nhỏ trước và sau tiêu đề
        pre_shareholder_title_spacer = Spacer(1, 0.4*cm)
        post_shareholder_title_spacer = Spacer(1, 0.1*cm)
        
        # Tạo bảng cổ đông lớn với căn lề cố định
        shareholder_table = Table(
            formatted_shareholders, 
            colWidths=[4.2*cm, 1.6*cm],  # Điều chỉnh độ rộng cột
            spaceBefore=3,
            spaceAfter=3
        )
        
        # Style mới cho bảng cổ đông
        shareholder_style = TableStyle([
            # Căn lề
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),     # Tên cổ đông căn trái
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),    # Phần trăm căn phải
            
            # Font
            ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),       # Font thường cho tên
            ('FONTNAME', (1, 0), (1, -1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'), # Font đậm cho phần trăm
            ('FONTSIZE', (0, 0), (-1, -1), 9),      # Kích thước font đồng nhất
            
            # Padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6), # Giảm padding dưới
            ('TOPPADDING', (0, 0), (-1, -1), 6),    # Giảm padding trên
            ('LEFTPADDING', (0, 0), (0, -1), 0),    # Không padding bên trái cột đầu
            ('RIGHTPADDING', (1, 0), (1, -1), 0),   # Không padding bên phải cột cuối
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Căn giữa theo chiều dọc
            
            # Đường viền trên và dưới cả bảng
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#0066CC')),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor('#0066CC')),
            
            # Nền cho toàn bộ bảng
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E6F0FA')),
        ])
        
        # Thêm style cho bảng
        shareholder_table.setStyle(shareholder_style)
        
        # Trả về một list các elements
        return [title, spacer, table, middle_spacer, pre_shareholder_title_spacer, shareholder_title, post_shareholder_title_spacer, shareholder_table]
        
    def draw_header_background(self, canvas, doc):
        """Vẽ background cho header"""
        width, height = A4
        # Vẽ background header màu xanh
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, height - 2.5*cm, width, 2.5*cm, fill=1, stroke=0)
        
    def draw_sidebar_background(self, canvas, doc):
        """Vẽ background cho sidebar"""
        width, height = A4
        # Vẽ đường phân cách giữa sidebar và phần nội dung
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(6.5*cm, 0, 6.5*cm, height - 2.5*cm)
    def create_stock_report(self, output_path, company_data, recommendation_data, market_data=None, analysis_data=None):
        """Tạo báo cáo chứng khoán theo mẫu mới"""
        width, height = A4
        
        # Lấy symbol từ company_data nếu có
        symbol = company_data.get('symbol')
        
        # Lấy giá hiện tại từ hàm current_price
        if symbol:
            try:
                current_price_value = current_price(symbol)
                # Format giá hiện tại với dấu phân cách hàng nghìn
                formatted_price = f"{current_price_value:,.0f}"
                # Cập nhật recommendation_data với giá hiện tại mới
                recommendation_data['current_price'] = formatted_price
                print(f"Đã lấy giá hiện tại của {symbol}: {formatted_price} VND")
            except Exception as e:
                print(f"Lỗi khi lấy giá hiện tại: {str(e)}")
                # Nếu có lỗi, giữ nguyên giá trị hiện tại trong recommendation_data nếu có
                if not recommendation_data.get('current_price'):
                    recommendation_data['current_price'] = "N/A"
        
        # Nếu không có dữ liệu thị trường được cung cấp, tự động lấy từ API
        if market_data is None or len(market_data) == 0:
            try:
                # Chuẩn bị thông tin cổ phiếu để truyền vào get_market_data
                stock_info = {
                    'current_price': float(recommendation_data.get('current_price', '0').replace(',', '')) if recommendation_data.get('current_price') and recommendation_data.get('current_price') != 'N/A' else 0,
                    'shares_outstanding': company_data.get('shares_outstanding', 1000),
                    'free_float': company_data.get('free_float', 35),
                    'ratios': company_data.get('ratios', {})
                }
                
                # Truyền thêm symbol vào get_market_data
                market_data = get_market_data(stock_info, symbol)
                print(f"Đã tự động lấy dữ liệu thị trường cho {symbol}: {market_data}")
            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu thị trường: {str(e)}")
                market_data = {"VNINDEX": "N/A", "HNXINDEX": "N/A"}
        
        # Đảm bảo analysis_data không là None
        if analysis_data is None:
            analysis_data = {
                "title": "Báo cáo phân tích",
                "content": []
            }
        
        # Tạo document với format mới
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.5*cm,
            leftMargin=0.1*cm,
            topMargin=3*cm,  # Để chỗ cho header
            bottomMargin=1*cm
        )
        
        # Tạo các frames cho layout
        left_column = Frame(
            0.5*cm,             # Giảm x position để tạo thêm không gian
            1*cm,               # y position
            5.5*cm,             # Tăng width từ 5cm lên 5.5cm
            height - 3.5*cm,    # Tăng height bằng cách giảm khoảng cách từ đỉnh (từ 4cm xuống 3.5cm)
            id='left_column',
            leftPadding=0.05*cm,  
            rightPadding=0*cm,   # Điều chỉnh padding bên phải về 0 thay vì -0.5cm
            bottomPadding=0.5*cm,
            topPadding=0.5*cm,
        )
        
        right_column = Frame(
            7*cm,                # x position
            1*cm,                # y position
            width - 8*cm,        # width (page width minus left col width and margins)
            height - 3.2*cm,       # height (subtract header and margins)
            id='right_column',
            leftPadding=0.05*cm,
            rightPadding=0.05*cm,
            bottomPadding=0.5*cm,
            topPadding=0.5*cm,
        )
        
        # Tạo page template với frames
        template = PageTemplate(
            id='two_column',
            frames=[left_column, right_column],
            onPage=lambda canvas, doc: self._draw_page_template(canvas, doc, company_data)
        )
        
        doc.addPageTemplates([template])
        
        # Tạo story (các elements sẽ được thêm vào PDF)
        story = []
        
        # 1. Phần bên trái (Sidebar)
        left_content = []
        
        # Thêm khoảng trống ở đầu để hạ nội dung xuống thấp hơn
        left_content.append(Spacer(1, 0.5*cm))
        
        # Thêm khuyến nghị - giảm kích thước chữ cho phần này và điều chỉnh style
        self.styles.add(ParagraphStyle(
            name='ReportDate',
            fontName='DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold',
            fontSize=12,  # Giảm từ 14 xuống 12
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=2,  # Giảm từ 6 xuống 2
            spaceAfter=2,   # Giảm từ 6 xuống 2
            leading=14,     # Giảm từ 16 xuống 14
            leftIndent=0,   # Không thụt lề
        ))
        
        date_str = recommendation_data.get('date', datetime.date.today().strftime('%d/%m/%Y'))
        left_content.append(Paragraph(f"Báo cáo cập nhật<br/>{date_str}", self.styles['ReportDate']))
        left_content.append(Spacer(1, 0.3*cm))  # Giảm từ 0.5cm xuống 0.3cm
        
        # Thêm giá hiện tại - đảm bảo căn trái chính xác 
        self.styles.add(ParagraphStyle(
            name='PriceLabel',
            fontName='DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold',
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            leftIndent=0,        # Không thụt lề
        ))
        
        price_label = Paragraph("Giá hiện tại", self.styles['PriceLabel'])
        
        self.styles.add(ParagraphStyle(
            name='PriceValueLeft',
            fontName='DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            leading=16,
            leftIndent=0,        # Không thụt lề
        ))
        
        price_value = Paragraph(f"<b>{recommendation_data.get('current_price', '')} VND</b>", self.styles['PriceValueLeft'])
        
        left_content.append(price_label)
        left_content.append(price_value)
        left_content.append(Spacer(1, 0.5*cm))
        
        # Thêm dữ liệu thị trường
        if market_data:
            market_elements = self.create_market_data_table(market_data)
            if market_elements:
                for element in market_elements:
                    left_content.append(element)
                left_content.append(Spacer(1, 0.3*cm))
        
        # Thêm các elements vào story với nextFrameFlowable để chuyển sang cột bên trái
        for element in left_content:
            story.append(element)
        
        # Chuyển sang cột bên phải bằng cách thêm FrameBreak
        story.append(FrameBreak())
        
        # Không hiển thị tiêu đề "Báo cáo phân tích" và dòng khuyến nghị nữa
        # Thay vào đó chỉ thêm một khoảng trống nhỏ trước khi hiển thị nội dung phân tích
        story.append(Spacer(1, 0.3*cm))
        
        # Nhận nội dung phân tích
        content_list = self._set_style_from_analysis_data_sample(analysis_data)
        
        # In ra để debug
        print(f"Number of content paragraphs: {len(content_list)}")
        
        # Nội dung phân tích với xử lý đặc biệt cho tiêu đề
        for paragraph in content_list:
            # Xử lý định dạng markdown và phát hiện tiêu đề
            content_type, processed_text = self._process_markdown_content(paragraph)
            
            if content_type == "heading":
                # Thêm khoảng cách trước tiêu đề để dễ đọc hơn
                story.append(Spacer(1, 0.4*cm))
                # Sử dụng style cho tiêu đề phân tích 
                title_text = processed_text.split(':')[0].strip() if ':' in processed_text else processed_text
                story.append(Paragraph(title_text, self.styles['SectionTitle']))
                
                # Nếu có nội dung sau dấu hai chấm, hiển thị như đoạn văn thông thường
                if ':' in processed_text:
                    content_text = processed_text.split(':', 1)[1].strip()
                    if content_text:
                        story.append(Spacer(1, 0.1*cm))
                        story.append(Paragraph(content_text, self.styles['NormalVN']))
            else:
                # Nội dung thông thường
                story.append(Paragraph(processed_text, self.styles['NormalVN']))
                story.append(Spacer(1, 0.2*cm))
        
        # Xuất PDF
        doc.build(story)
        return output_path
    
    def _draw_page_template(self, canvas, doc, company_data):
        """Vẽ template cho trang báo cáo"""
        try:
            print(f"Đang vẽ template với dữ liệu: {company_data}")
            width, height = A4
            
            # Vẽ header màu xanh
            canvas.setFillColor(self.blue_color)
            canvas.rect(0, height - 3*cm, width, 3*cm, fill=1, stroke=0)
            
            # Vẽ tên công ty
            canvas.setFont('DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold', 24)
            canvas.setFillColor(colors.white)
            company_name = company_data.get('name', 'CTCP Thép Nam Kim')
            print(f"Tên công ty: {company_name}")
            canvas.drawString(0.5*cm, height - 1.8*cm, company_name)  # Điều chỉnh vị trí x từ 1cm xuống 0.5cm
            
            # Vẽ thông tin phụ
            canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 12)
            info_text = company_data.get('info', '[ Việt Nam / Thép ]')
            print(f"Thông tin phụ: {info_text}")
            canvas.drawString(0.5*cm, height - 2.5*cm, info_text)  # Điều chỉnh vị trí x từ 1cm xuống 0.5cm
            
            # Vẽ đường kẻ phân cách giữa sidebar và phần nội dung
            canvas.setStrokeColor(colors.lightgrey)
            canvas.line(6.5*cm, 0, 6.5*cm, height - 3*cm)
        except Exception as e:
            print(f"Lỗi trong _draw_page_template: {str(e)}")
   
    def create_report(self, output_path, company_name, data, years, chart_paths=None, analysis=None):
        """Tạo báo cáo PDF hoàn chỉnh - Phương thức cũ được giữ lại để tương thích"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Danh sách các elements để thêm vào PDF
        elements = []
        
        # Thêm thông tin công ty (header)
        elements.extend(self.create_header(company_name, datetime.date.today()))
        
        # Thêm các bảng thông tin nếu có
        if 'info' in data:
            info_table = self.create_table(data['info'])
            elements.append(info_table)
            elements.append(Spacer(1, 1*cm))
        
        # Thêm các bảng tài chính
        for title, table_data in data.items():
            if title != 'info':  # Bỏ qua bảng thông tin đã xử lý
                elements.extend(self.create_financial_table(title, table_data, years))
        
        # Thêm biểu đồ nếu có
        if chart_paths and len(chart_paths) > 0:
            elements.append(PageBreak())  # Thêm ngắt trang
            elements.append(Paragraph("BIỂU ĐỒ TÀI CHÍNH", self.styles['TitleStyle']))
            elements.append(Spacer(1, 5*mm))
            
            for chart_path in chart_paths:
                if os.path.exists(chart_path):
                    try:
                        img = Image(chart_path, width=16*cm, height=10*cm)
                        elements.append(img)
                        elements.append(Spacer(1, 1*cm))
                    except Exception as e:
                        print(f"Lỗi khi thêm biểu đồ {chart_path}: {str(e)}")
                        elements.append(Paragraph(f"Không thể hiển thị biểu đồ: {chart_path}", self.styles['NormalVN']))
                        elements.append(Spacer(1, 5*mm))
        
        # Thêm phân tích nếu có
        if analysis:
            elements.append(PageBreak())  # Thêm ngắt trang
            elements.append(Paragraph("PHÂN TÍCH TÀI CHÍNH", self.styles['TitleStyle']))
            elements.append(Spacer(1, 5*mm))
            analysis_text = Paragraph(analysis, self.styles['NormalVN'])
            elements.append(analysis_text)
        
        # Xuất PDF
        doc.build(elements)
        return output_path

    def _set_style_from_analysis_data_sample(self, analysis_data):
        """Xử lý mẫu dữ liệu phân tích và chia thành các phần tiêu đề và nội dung"""
        content = []
        
        # Nếu không có dữ liệu phân tích, tạo mẫu
        if not analysis_data or not analysis_data.get('content'):
            sample_text = """**Giới thiệu về công ty** Công ty Cổ phần Thép Nam Kim (NKG) là một trong những công ty hàng đầu tại Việt Nam trong lĩnh vực thép mạ và ống thép. Thành lập vào năm 2002, Nam Kim đã nhanh chóng khẳng định vị thế của mình trong ngành công nghiệp thép Việt Nam. Công ty chuyên sản xuất và kinh doanh các sản phẩm thép mạ (tôn mạ kẽm, tôn mạ lạnh, tôn mạ màu), ống thép, xà gồ, và các sản phẩm thép công nghiệp khác. Nam Kim hiện sở hữu 5 nhà máy sản xuất với công suất lên tới hơn 1.2 triệu tấn sản phẩm mỗi năm, đáp ứng nhu cầu thị trường trong nước và xuất khẩu.
            
**Tình hình tài chính hiện nay** Nam Kim đã trải qua những biến động mạnh về tài chính trong những năm gần đây. Doanh thu của công ty có xu hướng tăng trưởng từ 11,559 tỷ đồng lên 28,173 tỷ đồng, sau đó điều chỉnh xuống 23,071 tỷ đồng. Tuy nhiên, lợi nhuận biến động đáng kể với biên lợi nhuận ròng dao động từ 2.55% lên 7.90% rồi giảm xuống -0.54% trong giai đoạn khó khăn. Tỷ lệ nợ trên vốn chủ sở hữu duy trì ở mức cao, khoảng 150-170%, phản ánh chiến lược sử dụng đòn bẩy tài chính của công ty. Hiện tại, Nam Kim đang trong quá trình cải thiện hiệu quả hoạt động, tối ưu hóa chi phí và tăng cường xuất khẩu để cải thiện biên lợi nhuận. Thị trường thép toàn cầu đang dần phục hồi sau giai đoạn khó khăn, tạo điều kiện thuận lợi cho Nam Kim cải thiện kết quả kinh doanh trong thời gian tới."""
            
            # Chia thành từng đoạn
            paragraphs = [p.strip() for p in sample_text.split('\n') if p.strip()]
            
            # Thêm vào nội dung
            content.extend(paragraphs)
            
            return content
            
        # Nếu có dữ liệu phân tích, sử dụng nó
        if isinstance(analysis_data.get('content'), list):
            # Kiểm tra và đảm bảo nội dung không bị mất
            content = analysis_data.get('content')
            print(f"Đã nhận {len(content)} đoạn phân tích")
            return content
        else:
            # Nếu không phải list, có thể là văn bản dài, chia thành các đoạn
            text = analysis_data.get('content', '')
            if isinstance(text, str):
                content = [p.strip() for p in text.split('\n\n') if p.strip()]
                print(f"Đã chuyển đổi văn bản thành {len(content)} đoạn phân tích")
            
        return content

