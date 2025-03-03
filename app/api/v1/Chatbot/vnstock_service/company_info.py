import os
import json
from .get_data import Vnstockk

class CompanyInfo:
    """Service for handling company information"""
    
    def __init__(self):
        self.time_period = "quarter"  # Default to quarterly data
        
    def get_company_info(self, symbol):
        """Get comprehensive company information"""
        vnstock_instance = Vnstockk()
        
        try:
            # Check if data already exists
            file_path = os.path.join("financial_data", f"{symbol}_{self.time_period}_company_info.json")
            print(f"Looking for file: {file_path}")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    company_data = json.load(f)
                    print(f"Found existing company data with sections: {list(company_data.keys())}")
            else:
                # Load new data
                print(f"File not found. Loading new data...")
                company_data = vnstock_instance.company_info(symbol, self.time_period)
                print(f"Loaded new company data")
                
            return True, company_data
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error loading company information: {str(e)}"
    
    def format_company_section_data(self, symbol, section, data):
        """Format company section data for display"""
        max_items = 20  # Limit number of items displayed
        result = ""
        
        if section == "overview":
            result = f"📋 Tổng quan {symbol}:\n\n"
            if isinstance(data, list) and data:
                overview = data[0]
                name = overview.get("short_name", symbol)
                exchange = overview.get("exchange", "N/A")
                industry = overview.get("industry", "N/A")
                website = overview.get("website", "N/A")
                established = overview.get("established_year", "N/A")
                employees = overview.get("no_employees", "N/A")
                foreign_percent = overview.get("foreign_percent", 0)
                
                result += f"Tên: {name}\n"
                result += f"Sàn: {exchange}\n"
                result += f"Ngành: {industry}\n"
                result += f"Website: {website}\n"
                result += f"Năm thành lập: {established}\n"
                result += f"Số nhân viên: {employees}\n"
                result += f"Tỷ lệ nước ngoài: {foreign_percent*100:.2f}%\n"
            else:
                result += "Không có thông tin tổng quan"
        
        elif section == "profile":
            result = f"📝 Hồ sơ {symbol}:\n\n"
            if isinstance(data, list) and data:
                profile = data[0]
                company_name = profile.get("company_name", "N/A")
                company_profile = profile.get("company_profile", "Không có thông tin")
                
                result += f"Tên công ty: {company_name}\n\n"
                result += f"{company_profile}\n"
            else:
                result += "Không có thông tin hồ sơ"
        
        elif section == "shareholders":
            result = f"👥 Cổ đông chính của {symbol}:\n\n"
            for i, item in enumerate(data[:max_items], 1):
                name = item.get("share_holder", "N/A")
                percent = item.get("share_own_percent", 0)
                percent_display = percent*100 if percent < 1 else percent
                result += f"{i}. {name}: {percent_display:.2f}%\n"
        
        elif section == "insider_deals":
            result = f"🤝 Giao dịch nội bộ gần đây của {symbol}:\n\n"
            for i, item in enumerate(data[:max_items], 1):
                date = item.get("deal_announce_date", "N/A")
                action = item.get("deal_action", "N/A")
                quantity = item.get("deal_quantity", 0)
                
                result += f"{i}. Ngày: {date}\n"
                result += f"   Hành động: {action}\n"
                result += f"   Khối lượng: {quantity:,.0f}\n\n"
        
        elif section == "subsidiaries":
            result = f"🏢 Công ty con của {symbol}:\n\n"
            for i, item in enumerate(data[:max_items], 1):
                name = item.get("sub_company_name", "N/A")
                percent = item.get("sub_own_percent", 0)
                percent_display = percent*100 if percent < 1 else percent
                result += f"{i}. {name}: {percent_display:.2f}%\n"
        
        elif section == "officers":
            result = f"👨‍💼 Ban lãnh đạo của {symbol}:\n\n"
            for i, item in enumerate(data[:max_items], 1):
                name = item.get("officer_name", "N/A")
                position = item.get("officer_position", "N/A") or "N/A"
                own_percent = item.get("officer_own_percent", 0)
                percent_display = own_percent*100 if own_percent < 1 else own_percent
                
                result += f"{i}. {name}\n"
                result += f"   Chức vụ: {position}\n"
                result += f"   Tỷ lệ sở hữu: {percent_display:.4f}%\n\n"
        
        elif section == "news":
            result = f"📰 Tin tức gần đây về {symbol}:\n\n"
            for i, item in enumerate(data[:max_items], 1):
                title = str(item.get("title", ""))
                if title.startswith(f"{symbol}:"):
                    title = title.split(":", 1)[1].strip()
                date = item.get("publish_date", "N/A")
                
                result += f"{i}. [{date}] {title}\n\n"
        
        else:
            result = f"Không có dữ liệu {section} cho {symbol}"
            
        return result
    
    def get_help(self):
        """Return a help message for company information functionality"""
        return (
            "Hướng dẫn sử dụng tìm kiếm thông tin công ty:\n\n"
            "1. Sử dụng lệnh /search [mã cổ phiếu] để bắt đầu.\n"
            "2. Chọn 'Thông tin công ty' để xem thông tin về công ty.\n"
            "3. Chọn mục thông tin cụ thể (Tổng quan, Hồ sơ, Cổ đông...).\n"
        )
