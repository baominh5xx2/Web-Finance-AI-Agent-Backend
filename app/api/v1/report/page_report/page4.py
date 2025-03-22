from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import io
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.font_manager as fm
from pathlib import Path

class Page4:
    def __init__(self, font_added=True):
        self.font_added = font_added
        self.styles = getSampleStyleSheet()
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
        
        # Main heading
        elements.append(Paragraph('<b>Tổng quan doanh nghiệp</b>', self.heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Subheading
        elements.append(Paragraph('<u>Lịch sử hình thành doanh nghiệp</u>', self.subheading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Company history text
        company_history = """
        Công ty Cổ phần Thép Nam Kim (NKG) được thành lập vào ngày 23/12/2002, đến năm 2011, công 
        ty được niêm yết trên sàn chứng khoán HOSE với mã cổ phiếu NKG. Công ty Cổ phần Thép Nam 
        Kim là một doanh nghiệp chuyên sản xuất tôn mạ hàng đầu tại Việt Nam. Công ty luôn tiên 
        phong trong đầu tư công nghệ để cung cấp những sản phẩm đạt tiêu chuẩn chất lượng tốt nhất 
        đến khách hàng trong nước và quốc tế. Hiện sản phẩm của Nam Kim được tin dùng trên toàn 
        quốc và xuất đến hơn 50 quốc gia trên toàn cầu.
        
        Sản phẩm chính chính của Nam Kim bao gồm các loại tôn mạ và ống thép. Trong đó mảng tôn 
        mạ chiếm gần 90% cơ cấu sản phẩm của Nam Kim.
        """
        elements.append(Paragraph(company_history, self.normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add charts
        chart_table = self._create_charts()
        elements.append(chart_table)
        
        # Add source note
        source_text = "Nguồn: Báo cáo công ty, Chứng khoán Shinhan Việt Nam"
        elements.append(Paragraph(source_text, self.source_style))
        
        # If buffer is provided, build a standalone PDF
        if pdf_buffer is not None:
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            doc.build(elements)
            return pdf_buffer
            
        # Otherwise return elements for inclusion in a larger document
        return elements
        
    def _create_charts(self):
        """Create the revenue and profit chart only (removed pie chart)"""
        # Create revenue and profit chart
        plt.figure(figsize=(8, 5))  # Increased size for better visibility
        
        years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
        revenue = [5000, 7000, 10000, 12000, 14000, 11000, 14000, 10000, 27000, 21000]
        profit = [1000, 2000, 6000, 3000, 3500, 3000, 3500, 2500, 7000, 5000]
        
        revenue_growth = [0]
        profit_growth = [0]
        for i in range(1, len(revenue)):
            revenue_growth.append(((revenue[i] - revenue[i-1]) / revenue[i-1]) * 100)
            profit_growth.append(((profit[i] - profit[i-1]) / profit[i-1]) * 100)
        
        x = np.arange(len(years))
        width = 0.4
        
        fig, ax1 = plt.subplots(figsize=(10, 6))  # Larger figure for better visibility
        
        # Bar chart for revenue
        bars = ax1.bar(x, revenue, width, label='Doanh thu (tỷ đồng)', color='#0052cc')
        
        # Set up the second y-axis for growth rates
        ax2 = ax1.twinx()
        
        # Line chart for revenue growth
        ax2.plot(x, revenue_growth, 'c-', label='Tăng trưởng DT (%)')
        
        # Line chart for profit growth
        ax2.plot(x, profit_growth, 'brown', label='Tăng trưởng LN (%)')
        
        # Labels and title
        ax1.set_xlabel('Năm', fontname='DejaVu Sans')
        ax1.set_ylabel('Doanh thu (tỷ đồng)', color='#0052cc', fontname='DejaVu Sans')
        ax2.set_ylabel('Tăng trưởng (%)', fontname='DejaVu Sans')
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(years)
        
        plt.title('Doanh thu và lợi nhuận Nam Kim 2014 - 2024', fontname='DejaVu Sans')
        
        # Add legend
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left')
        
        plt.tight_layout()
        
        chart_buffer = io.BytesIO()
        plt.savefig(chart_buffer, format='png', bbox_inches='tight')
        chart_buffer.seek(0)
        plt.close()
        
        # Create table with just the revenue chart
        chart_table = Table([
            [Image(chart_buffer, width=7*inch, height=4*inch)]  # Increased size
        ])
        
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return chart_table
    
    def _draw_page_template(self, canvas, doc, company_data=None):
        """Template drawing method for page template compatibility"""
        # This method is a placeholder for consistency with other page classes
        # It would be called by page templates
        pass

# For testing purposes
if __name__ == "__main__":
    buffer = io.BytesIO()
    page4 = Page4()
    page4.create_page4(buffer)
    with open("page4_test.pdf", "wb") as f:
        f.write(buffer.getvalue())
