import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

class PDFReport:
    def __init__(self):
        # Đăng ký font
        self.font_added = self._setup_fonts()
        self.styles = getSampleStyleSheet()
        
        # Sử dụng font DejaVuSans nếu đã đăng ký, nếu không thì dùng Helvetica
        title_font = 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'
        normal_font = 'DejaVuSans' if self.font_added else 'Helvetica'
        
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
    
    def create_report(self, output_path, company_name, data, years, chart_paths=None, analysis=None):
        """Tạo báo cáo PDF hoàn chỉnh"""
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
        
        
        # Xuất PDF
        doc.build(elements)
        return output_path
