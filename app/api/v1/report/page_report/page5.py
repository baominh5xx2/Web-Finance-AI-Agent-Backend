from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
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
        """Create P/E 1 năm qua chart"""
        # Generate dates for the past year
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=365)
        dates = [start_date + dt.timedelta(days=i) for i in range((end_date - start_date).days)]
        
        # Generate sample P/E data (normally would come from actual data)
        np.random.seed(42)  # For reproducibility
        pe_values = np.random.normal(11, 2, len(dates))
        pe_values = np.clip(pe_values, 7, 21)  # Clip to range seen in image
        
        # Create smooth transitions
        window_size = 10
        pe_values_smooth = np.convolve(pe_values, np.ones(window_size)/window_size, mode='same')
        
        # Create figure and plot
        fig, ax = plt.subplots(figsize=(5, 3.5))
        
        # Plot the P/E line
        ax.plot(dates, pe_values_smooth, '-', color='#0066cc', linewidth=2)
        
        # Add reference lines
        avg_pe = 11
        plus_one_sd = 13.5
        minus_one_sd = 8
        
        ax.axhline(y=avg_pe, color='navy', linestyle='-', alpha=0.7, linewidth=1)
        ax.axhline(y=plus_one_sd, color='brown', linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=minus_one_sd, color='#0099cc', linestyle='--', alpha=0.7, linewidth=1)
        
        # Format the x-axis to show months
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45, fontsize=8)
        
        # Set y-axis limits and ticks
        ax.set_ylim(5, 21)
        ax.set_yticks([5, 7, 9, 11, 13, 15, 17, 19, 21])
        
        # Add title and labels
        ax.set_title('P/E 1 năm qua', fontname='DejaVu Sans', fontsize=10, pad=10, color='#336699')
        
        # Add legend
        ax.legend(['P/E', '1-year average', '+1 SD', '-1 SD'], 
                 fontsize=8, loc='upper right', frameon=False)
        
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
        """Template drawing method for page template compatibility"""
        # This method is a placeholder for consistency with other page classes
        # It would be called by page templates
        pass

# For testing purposes
if __name__ == "__main__":
    buffer = io.BytesIO()
    page5 = Page5()
    page5.create_page5(buffer)
    with open("page5_test.pdf", "wb") as f:
        f.write(buffer.getvalue())
