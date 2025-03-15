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
            table = Table(data, colWidths=[6*cm] + [2.5*cm] * len(years))
            
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
                ('FONTSIZE', (0, 0), (-1, 0), 10),
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
            
        data = []
        for key, value in market_data.items():
            data.append([key, value])
            
        table = Table(data, colWidths=[4*cm, 2*cm])
        
        table_style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
        ])
        
        for i in range(len(data) - 1):
            table_style.add('LINEBELOW', (0, i), (-1, i), 0.5, colors.lightgrey)
            
        table.setStyle(table_style)
        return table
        
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
    
    def create_stock_report(self, output_path, company_data, recommendation_data, market_data, analysis_data):
        """Tạo báo cáo chứng khoán theo mẫu mới"""
        width, height = A4
        
        # Tạo document với format mới
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=3*cm,  # Để chỗ cho header
            bottomMargin=1*cm
        )
        
        # Tạo các frames cho layout
        left_column = Frame(
            1*cm,                # x position
            1*cm,                # y position
            5*cm,                # width
            height - 4*cm,       # height (subtract header and margins)
            id='left_column',
            leftPadding=0.05*cm,
            rightPadding=0.05*cm,
            bottomPadding=0.5*cm,
            topPadding=0.5*cm,
        )
        
        right_column = Frame(
            7*cm,                # x position
            1*cm,                # y position
            width - 8*cm,        # width (page width minus left col width and margins)
            height - 4*cm,       # height (subtract header and margins)
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
        
        # Thêm khuyến nghị - giảm kích thước chữ cho phần này
        date_str = recommendation_data.get('date', datetime.date.today().strftime('%d/%m/%Y'))
        left_content.append(Paragraph(f"<font size='14'>Báo cáo cập nhật {date_str}</font>", 
                                     self.styles['Recommendation']))
        left_content.append(Spacer(1, 0.5*cm))
        
        # Thêm giá hiện tại - đảm bảo tất cả nội dung căn trái
        price_label = Paragraph("Giá hiện tại", self.styles['LeftColumn'])
        price_value = Paragraph(f"<b>{recommendation_data.get('current_price', '')} VND</b>", 
                               self.styles['PriceValue'])
        
        left_content.append(price_label)
        left_content.append(price_value)
        left_content.append(Spacer(1, 0.5*cm))
        
        # Thêm dữ liệu thị trường
        if market_data:
            market_table = self.create_market_data_table(market_data)
            if market_table:
                left_content.append(market_table)
                left_content.append(Spacer(1, 0.5*cm))
        
        # Thêm các elements vào story với nextFrameFlowable để chuyển sang cột bên trái
        for element in left_content:
            story.append(element)
        
        # Chuyển sang cột bên phải bằng cách thêm FrameBreak
        story.append(FrameBreak())
        
        # Tiêu đề phân tích
        story.append(Paragraph(analysis_data.get('title', 'Đón sóng tăng trưởng'), 
                              self.styles['AnalysisTitle']))
        story.append(Spacer(1, 0.3*cm))
        
        # Khuyến nghị chi tiết
        story.append(Paragraph(analysis_data.get('recommendation', 
                              'Định giá cập nhật với khuyến nghị MUA, giá mục tiêu 19,900 đồng'), 
                              self.styles['NormalVN']))
        story.append(Spacer(1, 0.5*cm))
        
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
        width, height = A4
        
        # Vẽ header màu xanh
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, height - 3*cm, width, 3*cm, fill=1, stroke=0)
        
        # Vẽ tên công ty
        canvas.setFont('DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold', 24)
        canvas.setFillColor(colors.white)
        company_name = company_data.get('name', 'CTCP Thép Nam Kim')
        canvas.drawString(1*cm, height - 1.8*cm, company_name)
        
        # Vẽ thông tin phụ
        canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 12)
        canvas.drawString(1*cm, height - 2.5*cm, company_data.get('info', '[ Việt Nam / Thép ]'))
        
        # Vẽ đường kẻ phân cách giữa sidebar và phần nội dung
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(6.5*cm, 0, 6.5*cm, height - 3*cm)
    
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
            sample_text = """**PHÂN TÍCH TÀI CHÍNH** Doanh thu có xu hướng tăng trưởng mạnh mẽ từ 11,559,674,520,160.00 lên 28,173,402,236,226.00, sau đó giảm xuống 23,071,247,285,247.00. Tuy nhiên, lợi nhuận ròng lại biến động mạnh, từ 295,269,532,668.00 tăng vọt lên 2,225,261,058,221.00 rồi giảm sâu xuống -124,684,837,727.00. Biên lợi nhuận ròng cũng biến động tương tự 2.55% lên 7.90% rồi giảm xuống -0.54%. ROE và ROA cũng có xu hướng tương tự. Tỷ lệ D/E biến động từ 144.04% xuống 169.04% rồi giảm còn 153.04%, cho thấy mức độ sử dụng đòn bẩy tài chính cao. Nhìn chung, tình hình tài chính có sự biến động lớn, đặc biệt là về lợi nhuận.
            
**PHÂN TÍCH RỦI RO** Rủi ro tài chính của mã cổ phiếu này đến từ việc lợi nhuận biến động mạnh và tỷ lệ nợ trên vốn chủ sở hữu cao. Sự biến động lợi nhuận có thể ảnh hưởng đến việc trả nợ và thanh toán cổ tức của công ty. Tỷ lệ nợ cao cũng làm tăng rủi ro khi lãi suất tăng hoặc khi công ty gặp khó khăn trong hoạt động kinh doanh. Cần xem xét kỹ động tiền của công ty để đánh giá khả năng trả nợ trong tương lai.
            
**ĐÁNH GIÁ TRIỂN VỌNG ĐẦU TƯ** Tiềm năng tăng trưởng lợi nhuận và biến động chỉ tiêu qua các năm thể hiện công ty có thể đang trong giai đoạn cải thiện hiệu quả hoạt động. Doanh thu tăng trưởng nhưng lợi nhuận không tăng tương ứng đã tăng, cho thấy hiệu quả hoạt động cổ đang cải thiện. Cần theo dõi lợi nhuận trong những năm tới để đánh giá xu hướng vận hành mà cổ phiếu này có rủi ro tài chính và biến động lợi nhuận lớn."""
            
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
