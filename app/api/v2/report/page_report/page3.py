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

class Page3:
    def __init__(self, font_added=False):
        self.font_added = font_added
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """Thiết lập các styles cho page 3"""
        # Sử dụng font DejaVuSans nếu đã đăng ký, nếu không thì dùng Helvetica
        title_font = 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'
        normal_font = 'DejaVuSans' if self.font_added else 'Helvetica'
        
        # Màu sắc chính
        self.blue_color = colors.HexColor('#0066CC')
        self.light_blue = colors.HexColor('#E6F0FA')
        self.grey_color = colors.HexColor('#F5F5F5')
        
        # Tạo style cho tiêu đề và nội dung
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName=title_font,
            fontSize=14,
            textColor=self.blue_color,
            alignment=TA_LEFT,
            spaceAfter=6*mm
        ))
        
        self.styles.add(ParagraphStyle(
            name='ValuationText',
            fontName=normal_font,
            fontSize=10,
            leading=12,
            alignment=TA_LEFT,
            spaceAfter=3*mm
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            fontName=title_font,
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER,
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCell',
            fontName=normal_font,
            fontSize=8,
            alignment=TA_CENTER,
            leading=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCellLeft',
            fontName=normal_font,
            fontSize=8,
            alignment=TA_LEFT,
            leading=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='SummaryRow',
            fontName=title_font,
            fontSize=8,
            alignment=TA_LEFT,
            leading=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='PeerTableCompanyCell',
            fontName=title_font,
            fontSize=8,
            alignment=TA_LEFT,
            leading=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='RecommendationTitle',
            fontName=title_font,
            fontSize=12,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=3*mm
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
        company_name = company_data.get('company_name', '')
        symbol = company_data.get('symbol', '')
        header_text = f"{company_name} ({symbol}) - Định giá và Khuyến nghị"
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
        canvas.drawRightString(width - 1*cm, 3.5*mm, f"Trang 3")
        
        # Thông tin công ty
        canvas.drawString(1*cm, 3.5*mm, "FinBot - Trí tuệ tài chính cho mọi người")
    
    def create_valuation_summary_table(self, valuation_data):
        """Tạo bảng tóm tắt định giá"""
        data = []
        
        # Hardcode các giá trị P/E và EPS mục tiêu
        pe_target = "15.59"
        eps_target = "1537.53"
        
        # Định dạng giá trị upside với dấu % nếu cần
        upside = valuation_data.get('upside', 'N/A')
        if upside != 'N/A' and not upside.endswith('%'):
            upside = f"{upside}%"
        
        # Lấy các giá trị khác từ valuation_data
        price_target = valuation_data.get('price_target', 'N/A')
        current_price = valuation_data.get('current_price', 'N/A')
        
        # Thêm các dòng vào bảng - đã xóa các dòng P/E trung bình, trung vị và trung bình 10 năm
        data.append([Paragraph('P/E mục tiêu:', self.styles['SummaryRow']), 
                     Paragraph(f"{pe_target}", self.styles['TableCell'])])
        data.append([Paragraph('EPS trung bình ngành (VND):', self.styles['SummaryRow']), 
                     Paragraph(f"{eps_target}", self.styles['TableCell'])])
        data.append([Paragraph('Giá mục tiêu (VND):', self.styles['SummaryRow']), 
                     Paragraph(f"{price_target}", self.styles['TableCell'])])
        data.append([Paragraph('Giá hiện tại (VND):', self.styles['SummaryRow']), 
                     Paragraph(f"{current_price}", self.styles['TableCell'])])
        data.append([Paragraph('Tiềm năng tăng/giảm (%):', self.styles['SummaryRow']), 
                     Paragraph(f"{upside}", self.styles['TableCell'])])
        
        # Tạo bảng với chiều rộng khớp với bảng so sánh
        table = Table(data, colWidths=[9.5*cm, 7*cm])  # Giảm từ 10.5*cm và 8*cm
        
        # Thiết lập style cho bảng
        table_style = TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), self.light_blue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
        
        table.setStyle(table_style)
        return table

    def create_industry_peers_table(self, peer_data):
        """Create a table for industry peer comparison"""
        if not peer_data or len(peer_data) == 0:
            # If no peer data, return empty list
            return []
            
        # Set up column headers
        headers = [
            Paragraph('Công ty', self.styles['TableHeader']), 
            Paragraph('P/E', self.styles['TableHeader']), 
            Paragraph('Vốn hóa (tỷ)', self.styles['TableHeader']), 
            Paragraph('Tăng trưởng<br/>Doanh thu', self.styles['TableHeader']), 
            Paragraph('Tăng trưởng<br/>EPS', self.styles['TableHeader']), 
            Paragraph('ROA', self.styles['TableHeader']), 
            Paragraph('ROE', self.styles['TableHeader'])
        ]
        
        # Create data rows
        data = [headers]
        
        # Add each peer company to the table
        for i, peer in enumerate(peer_data):
            # Use Paragraph objects to ensure proper font rendering
            # First row (current company) uses bold style
            style_to_use = self.styles['PeerTableCompanyCell'] if i == 0 else self.styles['TableCellLeft']
            
            row = [
                Paragraph(peer.get('company_name', 'N/A'), style_to_use),
                Paragraph(peer.get('pe', 'N/A'), self.styles['TableCell']),
                Paragraph(peer.get('market_cap', 'N/A'), self.styles['TableCell']),
                Paragraph(peer.get('revenue_growth', 'N/A'), self.styles['TableCell']),
                Paragraph(peer.get('eps_growth', 'N/A'), self.styles['TableCell']),
                Paragraph(peer.get('roa', 'N/A'), self.styles['TableCell']),
                Paragraph(peer.get('roe', 'N/A'), self.styles['TableCell'])
            ]
            data.append(row)
            
        # Set column widths
        colWidths = [6*cm, 1.5*cm, 2*cm, 2*cm, 2*cm, 1.5*cm, 1.5*cm]  # Giảm cột đầu từ 7*cm xuống 6*cm và các cột Tăng trưởng từ 2.5*cm xuống 2*cm
        
        # Create table
        table = Table(data, colWidths=colWidths, repeatRows=1)
        
        # Style the table
        table_style = TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (-1, 0), self.blue_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            
            # Alternating row colors
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ])
        
        # Add alternating row colors
        for i in range(1, len(data), 2):
            table_style.add('BACKGROUND', (0, i), (-1, i), self.light_blue)
            
        table.setStyle(table_style)
        return table

    def create_page3(self, doc, company_data, peer_data, valuation_data, recommendation_data):
        """Tạo nội dung cho trang định giá và khuyến nghị"""
        story = []
        width, height = A4
            
        if valuation_data is None:
            valuation_data = {}  # Dict rỗng nếu không có dữ liệu
        
        # Tiêu đề phần định giá
        title = Paragraph("Phương pháp định giá", self.styles['SectionTitle'])
        story.append(title)
        story.append(Spacer(1, 10*mm))  # Tăng khoảng trống giữa tiêu đề và văn bản giải thích
        
        # Giải thích phương pháp định giá
        explanation_text = """Chúng tôi sử dụng phương pháp dự báo dòng tiền với các chỉ số cơ bản doanh nghiệp để định giá cổ phiếu. Giá mục tiêu được xác định dựa trên kết quả kinh doanh quá khứ và triển vọng tăng trưởng của công ty."""
        explanation = Paragraph(explanation_text, self.styles['ValuationText'])
        story.append(explanation)
        story.append(Spacer(1, 10*mm))  # Tăng khoảng trống
        
        # Thêm bảng so sánh doanh nghiệp cùng ngành
        if peer_data and len(peer_data) > 0:
            # Tiêu đề bảng so sánh doanh nghiệp
            peer_title = Paragraph("So sánh doanh nghiệp cùng ngành", self.styles['SectionTitle'])
            story.append(peer_title)
            story.append(Spacer(1, 5*mm))
            
            # Tạo bảng so sánh
            peer_table = self.create_industry_peers_table(peer_data)
            story.append(peer_table)
            
        # Bảng tóm tắt định giá - chỉ sử dụng một cột cho bảng này
        if valuation_data:
            valuation_table = self.create_valuation_summary_table(valuation_data)
            story.append(valuation_table)
            story.append(Spacer(1, 15*mm))  # Khoảng cách trước bảng doanh nghiệp cùng ngành
        
        # Thêm bình luận về định giá từ Gemini API
        try:
            from ..module_report.api_gemini import generate_valuation_commentary
            
            # Lấy mã cổ phiếu từ company_data
            symbol = company_data.get('symbol', 'N/A')
            
            # Gọi hàm từ api_gemini.py để tạo bình luận
            commentary = generate_valuation_commentary(symbol, valuation_data, peer_data)
            
            # Nếu có bình luận, thêm vào story
            if commentary and commentary != "Không thể tạo bình luận về định giá.":
                commentary_title = Paragraph("Nhận xét về định giá", self.styles['SectionTitle'])
                story.append(commentary_title)
                story.append(Spacer(1, 5*mm))
                
                commentary_text = Paragraph(commentary, self.styles['ValuationText'])
                story.append(commentary_text)
                story.append(Spacer(1, 10*mm))
        except Exception as e:
            print(f"Lỗi khi tạo bình luận định giá: {str(e)}")
            # Không làm gì nếu có lỗi, chỉ bỏ qua phần bình luận
            
        return story
