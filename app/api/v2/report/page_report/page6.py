from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.font_manager as fm
from pathlib import Path
import datetime as dt
import pandas as pd

class Page6:
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
        return self.create_page6(pdf_buffer)
    
    def create_page6(self, pdf_buffer=None, company_data=None):
        """
        Create page 6 content with financial ratio charts
        
        If pdf_buffer is provided, builds a standalone PDF and returns the buffer.
        If not, returns a list of flowable elements for inclusion in a larger document.
        """
        elements = []
        elements.append(Spacer(1, 1*inch))
        # Main heading
        elements.append(Spacer(1, 0.2*inch))
        
        # Create chart grid
        charts_table = self._create_chart_grid()
        elements.append(charts_table)
        
        # Add source note
        source_text = ""
        elements.append(Paragraph(source_text, self.source_style))
        
        # If buffer is provided, build a standalone PDF
        if pdf_buffer is not None:
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=36, bottomMargin=36)
            doc.build(elements)
            return pdf_buffer
            
        # Otherwise return elements for inclusion in a larger document
        return elements
    
    def _create_chart_grid(self):
        """Create a grid with steel price chart"""
        # Generate the main chart
        steel_chart_buffer = self._create_steel_price_chart()
        
        # Create a single-cell table with the chart
        chart_table = Table([
            [Image(steel_chart_buffer, width=7*inch, height=4.5*inch)]
        ])
        
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        return chart_table
    
    def _create_steel_price_chart(self):
        """Create steel price chart with annotations"""
        # Dữ liệu giá thép
        prices_raw = [2.48, 2.66, 2.94, 3.19, 3.31, 3.41, 3.58, 3.81, 3.93, 4.11, 4.15, 4.09, 4.02, 3.7, 3.72, 3.69, 3.35, 3.17, 3.56, 3.41, 3.55, 3.84, 3.79, 3.92, 4.1, 4.29, 4.22, 4.43, 4.38, 4.45, 4.2, 4.26, 5.12, 6.01, 6.24, 6.68, 7.37, 7.75, 7.91, 7.83, 8.3, 8.46, 8.64, 8.09, 8.04, 7.83, 8.46, 9.22, 10.57, 11.38, 12.09, 11.38, 12.43, 12.87, 13.32, 13.5, 13.58, 15.67, 15.95, 15.93, 16.55, 18.25, 16.66, 17.36, 17.34, 19.19, 17.18, 17.13, 16.45, 17.6, 19.84, 20.55, 20.65, 22.84, 24.72, 25.94, 28.26, 27.82, 28.07, 30.23, 32.52, 34.72, 34.09, 32.27, 31.24, 26.32, 27.2, 25.82, 23.22, 24.44, 23.4, 24.28, 23.0, 23.37, 20.43, 19.68, float('nan'), 24.56, 25.94, 25.88, 30.55, 31.3, 28.95, 31.3, 30.08, 28.14, 27.01, 23.69, 23.4, 21.62, 17.29, 18.61, 19.46, 18.54, 18.38, 13.98, 13.48, 14.57, 14.8, 15.5, 15.0, 13.87, 16.24, 16.94, 16.63, 17.1, 16.51, 17.92, 17.29, 16.48, 14.26, 11.76, 13.52, 12.35, 11.33, 9.35, 6.55, 7.05, 7.71, 9.78, 10.36, 10.98, 9.66, 9.54, 10.32, 10.94, 12.07, 12.27, 10.98, 10.52, 11.84, 11.68, 11.96, 13.01, 12.23, 12.39, 12.0, 11.53, 11.41, 11.02, 11.33, 11.3, 12.0, 11.37, 11.45, 12.35, 13.01, 13.09, 14.18, 13.44, 14.33, 15.07, 15.35, 15.42, 15.0, 15.19, 14.49, 14.1, 15.03, 17.02, 16.75, 16.24, 15.39, 14.92, 16.01, 14.33, 14.02, 15.0, 15.97, 17.02, 17.22, 17.84, 18.15, 18.11, 18.93, 19.2, 18.77, 18.19, 19.44, 19.79, 18.89, 18.97, 19.16, 18.19, 18.81, 18.66, 19.05, 19.86, 19.98, 19.05, 20.14, 17.1, 17.06, 17.76, 18.62, 19.32, 19.32, 19.01, 20.02, 20.02, 19.79, 18.35, 19.12, 20.02, 18.93, 18.19, 16.98, 16.55, 16.09, 17.25, 16.98, 16.24, 16.36, 16.71, 17.02, 16.9, 16.9, 16.28, 15.93, 16.32, 16.71, 14.88, 15.07, 15.11, 14.8, 14.8, 14.75, 14.6, 14.35, 13.6, 13.95, 13.3]
        
        # Nhân giá thép lên 1000 để hiển thị theo ngàn đồng
        prices = [p * 1000 for p in prices_raw]
        
        # Loại bỏ giá trị NaN
        prices_cleaned = [p for p in prices if not (isinstance(p, float) and np.isnan(p))]
        
        # Sử dụng danh sách nhãn thời gian được cung cấp
        time_labels = [
            '04/20', '06/20', '08/20', '10/20', '12/20',
            '02/21', '04/21', '06/21', '08/21', '10/21', '12/21',
            '02/22', '04/22', '06/22', '08/22', '10/22', '12/22',
            '02/23', '04/23', '06/23', '08/23', '10/23', '12/23',
            '02/24', '04/24', '06/24', '08/24', '10/24', '12/24',
            '02/25'
        ]
        
        # Tạo x_data - một mảng các điểm x đều nhau, với độ dài bằng số điểm dữ liệu giá
        x_data = np.linspace(0, 1, len(prices_cleaned))
        
        # Tạo vị trí cho nhãn thời gian - được rải đều trên trục x
        # Không cần khớp chính xác với giá trị x của dữ liệu
        time_ticks = np.linspace(0, 1, len(time_labels))
        
        # Setup figure
        plt.figure(figsize=(10, 5.5))
        ax = plt.gca()
        
        # Sử dụng phong cách màu nhẹ
        ax.set_facecolor('#f8f9fa')
        plt.gcf().patch.set_facecolor('#f8f9fa')
        
        # Vẽ đường giá - sử dụng tất cả các điểm dữ liệu
        plt.plot(x_data, prices_cleaned, '-', color='#0066FF', linewidth=2.5)
        
        # Cài đặt giới hạn trục y
        plt.ylim(0, 40000)
        
        # Loại bỏ khung viền
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        
        # Cài đặt nhãn trục x - các nhãn thời gian được rải đều
        plt.xticks(time_ticks, time_labels, rotation=90, fontsize=8)
        plt.tick_params(axis='x', which='major', pad=4)
        
        # Thêm lưới ngang
        ax.yaxis.grid(True, linestyle='--', alpha=0.7, color='#cccccc')
        
        # Thêm tiêu đề
        plt.title('Những sự kiện quan trọng của NKG', fontsize=12, fontweight='bold', loc='left', 
                 color='#333333', pad=10, fontname='DejaVu Sans')
        
        # Cài đặt nhãn trục y với giá trị VND
        y_ticks = [0, 5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000]
        plt.yticks(y_ticks, [f'{y:,}' for y in y_ticks], fontsize=10)
        
        # Tạo một bản đồ giữa vị trí trục x và các nhãn thời gian
        time_map = {}
        for i, label in enumerate(time_labels):
            month, year = map(int, label.split('/'))
            date_key = f"{month:02d}/{year-2000:02d}"
            time_map[date_key] = time_ticks[i]
        
        # Thêm các chú thích và vị trí
        annotations = [
            {
                'text': 'Giá thép tăng mạnh do xung đột Trung - Úc, \n làm ảnh hưởng đến sản xuất thép của Trung Quốc',
                'x_position': 0.22,  # Vị trí theo tỉ lệ trên trục x (0-1)
                'y_position': 8000,  # Vị trí trên trục y
                'ha': 'center',
                'va': 'center',
                'bbox_color': '#3366CC'
            },
            {
                'text': 'Giá thép giảm do bất động sản Trung Quốc đi xuống',
                'x_position': 0.43,
                'y_position': 25000,
                'ha': 'center',
                'va': 'center', 
                'bbox_color': '#3366CC'
            },
            {
                'text': 'Chiến tranh Ukraine - Nga và tình hình kinh tế thế giới suy giảm',
                'x_position': 0.55,
                'y_position': 15000,
                'ha': 'center',
                'va': 'center',
                'bbox_color': '#3366CC'
            },
            {
                'text': 'Trung Quốc mở cửa giúp giá thép hồi phục',
                'x_position': 0.7,
                'y_position': 7000,
                'ha': 'center',
                'va': 'center',
                'bbox_color': '#3366CC'
            },
            {
                'text': 'Nhu cầu Thép tại Trung Quốc yếu hơn kỳ vọng',
                'x_position': 0.83,
                'y_position': 20000,
                'ha': 'center',
                'va': 'center',
                'bbox_color': '#3366CC'
            }
        ]
        
        # Vẽ các chú thích
        for anno in annotations:
            box_props = dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=anno['bbox_color'], alpha=0.9)
            
            # Vẽ chú thích
            ax.annotate(
                anno['text'],
                xy=(anno['x_position'], anno['y_position']),
                ha=anno['ha'],
                va=anno['va'],
                bbox=box_props,
                fontsize=6,
                wrap=True
            )
        
        # Điều chỉnh layout thủ công - tăng bottom margin để chứa nhãn xoay
        plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.2)
        
        # Lưu biểu đồ vào buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    # Các hàm placeholder để tránh lỗi nếu được gọi từ nơi khác
    def _create_pe_chart(self): 
        """Placeholder to avoid errors if called"""
        return self._create_steel_price_chart()
    
    def _create_ev_ebitda_chart(self):
        """Placeholder to avoid errors if called"""
        return self._create_steel_price_chart()
    
    def _create_pb_chart(self):
        """Placeholder to avoid errors if called"""
        return self._create_steel_price_chart()
    
    def _create_price_ps_chart(self):
        """Placeholder to avoid errors if called"""
        return self._create_steel_price_chart()
    
    def _create_price_pb_chart(self):
        """Placeholder to avoid errors if called"""
        return self._create_steel_price_chart()
    
    def _create_roe_chart(self):
        """Placeholder to avoid errors if called"""
        return self._create_steel_price_chart()
    
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
        header_text = f"{company_name} ({symbol}) - Những sự kiện quan trọng của NKG"
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

# For testing purposes
if __name__ == "__main__":
    buffer = io.BytesIO()
    page6 = Page6()
    page6.create_page6(buffer)
    with open("page6_test.pdf", "wb") as f:
        f.write(buffer.getvalue())
