from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import io
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.font_manager as fm
from pathlib import Path
import datetime

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
        elements.append(Spacer(1, 1*inch))
        # Main heading
        elements.append(Paragraph('<b>Tổng quan doanh nghiệp</b>', self.heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
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
        """Create a combined chart with revenue, profit and growth rates"""
        # Create a single figure
        fig, ax1 = plt.subplots(figsize=(10, 6))  # Larger figure for better visibility
        
        years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
        revenue = [5756, 8941, 12637, 14860, 12224, 11613, 28206, 23128, 18621, 20707]
        profit = [126, 517, 707, 57, 47, 295, 222, -124, 117, 453]
        
        revenue_growth = [0]
        profit_growth = [0]
        for i in range(1, len(revenue)):
            revenue_growth.append(((revenue[i] - revenue[i-1]) / revenue[i-1]) * 100)
            profit_growth.append(((profit[i] - profit[i-1]) / profit[i-1]) * 100)
        
        x = np.arange(len(years))
        width = 0.35  # Chiều rộng mỗi cột
        
        # Vẽ cột doanh thu và lợi nhuận trên trục y trái
        bars1 = ax1.bar(x - width/2, revenue, width, label='Doanh thu (tỷ đồng)', color='#0052cc')
        bars2 = ax1.bar(x + width/2, profit, width, label='Lợi nhuận (tỷ đồng)', color='#ff9900')
        
        # Thêm giá trị doanh thu và lợi nhuận
        for i, (r, p) in enumerate(zip(revenue, profit)):
            # Doanh thu - chỉ hiển thị ở một số điểm
            if i % 2 == 0:
                ax1.annotate(f'{r}', xy=(i - width/2, r), xytext=(0, 5), 
                            textcoords='offset points', ha='center', va='bottom',
                            color='#0052cc', fontweight='bold')
            
            # Lợi nhuận
            va = 'bottom' if p >= 0 else 'top'
            offset = 5 if p >= 0 else -15
            ax1.annotate(f'{p}', xy=(i + width/2, p), xytext=(0, offset), 
                        textcoords='offset points', ha='center', va=va,
                        color='#ff9900', fontweight='bold')
        
        # Thiết lập trục y trái
        ax1.set_xlabel('Năm', fontname='DejaVu Sans')
        ax1.set_ylabel('Giá trị (tỷ đồng)', fontname='DejaVu Sans')
        ax1.set_xticks(x)
        ax1.set_xticklabels(years)
        ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        # Điều chỉnh giới hạn trục y trái
        min_val = min(min(profit), 0)
        max_val = max(revenue) * 1.05
        ax1.set_ylim(min_val * 1.1 if min_val < 0 else 0, max_val)
        
        # Tạo trục y thứ hai cho tỷ lệ tăng trưởng
        ax2 = ax1.twinx()
        
        # Vẽ đường tăng trưởng trên trục y phải
        line1 = ax2.plot(x, revenue_growth, 'c-', label='Tăng trưởng DT (%)', 
                        linewidth=2, marker='o', markersize=6, color='#00cccc')
        line2 = ax2.plot(x, profit_growth, 'r-', label='Tăng trưởng LN (%)', 
                        linewidth=2, marker='s', markersize=6, color='#cc0000')
        
        # Ẩn trục y bên phải nhưng vẫn giữ các đường tăng trưởng
        ax2.set_yticklabels([])
        ax2.tick_params(right=False)
        ax2.spines['right'].set_visible(False)
        
        # Điều chỉnh giới hạn trục y phải
        growth_min = min(min(revenue_growth), min(profit_growth))
        growth_max = max(max(revenue_growth), max(profit_growth))
        padding = (growth_max - growth_min) * 0.1
        ax2.set_ylim(growth_min - padding, growth_max + padding)
        
        # Thêm lưới cho trục y phải
        ax2.grid(True, axis='y', linestyle=':', alpha=0.3, color='#555555')
        
        # Tiêu đề và chú thích
        plt.title('Doanh thu, Lợi nhuận và Tỷ lệ tăng trưởng Nam Kim 2015 - 2024', 
                fontname='DejaVu Sans', fontsize=14)
        
        # Kết hợp các chú thích từ cả hai trục
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9)
        
        plt.tight_layout()
        
        # Lưu biểu đồ
        chart_buffer = io.BytesIO()
        fig.savefig(chart_buffer, format='png', bbox_inches='tight')
        chart_buffer.seek(0)
        plt.close('all')
        
        # Tạo bảng chứa biểu đồ
        chart_table = Table([
            [Image(chart_buffer, width=7*inch, height=4.5*inch)]
        ])
        
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return chart_table
    
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
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 9)
        canvas.drawRightString(width - 1*cm, height - 12*mm, f"Ngày: {current_date}")
        
        # Vẽ footer
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, 0, width, 10*mm, fill=1, stroke=0)
        
        # Số trang
        canvas.setFillColor(colors.white)
        canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 9)
        canvas.drawRightString(width - 1*cm, 3.5*mm, f"Trang 4")
        
        # Thông tin công ty
        canvas.drawString(1*cm, 3.5*mm, "FinBot - Trí tuệ tài chính cho mọi người")

# For testing purposes
if __name__ == "__main__":
    buffer = io.BytesIO()
    page4 = Page4()
    page4.create_page4(buffer)
    with open("page4_test.pdf", "wb") as f:
        f.write(buffer.getvalue())
