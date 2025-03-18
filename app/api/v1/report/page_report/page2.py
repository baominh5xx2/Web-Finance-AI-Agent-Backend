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

    def _draw_page_template(self, canvas, doc, company_data):
        """Draw the page template for page 2"""
        # Add any specific page template drawing if needed
        pass

    def create_projection_table(self, projection_data):
        """Create the business projection table"""
        if not projection_data:
            return [Paragraph("Không có dữ liệu dự phóng", self.styles['ProjectionTitle'])]
            
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
        
        # Convert text to Paragraph objects for both item name and comment
        def format_row(row_data):
            # Convert the first column (item name) to Paragraph
            row_data[0] = Paragraph(str(row_data[0]), self.styles['ItemCell'])
            # Convert the last column (comment) to Paragraph if it's not empty
            if len(row_data) > 5 and row_data[5] and row_data[5] != 'N/A':
                row_data[5] = Paragraph(str(row_data[5]), self.styles['CommentCell'])
            return row_data

        # Get data from projection_data and format each row
        data = [
            format_row(['Doanh thu thuần'] + projection_data.get('revenue', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['Sản lượng (ngàn tấn)'] + projection_data.get('volume', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['Tôn mạ'] + projection_data.get('coated_steel', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['Ống thép'] + projection_data.get('steel_pipe', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['Lợi nhuận gộp'] + projection_data.get('gross_profit', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['Biên lợi nhuận gộp'] + projection_data.get('gross_margin', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['Chi phí bán hàng và quản lý'] + projection_data.get('sga', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['Lợi nhuận từ HĐKD'] + projection_data.get('operating_profit', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['LNTT'] + projection_data.get('profit_before_tax', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])),
            format_row(['LNST'] + projection_data.get('profit_after_tax', ['N/A', 'N/A', 'N/A', 'N/A', 'N/A']))
        ]
        
        # Combine headers and data
        table_data = headers + data
        
        # Create table with specific column widths - adjusted for better fit
        width, height = A4
        available_width = width - (2 * cm)  # Subtract margins
        col_widths = [4*cm, 2.2*cm, 1.8*cm, 2.2*cm, 1.8*cm, available_width - (12*cm)]  # Dynamic last column width
        table = Table(table_data, colWidths=col_widths, repeatRows=2)  # repeatRows=2 to repeat header on new pages
        
        # Define table style
        style = TableStyle([
            # Headers
            ('SPAN', (0, 0), (0, 1)),  # Merge "Khoản mục" cells
            ('SPAN', (1, 0), (2, 0)),  # Merge "2024" cells
            ('SPAN', (3, 0), (4, 0)),  # Merge "2025F" cells
            ('SPAN', (5, 0), (5, 1)),  # Merge "Chú thích" cells
            
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
            
            # Background colors
            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#E6F0FA')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F5F5F5')),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F5F5F5')),
            ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#F5F5F5')),
            ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor('#F5F5F5')),
            ('BACKGROUND', (0, 10), (-1, 10), colors.HexColor('#F5F5F5')),
            
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
        
        # Add projection table
        elements.extend(self.create_projection_table(projection_data))
        
        return elements
