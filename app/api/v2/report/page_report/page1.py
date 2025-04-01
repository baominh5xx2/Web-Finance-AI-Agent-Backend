from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, Frame, NextPageTemplate, PageTemplate, FrameBreak, BaseDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen.canvas import Canvas
import datetime
import os

class Page1:
    def __init__(self, font_added=False):
        self.font_added = font_added
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """Thiết lập các styles cho page 1"""
        # Sử dụng font DejaVuSans nếu đã đăng ký, nếu không thì dùng Helvetica
        title_font = 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'
        normal_font = 'DejaVuSans' if self.font_added else 'Helvetica'
        
        # Màu sắc chính
        self.blue_color = colors.HexColor('#0066CC')
        self.light_blue = colors.HexColor('#E6F0FA')
        self.grey_color = colors.HexColor('#F5F5F5')
        
        # Tạo style cho tiêu đề và nội dung
        self.styles.add(ParagraphStyle(
            name='TitleStyle',
            fontName=title_font,
            fontSize=14,
            textColor=colors.HexColor('#0A64F0'),
            alignment=TA_LEFT,
            spaceAfter=6*mm
        ))
        self.styles.add(ParagraphStyle(
            name='NormalVN',
            fontName=normal_font,
            fontSize=10,
            leading=12,
            alignment=TA_LEFT
        ))
        self.styles.add(ParagraphStyle(
            name='Header',
            fontName=title_font,
            fontSize=16,
            alignment=TA_RIGHT,
        ))
        
        # Styles theo mẫu báo cáo mới
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            fontName=title_font,
            fontSize=24,
            textColor=colors.white,
            alignment=TA_LEFT,
            leading=28
        ))
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            fontName=title_font,
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=6,
            leading=20,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName=title_font,
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            leading=16,
            spaceBefore=6,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name='PriceData',
            fontName=title_font,
            fontSize=16,
            alignment=TA_RIGHT,
        ))
        self.styles.add(ParagraphStyle(
            name='AnalysisTitle',
            fontName=title_font,
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=6,
        ))
        
        # Thêm style cho tiêu đề phân tích
        self.styles.add(ParagraphStyle(
            name='AnalysisHeading',
            fontName=title_font,
            fontSize=11,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=4,
            leading=14,
            borderWidth=0,
            backColor=None,
        ))
        
        # Thêm style cho giá hiện tại
        self.styles.add(ParagraphStyle(
            name='PriceRow',
            fontName=normal_font,
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
        ))
        
        # Style cho giá trị
        self.styles.add(ParagraphStyle(
            name='PriceValue',
            fontName=title_font,
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            leading=16,
        ))

        # Style cho toàn bộ cột bên trái
        self.styles.add(ParagraphStyle(
            name='LeftColumn',
            fontName=normal_font,
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
        ))
        
        # Style mới cho phần giá mục tiêu và suất sinh lời
        self.styles.add(ParagraphStyle(name='TargetPriceLabel', fontSize=8, alignment=TA_LEFT, fontName='DejaVuSans', textColor=colors.gray))
        self.styles.add(ParagraphStyle(name='TargetPriceValue', fontSize=16, alignment=TA_LEFT, fontName='DejaVuSans-Bold', leading=18))
        self.styles.add(ParagraphStyle(name='ProfitLabel', fontSize=8, alignment=TA_LEFT, fontName='DejaVuSans', textColor=colors.gray))
        self.styles.add(ParagraphStyle(name='ProfitValue', fontSize=14, alignment=TA_LEFT, fontName='DejaVuSans-Bold', leading=16))
        
        # Thêm các style còn thiếu
        self.styles.add(ParagraphStyle(
            name='MarketDataTitle',
            fontName=title_font,
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            leading=16,
            leftIndent=0,
        ))
        
        # Style cho ngày báo cáo
        self.styles.add(ParagraphStyle(
            name='DateLabel',
            fontName=normal_font,
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_LEFT,
        ))
        
        self.styles.add(ParagraphStyle(
            name='DateValue',
            fontName=normal_font,
            fontSize=10,
            alignment=TA_LEFT,
            leading=12,
        ))
        
        # Style cho label giá hiện tại
        self.styles.add(ParagraphStyle(
            name='PriceLabel',
            fontName=normal_font,
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_LEFT,
        ))

    def _process_markdown_content(self, text):
        """Xử lý nội dung markdown, phát hiện tiêu đề và nội dung"""
        if not text or not isinstance(text, str):
            return ("normal", text if text else "")
            
        # Kiểm tra chuỗi bắt đầu với **
        if text.startswith('**'):
            # Tìm vị trí kết thúc của dấu **
            end_pos = text.find('**', 2)
            if end_pos > 0:
                # Trích xuất tiêu đề
                heading_text = text[2:end_pos]
                # Lấy phần còn lại của văn bản (nếu có)
                remaining_text = text[end_pos+2:].strip()
                
                if remaining_text:
                    # Kết hợp tiêu đề và phần còn lại để không mất nội dung
                    return ("heading", heading_text + ": " + remaining_text)
                else:
                    return ("heading", heading_text)
        
        # Nếu không phải tiêu đề, hoặc định dạng không đúng
        return ("normal", text)

    def create_market_data_table(self, market_data):
        """Tạo bảng dữ liệu thị trường cho phần sidebar"""
        if not market_data:
            return []
        
        # Tạo Spacer trước bảng
        spacer = Spacer(1, 0.2*cm)
        
        # Chuẩn bị dữ liệu cố định cho bảng - tất cả là N/A trước khi kiểm tra
        fixed_data = [
            ["VNINDEX", "N/A"],
            ["HNXINDEX", "N/A"],
            ["Vốn hóa (tỷ VND)", "N/A"],
            ["SLCP lưu hành (tr CP)", "N/A"],
            ["52-tuần cao/thấp", "N/A"],
            ["KLGD 90 ngày (tr CP)", "N/A"],
            ["GTGD 90 ngày (tỷ)", "N/A"]
        ]
        
        # Map keys từ market_data API sang keys trong giao diện hiển thị 
        key_mapping = {
            "VNINDEX": "VNINDEX",
            "HNXINDEX": "HNXINDEX",
            "Vốn hóa (tỷ VND)": "Vốn hóa (tỷ VND)",
            "SL CP lưu hành (triệu CP)": "SLCP lưu hành (tr CP)",
            "52-tuần cao/thấp": "52-tuần cao/thấp",
            "KLGD bình quân 90 ngày": "KLGD 90 ngày (tr CP)",
            "GTGD bình quân 90 ngày": "GTGD 90 ngày (tỷ)"
        }
        
        # Cập nhật giá trị từ market_data nếu có
        for i, row in enumerate(fixed_data):
            key_display = row[0]
            key_in_data = next((k for k, v in key_mapping.items() if v == key_display), None)
            
            if key_in_data and key_in_data in market_data:
                fixed_data[i][1] = market_data[key_in_data]
        
        # Điều chỉnh kích thước cột để vừa với không gian
        table = Table(fixed_data, colWidths=[3.2*cm, 2.6*cm], spaceBefore=3, spaceAfter=3)
        
        # Style cho bảng
        table_style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (0, 0), (0, -1), 2),
            ('LEFTPADDING', (1, 0), (1, -1), 2),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#0066CC')),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor('#0066CC')),
        ])
        
        # Thêm màu nền cho chỉ số thị trường
        table_style.add('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#E6F0FA'))
        
        table.setStyle(table_style)
        
        # Tăng khoảng cách giữa các bảng
        middle_spacer = Spacer(1, 0.3*cm)
        
        # Xử lý phần cổ đông lớn
        shareholders = []
        if "co_dong_lon" in market_data and market_data["co_dong_lon"] is not None:
            shareholders_df = market_data["co_dong_lon"]
            
            shareholder_title = Paragraph("Cổ đông lớn (%)", self.styles['MarketDataTitle'])
            shareholders.append(shareholder_title)
            shareholders.append(Spacer(1, 0.1*cm))
            
            if not shareholders_df.empty:
                try:
                    share_holder_col = None
                    share_percent_col = None
                    
                    for col in shareholders_df.columns:
                        if 'hold' in str(col).lower() or 'name' in str(col).lower():
                            share_holder_col = col
                            break
                    
                    for col in shareholders_df.columns:
                        if 'percent' in str(col).lower() or 'own' in str(col).lower() or 'ratio' in str(col).lower():
                            share_percent_col = col
                            break
                    
                    if share_holder_col and share_percent_col:
                        formatted_shareholders = []
                        for i in range(min(3, len(shareholders_df))):
                            try:
                                holder_name = str(shareholders_df.iloc[i][share_holder_col])
                                if len(holder_name) > 20:
                                    holder_name = holder_name[:18] + "..."
                                
                                ownership_ratio = float(shareholders_df.iloc[i][share_percent_col]) * 100
                                formatted_shareholders.append([holder_name, f"{ownership_ratio:.2f}%"])
                            except (ValueError, TypeError) as e:
                                print(f"Lỗi khi xử lý cổ đông {i}: {str(e)}")
                                continue
                        
                        if formatted_shareholders:
                            shareholder_table = Table(
                                formatted_shareholders, 
                                colWidths=[4.0*cm, 1.8*cm],
                                spaceBefore=3,
                                spaceAfter=3
                            )
                            
                            shareholder_style = TableStyle([
                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                                ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
                                ('FONTNAME', (1, 0), (1, -1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                                ('TOPPADDING', (0, 0), (-1, -1), 5),
                                ('LEFTPADDING', (0, 0), (0, -1), 0),
                                ('RIGHTPADDING', (1, 0), (1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
                            ])
                            
                            shareholder_table.setStyle(shareholder_style)
                            shareholders.append(shareholder_table)
                        else:
                            no_data = Paragraph("Không có dữ liệu", self.styles['NormalVN'])
                            shareholders.append(no_data)
                    else:
                        no_column = Paragraph("Không tìm thấy cột dữ liệu", self.styles['NormalVN'])
                        shareholders.append(no_column)
                except Exception as e:
                    error_msg = Paragraph(f"Lỗi: {str(e)[:30]}...", self.styles['NormalVN'])
                    shareholders.append(error_msg)
            else:
                empty_df = Paragraph("Không có dữ liệu cổ đông", self.styles['NormalVN'])
                shareholders.append(empty_df)
        
        elements = [spacer, table]
        
        if shareholders:
            elements.append(middle_spacer)
            elements.extend(shareholders)
        
        return elements

    def _draw_page_template(self, canvas, doc, company_data):
        """Vẽ template cho trang báo cáo"""
        try:
            width, height = A4
            
            # Vẽ background header màu xanh
            canvas.setFillColor(self.blue_color)
            canvas.rect(0, height - 3*cm, width, 3*cm, fill=1, stroke=0)
            
            # Chuẩn bị tên công ty
            company_name = "Công ty Cổ phần"
            info_text = "Thông tin công ty"
            
            # Lấy thông tin từ company_data nếu có
            if company_data is not None and isinstance(company_data, dict):
                if 'name' in company_data and company_data['name']:
                    company_name = str(company_data['name'])
                elif 'symbol' in company_data and company_data['symbol']:
                    company_name = f"Công ty Cổ phần {company_data['symbol']}"
                    
                if 'info' in company_data and company_data['info']:
                    info_text = str(company_data['info'])
            
            # Vẽ tên công ty
            canvas.setFont('DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold', 16)
            canvas.setFillColor(colors.white)
            canvas.drawString(0.5*cm, height - 1.8*cm, company_name)
            
            # Vẽ thông tin phụ
            canvas.setFont('DejaVuSans' if self.font_added else 'Helvetica', 12)
            canvas.drawString(0.5*cm, height - 2.5*cm, info_text)
            
            # Vẽ đường kẻ phân cách giữa sidebar và phần nội dung
            canvas.setStrokeColor(colors.lightgrey)
            canvas.line(6.5*cm, 0, 6.5*cm, height - 3*cm)
        except Exception as e:
            # Ghi lại lỗi nhưng vẫn tiếp tục
            print(f"Lỗi trong _draw_page_template: {str(e)}")
            
            # Để đảm bảo vẫn có header dù bị lỗi
            try:
                canvas.setFillColor(self.blue_color)
                canvas.rect(0, height - 3*cm, width, 3*cm, fill=1, stroke=0)
                canvas.setFont('DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold', 16)
                canvas.setFillColor(colors.white)
                canvas.drawString(0.5*cm, height - 1.8*cm, "Công ty Cổ phần")
            except:
                pass

    def create_financial_projection_table(self, projection_data=None):
        """Create a table for financial projections"""
        # Map keys to display names for table
        key_mapping = {
            'revenue': 'Doanh thu (tỷ VND)',
            'profit_after_tax': 'Lợi nhuận ròng (tỷ VND)',
            'eps': 'EPS (đồng)',
            'bps': 'BPS (đồng)',
            'npm': 'NPM (%)',
            'roa': 'ROA (%)',
            'roe': 'ROE (%)',
        }
        
        # Create header row with all years
        data = [['Năm', '2022', '2023', '2024', '2025F', '2026F']]
        
        # If projection_data is None, initialize with N/A values for all years
        if not projection_data:
            projection_data = {}
            for key in key_mapping.keys():
                projection_data[key] = ['N/A', 'N/A', 'N/A', 'N/A', 'N/A']
        
        # Add rows for each metric
        for key, display_name in key_mapping.items():
            row = [display_name]
            
            # Get values from projection_data or use N/A if key doesn't exist
            if key in projection_data:
                # After our changes to services.py, projection_data now has the structure:
                # [2022, 2023, 2024, 2025F, 2026F]
                
                # Make sure we have enough values (should be 5)
                if len(projection_data[key]) >= 5:
                    values = projection_data[key][:5]  # Take exactly 5 values
                else:
                    # Handle case where projection_data doesn't have enough values
                    values = projection_data[key] + ['N/A'] * (5 - len(projection_data[key]))
                
                # Special processing for percentage values (ROA, NPM, ROE)
                if key in ['roa', 'npm', 'roe']:
                    formatted_values = []
                    for val in values:
                        if val == 'N/A':
                            formatted_values.append('N/A')
                        else:
                            try:
                                # Try to convert to float and format as percentage
                                numeric_val = float(val.replace(',', '.').replace('%', ''))
                                formatted_values.append(f"{numeric_val:.1f}%")
                            except (ValueError, AttributeError):
                                # If conversion fails, use the original value
                                formatted_values.append(val)
                    row.extend(formatted_values)
                else:
                    row.extend(values)
            else:
                # If key doesn't exist in projection_data, use N/A for all columns
                row.extend(['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
                
            data.append(row)
        
        # Set column widths - adjust for 6 columns total (label + 5 data columns)
        colWidths = [5*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.8*cm]
        
        # Create table
        table = Table(data, colWidths=colWidths, spaceBefore=0.3*cm, spaceAfter=0.5*cm)
        
        # Create style for table
        style = TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (-1, 0), self.blue_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            
            # Main cells
            ('BACKGROUND', (0, 1), (-1, -1), self.light_blue),
            ('FONTNAME', (0, 1), (0, -1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Inner borders
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.white),
            
            # Font size
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])
        
        table.setStyle(style)
        return table

    def create_page1(self, doc, company_data, recommendation_data, market_data, analysis_data, projection_data=None):
        """Tạo nội dung cho trang 1"""
        width, height = A4
        
        # Tạo các frames
        frames = [
            Frame(0, height - 3*cm, width, 3*cm),
            Frame(0, 0, 6.5*cm, height - 3*cm, id='sidebar'),
            Frame(6.5*cm, 0, width - 6.5*cm, height - 3*cm)
        ]
        
        # Story là danh sách các elements để thêm vào PDF
        story = []
        
        # Thêm spacing để tránh chồng lấp với khung màu xanh
        story.append(Spacer(1,2.5*cm))
        
        # Date hiện tại
        date_today = datetime.date.today().strftime('%d/%m/%Y')
        date_label = Paragraph("Báo cáo cập nhật", self.styles['DateLabel'])
        date_value = Paragraph(date_today, self.styles['DateValue'])
        
        # Hiển thị giá hiện tại
        price_label = Paragraph("Giá hiện tại", self.styles['PriceLabel'])
        price_value = Paragraph("<b>{0} VND</b>".format(recommendation_data.get('current_price', 'N/A')), self.styles['PriceValue'])
        
        # Thêm hiển thị giá mục tiêu và suất sinh lời
        target_price_label = Paragraph("Giá mục tiêu dài hạn", self.styles['TargetPriceLabel'])
        target_price = recommendation_data.get('target_price', 'N/A')
        target_price_value = Paragraph("<b>{0} {1}</b>".format(
            target_price, 
            "VND" if target_price != "N/A" else ""
        ), self.styles['TargetPriceValue'])
        
        profit_label = Paragraph("Suất sinh lời", self.styles['ProfitLabel'])
        profit_percent = recommendation_data.get('profit_percent', 'N/A')
        
        if profit_percent == "N/A":
            profit_value = Paragraph("<b>N/A</b>", self.styles['ProfitValue'])
        else:
            try:
                profit_num = float(profit_percent)
                profit_display = profit_num * 100
                profit_color = "green" if profit_num > 0 else "red"
                sign = "+" if profit_num > 0 else ""
                profit_value = Paragraph("<b><font color='{0}'>{1}{2:.2f}%</font></b>".format(
                    profit_color, sign, profit_display
                ), self.styles['ProfitValue'])
            except (ValueError, TypeError):
                profit_value = Paragraph("<b>N/A</b>", self.styles['ProfitValue'])
        
        # Thêm thông tin giá và ngày vào story trong sidebar
        story.append(date_label)
        story.append(date_value)
        story.append(Spacer(1, 0.2*cm))
        story.append(price_label)
        story.append(price_value)
        story.append(Spacer(1, 0.2*cm))
        story.append(target_price_label)
        story.append(target_price_value)
        story.append(Spacer(1, 0.2*cm))
        story.append(profit_label)
        story.append(profit_value)
        story.append(Spacer(1, 0.5*cm))
        
        # Tạo bảng thông tin thị trường
        story.append(Paragraph("Thị trường", self.styles['MarketDataTitle']))
        story.append(Spacer(1, 0.1*cm))
        
        market_elements = self.create_market_data_table(market_data)
        if market_elements:
            story.extend(market_elements)
        
        # Chuyển sang cột bên phải
        story.append(FrameBreak())
        
        # Nhận nội dung phân tích
        content_list = self._set_style_from_analysis_data_sample(analysis_data)
        
        # Nội dung phân tích với xử lý đặc biệt cho tiêu đề
        for paragraph in content_list:
            content_type, processed_text = self._process_markdown_content(paragraph)
            
            if content_type == "heading":
                story.append(Spacer(1, 0.4*cm))
                title_text = processed_text.split(':')[0].strip() if ':' in processed_text else processed_text
                story.append(Paragraph(title_text, self.styles['SectionTitle']))
                
                if ':' in processed_text:
                    content_text = processed_text.split(':', 1)[1].strip()
                    if content_text:
                        story.append(Spacer(1, 0.1*cm))
                        story.append(Paragraph(content_text, self.styles['NormalVN']))
            else:
                story.append(Paragraph(processed_text, self.styles['NormalVN']))
                story.append(Spacer(1, 0.2*cm))
        
        # Add projection table title
        story.append(Spacer(1, 0.4*cm))
        story.append(Paragraph("Dự phóng tài chính", self.styles['SectionTitle']))
        story.append(Spacer(1, 0.1*cm))
        
        # Add financial projection table
        projection_table = self.create_financial_projection_table(projection_data)
        story.append(projection_table)
        
        return story

    def _set_style_from_analysis_data_sample(self, analysis_data):
        """Xử lý mẫu dữ liệu phân tích và chia thành các phần tiêu đề và nội dung"""
        content = []
        
        if not analysis_data or not analysis_data.get('content'):
            sample_text = """**Giới thiệu về công ty** Công ty Cổ phần Thép Nam Kim (NKG) là một trong những công ty hàng đầu tại Việt Nam trong lĩnh vực thép mạ và ống thép. Thành lập vào năm 2002, Nam Kim đã nhanh chóng khẳng định vị thế của mình trong ngành công nghiệp thép Việt Nam. Công ty chuyên sản xuất và kinh doanh các sản phẩm thép mạ (tôn mạ kẽm, tôn mạ lạnh, tôn mạ màu), ống thép, xà gồ, và các sản phẩm thép công nghiệp khác. Nam Kim hiện sở hữu 5 nhà máy sản xuất với công suất lên tới hơn 1.2 triệu tấn sản phẩm mỗi năm, đáp ứng nhu cầu thị trường trong nước và xuất khẩu.
            
**Tình hình tài chính hiện nay** Nam Kim đã trải qua những biến động mạnh về tài chính trong những năm gần đây. Doanh thu của công ty có xu hướng tăng trưởng từ 11,559 tỷ đồng lên 28,173 tỷ đồng, sau đó điều chỉnh xuống 23,071 tỷ đồng. Tuy nhiên, lợi nhuận biến động đáng kể với biên lợi nhuận ròng dao động từ 2.55% lên 7.90% rồi giảm xuống -0.54% trong giai đoạn khó khăn. Tỷ lệ nợ trên vốn chủ sở hữu duy trì ở mức cao, khoảng 150-170%, phản ánh chiến lược sử dụng đòn bẩy tài chính của công ty. Hiện tại, Nam Kim đang trong quá trình cải thiện hiệu quả hoạt động, tối ưu hóa chi phí và tăng cường xuất khẩu để cải thiện biên lợi nhuận. Thị trường thép toàn cầu đang dần phục hồi sau giai đoạn khó khăn, tạo điều kiện thuận lợi cho Nam Kim cải thiện kết quả kinh doanh trong thời gian tới."""
            
            paragraphs = [p.strip() for p in sample_text.split('\n') if p.strip()]
            content.extend(paragraphs)
            return content
            
        if isinstance(analysis_data.get('content'), list):
            content = analysis_data.get('content')
            return content
        else:
            text = analysis_data.get('content', '')
            if isinstance(text, str):
                content = [p.strip() for p in text.split('\n\n') if p.strip()]
            
        return content

    def format_row(self, row_data):
        # Đảm bảo row_data[0] (tên khoản mục) luôn tồn tại
        result = [Paragraph(str(row_data[0]), self.styles['ItemCell'])]
        
        # Thêm các cột dữ liệu, đảm bảo luôn đủ 5 cột
        for i in range(1, 6):
            if i < len(row_data):
                result.append(row_data[i])
            else:
                result.append('N/A')  # Thêm giá trị mặc định nếu thiếu
        
        # Chuyển comment (cột cuối) thành Paragraph nếu có
        if len(result) > 5 and result[5] and result[5] != 'N/A':
            result[5] = Paragraph(str(result[5]), self.styles['CommentCell'])
        
        return result
