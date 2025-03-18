import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageTemplate, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .finance_calc import get_market_data, current_price
from vnstock import Vnstock
from ..page_report.page1 import Page1
from ..page_report.page2 import Page2

class PDFReport:
    def __init__(self):
        # Đăng ký font
        self.font_added = self._setup_fonts()
        self.page1 = Page1(font_added=self.font_added)
        self.page2 = Page2(font_added=self.font_added)
    
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
    
    def create_stock_report(self, output_path, company_data, recommendation_data, market_data=None, analysis_data=None, projection_data=None):
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
        
        # Tạo template cho trang 1
        template1 = PageTemplate(
            id='page1',
            frames=[
                Frame(0, height - 3*cm, width, 3*cm),
                Frame(0, 0, 6.5*cm, height - 3*cm, id='sidebar'),
                Frame(6.5*cm, 0, width - 6.5*cm, height - 3*cm)
            ],
            onPage=lambda canvas, doc: self.page1._draw_page_template(canvas, doc, company_data)
        )
        
        # Tạo template cho trang 2
        template2 = PageTemplate(
            id='page2',
            frames=[
                Frame(0, 0, width, height)
            ],
            onPage=lambda canvas, doc: self.page2._draw_page_template(canvas, doc, company_data)
        )
        
        # Thêm các templates vào document
        doc.addPageTemplates([template1, template2])
        
        # Tạo nội dung cho trang 1
        story = self.page1.create_page1(doc, company_data, recommendation_data, market_data, analysis_data)
        
        # Chuyển sang trang 2
        story.append(NextPageTemplate('page2'))
        story.append(PageBreak())
        
        # Thêm nội dung trang 2 nếu có dữ liệu dự phóng
        page2_content = self.page2.create_page2(doc, company_data, projection_data)
        story.extend(page2_content)
        
        # Xuất PDF
        doc.build(story)
        return output_path

