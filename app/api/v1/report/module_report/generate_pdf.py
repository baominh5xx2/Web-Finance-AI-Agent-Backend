import os
import datetime
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, Frame, NextPageTemplate, PageTemplate, FrameBreak, BaseDocTemplate
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
        
        # Style mới cho phần giá mục tiêu và suất sinh lời
        self.styles.add(ParagraphStyle(name='TargetPriceLabel', fontSize=8, alignment=TA_LEFT, fontName='DejaVuSans', textColor=colors.gray))
        self.styles.add(ParagraphStyle(name='TargetPriceValue', fontSize=16, alignment=TA_LEFT, fontName='DejaVuSans-Bold', leading=18))
        self.styles.add(ParagraphStyle(name='ProfitLabel', fontSize=8, alignment=TA_LEFT, fontName='DejaVuSans', textColor=colors.gray))
        self.styles.add(ParagraphStyle(name='ProfitValue', fontSize=14, alignment=TA_LEFT, fontName='DejaVuSans-Bold', leading=16))
        
        # Thêm các style còn thiếu
        self.styles.add(ParagraphStyle(
            name='MarketDataTitle',
            fontName=title_font,
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            leading=16,
            leftIndent=0,
        ))
        
        # Style cho ngày báo cáo
        self.styles.add(ParagraphStyle(
            name='DateLabel',
            fontName=normal_font,
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_LEFT,
        ))
        
        self.styles.add(ParagraphStyle(
            name='DateValue',
            fontName=normal_font,
            fontSize=10,
            alignment=TA_LEFT,
            leading=12,
        ))
        
        # Style cho label giá hiện tại
        self.styles.add(ParagraphStyle(
            name='PriceLabel',
            fontName=normal_font,
            fontSize=8,
            textColor=colors.gray,
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
            # Trả về danh sách rỗng thay vì None để tránh lỗi khi extend
            return []
        
        # Tạo Spacer trước bảng
        spacer = Spacer(1, 0.2*cm)  # Tăng từ 0.2cm lên 0.3cm
        
        # In ra để debug các khóa có trong market_data
        print(f"Keys in market_data: {list(market_data.keys())}")
        
        # Chuẩn bị dữ liệu cố định cho bảng - tất cả là N/A trước khi kiểm tra
        fixed_data = [
            ["VNINDEX", "N/A"],
            ["HNXINDEX", "N/A"],
            ["Vốn hóa (tỷ VND)", "N/A"],
            ["SLCP lưu hành (tr CP)", "N/A"],
            ["52-tuần cao/thấp", "N/A"],
            ["KLGD 90 ngày (tr CP)", "N/A"],
            ["GTGD 90 ngày (tỷ)", "N/A"]
        ]
        
        # Map keys từ market_data API sang keys trong giao diện hiển thị 
        key_mapping = {
            "VNINDEX": "VNINDEX",
            "HNXINDEX": "HNXINDEX",
            "Vốn hóa (tỷ VND)": "Vốn hóa (tỷ VND)",
            "SL CP lưu hành (triệu CP)": "SLCP lưu hành (tr CP)",
            "52-tuần cao/thấp": "52-tuần cao/thấp",
            "KLGD bình quân 90 ngày": "KLGD 90 ngày (tr CP)",
            "GTGD bình quân 90 ngày": "GTGD 90 ngày (tỷ)"
        }
        
        # Cập nhật giá trị từ market_data nếu có
        for i, row in enumerate(fixed_data):
            key_display = row[0]  # Khóa hiển thị
            # Tìm khóa tương ứng trong market_data
            key_in_data = next((k for k, v in key_mapping.items() if v == key_display), None)
            
            if key_in_data and key_in_data in market_data:
                fixed_data[i][1] = market_data[key_in_data]
        
        # Điều chỉnh kích thước cột để vừa với không gian - giảm chiều rộng cột 1
        table = Table(fixed_data, colWidths=[3.2*cm, 2.6*cm], spaceBefore=3, spaceAfter=3)
        
        # Style mới cho bảng - đơn giản hơn, không có lưới
        table_style = TableStyle([
            # Căn lề
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            
            # Font
            ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),  # Kích thước font nhỏ
            
            # Padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Giảm padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),     # Giảm padding
            ('LEFTPADDING', (0, 0), (0, -1), 0),     # Giảm padding bên trái
            ('RIGHTPADDING', (0, 0), (0, -1), 2),    # Giảm padding bên phải
            ('LEFTPADDING', (1, 0), (1, -1), 2),     # Giảm padding bên trái
            ('RIGHTPADDING', (1, 0), (1, -1), 0),    # Giảm padding bên phải
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Đường viền trên và dưới
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#0066CC')),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor('#0066CC')),
        ])
        
        # Thêm màu nền cho chỉ số thị trường
        table_style.add('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#E6F0FA'))
        
        table.setStyle(table_style)
        
        # Tăng khoảng cách giữa các bảng
        middle_spacer = Spacer(1, 0.3*cm)  # Giảm từ 0.5cm xuống 0.3cm
        
        # Xử lý phần cổ đông lớn
        shareholders = []
        # Chỉ hiển thị tiêu đề cổ đông lớn nếu có dữ liệu
        if "co_dong_lon" in market_data and market_data["co_dong_lon"] is not None:
            shareholders_df = market_data["co_dong_lon"]
            
            # Tiêu đề cho phần cổ đông lớn
            shareholder_title = Paragraph("Cổ đông lớn (%)", self.styles['MarketDataTitle'])
            shareholders.append(shareholder_title)
            shareholders.append(Spacer(1, 0.1*cm))
            
            # Nếu có dữ liệu cổ đông, xử lý và hiển thị
            if not shareholders_df.empty:
                try:
                    # Tìm các cột liên quan
                    share_holder_col = None
                    share_percent_col = None
                    
                    # Tìm cột tên cổ đông
                    for col in shareholders_df.columns:
                        if 'hold' in str(col).lower() or 'name' in str(col).lower():
                            share_holder_col = col
                            break
                    
                    # Tìm cột tỷ lệ sở hữu
                    for col in shareholders_df.columns:
                        if 'percent' in str(col).lower() or 'own' in str(col).lower() or 'ratio' in str(col).lower():
                            share_percent_col = col
                            break
                    
                    # Nếu có đủ thông tin cột
                    if share_holder_col and share_percent_col:
                        # Chuẩn bị dữ liệu cổ đông
                        formatted_shareholders = []
                        for i in range(min(3, len(shareholders_df))):
                            try:
                                # Rút ngắn tên cổ đông nếu quá dài
                                holder_name = str(shareholders_df.iloc[i][share_holder_col])
                                if len(holder_name) > 20:
                                    holder_name = holder_name[:18] + "..."
                                
                                # Định dạng tỷ lệ sở hữu
                                ownership_ratio = float(shareholders_df.iloc[i][share_percent_col]) * 100
                                formatted_shareholders.append([holder_name, f"{ownership_ratio:.2f}%"])
                            except (ValueError, TypeError) as e:
                                print(f"Lỗi khi xử lý cổ đông {i}: {str(e)}")
                                continue
                        
                        # Tạo bảng cổ đông nếu có dữ liệu
                        if formatted_shareholders:
                            # Điều chỉnh kích thước cột cho phù hợp
                            shareholder_table = Table(
                                formatted_shareholders, 
                                colWidths=[4.0*cm, 1.8*cm],
                                spaceBefore=3,
                                spaceAfter=3
                            )
                            
                            # Style cho bảng cổ đông
                            shareholder_style = TableStyle([
                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                                ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
                                ('FONTNAME', (1, 0), (1, -1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                                ('TOPPADDING', (0, 0), (-1, -1), 5),
                                ('LEFTPADDING', (0, 0), (0, -1), 0),
                                ('RIGHTPADDING', (1, 0), (1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
                            ])
                            
                            shareholder_table.setStyle(shareholder_style)
                            shareholders.append(shareholder_table)
                        else:
                            # Thông báo không có dữ liệu
                            no_data = Paragraph("Không có dữ liệu", self.styles['NormalVN'])
                            shareholders.append(no_data)
                    else:
                        # Thông báo không tìm thấy cột
                        no_column = Paragraph("Không tìm thấy cột dữ liệu", self.styles['NormalVN'])
                        shareholders.append(no_column)
                except Exception as e:
                    # Xử lý lỗi
                    error_msg = Paragraph(f"Lỗi: {str(e)[:30]}...", self.styles['NormalVN'])
                    shareholders.append(error_msg)
            else:
                # DataFrame rỗng
                empty_df = Paragraph("Không có dữ liệu cổ đông", self.styles['NormalVN'])
                shareholders.append(empty_df)
        
        # Kết hợp tất cả elements
        elements = [spacer, table]
        
        # Chỉ thêm phần cổ đông nếu có
        if shareholders:
            elements.append(middle_spacer)
            elements.extend(shareholders)
        
        return elements
        
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
        
        # Tạo các frames
        frames = [
            # Header frame - trên cùng màu xanh
            Frame(0, height - 3*cm, width, 3*cm),
            
            # Sidebar frame - cột bên trái
            Frame(0, 0, 6.5*cm, height - 3*cm, id='sidebar'),
            
            # Main content frame - cột bên phải
            Frame(6.5*cm, 0, width - 6.5*cm, height - 3*cm)
        ]
        
        # Tạo document với multiple frames
        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0,
            leftMargin=0,
            topMargin=0,
            bottomMargin=0,
        )
        template = PageTemplate(
            id='multipagetemplate',
            frames=frames,
            onPage=lambda canvas, doc: self._draw_page_template(canvas, doc, company_data)
        )
        doc.addPageTemplates([template])
        
        # Story là danh sách các elements để thêm vào PDF
        story = []
        
        # Thêm spacing để tránh chồng lấp với khung màu xanh
        story.append(Spacer(1,2.5*cm))
        
        # Date hiện tại
        date_today = datetime.date.today().strftime('%d/%m/%Y')
        date_label = Paragraph("Báo cáo cập nhật", self.styles['DateLabel'])
        date_value = Paragraph(date_today, self.styles['DateValue'])
        
        # Hiển thị giá hiện tại
        price_label = Paragraph("Giá hiện tại", self.styles['PriceLabel'])
        price_value = Paragraph("<b>{0} VND</b>".format(recommendation_data.get('current_price', 'N/A')), self.styles['PriceValue'])
        
        # Thêm hiển thị giá mục tiêu và suất sinh lời
        target_price_label = Paragraph("Giá mục tiêu", self.styles['TargetPriceLabel'])
        target_price = recommendation_data.get('target_price', 'N/A')
        target_price_value = Paragraph("<b>{0} {1}</b>".format(
            target_price, 
            "VND" if target_price != "N/A" else ""
        ), self.styles['TargetPriceValue'])
        
        profit_label = Paragraph("Suất sinh lời", self.styles['ProfitLabel'])
        profit_percent = recommendation_data.get('profit_percent', 'N/A')
        
        # Xử lý trường hợp profit_percent là "N/A"
        if profit_percent == "N/A":
            profit_value = Paragraph("<b>N/A</b>", self.styles['ProfitValue'])
        else:
            try:
                # Chuyển đổi profit_percent thành số để xác định màu sắc
                profit_num = float(profit_percent)
                # Nhân với 100 để hiển thị đúng tỷ lệ phần trăm
                profit_display = profit_num * 100
                profit_color = "green" if profit_num > 0 else "red"
                # Thêm dấu + cho giá trị dương
                sign = "+" if profit_num > 0 else ""
                profit_value = Paragraph("<b><font color='{0}'>{1}{2:.2f}%</font></b>".format(
                    profit_color, sign, profit_display
                ), self.styles['ProfitValue'])
            except (ValueError, TypeError):
                # Nếu không thể chuyển đổi thành số, hiển thị giá trị mặc định
                profit_value = Paragraph("<b>N/A</b>", self.styles['ProfitValue'])
        
        # Thêm thông tin giá và ngày vào story trong sidebar
        story.append(date_label)
        story.append(date_value)
        story.append(Spacer(1, 0.2*cm))
        story.append(price_label)
        story.append(price_value)
        story.append(Spacer(1, 0.2*cm))
        story.append(target_price_label)
        story.append(target_price_value)
        story.append(Spacer(1, 0.2*cm))
        story.append(profit_label)
        story.append(profit_value)
        story.append(Spacer(1, 0.5*cm))
        
        # Tạo bảng thông tin thị trường - IMPORTANT FIX: extend instead of append
        story.append(Paragraph("Thị trường", self.styles['MarketDataTitle']))
        story.append(Spacer(1, 0.1*cm))
        
        market_elements = self.create_market_data_table(market_data)
        if market_elements:
            story.extend(market_elements)
        
        # Chuyển sang cột bên phải bằng cách thêm FrameBreak
        story.append(FrameBreak())
        
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
    
    def _draw_page_template(self, canvas, doc, company_data): # vẽ cái giao diện nền công ty
        """Vẽ template cho trang báo cáo"""
        try:
            print(f"Đang vẽ template với dữ liệu: {company_data}")
            width, height = A4
            
            # Vẽ background header màu xanh
            canvas.setFillColor(self.blue_color)
            canvas.rect(0, height - 3*cm, width, 3*cm, fill=1, stroke=0)
            
            # Vẽ tên công ty
            canvas.setFont('DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold', 16)
            canvas.setFillColor(colors.white)
            company_name = company_data.get('name')
            print(f"Tên công ty: {company_name}")
            canvas.drawString(0.5*cm, height - 1.8*cm, company_name)  # Điều chỉnh vị trí x từ 1cm xuống 0.5cm
            
            # Vẽ thông tin phụ
            canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 12)
            info_text = company_data.get('info')
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

