from fpdf import FPDF
import datetime
import os

class PDFReport(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        # Add fonts during initialization to avoid issues
        self.font_added = False
        self._add_default_fonts()
    
    def _add_default_fonts(self):
        """Add default fonts with proper error handling"""
        try:
            # Try to locate DejaVu font files - check multiple possible locations
            font_paths = [
                'DejaVuSans.ttf',  # Current directory
                os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf'),  # Same directory as this file
                'C:/Windows/Fonts/DejaVuSans.ttf',  # Windows fonts directory
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux common location
            ]
            
            # Try each path until one works
            font_found = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        self.add_font('DejaVu', '', font_path, uni=True)
                        self.add_font('DejaVu', 'B', font_path, uni=True)
                        self.add_font('DejaVu', 'I', font_path, uni=True)
                        font_found = True
                        self.font_added = True
                        print(f"Successfully added font from: {font_path}")
                        break
                    except Exception as e:
                        print(f"Failed to add font from {font_path}: {str(e)}")
                        continue
            
            if not font_found:
                print("Could not find DejaVu font. Using Arial as fallback.")
        except Exception as e:
            print(f"Font setup error: {str(e)}")
            print("Using default fonts.")
    
    def header(self, company_name="Company", today=None):
        if today is None:
            today = datetime.date.today()
        
        # Use fonts safely - fallback to standard fonts if custom fonts fail
        if self.font_added:
            self.set_font('DejaVu', '', 16)
        else:
            self.set_font('Arial', '', 16)
            
        # Set header content
        self.cell(0, 10, company_name, 0, 1, 'R')
        
        if self.font_added:
            self.set_font('DejaVu', '', 10)
        else:
            self.set_font('Arial', '', 10)
            
        self.cell(0, 5, f"Document Date: {today.strftime('%d-%b-%Y')}", 0, 1, 'R')
        self.ln(6)
        
        # Add horizontal line
        self.set_line_width(0.75)
        self.set_draw_color(10, 100, 240)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def create_table(self, data):
        """Create a table from the provided data"""
        row_count = 0
        for item in data:
            if row_count % 2 == 0:
                self.set_fill_color(230, 240, 250)
            else:
                self.set_fill_color(255, 255, 255)
            
            if self.font_added:
                self.set_font('DejaVu', '', 8)
            else:
                self.set_font('Arial', '', 8)
                
            self.cell(50, 6, str(item[0]), 0, 0, 'L', fill=True)
            self.cell(140, 6, str(item[1]), 0, 1, 'L', fill=True)
            row_count += 1
        self.ln(2)

    def add_images(self, chart_files, x_center, img_width, img_height):
        """Add images to the report"""
        y_offset = 35
        for chart_file in chart_files:
            try:
                self.image(chart_file, x=x_center, y=y_offset, w=img_width, h=img_height)
                y_offset += img_height + 10
            except Exception as e:
                print(f"Error adding image {chart_file}: {str(e)}")
                # Add placeholder text instead of image
                self.set_xy(x_center, y_offset)
                self.cell(img_width, 20, f"Image not found: {chart_file}", 1, 1, 'C')
                y_offset += 30
    
    def create_financial_table(self, title, data, years):
        """Create financial tables with standardized formatting"""
        # Header title
        if self.font_added:
            self.set_font("DejaVu", "B", 12)
        else:
            self.set_font("Arial", "B", 12)
            
        self.set_text_color(10, 100, 240)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(2)

        # Column headers
        if self.font_added:
            self.set_font("DejaVu", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
            
        self.set_text_color(0, 0, 0)
        col_width = 50
        year_width = 28
        total_width = col_width + len(years) * year_width
        margin_x = (210 - total_width) / 2
        self.set_x(margin_x)

        # Header row
        self.set_fill_color(255, 255, 255)
        self.cell(col_width, 8, "", 1, 0, "C", fill=True)
        for year in years:
            self.cell(year_width, 8, str(year), 1, 0, "C", fill=True)
        self.ln()

        # Data rows
        self.set_x(margin_x)
        if self.font_added:
            self.set_font("DejaVu", "", 9)
        else:
            self.set_font("Arial", "", 9)
            
        row_count = 0
        for key, values in data.items():
            self.set_fill_color(230, 240, 250) if row_count % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.cell(col_width, 8, key, 1, 0, "L", fill=True)
            for value in values:
                self.cell(year_width, 8, str(value), 1, 0, "R", fill=True)
            self.ln()
            row_count += 1
        self.ln(5)
