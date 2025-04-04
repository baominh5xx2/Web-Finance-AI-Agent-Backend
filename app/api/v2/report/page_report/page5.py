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
        Create page 5 content with financial ratio charts
        
        If pdf_buffer is provided, builds a standalone PDF and returns the buffer.
        If not, returns a list of flowable elements for inclusion in a larger document.
        """
        elements = []
        elements.append(Spacer(1, 1*inch))
        # Main heading
        elements.append(Paragraph('<b>Định giá và chỉ số tài chính</b>', self.heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Create chart grid
        charts_table = self._create_chart_grid()
        elements.append(charts_table)
        
        # Add source note
        source_text = "Nguồn: Bloomberg, Dữ liệu công ty, Shinhan Securities Vietnam"
        elements.append(Paragraph(source_text, self.source_style))
        
        # If buffer is provided, build a standalone PDF
        if pdf_buffer is not None:
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=36, bottomMargin=36)
            doc.build(elements)
            return pdf_buffer
            
        # Otherwise return elements for inclusion in a larger document
        return elements
    
    def _create_chart_grid(self):
        """Create a grid of 6 financial charts arranged in 3 rows and 2 columns"""
        # Generate all chart images
        pe_buffer = self._create_pe_chart()
        ev_ebitda_buffer = self._create_ev_ebitda_chart()
        pb_buffer = self._create_pb_chart()
        price_ps_buffer = self._create_price_ps_chart()
        price_pb_buffer = self._create_price_pb_chart()
        roe_buffer = self._create_roe_chart()
        
        # Create a table with 3 rows and 2 columns for the charts
        chart_table = Table([
            [Image(pe_buffer, width=3.3*inch, height=2.3*inch), 
             Image(ev_ebitda_buffer, width=3.3*inch, height=2.3*inch)],
            [Image(pb_buffer, width=3.3*inch, height=2.3*inch), 
             Image(price_ps_buffer, width=3.3*inch, height=2.3*inch)],
            [Image(price_pb_buffer, width=3.3*inch, height=2.3*inch), 
             Image(roe_buffer, width=3.3*inch, height=2.3*inch)]
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
    
    def _create_pe_chart(self): 
        """
        Create P/E 2020 - 2024 chart
        """
        # Tạo dữ liệu mẫu cho P/E chart
        # Danh sách chuỗi ngày tháng, định dạng "tháng/năm"
        date_strings = ['1/2020','2/2020','3/2020','4/2020','1/2021','2/2021','3/2021','4/2021','1/2022','2/2022','3/2022','4/2022','1/2023','2/2023','3/2023','4/2023','1/2024','2/2024','3/2024','4/2024']
        
        # Dữ liệu P/E mẫu (đã loại bỏ giá trị âm)
        pe_values = [5.59, 22.27, 19.50, 16.58, 9.33, 7.31, 3.64, 4.14, 2.09, 2.57, 4.98, 12.54, 7.86, 7.65, 10.56, 57.97, 21.04, 13.71, 9.43, 10.27]
        
        # Chuyển đổi chuỗi ngày thành đối tượng datetime
        valid_dates = []
        valid_values = []
        
        for i, date_str in enumerate(date_strings):
            if date_str.strip() == '':
                continue  # Bỏ qua chuỗi rỗng
                
            try:
                month, year = map(int, date_str.split('/'))
                valid_dates.append(dt.datetime(year, month, 1))
                if i < len(pe_values):
                    valid_values.append(pe_values[i])
            except (ValueError, IndexError):
                continue  # Bỏ qua nếu có lỗi khi xử lý
        
        # Nếu không có dữ liệu hợp lệ, tạo dữ liệu mẫu mặc định
        if not valid_dates:
            current_year = dt.datetime.now().year
            valid_dates = [dt.datetime(current_year-1, i+1, 1) for i in range(4)]
            valid_values = [10.5, 11.2, 12.4, 13.5]
                
        # Create figure and plot với màu nền sáng
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(5, 3.5))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        # Tính toán giá trị trung bình
        avg_pe = sum(valid_values) / len(valid_values)
        
        # Tính độ lệch chuẩn
        sum_squared_diff = sum((x - avg_pe) ** 2 for x in valid_values)
        std_dev = (sum_squared_diff / len(valid_values)) ** 0.5
        
        plus_one_sd = avg_pe + std_dev
        minus_one_sd = avg_pe - std_dev
        
        # Plot the P/E line với marker và màu đẹp hơn
        ax.plot(valid_dates, valid_values, '-o', color='#0066cc', linewidth=2, 
                markersize=4, markerfacecolor='white', markeredgecolor='#0066cc')
        
        # Add reference lines với màu đẹp hơn
        ax.axhline(y=avg_pe, color='#ff7f0e', linestyle='-', alpha=0.7, linewidth=1.5)
        ax.axhline(y=plus_one_sd, color='#d62728', linestyle='--', alpha=0.5, linewidth=1.5)
        ax.axhline(y=minus_one_sd, color='#2ca02c', linestyle='--', alpha=0.5, linewidth=1.5)
        
        # Format the x-axis to show quarters
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45, fontsize=8)
        
        # Highlight years with different background colors
        years = set(date.year for date in valid_dates)
        colors = ['#f2f2f2', '#e6e6e6']
        
        for i, year in enumerate(sorted(years)):
            year_dates = [d for d in valid_dates if d.year == year]
            if year_dates:
                start = min(year_dates)
                end = dt.datetime(year+1, 1, 1) if year < max(years) else max(valid_dates)
                ax.axvspan(start, end, alpha=0.1, color=colors[i % 2])
        
        # Set y-axis limits and ticks
        max_value = max(valid_values)
        min_value = min(valid_values)
        buffer = (max_value - min_value) * 0.1  # 10% buffer
        
        # Make sure min_value is positive
        min_value = max(0, min_value - buffer)
        max_value = max_value + buffer
        
        # Tạo khoảng cách đều cho trục y
        y_range = max_value - min_value
        tick_step = y_range / 6  # Khoảng 6-7 mức giá trị
        
        # Làm tròn tick_step để dễ nhìn hơn
        if tick_step >= 10:
            tick_step = round(tick_step / 10) * 10
        elif tick_step >= 1:
            tick_step = round(tick_step)
        elif tick_step >= 0.1:
            tick_step = round(tick_step * 10) / 10
        else:
            tick_step = round(tick_step * 100) / 100
            
        y_ticks = []
        current = min_value
        while current <= max_value:
            y_ticks.append(current)
            current += tick_step
        
        ax.set_ylim(min_value, max_value)
        ax.set_yticks(y_ticks)
        
        # Add grid lines for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add title and labels
        ax.set_title('P/E 2020 - 2024', fontname='DejaVu Sans', fontsize=12, pad=10, color='#336699', fontweight='bold')
        ax.set_ylabel('P/E', fontsize=10, color='#336699')
        
        # Add legend with formatted values
        ax.legend([
            'P/E', 
            f'TB ({avg_pe:.2f})', 
            f'+1SD ({plus_one_sd:.2f})', 
            f'-1SD ({minus_one_sd:.2f})'
        ], fontsize=8, loc='upper right', frameon=True, facecolor='white', edgecolor='lightgray')
        
        # Thêm annotations cho giá trị cao nhất và thấp nhất
        max_idx = valid_values.index(max(valid_values))
        min_idx = valid_values.index(min(valid_values))
        
        ax.annotate(f'{valid_values[max_idx]:.2f}', 
                   xy=(valid_dates[max_idx], valid_values[max_idx]),
                   xytext=(10, 15), textcoords='offset points',
                   arrowprops=dict(arrowstyle='->', color='red'),
                   fontsize=8, color='red')
                   
        ax.annotate(f'{valid_values[min_idx]:.2f}', 
                   xy=(valid_dates[min_idx], valid_values[min_idx]),
                   xytext=(10, -15), textcoords='offset points',
                   arrowprops=dict(arrowstyle='->', color='green'),
                   fontsize=8, color='green')
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
    
    def _create_ev_ebitda_chart(self):
        """Create EV/EBITDA 1 năm qua chart"""
        # Generate dates for the past year
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=365)
        dates = [start_date + dt.timedelta(days=i) for i in range((end_date - start_date).days)]
        
        # Generate sample EV/EBITDA data
        np.random.seed(43)  # Different seed for variation
        ev_ebitda_values = np.random.normal(8, 1, len(dates))
        
        # Create patterns similar to image
        for i in range(len(ev_ebitda_values)):
            # Create the downward trend in the middle
            if i > len(dates) // 3 and i < 2 * len(dates) // 3:
                ev_ebitda_values[i] -= 1.5 * (i - len(dates) // 3) / (len(dates) // 3)
            # Create recovery at the end
            if i > 2 * len(dates) // 3:
                ev_ebitda_values[i] += 2 * (i - 2 * len(dates) // 3) / (len(dates) // 3)
        
        ev_ebitda_values = np.clip(ev_ebitda_values, 6, 10)
        
        # Create smooth transitions
        window_size = 10
        ev_ebitda_smooth = np.convolve(ev_ebitda_values, np.ones(window_size)/window_size, mode='same')
        
        # Create figure and plot
        fig, ax = plt.subplots(figsize=(5, 3.5))
        
        # Plot the EV/EBITDA line
        ax.plot(dates, ev_ebitda_smooth, '-', color='#0066cc', linewidth=2)
        
        # Add reference lines
        avg_ev_ebitda = 8
        plus_one_sd = 9
        minus_one_sd = 7
        
        ax.axhline(y=avg_ev_ebitda, color='navy', linestyle='-', alpha=0.7, linewidth=1)
        ax.axhline(y=plus_one_sd, color='brown', linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=minus_one_sd, color='#0099cc', linestyle='--', alpha=0.7, linewidth=1)
        
        # Format the x-axis to show months
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45, fontsize=8)
        
        # Set y-axis limits and ticks
        ax.set_ylim(6, 10)
        ax.set_yticks([6, 7, 8, 9, 10])
        
        # Add title and labels
        ax.set_title('EV/EBITDA 1 năm qua', fontname='DejaVu Sans', fontsize=10, pad=10, color='#336699')
        
        # Add legend
        ax.legend(['EV/EBITDA', 'Trung bình 1 năm', '+1 SD', '-1 SD'], 
                 fontsize=8, loc='upper right', frameon=False)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
    
    def _create_pb_chart(self):
        """Create P/B 1 năm qua chart"""
        # Generate dates for the past year
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=365)
        dates = [start_date + dt.timedelta(days=i) for i in range((end_date - start_date).days)]
        
        # Generate sample P/B data
        np.random.seed(44)  # Different seed for variation
        pb_values = np.random.normal(1.1, 0.2, len(dates))
        
        # Create a downward trend similar to the image
        for i in range(len(pb_values)):
            if i > len(dates) // 3:
                pb_values[i] -= 0.4 * (i - len(dates) // 3) / (2 * len(dates) // 3)
        
        # Create upward trend at the end
        for i in range(len(pb_values)-1, len(pb_values)-30, -1):
            pb_values[i] += 0.1
        
        pb_values = np.clip(pb_values, 0.7, 1.5)
        
        # Create smooth transitions
        window_size = 10
        pb_smooth = np.convolve(pb_values, np.ones(window_size)/window_size, mode='same')
        
        # Create figure and plot
        fig, ax = plt.subplots(figsize=(5, 3.5))
        
        # Plot the P/B line
        ax.plot(dates, pb_smooth, '-', color='#0066cc', linewidth=2)
        
        # Add reference lines
        avg_pb = 1.0
        plus_one_sd = 1.2
        minus_one_sd = 0.8
        
        ax.axhline(y=avg_pb, color='navy', linestyle='-', alpha=0.7, linewidth=1)
        ax.axhline(y=plus_one_sd, color='brown', linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=minus_one_sd, color='#0099cc', linestyle='--', alpha=0.7, linewidth=1)
        
        # Format the x-axis to show months
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45, fontsize=8)
        
        # Set y-axis limits and ticks
        ax.set_ylim(0.5, 1.5)
        ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5])
        
        # Add title and labels
        ax.set_title('P/B 1 năm qua', fontname='DejaVu Sans', fontsize=10, pad=10, color='#336699')
        
        # Add legend
        ax.legend(['P/B', 'Trung bình 1 năm', '+1 SD', '-1 SD'], 
                 fontsize=8, loc='upper right', frameon=False)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
    
    def _create_price_ps_chart(self):
        """Create Giá và các mức P/S chart"""
        # Generate dates for the past year
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=365)
        dates = [start_date + dt.timedelta(days=i) for i in range((end_date - start_date).days)]
        
        # Generate sample price data
        np.random.seed(45)  # Different seed for variation
        price_values = np.random.normal(17000, 3000, len(dates))
        
        # Create a pattern similar to the image
        for i in range(len(price_values)):
            # Create a decline in the middle
            if i > len(dates) // 4 and i < 3 * len(dates) // 4:
                price_values[i] -= 3000 * (i - len(dates) // 4) / (len(dates) // 2)
            # Create recovery at the end
            if i > 3 * len(dates) // 4:
                price_values[i] += 6000 * (i - 3 * len(dates) // 4) / (len(dates) // 4)
        
        price_values = np.clip(price_values, 10000, 25000)
        
        # Create smooth transitions
        window_size = 10
        price_smooth = np.convolve(price_values, np.ones(window_size)/window_size, mode='same')
        
        # Create figure and plot
        fig, ax = plt.subplots(figsize=(5, 3.5))
        
        # Plot the price line
        ax.plot(dates, price_smooth, '-', color='#0066cc', linewidth=2)
        
        # Add reference lines for different P/S ratios
        ps_16x = np.ones(len(dates)) * 29000
        ps_15x = np.ones(len(dates)) * 24000
        ps_14x = np.ones(len(dates)) * 19000
        ps_13x = np.ones(len(dates)) * 14000
        ps_12x = np.ones(len(dates)) * 9000
        
        ax.plot(dates, ps_16x, '--', color='#99ccff', alpha=0.8, linewidth=1)
        ax.plot(dates, ps_15x, '--', color='#336699', alpha=0.8, linewidth=1)
        ax.plot(dates, ps_14x, '--', color='#003366', alpha=0.8, linewidth=1)
        ax.plot(dates, ps_13x, '--', color='#669999', alpha=0.8, linewidth=1)
        ax.plot(dates, ps_12x, '--', color='#99cccc', alpha=0.8, linewidth=1)
        
        # Format the x-axis to show months
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45, fontsize=8)
        
        # Set y-axis limits and ticks
        ax.set_ylim(4000, 30000)
        ax.set_yticks([4000, 9000, 14000, 19000, 24000, 29000])
        
        # Add title and labels
        ax.set_title('Giá và các mức P/S', fontname='DejaVu Sans', fontsize=10, pad=10, color='#336699')
        
        # Add legend
        ax.legend(['Giá', 'P/S 1.6x', 'P/S 1.5x', 'P/S 1.4x', 'P/S 1.3x'], 
                 fontsize=8, loc='upper right', frameon=False)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
    
    def _create_price_pb_chart(self):
        """Create Giá và các mức P/B chart"""
        # Generate dates for the past year
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=365)
        dates = [start_date + dt.timedelta(days=i) for i in range((end_date - start_date).days)]
        
        # Generate sample price data
        np.random.seed(46)  # Different seed for variation
        price_values = np.random.normal(17000, 3000, len(dates))
        
        # Create a pattern similar to the image
        for i in range(len(price_values)):
            if i < len(dates) // 4:
                price_values[i] += 1000
            elif i < len(dates) // 2:
                price_values[i] += 3000 - 2000 * (i - len(dates) // 4) / (len(dates) // 4)
            elif i < 3 * len(dates) // 4:
                price_values[i] -= 3000 * (i - len(dates) // 2) / (len(dates) // 4)
            else:
                price_values[i] = price_values[i-1] * 0.99
        
        price_values = np.clip(price_values, 10000, 25000)
        
        # Create smooth transitions
        window_size = 10
        price_smooth = np.convolve(price_values, np.ones(window_size)/window_size, mode='same')
        
        # Create figure and plot
        fig, ax = plt.subplots(figsize=(5, 3.5))
        
        # Plot the price line
        ax.plot(dates, price_smooth, '-', color='#0066cc', linewidth=2)
        
        # Add reference lines for different P/B ratios
        pb_17x = np.ones(len(dates)) * 24000
        pb_13x = np.ones(len(dates)) * 20000
        pb_09x = np.ones(len(dates)) * 16000
        pb_05x = np.ones(len(dates)) * 12000
        pb_01x = np.ones(len(dates)) * 8000
        
        ax.plot(dates, pb_17x, '--', color='#99ccff', alpha=0.8, linewidth=1)
        ax.plot(dates, pb_13x, '--', color='#336699', alpha=0.8, linewidth=1)
        ax.plot(dates, pb_09x, '--', color='#003366', alpha=0.8, linewidth=1)
        ax.plot(dates, pb_05x, '--', color='#669999', alpha=0.8, linewidth=1)
        ax.plot(dates, pb_01x, '-', color='#996633', alpha=0.8, linewidth=1)
        
        # Format the x-axis to show months
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45, fontsize=8)
        
        # Set y-axis limits and ticks
        ax.set_ylim(5000, 30000)
        ax.set_yticks([5000, 10000, 15000, 20000, 25000, 30000])
        
        # Add title and labels
        ax.set_title('Giá và các mức P/B', fontname='DejaVu Sans', fontsize=10, pad=10, color='#336699')
        
        # Add legend
        ax.legend(['P/B', 'P/BV 1.7x', 'P/BV 1.3x', 'P/BV 0.9x', 'P/BV 0.5x'], 
                 fontsize=8, loc='upper right', frameon=False)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
    
    def _create_roe_chart(self):
        """Create ROE và đường trung bình 1 năm qua chart"""
        # Generate monthly dates for ROE
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=365 * 3)  # 3 years of data for ROE
        months = pd.date_range(start=start_date, end=end_date, freq='M')
        
        # Generate sample ROE data (volatile like in the image)
        np.random.seed(47)  # Different seed for variation
        roe_values = []
        
        # Create the pattern from the image
        for i in range(len(months)):
            if i < 5:  # High at start
                roe_values.append(np.random.uniform(30, 40))
            elif i < 10:  # Declining
                roe_values.append(np.random.uniform(15, 25))
            elif i < 20:  # Low point
                roe_values.append(np.random.uniform(0, 15))
            elif i < 30:  # Recovery
                roe_values.append(np.random.uniform(15, 25))
            else:  # Stabilizing
                roe_values.append(np.random.uniform(10, 20))
        
        # Create price data (for the second y-axis)
        price_values = []
        for i in range(len(months)):
            if i < 5:  # Start high
                price_values.append(np.random.uniform(25000, 30000))
            elif i < 15:  # Declining with ROE
                price_values.append(np.random.uniform(15000, 25000))
            elif i < 25:  # Low point
                price_values.append(np.random.uniform(5000, 15000))
            else:  # Recovery
                price_values.append(np.random.uniform(15000, 20000))
        
        # Create figure with two y-axes
        fig, ax1 = plt.subplots(figsize=(5, 3.5))
        
        # Plot ROE on primary y-axis
        ax1.plot(months, roe_values, '-', color='#0066cc', linewidth=1.5, marker='o', markersize=3)
        
        # Add moving averages
        ma_50 = np.convolve(roe_values, np.ones(5)/5, mode='valid')
        ma_100 = np.convolve(roe_values, np.ones(10)/10, mode='valid')
        
        # Plot moving averages
        ma_50_dates = months[4:]
        ma_100_dates = months[9:]
        
        ax1.plot(ma_50_dates, ma_50, '-', color='#66cc99', linewidth=1.5)
        ax1.plot(ma_100_dates, ma_100, '-', color='#cc6633', linewidth=1.5)
        
        # Create a second y-axis for price
        ax2 = ax1.twinx()
        ax2.plot(months, price_values, '-', color='#999999', linewidth=1, alpha=0.7)
        
        # Set y-axis limits
        ax1.set_ylim(-20, 60)
        ax2.set_ylim(0, 40000)
        
        # Set primary y-axis ticks
        ax1.set_yticks([-20, -10, 0, 10, 20, 30, 40, 50, 60])
        
        # Format the x-axis to show years and quarters
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        plt.xticks(rotation=45, fontsize=8)
        
        # Add title and labels
        ax1.set_title('ROE và đường trung bình 1 năm qua', fontname='DejaVu Sans', fontsize=10, pad=10, color='#336699')
        
        # Add legend
        ax1.legend(['Giá', 'MA 50', 'MA 100', 'MA 150'], 
                 fontsize=8, loc='upper right', frameon=False)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
    
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
        header_text = f"{company_name} ({symbol}) - Các Tỷ số Tài chính"
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
        
        # Thông tin công ty
        canvas.drawString(1*cm, 3.5*mm, "FinBot - Trí tuệ tài chính cho mọi người")

# For testing purposes
if __name__ == "__main__":
    buffer = io.BytesIO()
    page5 = Page5()
    page5.create_page5(buffer)
    with open("page5_test.pdf", "wb") as f:
        f.write(buffer.getvalue())
