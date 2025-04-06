from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.font_manager as fm
from pathlib import Path
import datetime as dt
import matplotlib.dates as mdates

class Page4:
    def __init__(self, font_added=True):
        self.font_added = font_added
        self.styles = getSampleStyleSheet()
        # Define blue color for header and footer
        self.blue_color = colors.HexColor('#0066CC')
        self.heading_style = ParagraphStyle(
            'Heading1',
            parent=self.styles['Heading1'],
            fontName='DejaVuSans',
            fontSize=18,
            textColor=colors.blue,
            spaceAfter=12,
            alignment=1  # Center alignment
        )
        self.subheading_style = ParagraphStyle(
            'Heading2',
            parent=self.styles['Heading2'],
            fontName='DejaVuSans',
            fontSize=14,
            textColor=colors.blue,
            spaceAfter=8
        )
        self.normal_style = ParagraphStyle(
            'Normal',
            parent=self.styles['Normal'],
            fontName='DejaVuSans',
            fontSize=10,
            leading=14,
            spaceAfter=8
        )
        self.source_style = ParagraphStyle(
            'Source',
            parent=self.styles['Normal'],
            fontName='DejaVuSans',
            fontSize=8,
            alignment=1  # Center alignment
        )
    
    def __call__(self, pdf_buffer):
        """
        Legacy support for direct function call style
        """
        return self.create_page4(pdf_buffer)
    
    def create_page4(self, pdf_buffer=None, company_data=None):
        """
        Create page 4 content
        
        If pdf_buffer is provided, builds a standalone PDF and returns the buffer.
        If not, returns a list of flowable elements for inclusion in a larger document.
        """
        elements = []
        elements.append(Spacer(1, 0.7*inch))  # Giảm khoảng cách trên cùng
        # Main heading
        elements.append(Paragraph('<b>Tổng quan doanh nghiệp</b>', self.heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Subheading
        elements.append(Paragraph('<u>Lịch sử hình thành doanh nghiệp</u>', self.subheading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Company history text - split into separate paragraphs instead of one block
        history_text1 = """Thành lập vào ngày 23/12/2002, NKG nhanh chóng khẳng định vị thế là một trong những nhà sản xuất tôn mạ hàng đầu Việt Nam. Cổ phiếu NKG chính thức niêm yết trên sàn HOSE từ ngày 21/01/2011, đánh dấu bước ngoặt quan trọng trong quá trình phát triển."""
        
        history_text2 = """Là một doanh nghiệp chuyên sản xuất tôn mạ hàng đầu tại Việt Nam, Tôn Nam Kim luôn tiên phong trong đầu tư công nghệ để cung cấp những sản phẩm đạt tiêu chuẩn chất lượng tốt nhất đến khách hàng trong nước và quốc tế. Hiện sản phẩm Tôn Nam Kim được tin dùng trên toàn quốc và xuất khẩu đến hơn 65 quốc gia, vùng lãnh thổ trên toàn cầu."""
        
        history_text3 = """Tôn Nam Kim sử dụng trang thiết bị công nghệ hiện đại của các tập đoàn hàng đầu thế giới trong ngành công nghiệp thép như SMS (Đức), Drever (Bỉ). Nguồn nguyên liệu thép được lựa chọn từ các tập đoàn lớn nổi tiếng như Nippon Steel (Nhật Bản), Hyundai Steel (Hàn Quốc), CSC (Đài Loan), Formosa (Việt Nam) … Hơn nữa, ở tất cả các công đoạn sản xuất, sản phẩm đều phải trải qua các quy trình kiểm soát chất lượng nghiêm ngặt. Vì vậy Tôn Nam Kim đã đạt được các tiêu chuẩn chất lượng khắt khe nhất thế giới như JIS (Nhật Bản), AS (Úc), ASTM (Mỹ) và EN (Châu Âu), ISO 9001, và ISO 14001. NKG sở hữu hệ thống nhà máy hiện đại với tổng công suất lớn, không chỉ phục vụ thị trường trong nước mà còn xuất khẩu sang nhiều quốc gia trên thế giới. Cơ cấu sản phẩm của NKG khá cân đối, với tôn mạ là sản phẩm chủ lực, bên cạnh đó ống thép và xà gồ cũng đóng góp đáng kể vào doanh thu chung của công ty. Với chiến lược phát triển bền vững và tầm nhìn dài hạn, NKG hứa hẹn sẽ tiếp tục gặt hái được nhiều thành công trong tương lai."""
        
        history_text4 = """Với công nghệ tiên tiến, đội ngũ nhân sự có chuyên môn sâu và nhiều năm kinh nghiệm, Tôn Nam Kim cam kết cung cấp những sản phẩm có giá trị chất lượng bền vững, thân thiện với môi trường và mang lại hiệu quả kinh tế cao cho khách hàng."""
        
        # Add each paragraph separately with spacing between them
        elements.append(Paragraph(history_text1, self.normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(history_text2, self.normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(history_text3, self.normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(history_text4, self.normal_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Add source note
        source_text = ""
        elements.append(Paragraph(source_text, self.source_style))
        
        # If buffer is provided, build a standalone PDF
        if pdf_buffer is not None:
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=36, bottomMargin=18)
            doc.build(elements)
            return pdf_buffer
            
        # Otherwise return elements for inclusion in a larger document
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
        header_text = f"{company_name} ({symbol}) - Tổng quan Công ty"
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
        canvas.drawRightString(width - 1*cm, 3.5*mm, f"Trang 4")

# For testing purposes
if __name__ == "__main__":
    buffer = io.BytesIO()
    page4 = Page4()
    page4.create_page4(buffer)
    with open("page4_test.pdf", "wb") as f:
        f.write(buffer.getvalue())
