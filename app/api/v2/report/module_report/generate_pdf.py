import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageTemplate, PageBreak, Table, TableStyle, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .finance_calc import get_market_data, current_price
from vnstock import Vnstock
from ..page_report.page1 import Page1
from ..page_report.page2 import Page2
from ..page_report.page3 import Page3
from ..page_report.page4 import Page4
from ..page_report.page5 import Page5
import io

class PDFReport:
    def __init__(self):
        # Đăng ký font
        self.font_added = self._setup_fonts()
        self.page1 = Page1(font_added=self.font_added)
        self.page2 = Page2(font_added=self.font_added)
        self.page3 = Page3(font_added=self.font_added)
        self.page4 = Page4(font_added=self.font_added)
        self.page5 = Page5(font_added=self.font_added)
        
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
    
    def create_stock_report(self, output_path, company_data, recommendation_data, market_data=None, analysis_data=None, projection_data=None, page2_projection_data=None, peer_data=None, valuation_data=None):
        """Tạo báo cáo chứng khoán theo mẫu mới"""
        width, height = A4
        
        # Tạo document với multiple frames
        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0,
            leftMargin=0,
            topMargin=0,
            bottomMargin=0,
        )
        
        # Lưu company_data vào biến cục bộ để sử dụng trong các closure
        _company_data = company_data
        
        # Tạo template cho trang 1
        template1 = PageTemplate(
            id='page1',
            frames=[
                Frame(0, height - 3*cm, width, 3*cm),
                Frame(0, 0, 6.5*cm, height - 3*cm, id='sidebar'),
                Frame(6.5*cm, 0, width - 6.5*cm, height - 3*cm)
            ],
            onPage=lambda canvas, doc: self.page1._draw_page_template(canvas, doc, _company_data)
        )
        
        # Tạo template cho trang 2
        template2 = PageTemplate(
            id='page2',
            frames=[
                Frame(0, 0, width, height)
            ],
            onPage=lambda canvas, doc: self.page2._draw_page_template(canvas, doc, _company_data)
        )
        
        # Tạo template cho trang 3
        template3 = PageTemplate(
            id='page3',
            frames=[
                Frame(1*cm, 1*cm, width-2*cm, height-2*cm)
            ],
            onPage=lambda canvas, doc: self.page3._draw_page_template(canvas, doc, _company_data)
        )
        
        # Tạo template cho trang 4
        template4 = PageTemplate(
            id='page4',
            frames=[
                Frame(1*cm, 1*cm, width-2*cm, height-2*cm)
            ],
            onPage=lambda canvas, doc: self.page4._draw_page_template(canvas, doc, _company_data)
        )
        
        # Tạo template cho trang 5
        template5 = PageTemplate(
            id='page5',
            frames=[
                Frame(0, 0, width, height)
            ],
            onPage=lambda canvas, doc: self.page5._draw_page_template(canvas, doc, _company_data)
        )
        
        # Thêm các templates vào document
        doc.addPageTemplates([template1, template2, template3, template4, template5])
        
        # Tạo nội dung cho trang 1 - sử dụng projection_data cho page1
        story = self.page1.create_page1(doc, company_data, recommendation_data, market_data, analysis_data, projection_data)
        
        # Chuyển sang trang 2
        story.append(NextPageTemplate('page2'))
        story.append(PageBreak())
        
        # Thêm nội dung trang 2 - sử dụng page2_projection_data riêng biệt cho page2
        # Fallback to projection_data if page2_projection_data is None (for backwards compatibility)
        page2_data = page2_projection_data if page2_projection_data is not None else projection_data
        page2_content = self.page2.create_page2(doc, company_data, page2_data)
        story.extend(page2_content)
        
        # Chuyển sang trang 3 nếu có dữ liệu định giá
        if valuation_data:
            story.append(NextPageTemplate('page3'))
            story.append(PageBreak())
            
            # Thêm nội dung trang 3 - sử dụng peer_data thay vì list rỗng
            page3_content = self.page3.create_page3(doc, company_data, peer_data, valuation_data, recommendation_data)
            story.extend(page3_content)
        
        # Chuyển sang trang 4
        story.append(NextPageTemplate('page4'))
        story.append(PageBreak())
        
        # Thêm nội dung trang 4
        page4_content = self.page4.create_page4(company_data=company_data)
        story.extend(page4_content)
        
        # Chuyển sang trang 5
        story.append(NextPageTemplate('page5'))
        story.append(PageBreak())
        
        # Thêm nội dung trang 5
        page5_content = self.page5.create_page5(company_data=company_data)
        story.extend(page5_content)
        # Xuất PDF
        doc.build(story)
        return output_path

def generate_page4_pdf(output_path="company_overview.pdf"):
    """
    Generate a PDF file with company overview information using page4.
    
    Args:
        output_path (str): Path where the PDF file will be saved
        
    Returns:
        str: Path to the generated PDF file
    """
    # Create a buffer for the PDF
    buffer = io.BytesIO()
    
    # Create Page4 instance and generate content
    page4 = Page4()
    page4.create_page4(buffer)
    
    # Save the buffer to a file
    buffer.seek(0)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    
    print(f"PDF saved to {output_path}")
    return output_path

def generate_page5_pdf(output_path="financial_ratios.pdf"):
    """
    Generate a PDF file with financial ratios information using page5.
    
    Args:
        output_path (str): Path where the PDF file will be saved
        
    Returns:
        str: Path to the generated PDF file
    """
    # Create a buffer for the PDF
    buffer = io.BytesIO()
    
    # Create Page5 instance and generate content
    page5 = Page5()
    page5.create_page5(buffer)
    
    # Save the buffer to a file
    buffer.seek(0)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    
    print(f"PDF saved to {output_path}")
    return output_path



