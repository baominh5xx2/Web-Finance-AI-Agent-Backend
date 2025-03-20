from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    Image, PageBreak, Frame, NextPageTemplate, PageTemplate, 
    FrameBreak, BaseDocTemplate
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen.canvas import Canvas
import datetime
import os


class Page3:
    def __init__(self, font_added=False):
        self.font_added = font_added
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """Thiết lập các styles cho page 3"""
        # Font configuration
        title_font = 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'
        normal_font = 'DejaVuSans' if self.font_added else 'Helvetica'
        
        # Color configuration
        self.blue_color = colors.HexColor('#0066CC')
        self.light_blue = colors.HexColor('#E6F0FA')
        self.grey_color = colors.HexColor('#F5F5F5')
        
        # Style definitions
        style_configs = [
            ('SectionTitle', {
                'fontName': title_font,
                'fontSize': 14,
                'textColor': self.blue_color,
                'alignment': TA_LEFT,
                'spaceAfter': 6*mm
            }),
            ('ValuationText', {
                'fontName': normal_font,
                'fontSize': 10,
                'leading': 12,
                'alignment': TA_LEFT,
                'spaceAfter': 3*mm
            }),
            ('TableHeader', {
                'fontName': title_font,
                'fontSize': 10,
                'textColor': colors.white,
                'alignment': TA_CENTER,
                'leading': 12
            }),
            ('TableCell', {
                'fontName': normal_font,
                'fontSize': 9,
                'alignment': TA_CENTER,
                'leading': 11
            }),
            ('TableCellLeft', {
                'fontName': normal_font,
                'fontSize': 9,
                'alignment': TA_LEFT,
                'leading': 11
            }),
            ('SummaryRow', {
                'fontName': title_font,
                'fontSize': 9,
                'alignment': TA_LEFT,
                'leading': 11
            }),
            ('RecommendationTitle', {
                'fontName': title_font,
                'fontSize': 12,
                'textColor': colors.black,
                'alignment': TA_CENTER,
                'spaceAfter': 3*mm
            })
        ]
        
        # Add styles
        for style_name, style_props in style_configs:
            self.styles.add(ParagraphStyle(name=style_name, **style_props))

    def _draw_page_template(self, canvas, doc, company_data):
        """Vẽ header và footer cho trang"""
        width, height = A4
        font = 'DejaVuSans' if self.font_added else 'Helvetica'
        bold_font = 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'
        
        # Header
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, height - 20*mm, width, 20*mm, fill=1, stroke=0)
        
        # Company info in header
        canvas.setFillColor(colors.white)
        canvas.setFont(bold_font, 12)
        company_name = company_data.get('company_name', '')
        symbol = company_data.get('symbol', '')
        header_text = f"{company_name} ({symbol}) - Định giá và Khuyến nghị"
        canvas.drawString(1*cm, height - 12*mm, header_text)
        
        # Date in header
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        canvas.setFont(font, 9)
        canvas.drawRightString(width - 1*cm, height - 12*mm, f"Ngày: {current_date}")
        
        # Footer
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, 0, width, 10*mm, fill=1, stroke=0)
        
        # Footer text
        canvas.setFillColor(colors.white)
        canvas.setFont(font, 9)
        canvas.drawRightString(width - 1*cm, 3.5*mm, "Trang 3")
        canvas.drawString(1*cm, 3.5*mm, "FinBot - Trí tuệ tài chính cho mọi người")

    def create_peer_comparison_table(self, peer_data):
        """Tạo bảng so sánh với các doanh nghiệp trong ngành"""
        headers = [
            'Công ty', 'Quốc gia', 'P/E', 'Vốn hóa (tỷ USD)', 
            'Tăng trưởng doanh thu (%)', 'Tăng trưởng EPS TTM (%)', 
            'ROA (%)', 'ROE (%)'
        ]
        
        # Convert headers to Paragraphs
        header_cells = [Paragraph(h, self.styles['TableHeader']) for h in headers]
        data = [header_cells]
        
        # Add peer data rows
        for peer in peer_data:
            row = [
                Paragraph(peer.get('company_name', 'N/A'), self.styles['TableCellLeft']),
                Paragraph(peer.get('country', 'N/A'), self.styles['TableCell']),
                Paragraph(f"{peer.get('pe', 'N/A')}", self.styles['TableCell']),
                Paragraph(f"{peer.get('market_cap', 'N/A')}", self.styles['TableCell']),
                Paragraph(f"{peer.get('revenue_growth', 'N/A')}", self.styles['TableCell']),
                Paragraph(f"{peer.get('eps_growth', 'N/A')}", self.styles['TableCell']),
                Paragraph(f"{peer.get('roa', 'N/A')}", self.styles['TableCell']),
                Paragraph(f"{peer.get('roe', 'N/A')}", self.styles['TableCell'])
            ]
            data.append(row)
        
        # Create and style table
        col_widths = [4*cm, 2*cm, 1.5*cm, 2.5*cm, 3*cm, 3*cm, 2*cm, 2*cm]
        table = Table(data, colWidths=col_widths)
        
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.blue_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_blue])
        ])
        
        table.setStyle(table_style)
        return table

    def create_valuation_summary_table(self, valuation_data):
        """Tạo bảng tóm tắt định giá"""
        # Define row labels and their corresponding data keys
        summary_rows = [
            ('P/E trung bình ngành:', 'pe_avg'),
            ('P/E trung vị ngành:', 'pe_median'),
            ('P/E trung bình 10 năm của công ty:', 'pe_10yr_avg'),
            ('P/E mục tiêu:', 'pe_target'),
            ('EPS mục tiêu (VND):', 'eps_target'),
            ('Giá mục tiêu (VND):', 'price_target'),
            ('Giá hiện tại (VND):', 'current_price'),
            ('Tiềm năng tăng/giảm (%):', 'upside')
        ]
        
        # Create table data
        data = [
            [
                Paragraph(label, self.styles['SummaryRow']),
                Paragraph(str(valuation_data.get(key, 'N/A')), self.styles['TableCell'])
            ]
            for label, key in summary_rows
        ]
        
        # Create and style table
        table = Table(data, colWidths=[12*cm, 6*cm])
        table_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.light_blue]),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
        ])
        
        table.setStyle(table_style)
        return table

    def create_page3(self, doc, company_data, peer_data, valuation_data, recommendation_data):
        """Tạo nội dung cho trang định giá và khuyến nghị"""
        story = []
        width, height = A4
        
        # Tiêu đề phần định giá
        title = Paragraph("Phương pháp P/E", self.styles['SectionTitle'])
        story.append(title)
        story.append(Spacer(1, 10*mm))  # Tăng khoảng trống giữa tiêu đề và văn bản giải thích
        
        # Giải thích phương pháp định giá
        explanation_text = """Chúng tôi sử dụng phương pháp so sánh P/E để định giá cổ phiếu. P/E mục tiêu được xác định dựa trên P/E trung bình ngành, có điều chỉnh theo đặc thù hoạt động và vị thế của công ty trong ngành. EPS mục tiêu được dự phóng dựa trên kết quả kinh doanh quá khứ và triển vọng tăng trưởng."""
        explanation = Paragraph(explanation_text, self.styles['ValuationText'])
        story.append(explanation)
        story.append(Spacer(1, 10*mm))  # Tăng khoảng trống
        
        # Bảng so sánh với các doanh nghiệp trong ngành
        peer_table = self.create_peer_comparison_table(peer_data)
        story.append(peer_table)
        story.append(Spacer(1, 10*mm))  # Tăng khoảng trống
        
        # Tạo 2 cột cho phần còn lại
        remaining_content = []
        
        # Cột trái: Bảng tóm tắt định giá
        valuation_table = self.create_valuation_summary_table(valuation_data)
        remaining_content.append(valuation_table)
        
        # Tạo layout 2 cột
        col_data = [[valuation_table]]
        col_table = Table(col_data, colWidths=[10*cm, 5*cm])  # Điều chỉnh kích thước cột nếu cần
        col_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('LEFTPADDING', (1, 0), (1, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ]))
        
        story.append(col_table)
        
        return story
