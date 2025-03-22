from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import io
import datetime as dt
import os

class Page6:
    def __init__(self, font_added=True):
        self.font_added = font_added
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """Thiết lập các styles cho Page6"""
        # Màu sắc chính
        self.blue_color = colors.HexColor('#0066CC')
        self.light_blue = colors.HexColor('#E6F0FA')
        
        # Sử dụng font DejaVuSans nếu đã đăng ký, nếu không thì dùng Helvetica
        title_font = 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'
        normal_font = 'DejaVuSans' if self.font_added else 'Helvetica'
        
        # Style cho tiêu đề
        self.styles.add(ParagraphStyle(
            name='Page6Title',
            fontName=title_font,
            fontSize=16,
            textColor=self.blue_color,
            alignment=TA_CENTER,
            spaceAfter=0.3*inch
        ))
        
        # Style cho tiêu đề phần
        self.styles.add(ParagraphStyle(
            name='Page6SectionTitle',
            fontName=title_font,
            fontSize=14,
            textColor=self.blue_color,
            alignment=TA_LEFT,
            spaceAfter=0.2*inch
        ))
        
        # Style cho văn bản thông thường
        self.styles.add(ParagraphStyle(
            name='Page6Normal',
            fontName=normal_font,
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=0.1*inch
        ))
        
        # Style cho nguồn dữ liệu
        self.styles.add(ParagraphStyle(
            name='Page6Source',
            fontName=normal_font,
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_RIGHT,
            spaceAfter=0.05*inch
        ))
    
    def create_page6(self, pdf_buffer=None, company_data=None):
        """
        Tạo nội dung cho trang 6
        
        Args:
            pdf_buffer: Buffer để ghi PDF vào (nếu tạo PDF độc lập)
            company_data: Dữ liệu công ty
        
        Returns:
            Danh sách các phần tử để đưa vào story nếu tạo trong báo cáo đầy đủ,
            hoặc tạo file PDF nếu pdf_buffer được cung cấp
        """
        # Tạo danh sách các elements
        elements = []
        
        # Tiêu đề trang
        title = Paragraph("Trang Thông tin Bổ sung", self.styles['Page6Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Phần 1: Mẫu content
        section_title = Paragraph("Phần 1: Nội dung mẫu", self.styles['Page6SectionTitle'])
        elements.append(section_title)
        
        # Nội dung mẫu
        content = Paragraph("""
        Đây là nội dung mẫu cho trang 6. Trang này có thể được sử dụng để hiển thị 
        thông tin bổ sung về công ty, phân tích sâu hơn, hoặc bất kỳ nội dung nào khác 
        mà bạn muốn đưa vào báo cáo tài chính.
        """, self.styles['Page6Normal'])
        elements.append(content)
        elements.append(Spacer(1, 0.2*inch))
        
        # Phần 2: Mẫu bảng
        section_title = Paragraph("Phần 2: Bảng dữ liệu mẫu", self.styles['Page6SectionTitle'])
        elements.append(section_title)
        
        # Tạo bảng mẫu
        data = [
            ['STT', 'Chỉ tiêu', 'Giá trị'],
            ['1', 'Chỉ tiêu 1', '1,000,000'],
            ['2', 'Chỉ tiêu 2', '2,500,000'],
            ['3', 'Chỉ tiêu 3', '3,750,000'],
            ['4', 'Chỉ tiêu 4', '5,000,000'],
        ]
        
        table = Table(data, colWidths=[1*cm, 10*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.blue_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Nếu pdf_buffer được cung cấp thì tạo PDF độc lập
        if pdf_buffer is not None:
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                topMargin=1.5*cm,
                leftMargin=1.5*cm,
                rightMargin=1.5*cm,
                bottomMargin=1.5*cm
            )
            doc.build(elements)
            return None
        
        # Trả về elements để sử dụng trong báo cáo đầy đủ
        return elements
    
    def _draw_page_template(self, canvas, doc, company_data=None):
        """Vẽ header và footer cho trang"""
        width, height = A4
    
        # Vẽ header
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, height - 20*mm, width, 20*mm, fill=1, stroke=0)
        
        # Tên công ty và mã chứng khoán
        canvas.setFillColor(colors.white)
        canvas.setFont('DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold', 12)
        company_name = company_data.get('name', '') if company_data else ''
        symbol = company_data.get('symbol', '') if company_data else ''
        header_text = f"{company_name} ({symbol}) - Thông tin Bổ sung"
        canvas.drawString(1*cm, height - 12*mm, header_text)
        
        # Ngày tạo báo cáo
        current_date = dt.datetime.now().strftime("%d/%m/%Y")
        canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 9)
        canvas.drawRightString(width - 1*cm, height - 12*mm, f"Ngày: {current_date}")
        
        # Vẽ footer
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, 0, width, 10*mm, fill=1, stroke=0)
        
        # Số trang
        canvas.setFillColor(colors.white)
        canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 9)
        canvas.drawRightString(width - 1*cm, 3.5*mm, f"Trang 6")
        
        # Thông tin công ty
        canvas.drawString(1*cm, 3.5*mm, "FinBot - Trí tuệ tài chính cho mọi người")

# For testing purposes
if __name__ == "__main__":
    # Create a buffer to write the PDF to
    buffer = io.BytesIO()
    
    # Create Page6 instance and generate content
    page6 = Page6()
    page6.create_page6(buffer)
    
    # Save the buffer to a file
    buffer.seek(0)
    with open("page6_test.pdf", "wb") as f:
        f.write(buffer.getvalue())
        
    print("PDF saved to page6_test.pdf") 