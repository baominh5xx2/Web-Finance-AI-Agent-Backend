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
import json
from ..module_report.api_gemini import generate_financial_commentary

class Page2:
    def __init__(self, font_added=False):
        self.font_added = font_added
        self.styles = getSampleStyleSheet()
        
        # Define colors
        self.blue_color = colors.HexColor('#0066CC')
        
        # Font configuration
        title_font = 'DejaVuSans-Bold' if font_added else 'Helvetica-Bold'
        normal_font = 'DejaVuSans' if font_added else 'Helvetica'
        
        # Add styles
        self.styles.add(ParagraphStyle(
            name='ProjectionTitle',
            fontName=title_font,
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=6,
            leading=16
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            fontName=title_font,
            fontSize=10,
            textColor=colors.black,
            alignment=TA_CENTER,
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCell',
            fontName=normal_font,
            fontSize=9,
            alignment=TA_LEFT,
            leading=12
        ))

        # Add styles for comment cells
        self.styles.add(ParagraphStyle(
            name='CommentCell',
            fontName='DejaVuSans' if self.font_added else 'Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leading=12,
            wordWrap='CJK',  # Better word wrapping for Asian languages
            firstLineIndent=0,
            leftIndent=0,
            rightIndent=0
        ))

        # Add styles for item name cells
        self.styles.add(ParagraphStyle(
            name='ItemCell',
            fontName='DejaVuSans' if self.font_added else 'Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leading=12,
            wordWrap='CJK'  # Better word wrapping for Asian languages
        ))

        # Add styles for bold item name cells (for parent items)
        self.styles.add(ParagraphStyle(
            name='BoldItemCell',
            fontName='DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold',
            fontSize=9,
            alignment=TA_LEFT,
            leading=12,
            wordWrap='CJK'  # Better word wrapping for Asian languages
        ))

        # Add styles for sub-item name cells
        self.styles.add(ParagraphStyle(
            name='SubItemCell',
            fontName='DejaVuSans' if self.font_added else 'Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leading=12,
            leftIndent=10,  # Thụt lề để phân biệt mục con
            wordWrap='CJK'
        ))

    def _draw_page_template(self, canvas, doc, company_data):
        """Vẽ header và footer cho trang"""
        width, height = A4
    
        # Vẽ header
        canvas.setFillColor(self.blue_color)
        canvas.rect(0, height - 20*mm, width, 20*mm, fill=1, stroke=0)
        
        # Tên công ty và mã chứng khoán
        canvas.setFillColor(colors.white)
        canvas.setFont('DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold', 12)
        company_name = company_data.get('name', '')
        symbol = company_data.get('symbol', '')
        header_text = f"{company_name} ({symbol}) - Dự phóng Tài chính"
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
        canvas.drawRightString(width - 1*cm, 3.5*mm, f"Trang 2")
        
        # Thông tin công ty
        canvas.drawString(1*cm, 3.5*mm, "FinBot - Trí tuệ tài chính cho mọi người")

    def format_row(self, row_data, is_sub_item=False, is_bold=False):
        """Format a table row with appropriate styles"""
        # Tạo bản sao của row_data để tránh thay đổi tham chiếu gốc
        result = row_data.copy()
        
        # Đảm bảo dữ liệu có đủ 6 phần tử
        while len(result) < 6:
            result.append('N/A')
            
        # Convert the first column (item name) to Paragraph with appropriate style
        if is_bold:
            style = self.styles['BoldItemCell']
        elif is_sub_item:
            style = self.styles['SubItemCell']
        else:
            style = self.styles['ItemCell']
            
        result[0] = Paragraph(str(result[0]), style)
        
        # Format value columns (number formatting)
        for i in range(1, 5):
            if result[i] != 'N/A' and result[i]:
                # Already formatted with commas, don't modify
                pass
        
        # Debug print to check the comment value before conversion
        comment_value = result[5]
        print(f"Comment for row: '{comment_value}'")
        
        # Convert comments to Paragraph for proper wrapping
        if result[5] and result[5] != 'N/A':
            # Use CommentCell style which has proper word wrapping
            result[5] = Paragraph(str(result[5]), self.styles['CommentCell'])
        else:
            # Set empty string for empty comments to avoid N/A display
            result[5] = ''
            
        return result

    def create_projection_table(self, projection_data):
        """Create the business projection table"""
        elements = []
        
        # Add title
        title = Paragraph("Cập nhật kết quả kinh doanh 2024 và dự phóng 2025", self.styles['ProjectionTitle'])
        elements.append(title)
        elements.append(Spacer(1, 5*mm))
        
        # Prepare table headers
        headers = [
            [Paragraph('Khoản mục', self.styles['TableHeader']), '2024', '', '2025F', '', Paragraph('Chú thích', self.styles['TableHeader'])],
            ['', '(Tỷ đồng)', '%YoY', '(Tỷ đồng)', '%YoY', '']
        ]
        
        # Test comment data - remove this when connecting to database
        chú_thích = {
            'Doanh thu thuần': '',
            'Lợi nhuận gộp': '',
            'Chi phí': '',
            'Lợi nhuận từ HĐKD': '',
            'Lợi nhuận trước thuế': '',
            'Lợi nhuận sau thuế': ''
        }
        
        # Check if we should generate AI commentary
        try:
            # Load NKG_data.json for additional context
            company_data_path = os.path.join("backend", "app", "api", "v2", "report", "data", "NKG_data.json")
            company_data = None
            if os.path.exists(company_data_path):
                with open(company_data_path, 'r', encoding='utf-8') as f:
                    company_data = json.load(f)
                    
            # Check for cached commentary file
            cached_comments_path = os.path.join("backend", "app", "api", "v2", "report", "data", "NKG_page2_comments_cache.json")
            cached_comments = None
            try:
                if os.path.exists(cached_comments_path):
                    with open(cached_comments_path, 'r', encoding='utf-8') as f:
                        cached_comments = json.load(f)
                    print(f"Loaded cached comments as fallback: {list(cached_comments.keys())}")
            except Exception as e:
                print(f"Error loading cached comments: {str(e)}")
                cached_comments = None
            
            # Always generate fresh AI commentary
            print("Generating fresh AI commentary through Gemini API...")
            
            print("Original chú_thích keys before AI generation:", list(chú_thích.keys()))
            ai_commentaries = self.generate_financial_commentaryy(projection_data)
            
            if ai_commentaries:
                print("AI commentaries returned these keys:", list(ai_commentaries.keys()))
                # Update chú_thích with AI-generated commentaries
                updated_keys = []
                for key, value in ai_commentaries.items():
                    if value:  # Only update if we got a valid commentary
                        chú_thích[key] = value
                        updated_keys.append(key)
                        print(f"Updated chú_thích[{key}] = {value[:50]}...")
                
                # Ensure all three main sections have content
                required_keys = ['Doanh thu thuần', 'Lợi nhuận gộp', 'Lợi nhuận từ HĐKD']
                for key in required_keys:
                    if key not in updated_keys:
                        print(f"WARNING: Missing commentary for {key}, attempting to regenerate")
                        # Try one more time with fallback data
                        try:
                            fallback_path = os.path.join("backend", "app", "api", "v2", "report", "data", "NKG_page2_data.json")
                            if os.path.exists(fallback_path):
                                with open(fallback_path, 'r', encoding='utf-8') as f:
                                    fallback_data = json.load(f)
                                print(f"Using fallback data from {fallback_path}")
                                
                                # Try to get the specific commentary from fallback data
                                comment_key = "comment_" + key.lower().replace(' ', '_').replace('ậ', 'a').replace('ừ', 'u').replace('đ', 'd')
                                if comment_key in fallback_data:
                                    chú_thích[key] = fallback_data[comment_key]
                                    print(f"Used fallback comment for {key}")
                        except Exception as e:
                            print(f"Error using fallback data: {str(e)}")
                
                print("Successfully generated AI commentaries for all sections")
                
                # Save generated commentaries to cache file
                try:
                    with open(cached_comments_path, 'w', encoding='utf-8') as f:
                        json.dump(chú_thích, f, ensure_ascii=False, indent=2)
                    print(f"Saved commentaries to cache file: {cached_comments_path}")
                except Exception as e:
                    print(f"Error saving commentaries to cache: {str(e)}")
            else:
                print("WARNING: AI commentaries returned None or empty dictionary!")
                if cached_comments:
                    # Use cached comments as fallback
                    print("Using cached comments as fallback")
                    for key, value in cached_comments.items():
                        if value:  # Only update if we got a valid commentary
                            chú_thích[key] = value
                else:
                    # Use fallback commentaries from NKG_page2_data.json
                    try:
                        fallback_path = os.path.join("backend", "app", "api", "v2", "report", "data", "NKG_page2_data.json")
                        if os.path.exists(fallback_path):
                            with open(fallback_path, 'r', encoding='utf-8') as f:
                                fallback_data = json.load(f)
                                print(f"Using comments from NKG_page2_data.json")
                                
                                comment_mapping = {
                                    'Doanh thu thuần': 'comment_doanh_thu',
                                    'Lợi nhuận gộp': 'comment_loi_nhuan_gop', 
                                    'Lợi nhuận từ HĐKD': 'comment_loi_nhuan_hdkd'
                                }
                                
                                for display_key, json_key in comment_mapping.items():
                                    if json_key in fallback_data:
                                        chú_thích[display_key] = fallback_data[json_key]
                                        print(f"Used comment from NKG_page2_data.json for {display_key}")
                        else:
                            # Last resort: use hardcoded fallback commentaries
                            print("Using hardcoded fallback commentaries")
                            fallback_commentaries = {
                                'Doanh thu thuần': '',
                                'Lợi nhuận gộp': '',
                                'Lợi nhuận từ HĐKD': ''
                            }
                            
                            for key, value in fallback_commentaries.items():
                                chú_thích[key] = value
                    except Exception as e:
                        print(f"Error using NKG_page2_data.json: {str(e)}")
                        # Use hardcoded fallback commentaries
                        print("Using hardcoded fallback commentaries due to error")
                        fallback_commentaries = {
                            'Doanh thu thuần': '',
                            'Lợi nhuận gộp': '',
                            'Lợi nhuận từ HĐKD': ''
                        }
                        
                        for key, value in fallback_commentaries.items():
                            chú_thích[key] = value
            
            print("Final chú_thích keys after AI generation:", list(chú_thích.keys()))
            
            # Additional logic for enhancing commentary with specific metrics
            if projection_data:
                # Helper function to determine if a growth value is positive
                def is_growth_positive(growth_str):
                    try:
                        if not growth_str or growth_str == 'N/A':
                            return False
                        # Remove percentage sign and check if value is positive
                        value = float(growth_str.replace('%', '').strip())
                        return value >= 0
                    except (ValueError, AttributeError):
                        return False
                    
                # Helper function to safely convert financial values
                def safe_float_convert(value_str):
                    try:
                        if not value_str or value_str == 'N/A':
                            return 0
                        # Remove negative sign, commas and convert to float
                        return float(value_str.replace('-', '').replace(',', '').replace('%', ''))
                    except (ValueError, AttributeError):
                        return 0

                # Enhancement of gross profit commentary with expense details
                gross_profit_commentary = chú_thích.get('Lợi nhuận gộp', '')
                financial_expenses = []
                
                # Add financial expenses details if they are significant
                if projection_data.get('chi_phi_tai_chinh') and safe_float_convert(projection_data.get('chi_phi_tai_chinh', '0')) > 0:
                    direction = "tăng" if is_growth_positive(projection_data.get('yoy_chi_phi_tai_chinh', '')) else "giảm"
                    financial_expenses.append(f"Chi phí tài chính {direction} ({projection_data.get('yoy_chi_phi_tai_chinh', 'N/A')}) {direction == 'giảm' and 'nhờ tái cấu trúc nợ' or 'do biến động tỷ giá và lãi suất'}.")
                
                # Add selling expenses details if they are significant
                if projection_data.get('chi_phi_ban_hang') and safe_float_convert(projection_data.get('chi_phi_ban_hang', '0')) > 0:
                    direction = "tăng" if is_growth_positive(projection_data.get('yoy_chi_phi_ban_hang', '')) else "giảm"
                    financial_expenses.append(f"Chi phí bán hàng {direction} ({projection_data.get('yoy_chi_phi_ban_hang', 'N/A')}) {direction == 'giảm' and 'nhờ tối ưu hóa kênh phân phối' or 'do đẩy mạnh marketing'}.")
                
                # Add management expenses details if they are significant
                if projection_data.get('chi_phi_quan_ly') and safe_float_convert(projection_data.get('chi_phi_quan_ly', '0')) > 0:
                    direction = "tăng" if is_growth_positive(projection_data.get('yoy_chi_phi_quan_ly', '')) else "giảm"
                    financial_expenses.append(f"Chi phí quản lý {direction} ({projection_data.get('yoy_chi_phi_quan_ly', 'N/A')}) {direction == 'giảm' and 'nhờ tối ưu hóa bộ máy quản lý' or 'do mở rộng hoạt động'}.")
                
                # Combine all commentary parts
                if financial_expenses:
                    combined_commentary = gross_profit_commentary
                    if combined_commentary and not combined_commentary.endswith('.'):
                        combined_commentary += '.'
                    combined_commentary += ' ' + ' '.join(financial_expenses)
                    chú_thích['Lợi nhuận gộp'] = combined_commentary
                
                # Combine profit-related commentaries
                operating_profit_commentary = chú_thích.get('Lợi nhuận từ HĐKD', '')
                profit_details = []
                
                # Add profit before tax details
                if projection_data.get('loi_nhuan_truoc_thue') and safe_float_convert(projection_data.get('loi_nhuan_truoc_thue', '0')) > 0:
                    direction = "tăng" if is_growth_positive(projection_data.get('yoy_loi_nhuan_truoc_thue', '')) else "giảm"
                    profit_details.append(f"Lợi nhuận trước thuế {direction} ({projection_data.get('yoy_loi_nhuan_truoc_thue', 'N/A')}) nhờ {direction == 'tăng' and 'cải thiện biên lợi nhuận' or 'các yếu tố đặc biệt'}.")
                
                # Add profit after tax details
                if projection_data.get('loi_nhuan_sau_thue') and safe_float_convert(projection_data.get('loi_nhuan_sau_thue', '0')) > 0:
                    direction = "tăng" if is_growth_positive(projection_data.get('yoy_loi_nhuan_sau_thue', '')) else "giảm"
                    profit_details.append(f"Lợi nhuận sau thuế {direction} {direction == 'tăng' and 'trưởng tích cực' or ''} ({projection_data.get('yoy_loi_nhuan_sau_thue', 'N/A')}) nhờ {direction == 'tăng' and 'tối ưu hóa thuế và hiệu quả kinh doanh' or 'các điều chỉnh thuế'}.")
                
                # Combine all profit commentary parts
                if profit_details:
                    combined_commentary = operating_profit_commentary
                    if combined_commentary and not combined_commentary.endswith('.'):
                        combined_commentary += '.'
                    combined_commentary += ' ' + ' '.join(profit_details)
                    chú_thích['Lợi nhuận từ HĐKD'] = combined_commentary
                
                print("Updated commentaries with AI-generated content and enhanced merged cell commentaries")
        except Exception as e:
            print(f"Error generating AI commentaries: {str(e)}")
            # Continue with default commentaries
            
        # Check if we have valid projection data
        if projection_data:
            # Prepare data for table using values from projection_data
            # Dictionary mapping from field names to row data (item name, value, growth rate)
            data_mapping = {
                # [value_key, growth_key, is_bold, is_sub_item]
                'Doanh thu thuần': ['doanh_thu_thuan', 'yoy_doanh_thu', True, False],
                'Lợi nhuận gộp': ['loi_nhuan_gop', 'yoy_loi_nhuan_gop', True, False],
                'Chi phí tài chính': ['chi_phi_tai_chinh', 'yoy_chi_phi_tai_chinh', False, True],
                'Chi phí bán hàng': ['chi_phi_ban_hang', 'yoy_chi_phi_ban_hang', False, True],
                'Chi phí quản lý': ['chi_phi_quan_ly', 'yoy_chi_phi_quan_ly', False, True],
                'Lợi nhuận từ HĐKD': ['loi_nhuan_hdkd', 'yoy_loi_nhuan_hdkd', True, False],
                'LNTT': ['loi_nhuan_truoc_thue', 'yoy_loi_nhuan_truoc_thue', False, True],
                'LNST': ['loi_nhuan_sau_thue', 'yoy_loi_nhuan_sau_thue', False, True]
            }
            
            # Create table rows with data from projection_data
            data = []
            
            print("Processing projection data")
            for item_name, info in data_mapping.items():
                value_key, growth_key, is_bold, is_sub_item = info
                
                # For items with a 2025F projection, we need to extract the values
                # The dictionary keys have a specific pattern
                value_key_2025 = f"{value_key}_2025F"  # Key for 2025F value
                growth_key_2025 = f"{growth_key}_2025F"  # Key for 2025F growth rate
                
                # Prefix for LNTT and LNST rows
                prefix = "    " if item_name in ["LNTT", "LNST"] else ""
                
                # Get values from projection_data
                value_2024 = projection_data.get(value_key, 'N/A')
                growth_2024 = projection_data.get(growth_key, 'N/A')
                value_2025 = projection_data.get(value_key_2025, 'N/A')
                growth_2025 = projection_data.get(growth_key_2025, 'N/A')
                
                # Get comment based on whether item is in the chú_thích dictionary
                if item_name in chú_thích:
                    # Use comment from Gemini API
                    comment = chú_thích.get(item_name, '')
                    print(f"Using API comment for {item_name}: {comment[:40]}...")
                elif item_name in ['Chi phí tài chính', 'Chi phí bán hàng', 'Chi phí quản lý']:
                    # Use the shared "Chi phí" comment for all expense items
                    comment = chú_thích.get('Chi phí', '')
                    print(f"Using shared 'Chi phí' comment for {item_name}: {comment[:40]}...")
                else:
                    # For items not in chú_thích, keep empty
                    comment = ''
                    print(f"No API comment for {item_name}, using empty string")
                    
                # Debug output
                print(f"Item: {item_name}, Keys: {value_key}, {growth_key}")
                print(f"Values: 2024={value_2024}, %={growth_2024}, 2025={value_2025}, %={growth_2025}")
                
                # Create row with available data and comment
                row = [prefix + item_name, value_2024, growth_2024, value_2025, growth_2025, comment]
                
                # Format the row
                data.append(self.format_row(row, is_sub_item, is_bold))
        else:
            # Fallback to default rows with N/A values but with EMPTY comments
            data = [
                self.format_row(['Doanh thu thuần', 'N/A', 'N/A', 'N/A', 'N/A', 
                                ''], is_bold=True),
                self.format_row(['Lợi nhuận gộp', 'N/A', 'N/A', 'N/A', 'N/A', 
                                 ''], is_bold=True),
                self.format_row(['Chi phí tài chính', 'N/A', 'N/A', 'N/A', 'N/A', 
                                 ''], True),
                self.format_row(['Chi phí bán hàng', 'N/A', 'N/A', 'N/A', 'N/A', 
                                 ''], True),
                self.format_row(['Chi phí quản lý', 'N/A', 'N/A', 'N/A', 'N/A', 
                                 ''], True),
                self.format_row(['Lợi nhuận từ HĐKD', 'N/A', 'N/A', 'N/A', 'N/A', 
                                ''], is_bold=True),
                self.format_row(['    LNTT', 'N/A', 'N/A', 'N/A', 'N/A', 
                                ''], True),
                self.format_row(['    LNST', 'N/A', 'N/A', 'N/A', 'N/A', 
                                ''], True)
            ]
        
        # Combine headers and data
        table_data = headers + data
        
        # Create table with specific column widths - adjusted for better fit
        width, height = A4
        available_width = width - (2 * cm)  # Subtract margins
        
        # Simplify column widths - ensure comment column has enough width
        col_widths = [4.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 7.5*cm]  # Fixed width for last column
        
        print(f"Column widths: {col_widths}")
        print(f"Comment column width: {col_widths[-1]}")
        
        table = Table(table_data, colWidths=col_widths, repeatRows=2)  # repeatRows=2 to repeat header on new pages
        
        # Define table style with minimal configuration for comments
        style = TableStyle([
            # Headers
            ('SPAN', (0, 0), (0, 1)),  # Merge "Khoản mục" cells
            ('SPAN', (1, 0), (2, 0)),  # Merge "2024" cells
            ('SPAN', (3, 0), (4, 0)),  # Merge "2025F" cells
            ('SPAN', (5, 0), (5, 1)),  # Merge "Chú thích" cells
            
            # Chỉ gộp ô chú thích của 3 loại chi phí - chú ý chỉ số hàng
            ('SPAN', (5, 4), (5, 6)),  # Gộp cột chú thích (index 5) của 3 dòng chi phí
            
            # Merge chú thích của Lợi nhuận từ HĐKD và 2 chỉ số lợi nhuận (chỉ gộp cột chú thích)
            ('SPAN', (5, 7), (5, 9)),  # Gộp cột chú thích (index 5) của 3 dòng từ Lợi nhuận từ HĐKD đến LNST
            
            # Fonts
            ('FONTNAME', (0, 0), (-1, 1), 'DejaVuSans-Bold' if self.font_added else 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, -1), 'DejaVuSans' if self.font_added else 'Helvetica'),
            
            # Font sizes
            ('FONTSIZE', (0, 0), (-1, 1), 9),
            ('FONTSIZE', (0, 2), (-1, -1), 9),
            
            # Alignment
            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('ALIGN', (1, 2), (4, -1), 'RIGHT'),  # Only align numbers to right
            ('ALIGN', (5, 2), (5, -1), 'LEFT'),   # Ensure comments are left-aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('VALIGN', (5, 4), (5, 6), 'TOP'),    # Vertical alignment for first merged comment
            ('VALIGN', (5, 7), (5, 9), 'TOP'),    # Vertical alignment for second merged comment
            
            # Background colors
            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#E6F0FA')),  # Header
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F5F5F5')),  # Doanh thu thuần
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#F5F5F5')),  # Lợi nhuận gộp
            ('BACKGROUND', (0, 4), (-1, 6), colors.white),    # Các dòng con của Lợi nhuận gộp
            ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#F5F5F5')),  # Lợi nhuận từ HĐKD
            ('BACKGROUND', (0, 8), (-1, 9), colors.white),   # LNTT và LNST (mục con của HĐKD)
            
            # Định dạng đặc biệt cho dòng con
            ('LEFTPADDING', (0, 4), (0, 6), 15),  # Thêm padding bên trái cho dòng con của Lợi nhuận gộp
            ('TEXTCOLOR', (0, 4), (0, 6), colors.HexColor('#666666')),  # Màu chữ nhạt hơn cho dòng con
            ('LEFTPADDING', (0, 8), (0, 9), 15),  # Thêm padding bên trái cho LNTT và LNST
            ('TEXTCOLOR', (0, 8), (0, 9), colors.HexColor('#666666')),  # Màu chữ nhạt hơn cho LNTT và LNST
            
            # Comment column formatting - Ensure proper wrapping
            ('LEFTPADDING', (5, 0), (5, -1), 8),  # Left padding for comments
            ('RIGHTPADDING', (5, 0), (5, -1), 8),  # Right padding for comments
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        return elements

    def create_page2(self, doc, company_data, projection_data=None):
        """Create the complete second page"""
        elements = []
        elements.append(Spacer(1, 1*inch))
        
        # Use sample data if projection_data is None or empty
        if projection_data is None or not projection_data:
            print("Using sample data for page2 projection")
            projection_data = self.generate_sample_data()
            print(f"Generated sample data keys: {projection_data.keys()}")
        else:
            print("Using provided data for page2 projection")
        
        # Note: Financial commentaries will always be generated through the Gemini API
        # Any existing comment fields in projection_data will be ignored
        
        # Add projection table
        elements.extend(self.create_projection_table(projection_data))
        
        return elements

    def generate_sample_data(self):
        """Generate sample data without comments for testing with Gemini API"""
        return {
            'doanh_thu_thuan': '5,240.58',
            'yoy_doanh_thu': '15.20%',
            'doanh_thu_thuan_2025F': '6,026.66',
            'yoy_doanh_thu_2025F': '15.00%',
            'sector_growth': '8.5%',
            'market_share': '12.4%',
            
            'loi_nhuan_gop': '1,624.58',
            'yoy_loi_nhuan_gop': '18.30%',
            'loi_nhuan_gop_2025F': '1,929.33',
            'yoy_loi_nhuan_gop_2025F': '18.75%',
            'bien_loi_nhuan_gop': '31.00%',
            'bien_loi_nhuan_gop_2024': '30.25%',
            
            'chi_phi_tai_chinh': '356.20',
            'yoy_chi_phi_tai_chinh': '-5.80%',
            'chi_phi_tai_chinh_2025F': '338.39',
            'yoy_chi_phi_tai_chinh_2025F': '-5.00%',
            
            'chi_phi_ban_hang': '524.06',
            'yoy_chi_phi_ban_hang': '12.30%',
            'chi_phi_ban_hang_2025F': '602.67',
            'yoy_chi_phi_ban_hang_2025F': '15.00%',
            
            'chi_phi_quan_ly': '262.03',
            'yoy_chi_phi_quan_ly': '7.50%',
            'chi_phi_quan_ly_2025F': '271.20',
            'yoy_chi_phi_quan_ly_2025F': '3.50%',
            'expense_to_revenue_ratio': '21.80%',
            
            'loi_nhuan_hdkd': '482.29',
            'yoy_loi_nhuan_hdkd': '35.40%',
            'loi_nhuan_hdkd_2025F': '717.07',
            'yoy_loi_nhuan_hdkd_2025F': '48.68%',
            'bien_loi_nhuan_hdkd': '9.20%',
            'thue_suat_thuc_te': '20.00%',
            
            'loi_nhuan_truoc_thue': '465.41',
            'yoy_loi_nhuan_truoc_thue': '32.80%',
            'loi_nhuan_truoc_thue_2025F': '702.40',
            'yoy_loi_nhuan_truoc_thue_2025F': '50.92%',
            
            'loi_nhuan_sau_thue': '372.32',
            'yoy_loi_nhuan_sau_thue': '32.80%',
            'loi_nhuan_sau_thue_2025F': '561.92',
            'yoy_loi_nhuan_sau_thue_2025F': '50.92%',
        }

    def generate_financial_commentaryy(self, projection_data):
        """Generate AI-based financial commentary for the key metrics using Gemini API"""
        from app.api.v2.report.module_report.api_gemini import generate_financial_commentary
        import os
        import json
        
        print(f"Calling generate_financial_commentary with data keys: {list(projection_data.keys())}")
        company_code = projection_data.get('company_code', 'NKG')
        
        # Load NKG_page2_data.json as a fallback dataset
        fallback_data = None
        try:
            fallback_path = os.path.join("backend", "app", "api", "v2", "report", "data", "NKG_page2_data.json")
            if os.path.exists(fallback_path):
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    fallback_data = json.load(f)
                print(f"Loaded fallback data from {fallback_path}")
        except Exception as e:
            print(f"Error loading fallback data: {str(e)}")
        
        # Ensure we have needed fields by enriching with fallback data if necessary
        enhanced_data = projection_data.copy()
        if fallback_data:
            for key, value in fallback_data.items():
                if key not in enhanced_data and not key.startswith('comment_'):
                    enhanced_data[key] = value
                    print(f"Added missing field {key} from fallback data")
        
        # Call the API to get fresh commentary for all sections
        print("Calling Gemini API for fresh commentary generation")
        try:
            result = generate_financial_commentary(company_code, enhanced_data)
            print(f"API returned commentary with keys: {list(result.keys() if result else [])}")
            
            # Check if we have all necessary commentaries
            required_keys = ['Doanh thu thuần', 'Lợi nhuận gộp', 'Chi phí', 'Lợi nhuận từ HĐKD']
            missing_keys = [key for key in required_keys if key not in result or not result[key]]
            
            if missing_keys:
                print(f"WARNING: Missing commentaries for: {missing_keys}")
                # Try one more call with even more emphasis on the missing sections
                print("Making second attempt to generate missing commentaries")
                retry_result = generate_financial_commentary(company_code, enhanced_data)
                
                if retry_result:
                    # Update only the missing keys if they're now available
                    for key in missing_keys:
                        if key in retry_result and retry_result[key]:
                            result[key] = retry_result[key]
                            print(f"Successfully generated commentary for {key} on second attempt")
            
            # Final check for any still-missing commentaries
            final_missing = [key for key in required_keys if key not in result or not result[key]]
            if final_missing:
                print(f"WARNING: Still missing commentaries after retries: {final_missing}")
                
                # Use fallback data for any missing sections
                if fallback_data:
                    for key in final_missing:
                        # Adjust mapping for Chi phí
                        if key == 'Chi phí':
                            for expense_type in ['chi_phi_tai_chinh', 'chi_phi_ban_hang', 'chi_phi_quan_ly']:
                                comment_key = f"comment_{expense_type}"
                                if comment_key in fallback_data:
                                    result[key] = fallback_data[comment_key]
                                    print(f"Used fallback comment for {key} from {comment_key}")
                                    break
                        else:
                            comment_key = key.lower().replace(' ', '_').replace('ậ', 'a').replace('ừ', 'u').replace('đ', 'd')
                            comment_key = f"comment_{comment_key}"
                            
                            if comment_key in fallback_data:
                                result[key] = fallback_data[comment_key]
                                print(f"Used fallback comment for {key} from fallback data")
                            else:
                                # Use empty values as last resort
                                result[key] = ""
                                print(f"Used empty value for {key} due to missing data")
            
            # Ensure all profit commentaries are from the same source as operating profit
            if 'Lợi nhuận từ HĐKD' in result:
                result['Lợi nhuận trước thuế'] = result['Lợi nhuận từ HĐKD']
                result['Lợi nhuận sau thuế'] = result['Lợi nhuận từ HĐKD']
            
            print(f"Final commentary includes all required sections: {all(key in result for key in required_keys)}")
            return result
        
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            
            # Use fallback data if available
            if fallback_data:
                fallback_comments = {}
                
                # Map for comment keys
                comment_mapping = {
                    'Doanh thu thuần': 'comment_doanh_thu',
                    'Lợi nhuận gộp': 'comment_loi_nhuan_gop',
                    'Chi phí': 'comment_chi_phi_tai_chinh',  # Sử dụng bất kỳ comment chi phí nào làm đại diện
                    'Lợi nhuận từ HĐKD': 'comment_loi_nhuan_hdkd'
                }
                
                for display_key, json_key in comment_mapping.items():
                    if json_key in fallback_data:
                        fallback_comments[display_key] = fallback_data[json_key]
                
                if fallback_comments:
                    print(f"Using fallback comments from data file")
                    return fallback_comments
            
            # Last resort - empty commentaries
            print("Using empty commentaries due to API error")
            return {
                'Doanh thu thuần': '',
                'Lợi nhuận gộp': '',
                'Chi phí': '',
                'Lợi nhuận từ HĐKD': ''
            }