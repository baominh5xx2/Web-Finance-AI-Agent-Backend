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
import datetime as dt
import matplotlib.dates as mdates

class Page5:
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
        return self.create_page5(pdf_buffer)
    
    def create_page5(self, pdf_buffer=None, company_data=None):
        """
        Create page 5 content with charts
        
        If pdf_buffer is provided, builds a standalone PDF and returns the buffer.
        If not, returns a list of flowable elements for inclusion in a larger document.
        """
        elements = []
        elements.append(Spacer(1, 1*inch))  # Giảm khoảng cách trên cùng
        # Main heading
        elements.append(Paragraph('<b>Biểu đồ tài chính</b>', self.heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Add charts
        chart_table = self._create_charts()
        elements.append(chart_table)
        
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
    
    def _create_pe_chart(self): 
        """
        Create P/E 2020 - 2024 chart
        """
        # Tạo dữ liệu nhãn tháng phân bố đều cho trục x
        months = ['1/2024', '2/2024', '3/2024', '4/2024', '5/2024', '6/2024', 
                 '7/2024', '8/2024', '9/2024', '10/2024', '11/2024', '12/2024', '1/2025']
        
        # Sử dụng toàn bộ dữ liệu P/E
        pe_values_full = [14.45, 14.65, 14.6, 14.75, 14.95, 14.8, 14.7, 14.75, 14.75, 14.41, 14.26, 14.57, 14.8, 15.11, 15.19, 15.31, 15.31, 14.8, 15.03, 14.57, 14.96, 15.11, 15.11, 15.11, 15.19, 15.15, 15.07, 15.07, 15.03, 14.88, 14.72, 14.92, 14.88, 15.46, 16.16, 16.55, 16.83, 16.71, 16.51, 16.63, 16.28, 16.13, 16.32, 16.09, 16.09, 16.16, 16.13, 15.93, 15.93, 15.93, 15.89, 15.97, 16.28, 16.51, 16.4, 16.75, 16.87, 16.9, 16.9, 17.18, 17.18, 16.94, 16.9, 16.83, 17.22, 17.22, 17.22, 17.02, 16.98, 16.9, 16.44, 16.55, 16.71, 16.75, 16.51, 16.44, 16.05, 16.36, 16.51, 16.67, 16.4, 16.67, 16.24, 16.13, 16.63, 16.98, 17.22, 17.22, 16.98, 17.06, 17.25, 16.75, 16.98, 16.71, 16.48, 16.09, 15.46, 15.89, 16.2, 16.51, 16.55, 16.2, 16.24, 16.16, 15.81, 16.98, 16.51, 17.61, 18.31, 18.38, 18.19, 18.07, 18.23, 17.92, 18.35, 18.93, 19.63, 19.32, 19.79, 20.02, 20.02, 19.48, 19.75, 19.79, 19.67, 19.12, 19.32, 19.32, 19.32, 18.66, 18.35, 19.2, 19.4, 19.24, 18.85, 19.79, 20.33, 20.64, 20.72, 20.88, 20.02, 20.72, 20.68, 20.68, 20.64, 20.02, 20.02, 19.86, 19.86, 19.36, 19.01, 18.97, 19.28, 19.51, 19.4, 19.32, 19.94, 19.4, 19.48, 19.63, 19.32, 19.12, 19.09, 18.73, 18.7, 18.62, 18.5, 18.5, 18.35, 18.23, 17.76, 17.68, 17.06, 17.14, 17.41, 16.59, 17.8, 17.1, 17.92, 18.42, 18.73, 20.14, 20.06, 19.32, 19.55, 19.16, 19.05, 19.59, 19.86, 20.37, 20.06, 19.98, 20.33, 20.25, 20.25, 19.71, 19.86, 19.75, 19.59, 19.63, 18.46, 19.05, 18.73, 18.85, 18.31, 18.38, 18.66, 19.12, 19.16, 19.2, 19.05, 18.81, 18.66, 18.81, 18.77, 18.46, 18.19, 18.54, 18.73, 18.93, 19.05, 19.16, 19.28, 18.97, 18.89, 18.93, 18.89, 18.7, 18.85, 19.48, 19.28, 19.79, 19.63, 19.36, 19.55, 19.63, 19.44, 19.63, 19.36, 19.4, 18.15, 18.19, 18.31, 17.99, 18.38, 18.58, 18.77, 18.77, 18.85, 18.5]
        pe_values_full = [x/1.537 for x in pe_values_full]
        # Phân bố dữ liệu đều trên trục thời gian
        num_points = len(pe_values_full)
        
        # Tạo danh sách thời gian trải đều từ 1/1/2024 đến 31/12/2024
        start_date = dt.datetime(2024, 1, 1)
        end_date = dt.datetime(2025, 1, 1)
        total_days = (end_date - start_date).days
        
        # Tạo khoảng thời gian đều đặn
        time_interval = total_days / (num_points - 1) if num_points > 1 else 1
        valid_dates = []
        
        for i in range(num_points):
            days_to_add = int(i * time_interval)
            current_date = start_date + dt.timedelta(days=days_to_add)
            valid_dates.append(current_date)
        
        valid_values = pe_values_full
        
        # Tạo điểm dữ liệu trung bình tháng
        monthly_data = {}
        monthly_dates = []
        monthly_values = []
        
        for date_str in months[:-1]:  # Bỏ qua tháng 1/2025
            month, year = map(int, date_str.split('/'))
            month_date = dt.datetime(year, month, 15)  # Ngày giữa tháng
            monthly_dates.append(month_date)
            
            # Tìm các giá trị P/E trong tháng này
            month_values = [pe for d, pe in zip(valid_dates, valid_values) 
                          if d.month == month and d.year == year]
            
            if month_values:
                monthly_values.append(sum(month_values) / len(month_values))
            else:
                # Nếu không có dữ liệu trong tháng, sử dụng giá trị trung bình tổng thể
                monthly_values.append(sum(valid_values) / len(valid_values))
            
            monthly_data[month_date] = month_values
        
        # Tạo figure và axes
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(9, 4))
        
        # Thiết lập màu nền
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        # Tính toán giá trị thống kê
        avg_pe = sum(valid_values) / len(valid_values)
        sum_squared_diff = sum((x - avg_pe) ** 2 for x in valid_values)
        std_dev = (sum_squared_diff / len(valid_values)) ** 0.5
        plus_one_sd = avg_pe + std_dev
        minus_one_sd = avg_pe - std_dev
        
        # Vẽ điểm dữ liệu
        scatter = ax.scatter(valid_dates, valid_values, s=18, color='#3182bd', alpha=0.3, label='P/E hàng ngày')
        
        # Vẽ đường xu hướng với điểm biến động
        # Chọn các điểm đặc biệt để tạo đường xu hướng biến động
        key_indices = []
        step = max(len(valid_dates) // 60, 1)  # Khoảng 60 điểm trên đường xu hướng
        
        # Đảm bảo bắt các điểm đỉnh, đáy và biến động lớn
        for i in range(1, len(valid_values)-1, step):
            key_indices.append(i)
            # Thêm các điểm đột biến
            if abs(valid_values[i] - valid_values[i-1]) > 0.3:
                if i-1 not in key_indices:
                    key_indices.append(i-1)
                if i+1 < len(valid_values) and i+1 not in key_indices:
                    key_indices.append(i+1)
        
        # Thêm điểm đầu và cuối
        if 0 not in key_indices:
            key_indices.append(0)
        if len(valid_values)-1 not in key_indices:
            key_indices.append(len(valid_values)-1)
        
        # Sắp xếp và loại bỏ trùng lặp
        key_indices = sorted(set(key_indices))
        
        # Lấy tọa độ
        key_dates = [valid_dates[i] for i in key_indices]
        key_values = [valid_values[i] for i in key_indices]
        
        # Vẽ đường xu hướng chính
        trend_line = ax.plot(key_dates, key_values, '-', color='#0066cc', 
                      linewidth=2, alpha=0.9, zorder=3)
        
        # Vẽ đường trung bình tháng theo dạng đường đứt và điểm tròn lớn
        month_line = ax.plot(monthly_dates, monthly_values, 'o-', color='#e41a1c', 
                      linewidth=1.5, linestyle='--', marker='o', markersize=6, 
                      markerfacecolor='white', markeredgecolor='#e41a1c', 
                      markeredgewidth=1.5, alpha=0.8, label='Trung bình tháng')
        
        # Thêm vùng độ lệch chuẩn
        ax.fill_between(valid_dates, [minus_one_sd] * len(valid_dates), 
                       [plus_one_sd] * len(valid_dates), color='#9ecae1', alpha=0.15)
        
        # Vẽ các đường tham chiếu
        ax.axhline(y=avg_pe, color='#e41a1c', linestyle='-', alpha=0.7, linewidth=1.5, 
                  label=f'Trung bình ({avg_pe:.2f})')
        ax.axhline(y=plus_one_sd, color='#ff7f00', linestyle='--', alpha=0.7, linewidth=1.5, 
                  label=f'+1 SD ({plus_one_sd:.2f})')
        ax.axhline(y=minus_one_sd, color='#4daf4a', linestyle='--', alpha=0.7, linewidth=1.5, 
                  label=f'-1 SD ({minus_one_sd:.2f})')
        
        # Định dạng trục x - phân bố đều các tháng
        date_ticks = []
        for month_str in months:
            month, year = map(int, month_str.split('/'))
            date_ticks.append(dt.datetime(year, month, 1))
        
        ax.set_xticks(date_ticks)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        plt.xticks(rotation=45, fontsize=9, ha='right')
        
        # Tô màu nền cho từng tháng - phân biệt bằng màu xen kẽ
        for i in range(len(months)-1):
            month_start = date_ticks[i]
            month_end = date_ticks[i+1]
            
            color = '#f0f0f0' if i % 2 == 0 else '#e6e6e6'
            ax.axvspan(month_start, month_end, alpha=0.2, color=color)
        
        # Thiết lập giới hạn trục y phù hợp
        min_val = min(valid_values) * 0.95
        max_val = max(valid_values) * 1.05
        
        # Làm tròn giới hạn để dễ đọc
        min_val = round(min_val - 0.5)
        max_val = round(max_val + 0.5)
        
        # Tạo các mức đều cho trục y
        y_range = max_val - min_val
        num_ticks = 8
        tick_step = y_range / num_ticks
        
        if tick_step >= 1:
            tick_step = round(tick_step)
        else:
            tick_step = round(tick_step * 10) / 10
            
        y_ticks = []
        current = min_val
        while current <= max_val:
            y_ticks.append(round(current, 1))
            current += tick_step
        
        ax.set_ylim(min_val, max_val)
        ax.set_yticks(y_ticks)
        ax.tick_params(axis='y', labelsize=9)
        
        # Hiển thị lưới
        ax.grid(True, linestyle='--', alpha=0.5, color='#cccccc')
        
        # Xác định và đánh dấu giá trị cao nhất và thấp nhất
        max_idx = valid_values.index(max(valid_values))
        min_idx = valid_values.index(min(valid_values))
        
        # Tiêu đề và nhãn trục
        ax.set_title('Diễn biến P/E 2024', fontname='DejaVu Sans', fontsize=14, 
                    pad=15, color='#336699', fontweight='bold')
        ax.set_ylabel('P/E', fontsize=10, color='#336699', fontweight='bold')
        

        plt.tight_layout()
        
        # Lưu biểu đồ
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
    
    def _create_charts(self):
        """Create a combined chart with revenue, profit, growth rates and P/E chart"""
        # Tạo các buffer cho 2 biểu đồ
        revenue_chart_buffer = self._create_revenue_profit_chart()
        pe_chart_buffer = self._create_pe_chart()
        
        # Tạo bảng chứa cả hai biểu đồ xếp chồng lên nhau
        chart_table = Table([
            [Image(revenue_chart_buffer, width=6.3*inch, height=3.2*inch)],
            [Image(pe_chart_buffer, width=6.3*inch, height=3.2*inch)]
        ])
        
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (0, 1), 5),  # Padding giữa hai biểu đồ
            ('BOTTOMPADDING', (0, 0), (0, 0), 5),  # Padding dưới biểu đồ đầu tiên
        ]))
        
        return chart_table
    
    def _create_revenue_profit_chart(self):
        """Create chart showing revenue, profit and growth rates"""
        # Create a single figure
        fig, ax1 = plt.subplots(figsize=(9, 4))  # Điều chỉnh kích thước phù hợp
        
        # Thêm tiêu đề biểu đồ
        fig.suptitle('Doanh thu, Lợi nhuận và Tỷ lệ tăng trưởng Nam Kim 2015 - 2024', 
                  fontname='DejaVu Sans', fontsize=14, y=0.98)
        
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
                            color='#0052cc', fontweight='bold', fontsize=8)
            
            # Lợi nhuận
            va = 'bottom' if p >= 0 else 'top'
            offset = 5 if p >= 0 else -15
            ax1.annotate(f'{p}', xy=(i + width/2, p), xytext=(0, offset), 
                        textcoords='offset points', ha='center', va=va,
                        color='#ff9900', fontweight='bold', fontsize=8)
        
        # Thiết lập trục y trái
        ax1.set_xlabel('Năm', fontname='DejaVu Sans', fontsize=10)
        ax1.set_ylabel('Giá trị (tỷ đồng)', fontname='DejaVu Sans', fontsize=10)
        ax1.set_xticks(x)
        ax1.set_xticklabels(years, fontsize=9)
        ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
        ax1.tick_params(axis='y', labelsize=9)
        
        # Điều chỉnh giới hạn trục y trái
        min_val = min(min(profit), 0)
        max_val = max(revenue) * 1.05
        ax1.set_ylim(min_val * 1.1 if min_val < 0 else 0, max_val)
        
        # Tạo trục y thứ hai cho tỷ lệ tăng trưởng
        ax2 = ax1.twinx()
        
        # Vẽ đường tăng trưởng trên trục y phải
        line1 = ax2.plot(x, revenue_growth, 'c-', label='Tăng trưởng DT (%)', 
                        linewidth=2, marker='o', markersize=5, color='#00cccc')
        line2 = ax2.plot(x, profit_growth, 'r-', label='Tăng trưởng LN (%)', 
                        linewidth=2, marker='s', markersize=5, color='#cc0000')
        
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
        
        # Kết hợp các chú thích từ cả hai trục
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9, fontsize=8)
        
        plt.tight_layout()
        
        # Lưu biểu đồ
        chart_buffer = io.BytesIO()
        fig.savefig(chart_buffer, format='png', dpi=120, bbox_inches='tight')
        chart_buffer.seek(0)
        plt.close(fig)
        
        return chart_buffer
        
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
        header_text = f"{company_name} ({symbol}) - Biểu đồ Tài Chính"
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
        canvas.drawRightString(width - 1*cm, 3.5*mm, f"Trang 5")


# For testing purposes
if __name__ == "__main__":
    buffer = io.BytesIO()
    page5 = Page5()
    page5.create_page5(buffer)
    with open("page5_test.pdf", "wb") as f:
        f.write(buffer.getvalue())
