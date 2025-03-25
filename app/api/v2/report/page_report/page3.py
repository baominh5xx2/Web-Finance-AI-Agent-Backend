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
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER,
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCell',
            fontName=normal_font,
            fontSize=9,
            alignment=TA_CENTER,
            leading=11
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCellLeft',
            fontName=normal_font,
            fontSize=9,
            alignment=TA_LEFT,
            leading=11
        ))
        
        self.styles.add(ParagraphStyle(
            name='SummaryRow',
            fontName=title_font,
            fontSize=9,
            alignment=TA_LEFT,
            leading=11
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
        
    def create_peer_comparison_table(self, peer_data):
        """Tạo bảng so sánh với các doanh nghiệp trong ngành"""
        # Headers cho bảng
        headers = [
            'Công ty', 'Quốc gia', 'P/E', 'Vốn hóa (tỷ USD)', 'Tăng trưởng doanh thu (%)', 
            'Tăng trưởng EPS TTM (%)', 'ROA (%)', 'ROE (%)'
        ]
        
        # Chuyển đổi header thành Paragraph
        header_cells = [Paragraph(h, self.styles['TableHeader']) for h in headers]
        
        # Tạo các dòng dữ liệu
        data = [header_cells]
        
        # Thêm dữ liệu từ các công ty trong cùng ngành
        for peer in peer_data:
            company = Paragraph(peer.get('company_name', 'N/A'), self.styles['TableCellLeft'])
            country = Paragraph(peer.get('country', 'N/A'), self.styles['TableCell'])
            
            # Định dạng lại giá trị P/E để hiển thị đẹp hơn
            pe_value = peer.get('pe', 'N/A')
            pe = Paragraph(pe_value, self.styles['TableCell'])
            
            market_cap = Paragraph(f"{peer.get('market_cap', 'N/A')}", self.styles['TableCell'])
            
            # Đảm bảo các giá trị % có ký hiệu % nếu chưa có
            revenue_growth = peer.get('revenue_growth', 'N/A')
            if revenue_growth != 'N/A' and not revenue_growth.endswith('%'):
                revenue_growth = f"{revenue_growth}%"
            
            eps_growth = peer.get('eps_growth', 'N/A')
            if eps_growth != 'N/A' and not eps_growth.endswith('%'):
                eps_growth = f"{eps_growth}%"
                
            roa = peer.get('roa', 'N/A')
            if roa != 'N/A' and not roa.endswith('%'):
                roa = f"{roa}%"
                
            roe = peer.get('roe', 'N/A')
            if roe != 'N/A' and not roe.endswith('%'):
                roe = f"{roe}%"
            
            # Tạo Paragraph cho các giá trị
            revenue_growth_cell = Paragraph(revenue_growth, self.styles['TableCell'])
            eps_growth_cell = Paragraph(eps_growth, self.styles['TableCell'])
            roa_cell = Paragraph(roa, self.styles['TableCell'])
            roe_cell = Paragraph(roe, self.styles['TableCell'])
            
            data.append([company, country, pe, market_cap, revenue_growth_cell, eps_growth_cell, roa_cell, roe_cell])
        
        # Tạo bảng
        col_widths = [4*cm, 2*cm, 1.5*cm, 2.5*cm, 3*cm, 3*cm, 2*cm, 2*cm]
        table = Table(data, colWidths=col_widths)
        
        # Thiết lập style cho bảng
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
        data = []
        
        # Định dạng lại các giá trị P/E để thêm 'x' vào cuối nếu cần      
        pe_target = valuation_data.get('pe_target', 'N/A')
        
        # Định dạng giá trị upside với dấu % nếu cần
        upside = valuation_data.get('upside', 'N/A')
        if upside != 'N/A' and not upside.endswith('%'):
            upside = f"{upside}%"
        
        # Các dòng dữ liệu định giá        
        eps_target = valuation_data.get('eps_target', 'N/A')
        price_target = valuation_data.get('price_target', 'N/A')
        current_price = valuation_data.get('current_price', 'N/A')
        
        # Thêm các dòng vào bảng - đã xóa các dòng P/E trung bình, trung vị và trung bình 10 năm
        data.append([Paragraph('P/E mục tiêu:', self.styles['SummaryRow']), 
                     Paragraph(f"{pe_target}", self.styles['TableCell'])])
        data.append([Paragraph('EPS mục tiêu (VND):', self.styles['SummaryRow']), 
                     Paragraph(f"{eps_target}", self.styles['TableCell'])])
        data.append([Paragraph('Giá mục tiêu (VND):', self.styles['SummaryRow']), 
                     Paragraph(f"{price_target}", self.styles['TableCell'])])
        data.append([Paragraph('Giá hiện tại (VND):', self.styles['SummaryRow']), 
                     Paragraph(f"{current_price}", self.styles['TableCell'])])
        data.append([Paragraph('Tiềm năng tăng/giảm (%):', self.styles['SummaryRow']), 
                     Paragraph(f"{upside}", self.styles['TableCell'])])
        
        # Tạo bảng với chiều rộng khớp với bảng so sánh
        table = Table(data, colWidths=[12*cm, 8*cm])  # Điều chỉnh tổng chiều rộng cho phù hợp
        
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
   
    def create_page3(self, doc, company_data, peer_data, valuation_data, recommendation_data):
        """Tạo nội dung cho trang định giá và khuyến nghị"""
        story = []
        width, height = A4
        
        # Kiểm tra đảm bảo có dữ liệu
        if peer_data is None:
            peer_data = []  # Mảng rỗng nếu không có dữ liệu
            
        if valuation_data is None:
            valuation_data = {}  # Dict rỗng nếu không có dữ liệu
        
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
        if peer_data:
            peer_table = self.create_peer_comparison_table(peer_data)
            story.append(peer_table)
            story.append(Spacer(1, 10*mm))  # Tăng khoảng trống
        
        # Bảng tóm tắt định giá - chỉ sử dụng một cột cho bảng này
        if valuation_data:
            valuation_table = self.create_valuation_summary_table(valuation_data)
            story.append(valuation_table)
        
        # Không sử dụng Table trong Table nữa để tránh vấn đề về định dạng
        return story
