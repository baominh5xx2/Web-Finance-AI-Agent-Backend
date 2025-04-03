from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, Frame, NextPageTemplate, PageTemplate, FrameBreak, BaseDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen.canvas import Canvas
import datetime
import os

class Page2:
    def __init__(self, font_added=False):
        self.font_added = font_added
        self.styles = getSampleStyleSheet()
        
        # Define colors
        self.blue_color = colors.HexColor('#0066CC')
        
        # Font configuration
        title_font = 'DejaVuSans-Bold' if font_added else 'Helvetica-Bold'
        normal_font = 'DejaVuSans' if font_added else 'Helvetica'
        
        # Add styles
        self.styles.add(ParagraphStyle(
            name='ProjectionTitle',
            fontName=title_font,
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=6,
            leading=16
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            fontName=title_font,
            fontSize=10,
            textColor=colors.black,
            alignment=TA_CENTER,
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCell',
            fontName=normal_font,
            fontSize=9,
            alignment=TA_LEFT,
            leading=12
        ))

        # Add styles for comment cells
        self.styles.add(ParagraphStyle(
            name='CommentCell',
            fontName='DejaVuSans' if self.font_added else 'Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leading=12,
            wordWrap='CJK'  # Better word wrapping for Asian languages
        ))

        # Add styles for item name cells
        self.styles.add(ParagraphStyle(
            name='ItemCell',
            fontName='DejaVuSans' if self.font_added else 'Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leading=12,
            wordWrap='CJK'  # Better word wrapping for Asian languages
        ))

        # Add styles for bold item name cells (for parent items)
        self.styles.add(ParagraphStyle(
            name='BoldItemCell',
            fontName='DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold',
            fontSize=9,
            alignment=TA_LEFT,
            leading=12,
            wordWrap='CJK'  # Better word wrapping for Asian languages
        ))

        # Add styles for sub-item name cells
        self.styles.add(ParagraphStyle(
            name='SubItemCell',
            fontName='DejaVuSans' if self.font_added else 'Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leading=12,
            leftIndent=10,  # Thụt lề để phân biệt mục con
            wordWrap='CJK'
        ))

    def _draw_page_template(self, canvas, doc, company_data):
        """Vẽ header và footer cho trang"""
        width, height = A4
    
        # Vẽ header
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, height - 20*mm, width, 20*mm, fill=1, stroke=0)
        
        # Tên công ty và mã chứng khoán
        canvas.setFillColor(colors.white)
        canvas.setFont('DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold', 12)
        company_name = company_data.get('name', '')
        symbol = company_data.get('symbol', '')
        header_text = f"{company_name} ({symbol}) - Dự phóng Tài chính"
        canvas.drawString(1*cm, height - 12*mm, header_text)
        
        # Ngày tạo báo cáo
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 9)
        canvas.drawRightString(width - 1*cm, height - 12*mm, f"Ngày: {current_date}")
        
        # Vẽ footer
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, 0, width, 10*mm, fill=1, stroke=0)
        
        # Số trang
        canvas.setFillColor(colors.white)
        canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 9)
        canvas.drawRightString(width - 1*cm, 3.5*mm, f"Trang 2")
        
        # Thông tin công ty
        canvas.drawString(1*cm, 3.5*mm, "FinBot - Trí tuệ tài chính cho mọi người")

    def format_row(self, row_data, is_sub_item=False, is_bold=False):
        """Format a table row with appropriate styles"""
        # Tạo bản sao của row_data để tránh thay đổi tham chiếu gốc
        result = row_data.copy()
        
        # Đảm bảo dữ liệu có đủ 6 phần tử
        while len(result) < 6:
            result.append('N/A')
            
        # Convert the first column (item name) to Paragraph with appropriate style
        if is_bold:
            style = self.styles['BoldItemCell']
        elif is_sub_item:
            style = self.styles['SubItemCell']
        else:
            style = self.styles['ItemCell']
            
        result[0] = Paragraph(str(result[0]), style)
        
        # Convert the last column (comment) to Paragraph if it's not empty
        if result[5] and result[5] != 'N/A':
            result[5] = Paragraph(str(result[5]), self.styles['CommentCell'])
            
        return result

    def create_projection_table(self, projection_data):
        """Create the business projection table"""
        elements = []
        
        # Add title
        title = Paragraph("Cập nhật kết quả kinh doanh 2024 và dự phóng 2025", self.styles['ProjectionTitle'])
        elements.append(title)
        elements.append(Spacer(1, 5*mm))
        
        # Prepare table headers
        headers = [
            [Paragraph('Khoản mục', self.styles['TableHeader']), '2024', '', '2025F', '', Paragraph('Chú thích', self.styles['TableHeader'])],
            ['', '(Tỷ đồng)', '%YoY', '(Tỷ đồng)', '%YoY', '']
        ]
        
        # Check if we have valid projection data
        if projection_data:
            # Prepare data for table using values from projection_data
            # Dictionary mapping from field names to row data (item name, value, growth rate)
            data_mapping = {
                # [item name, is_bold, is_sub_item]
                'Doanh thu thuần': ['doanh_thu_thuan', 'yoy_doanh_thu', True, False],
                'Lợi nhuận gộp': ['loi_nhuan_gop', 'yoy_loi_nhuan_gop', True, False],
                'Chi phí tài chính': ['chi_phi_tai_chinh', 'yoy_chi_phi_tai_chinh', False, True],
                'Chi phí bán hàng': ['chi_phi_ban_hang', 'yoy_chi_phi_ban_hang', False, True],
                'Chi phí quản lý': ['chi_phi_quan_ly', 'yoy_chi_phi_quan_ly', False, True],
                'Lợi nhuận từ HĐKD': ['loi_nhuan_hdkd', 'yoy_loi_nhuan_hdkd', True, False],
                'LNTT': ['loi_nhuan_truoc_thue', 'yoy_loi_nhuan_truoc_thue', False, True],
                'LNST': ['loi_nhuan_sau_thue', 'yoy_loi_nhuan_sau_thue', False, True]
            }
            
            # Create table rows with data from projection_data
            data = []
            for item_name, info in data_mapping.items():
                value_key, growth_key, is_bold, is_sub_item = info
                
                # For items with a 2025F projection, we need to extract the values
                # The dictionary keys have a specific pattern
                value_key_2025 = f"{value_key}_2025F"  # Key for 2025F value
                growth_key_2025 = f"{growth_key}_2025F"  # Key for 2025F growth rate
                
                # Prefix for LNTT and LNST rows
                prefix = "    " if item_name in ["LNTT", "LNST"] else ""
                
                # Get values from projection_data
                value_2024 = projection_data.get(value_key, 'N/A')
                growth_2024 = projection_data.get(growth_key, 'N/A')
                value_2025 = projection_data.get(value_key_2025, 'N/A')
                growth_2025 = projection_data.get(growth_key_2025, 'N/A')
                
                # Create row with available data
                row = [prefix + item_name, value_2024, growth_2024, value_2025, growth_2025, '']
                
                # Format the row
                data.append(self.format_row(row, is_sub_item, is_bold))
        else:
            # Fallback to default rows with N/A values
            data = [
                self.format_row(['Doanh thu thuần', 'N/A', 'N/A', 'N/A', 'N/A', ''], is_bold=True),
                self.format_row(['Lợi nhuận gộp', 'N/A', 'N/A', 'N/A', 'N/A', ''], is_bold=True),
                self.format_row(['Chi phí tài chính', 'N/A', 'N/A', 'N/A', 'N/A', ''], True),
                self.format_row(['Chi phí bán hàng', 'N/A', 'N/A', 'N/A', 'N/A', ''], True),
                self.format_row(['Chi phí quản lý', 'N/A', 'N/A', 'N/A', 'N/A', ''], True),
                self.format_row(['Lợi nhuận từ HĐKD', 'N/A', 'N/A', 'N/A', 'N/A', ''], is_bold=True),
                self.format_row(['    LNTT', 'N/A', 'N/A', 'N/A', 'N/A', ''], True),
                self.format_row(['    LNST', 'N/A', 'N/A', 'N/A', 'N/A', ''], True)
            ]
        
        # Combine headers and data
        table_data = headers + data
        
        # Create table with specific column widths - adjusted for better fit
        width, height = A4
        available_width = width - (2 * cm)  # Subtract margins
        col_widths = [4*cm, 2.2*cm, 1.8*cm, 2.2*cm, 1.8*cm, available_width - (12*cm)]  # Dynamic last column width
        table = Table(table_data, colWidths=col_widths, repeatRows=2)  # repeatRows=2 to repeat header on new pages
        
        # Define table style - UPDATED SPANS TO MATCH NEW ROW COUNT
        style = TableStyle([
            # Headers
            ('SPAN', (0, 0), (0, 1)),  # Merge "Khoản mục" cells
            ('SPAN', (1, 0), (2, 0)),  # Merge "2024" cells
            ('SPAN', (3, 0), (4, 0)),  # Merge "2025F" cells
            ('SPAN', (5, 0), (5, 1)),  # Merge "Chú thích" cells
            
            # Gộp chú thích cho mục Lợi nhuận gộp và các mục con - ADJUSTED
            ('SPAN', (5, 3), (5, 6)), # Chỉnh span cho phù hợp với số dòng mới
            
            # Gộp chú thích cho mục Lợi nhuận từ HĐKD và các mục con - ADJUSTED
            ('SPAN', (5, 7), (5, 9)), # Chỉnh span cho phù hợp với số dòng mới
            
            # Ẩn đường viền giữa các ô đã gộp cho Lợi nhuận gộp - ADJUSTED
            ('LINEAFTER', (5, 3), (5, 5), 0, colors.white),  # Chỉnh span cho phù hợp với số dòng mới
            ('LINEBEFORE', (5, 4), (5, 6), 0, colors.white), # Chỉnh span cho phù hợp với số dòng mới
            ('LINEBELOW', (5, 3), (5, 5), 0, colors.white),  # Chỉnh span cho phù hợp với số dòng mới
            ('LINEABOVE', (5, 4), (5, 6), 0, colors.white),  # Chỉnh span cho phù hợp với số dòng mới
            
            # Ẩn đường viền giữa các ô đã gộp cho Lợi nhuận từ HĐKD - ADJUSTED
            ('LINEAFTER', (5, 7), (5, 8), 0, colors.white),  # Chỉnh span cho phù hợp với số dòng mới
            ('LINEBEFORE', (5, 8), (5, 9), 0, colors.white), # Chỉnh span cho phù hợp với số dòng mới
            ('LINEBELOW', (5, 7), (5, 8), 0, colors.white),  # Chỉnh span cho phù hợp với số dòng mới
            ('LINEABOVE', (5, 8), (5, 9), 0, colors.white),  # Chỉnh span cho phù hợp với số dòng mới
            
            # Fonts
            ('FONTNAME', (0, 0), (-1, 1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            
            # Font sizes
            ('FONTSIZE', (0, 0), (-1, 1), 9),
            ('FONTSIZE', (0, 2), (-1, -1), 9),
            
            # Alignment
            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('ALIGN', (1, 2), (4, -1), 'RIGHT'),  # Only align numbers to right
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Căn giữa theo chiều dọc cho ô chú thích đã gộp - ADJUSTED
            ('VALIGN', (5, 3), (5, 6), 'TOP'),  # Chỉnh span cho phù hợp với số dòng mới
            ('VALIGN', (5, 7), (5, 9), 'TOP'),  # Chỉnh span cho phù hợp với số dòng mới
            
            # Background colors - ADJUSTED FOR NEW ROW COUNT
            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#E6F0FA')),  # Header
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F5F5F5')),  # Doanh thu thuần
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#F5F5F5')),  # Lợi nhuận gộp
            ('BACKGROUND', (0, 4), (-1, 6), colors.white),    # Các dòng con của Lợi nhuận gộp - ADJUSTED
            ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#F5F5F5')),  # Lợi nhuận từ HĐKD
            ('BACKGROUND', (0, 8), (-1, 9), colors.white),   # LNTT và LNST (mục con của HĐKD)
            
            # Định dạng đặc biệt cho dòng con - ADJUSTED
            ('LEFTPADDING', (0, 4), (0, 6), 15),  # Thêm padding bên trái cho dòng con của Lợi nhuận gộp - ADJUSTED
            ('TEXTCOLOR', (0, 4), (0, 6), colors.HexColor('#666666')),  # Màu chữ nhạt hơn cho dòng con - ADJUSTED
            ('LEFTPADDING', (0, 8), (0, 9), 15),  # Thêm padding bên trái cho LNTT và LNST
            ('TEXTCOLOR', (0, 8), (0, 9), colors.HexColor('#666666')),  # Màu chữ nhạt hơn cho LNTT và LNST
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        return elements

    def create_page2(self, doc, company_data, projection_data=None):
        """Create the complete second page"""
        elements = []
        elements.append(Spacer(1, 1*inch))
        # Add projection table
        elements.extend(self.create_projection_table(projection_data))
        
        return elements
