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
            wordWrap='CJK',  # Better word wrapping for Asian languages
            firstLineIndent=0,
            leftIndent=0,
            rightIndent=0
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
        
        # Format value columns (number formatting)
        for i in range(1, 5):
            if result[i] != 'N/A' and result[i]:
                # Already formatted with commas, don't modify
                pass
        
        # Debug print to check the comment value before conversion
        comment_value = result[5]
        print(f"Comment for row: '{comment_value}'")
        
        # Convert comments to Paragraph for proper wrapping
        if result[5] and result[5] != 'N/A':
            # Use CommentCell style which has proper word wrapping
            result[5] = Paragraph(str(result[5]), self.styles['CommentCell'])
        else:
            # Set empty string for empty comments to avoid N/A display
            result[5] = ''
            
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
        
        # Test comment data - remove this when connecting to database
        chú_thích = {
            'Doanh thu thuần': 'Doanh thu thuần tăng trưởng ổn định nhờ mở rộng thị trường và cải thiện sản phẩm.',
            'Giá vốn': 'Giá vốn hàng bán giảm nhờ tối ưu hóa quy trình sản xuất.',
            'Lợi nhuận gộp': 'Biên lợi nhuận gộp cải thiện nhờ tối ưu hóa chi phí sản xuất và tăng giá bán. Chi phí tài chính giảm do tái cấu trúc nợ. Chi phí bán hàng kiểm soát tốt. Chi phí quản lý doanh nghiệp tiết kiệm nhờ tối ưu nhân sự.',
            'Chi phí tài chính': '',
            'Chi phí bán hàng': '',
            'Chi phí quản lý': '',
            'Lợi nhuận từ HĐKD': 'Lợi nhuận từ hoạt động kinh doanh cải thiện nhờ tăng doanh thu và kiểm soát chi phí. Lợi nhuận trước thuế tăng nhờ cải thiện biên lợi nhuận. Lợi nhuận sau thuế tăng trưởng tích cực nhờ tối ưu hóa thuế và hiệu quả kinh doanh.',
            'LNTT': '',
            'LNST': ''
        }
        
        # Check if we have valid projection data
        if projection_data:
            # Prepare data for table using values from projection_data
            # Dictionary mapping from field names to row data (item name, value, growth rate)
            data_mapping = {
                # [value_key, growth_key, is_bold, is_sub_item]
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
            
            print("Processing projection data")
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
                
                # Get comment from projection_data or use hardcoded chú_thích
                comment_key = f"comment_{value_key.split('_')[0]}"
                for potential_key in [f"comment_{value_key}", comment_key]:
                    if potential_key in projection_data:
                        comment = projection_data[potential_key]
                        print(f"Found comment for {item_name} using key: {potential_key}")
                        break
                else:
                    comment = chú_thích.get(item_name, '')
                    
                # Debug output
                print(f"Item: {item_name}, Keys: {value_key}, {growth_key}")
                print(f"Values: 2024={value_2024}, %={growth_2024}, 2025={value_2025}, %={growth_2025}")
                
                # Create row with available data and comment
                row = [prefix + item_name, value_2024, growth_2024, value_2025, growth_2025, comment]
                
                # Format the row
                data.append(self.format_row(row, is_sub_item, is_bold))
        else:
            # Fallback to default rows with N/A values but with sample comments
            data = [
                self.format_row(['Doanh thu thuần', 'N/A', 'N/A', 'N/A', 'N/A', 
                                'Tăng trưởng theo kế hoạch'], is_bold=True),
                self.format_row(['Lợi nhuận gộp', 'N/A', 'N/A', 'N/A', 'N/A', 
                                 'Biên lợi nhuận gộp dự kiến cải thiện nhờ tối ưu hóa chi phí sản xuất và cải tiến quy trình. Chi phí tài chính giảm nhờ tái cấu trúc nợ, trong khi chi phí bán hàng tăng do đẩy mạnh marketing. Chi phí quản lý được tối ưu hóa qua hiện đại hóa bộ máy.'], is_bold=True),
                self.format_row(['Chi phí tài chính', 'N/A', 'N/A', 'N/A', 'N/A', 
                                 ''], True),
                self.format_row(['Chi phí bán hàng', 'N/A', 'N/A', 'N/A', 'N/A', 
                                 ''], True),
                self.format_row(['Chi phí quản lý', 'N/A', 'N/A', 'N/A', 'N/A', 
                                 ''], True),
                self.format_row(['Lợi nhuận từ HĐKD', 'N/A', 'N/A', 'N/A', 'N/A', 
                                'Lợi nhuận từ hoạt động kinh doanh cải thiện nhờ tăng doanh thu và kiểm soát chi phí. Lợi nhuận trước thuế tăng nhờ cải thiện biên lợi nhuận. Lợi nhuận sau thuế tăng trưởng tích cực nhờ tối ưu hóa thuế và hiệu quả kinh doanh.'], is_bold=True),
                self.format_row(['    LNTT', 'N/A', 'N/A', 'N/A', 'N/A', 
                                ''], True),
                self.format_row(['    LNST', 'N/A', 'N/A', 'N/A', 'N/A', 
                                ''], True)
            ]
        
        # Combine headers and data
        table_data = headers + data
        
        # Create table with specific column widths - adjusted for better fit
        width, height = A4
        available_width = width - (2 * cm)  # Subtract margins
        
        # Simplify column widths - ensure comment column has enough width
        col_widths = [4.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 7.5*cm]  # Fixed width for last column
        
        print(f"Column widths: {col_widths}")
        print(f"Comment column width: {col_widths[-1]}")
        
        table = Table(table_data, colWidths=col_widths, repeatRows=2)  # repeatRows=2 to repeat header on new pages
        
        # Define table style with minimal configuration for comments
        style = TableStyle([
            # Headers
            ('SPAN', (0, 0), (0, 1)),  # Merge "Khoản mục" cells
            ('SPAN', (1, 0), (2, 0)),  # Merge "2024" cells
            ('SPAN', (3, 0), (4, 0)),  # Merge "2025F" cells
            ('SPAN', (5, 0), (5, 1)),  # Merge "Chú thích" cells
            
            # Merge chú thích của Lợi nhuận gộp và 3 chỉ số chi phí (chỉ gộp cột chú thích)
            ('SPAN', (5, 3), (5, 6)),  # Gộp cột chú thích (index 5) của 4 dòng từ Lợi nhuận gộp đến Chi phí quản lý
            
            # Merge chú thích của Lợi nhuận từ HĐKD và 2 chỉ số lợi nhuận (chỉ gộp cột chú thích)
            ('SPAN', (5, 7), (5, 9)),  # Gộp cột chú thích (index 5) của 3 dòng từ Lợi nhuận từ HĐKD đến LNST
            
            # Fonts
            ('FONTNAME', (0, 0), (-1, 1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            
            # Font sizes
            ('FONTSIZE', (0, 0), (-1, 1), 9),
            ('FONTSIZE', (0, 2), (-1, -1), 9),
            
            # Alignment
            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('ALIGN', (1, 2), (4, -1), 'RIGHT'),  # Only align numbers to right
            ('ALIGN', (5, 2), (5, -1), 'LEFT'),   # Ensure comments are left-aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('VALIGN', (5, 3), (5, 6), 'TOP'),    # Vertical alignment for first merged comment
            ('VALIGN', (5, 7), (5, 9), 'TOP'),    # Vertical alignment for second merged comment
            
            # Background colors
            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#E6F0FA')),  # Header
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F5F5F5')),  # Doanh thu thuần
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#F5F5F5')),  # Lợi nhuận gộp
            ('BACKGROUND', (0, 4), (-1, 6), colors.white),    # Các dòng con của Lợi nhuận gộp
            ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#F5F5F5')),  # Lợi nhuận từ HĐKD
            ('BACKGROUND', (0, 8), (-1, 9), colors.white),   # LNTT và LNST (mục con của HĐKD)
            
            # Định dạng đặc biệt cho dòng con
            ('LEFTPADDING', (0, 4), (0, 6), 15),  # Thêm padding bên trái cho dòng con của Lợi nhuận gộp
            ('TEXTCOLOR', (0, 4), (0, 6), colors.HexColor('#666666')),  # Màu chữ nhạt hơn cho dòng con
            ('LEFTPADDING', (0, 8), (0, 9), 15),  # Thêm padding bên trái cho LNTT và LNST
            ('TEXTCOLOR', (0, 8), (0, 9), colors.HexColor('#666666')),  # Màu chữ nhạt hơn cho LNTT và LNST
            
            # Comment column formatting - Ensure proper wrapping
            ('LEFTPADDING', (5, 0), (5, -1), 8),  # Left padding for comments
            ('RIGHTPADDING', (5, 0), (5, -1), 8),  # Right padding for comments
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        return elements

    def create_page2(self, doc, company_data, projection_data=None):
        """Create the complete second page"""
        elements = []
        elements.append(Spacer(1, 1*inch))
        
        # Use sample data if projection_data is None or empty
        if projection_data is None or not projection_data:
            print("Using sample data for page2 projection")
            projection_data = self.generate_sample_data()
            print(f"Generated sample data keys: {projection_data.keys()}")
        else:
            print("Using provided data for page2 projection")
        
        # Add projection table
        elements.extend(self.create_projection_table(projection_data))
        
        return elements

    def generate_sample_data(self):
        """Generate sample data with comments for testing"""
        return {
            'doanh_thu_thuan': '5,240.58',
            'yoy_doanh_thu': '15.20%',
            'doanh_thu_thuan_2025F': '6,026.66',
            'yoy_doanh_thu_2025F': '15.00%',
            'comment_doanh_thu': 'Dự kiến tăng trưởng doanh thu dựa trên kế hoạch mở rộng thị trường và phát triển sản phẩm mới',
            
            'loi_nhuan_gop': '1,624.58',
            'yoy_loi_nhuan_gop': '18.30%',
            'loi_nhuan_gop_2025F': '1,929.33',
            'yoy_loi_nhuan_gop_2025F': '18.75%',
            'comment_loi_nhuan_gop': 'Biên lợi nhuận gộp dự kiến cải thiện nhờ tối ưu hóa chi phí sản xuất và cải tiến quy trình',
            
            'chi_phi_tai_chinh': '356.20',
            'yoy_chi_phi_tai_chinh': '-5.80%',
            'chi_phi_tai_chinh_2025F': '338.39',
            'yoy_chi_phi_tai_chinh_2025F': '-5.00%',
            'comment_chi_phi_tai_chinh': 'Chi phí lãi vay dự kiến giảm do trả nợ vay và tái cấu trúc nợ',
            
            'chi_phi_ban_hang': '524.06',
            'yoy_chi_phi_ban_hang': '12.30%',
            'chi_phi_ban_hang_2025F': '602.67',
            'yoy_chi_phi_ban_hang_2025F': '15.00%',
            'comment_chi_phi_ban_hang': 'Tăng chi phí marketing và phát triển kênh phân phối mới',
            
            'chi_phi_quan_ly': '262.03',
            'yoy_chi_phi_quan_ly': '7.50%',
            'chi_phi_quan_ly_2025F': '271.20',
            'yoy_chi_phi_quan_ly_2025F': '3.50%',
            'comment_chi_phi_quan_ly': 'Tối ưu hóa bộ máy quản lý và ứng dụng công nghệ số',
            
            'loi_nhuan_hdkd': '482.29',
            'yoy_loi_nhuan_hdkd': '35.40%',
            'loi_nhuan_hdkd_2025F': '717.07',
            'yoy_loi_nhuan_hdkd_2025F': '48.68%',
            'comment_loi_nhuan_hdkd': 'Cải thiện hiệu quả hoạt động nhờ tăng doanh thu và kiểm soát chi phí tốt',
            
            'loi_nhuan_truoc_thue': '465.41',
            'yoy_loi_nhuan_truoc_thue': '32.80%',
            'loi_nhuan_truoc_thue_2025F': '702.40',
            'yoy_loi_nhuan_truoc_thue_2025F': '50.92%',
            'comment_loi_nhuan_truoc_thue': 'Dự kiến tăng trưởng ổn định nhờ cải thiện biên lợi nhuận và kiểm soát chi phí',
            
            'loi_nhuan_sau_thue': '372.32',
            'yoy_loi_nhuan_sau_thue': '32.80%',
            'loi_nhuan_sau_thue_2025F': '561.92',
            'yoy_loi_nhuan_sau_thue_2025F': '50.92%',
            'comment_loi_nhuan_sau_thue': 'Lợi nhuận sau thuế tăng trưởng tích cực nhờ tối ưu hóa thuế và cải thiện hiệu quả kinh doanh'
        }
