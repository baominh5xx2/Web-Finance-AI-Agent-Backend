from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import os
import json
from .get_data import Vnstockk
from .finance_info import FinanceInfo
from .company_info import CompanyInfo

class VNStockService:
    """Enhanced VNStock service that provides stock information via Telegram"""
    
    def __init__(self):
        self.vnstock = Vnstockk()
        self.finance_info = FinanceInfo()
        self.company_info = CompanyInfo()
        self.current_symbol = None
        self.time_period = "quarter"  # Default to quarterly data
        
        # Create directory for financial data if it doesn't exist
        os.makedirs("financial_data", exist_ok=True)

    async def search_stock(self, update: Update, context: CallbackContext):
        """Handle the /search command"""
        if not context.args or len(context.args) != 1:
            # Show interactive menu for stock selection
            keyboard = [
                [
                    InlineKeyboardButton("Nhập mã cổ phiếu", callback_data="vnstock_input_symbol"),
                    InlineKeyboardButton("Xem danh sách", callback_data="vnstock_list_symbols")
                ],
                [
                    InlineKeyboardButton("Thông tin sử dụng", callback_data="vnstock_help")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Vui lòng sử dụng lệnh: /search [mã cổ phiếu] hoặc chọn một tùy chọn bên dưới:",
                reply_markup=reply_markup
            )
            return
            
        symbol = context.args[0].upper()
        self.current_symbol = symbol
        self.finance_info.current_symbol = symbol
        self.company_info.time_period = self.time_period
        
        keyboard = [
            [
                InlineKeyboardButton("Thông tin tài chính", callback_data=f"vnstock_financial_info_{symbol}"),
                InlineKeyboardButton("Thông tin công ty", callback_data=f"vnstock_company_info_{symbol}")
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Chọn loại thông tin về {symbol} bạn muốn xem:",
            reply_markup=reply_markup
        )

    async def get_financial_data(self, update: Update, context: CallbackContext):
        """Handle the /search_get command to retrieve financial data"""
        if not self.current_symbol:
            await update.message.reply_text("Vui lòng sử dụng /search [mã cổ phiếu] trước!")
            return
            
        if not context.args:
            await update.message.reply_text(self.finance_info.get_categories_menu())
            return
            
        category = context.args[0]
        result = self.finance_info.get_indicators(category)
        await update.message.reply_text(result)
        
    async def get_stock_chart(self, update: Update, context: CallbackContext):
        """Handle the /search_chart command to get stock charts"""
        if not self.current_symbol:
            await update.message.reply_text("Vui lòng sử dụng /search [mã cổ phiếu] trước!")
            return
        
        # This would normally fetch and display a chart
        await update.message.reply_text(
            f"📊 Biểu đồ cho {self.current_symbol}:\n\n"
            "Tính năng đang được phát triển. Sẽ có trong bản cập nhật tiếp theo!"
        )
        
    async def handle_callback(self, update: Update, context: CallbackContext):
        """Handle callback queries for VNStock interactions"""
        query = update.callback_query
        await query.answer()
        
        # Handle period selection
        if query.data.startswith("vnstock_period_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                self.time_period = parts[2]  # quarter or yearly
                self.finance_info.time_period = self.time_period
                self.company_info.time_period = self.time_period
                symbol = parts[3]
                self.current_symbol = symbol
                
                await query.edit_message_text(f"Đã tải dữ liệu thành công cho {symbol}!")
                
                keyboard = [
                    [
                        InlineKeyboardButton("Thông tin tài chính", callback_data=f"vnstock_financial_info_{symbol}"),
                        InlineKeyboardButton("Thông tin công ty", callback_data=f"vnstock_company_info_{symbol}"),
                    ],
                    [
                        InlineKeyboardButton("Biểu đồ", callback_data="vnstock_chart")
                    ],
                    [
                        InlineKeyboardButton("Đổi loại dữ liệu", callback_data=f"vnstock_change_period_{symbol}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(f"Chọn loại thông tin về {symbol} bạn muốn xem:", reply_markup=reply_markup)
                return
                
        elif query.data.startswith("vnstock_change_period_"):
            symbol = query.data.replace("vnstock_change_period_", "")
            keyboard = [
                [
                    InlineKeyboardButton("Dữ liệu Quý (Quarterly)", callback_data=f"vnstock_period_quarter_{symbol}"),
                    InlineKeyboardButton("Dữ liệu Năm (Yearly)", callback_data=f"vnstock_period_yearly_{symbol}")
                ],
                [
                    InlineKeyboardButton("← Quay lại", callback_data="vnstock_back_to_main")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"Chọn loại dữ liệu tài chính cho mã {symbol}:",
                reply_markup=reply_markup
            )
            return

        elif query.data.startswith("vnstock_company_info_"):
            symbol = query.data.replace("vnstock_company_info_", "")
            
            await query.edit_message_text(f"Đang tải thông tin công ty {symbol}...")
            
            try:
                success, company_data = self.company_info.get_company_info(symbol)
                
                if not success:
                    await query.edit_message_text(company_data)  # Error message in company_data
                    return
                    
                keyboard = [
                    [
                        InlineKeyboardButton("Tổng quan", callback_data=f"company_section_{symbol}_overview"),
                        InlineKeyboardButton("Hồ sơ", callback_data=f"company_section_{symbol}_profile")
                    ],
                    [
                        InlineKeyboardButton("Cổ đông", callback_data=f"company_section_{symbol}_shareholders"),
                        InlineKeyboardButton("Giao dịch nội bộ", callback_data=f"company_section_{symbol}_insider_deals")
                    ],
                    [
                        InlineKeyboardButton("Công ty con", callback_data=f"company_section_{symbol}_subsidiaries"),
                        InlineKeyboardButton("Ban lãnh đạo", callback_data=f"company_section_{symbol}_officers")
                    ],
                    [
                        InlineKeyboardButton("Tin tức", callback_data=f"company_section_{symbol}_news"),
                    ],
                    [
                        InlineKeyboardButton("← Quay lại", callback_data="vnstock_back_to_main")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(f"Thông tin công ty {symbol}:", reply_markup=reply_markup)
            except Exception as e:
                import traceback
                traceback.print_exc()
                await query.edit_message_text(f"Lỗi khi tải thông tin công ty: {str(e)}")
            
        elif query.data.startswith("vnstock_category_"):
            category = query.data.replace("vnstock_category_", "")
            
            if category == "all":
                result = self.finance_info.get_indicators("all")
                await query.edit_message_text(text=result)
                return
            
            try:
                # Convert category string to index
                category_idx = int(category)
                
                # Get the category name
                categories = [cat for cat in self.finance_info.stock_data.columns.get_level_values(0).unique() 
                             if cat != "Meta"]
                
                if category_idx < 1 or category_idx > len(categories):
                    await query.edit_message_text("Danh mục không hợp lệ.")
                    return
                    
                category_name = categories[category_idx - 1]
                
                # Get indicators for this category
                indicators = [col[1] for col in self.finance_info.stock_data.columns if col[0] == category_name]
                
                # Create buttons for each indicator
                keyboard = []
                # Add buttons with 2 indicators per row
                for i in range(0, len(indicators), 2):
                    row = []
                    row.append(InlineKeyboardButton(
                        indicators[i], 
                        callback_data=f"vn_ind_{category_idx}_{i}"
                    ))
                    
                    if i+1 < len(indicators):
                        row.append(InlineKeyboardButton(
                            indicators[i+1], 
                            callback_data=f"vn_ind_{category_idx}_{i+1}"
                        ))
                        
                    keyboard.append(row)
                    
                # Add "Show All" button
                keyboard.append([
                    InlineKeyboardButton(
                        "Hiển thị tất cả chỉ số", 
                        callback_data=f"vn_ind_{category_idx}_all"
                    )
                ])
                
                # Add back button
                keyboard.append([
                    InlineKeyboardButton("← Quay lại", callback_data="vnstock_back_to_main")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    f"Chọn chỉ số {category_name} bạn muốn xem ({self.time_period}):",
                    reply_markup=reply_markup
                )
            except Exception as e:
                await query.edit_message_text(f"Lỗi xử lý yêu cầu: {str(e)}")
            
        elif query.data.startswith("vn_ind_"):
            parts = query.data.split("_")
            if len(parts) == 4:
                category_idx = int(parts[2])  # Category index
                indicator_idx = parts[3]      # Indicator index or "all"
                
                # Get the category name
                categories = [cat for cat in self.finance_info.stock_data.columns.get_level_values(0).unique() 
                            if cat != "Meta"]
                if not categories or category_idx > len(categories):
                    await query.edit_message_text("Dữ liệu không hợp lệ.")
                    return
                    
                category_name = categories[category_idx - 1]
                
                if indicator_idx == "all":
                    # Show all indicators in this category
                    result = self.finance_info._get_specific_category_indicators(category_name)
                    await query.edit_message_text(text=result)
                else:
                    # Show the specific indicator based on index
                    try:
                        indicator_idx = int(indicator_idx)
                        indicators = [col[1] for col in self.finance_info.stock_data.columns if col[0] == category_name]
                        
                        if indicator_idx >= len(indicators):
                            await query.edit_message_text("Chỉ số không hợp lệ.")
                            return
                            
                        indicator_name = indicators[indicator_idx]
                        result = self.finance_info._get_specific_indicator(category_name, indicator_name)
                        
                        # Add a back button - use shortened callback data
                        keyboard = [[InlineKeyboardButton("← Quay lại", callback_data=f"vnstock_category_{category_idx}")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await query.edit_message_text(text=result, reply_markup=reply_markup)
                    except (ValueError, IndexError) as e:
                        await query.edit_message_text(f"Lỗi khi xử lý yêu cầu: {str(e)}")
            else:
                await query.edit_message_text("Định dạng dữ liệu không hợp lệ.")
                
        elif query.data.startswith("company_section_"):
            parts = query.data.split("_")
            
            if len(parts) >= 4:
                symbol = parts[2]
                section = parts[3]
                
                await query.answer()
                await query.edit_message_text(f"Đang tải thông tin {section} cho {symbol}...")
                
                try:
                    success, company_data = self.company_info.get_company_info(symbol)
                    
                    if not success:
                        await query.edit_message_text(
                            company_data,  # Error message
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("← Quay lại", callback_data=f"vnstock_company_info_{symbol}")
                            ]])
                        )
                        return
                    
                    if section not in company_data:
                        await query.edit_message_text(
                            f"Không có dữ liệu {section} cho {symbol}", 
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("← Quay lại", callback_data=f"vnstock_company_info_{symbol}")
                            ]])
                        )
                        return
                    
                    # Format the specific section data
                    result = self.company_info.format_company_section_data(symbol, section, company_data[section])
                    
                    # Add back button
                    keyboard = [
                        [InlineKeyboardButton("← Quay lại", callback_data=f"vnstock_company_info_{symbol}")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(result, reply_markup=reply_markup)
                        
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    await query.edit_message_text(
                        f"Lỗi khi hiển thị thông tin {section} cho {symbol}: {str(e)}",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("← Quay lại", callback_data=f"vnstock_company_info_{symbol}")
                        ]])
                    )
                    
        elif query.data == "vnstock_chart":
            try:
                await self.get_stock_chart(update, context)
            except Exception as e:
                await query.edit_message_text(f"Lỗi khi tạo biểu đồ: {str(e)}")
                
        elif query.data.startswith("vnstock_financial_info_"):
            symbol = query.data.replace("vnstock_financial_info_", "")
            
            keyboard = [
                [
                    InlineKeyboardButton("Dữ liệu Quý (Quarterly)", callback_data=f"vnstock_fin_period_quarter_{symbol}"),
                    InlineKeyboardButton("Dữ liệu Năm (Yearly)", callback_data=f"vnstock_fin_period_yearly_{symbol}")
                ],
                [
                    InlineKeyboardButton("← Quay lại", callback_data="vnstock_back_to_main")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"Chọn loại dữ liệu tài chính cho mã {symbol}:",
                reply_markup=reply_markup
            )
            
        elif query.data.startswith("vnstock_fin_period_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                self.time_period = parts[3]
                self.finance_info.time_period = self.time_period
                self.company_info.time_period = self.time_period
                symbol = parts[4]
                self.current_symbol = symbol
                
                await query.edit_message_text(f"Đang tải dữ liệu tài chính {self.time_period} cho {symbol}...")
                
                try:
                    success, message = self.finance_info.get_stock_info(symbol)
                    if not success:
                        await query.edit_message_text(message)
                        return
                except Exception as e:
                    await query.edit_message_text(f"Lỗi khi tải dữ liệu tài chính: {str(e)}")
                    return
                
                # Show financial categories
                categories = [cat for cat in self.finance_info.stock_data.columns.get_level_values(0).unique() 
                            if cat != "Meta"]
                
                # Create buttons for each category
                keyboard = []
                for idx, category in enumerate(categories, 1):
                    keyboard.append([
                        InlineKeyboardButton(category, callback_data=f"vnstock_category_{idx}")
                    ])
                
                # Add "All indicators" button
                keyboard.append([
                    InlineKeyboardButton("Tất cả chỉ số", callback_data="vnstock_category_all")
                ])
                
                # Add back button
                keyboard.append([
                    InlineKeyboardButton("← Quay lại", callback_data=f"vnstock_financial_info_{symbol}")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    f"Chọn chỉ số tài chính của {symbol} bạn muốn xem ({self.time_period}):",
                    reply_markup=reply_markup
                )
                
        elif query.data == "vnstock_back_to_main":
            if self.current_symbol:
                keyboard = [
                    [
                        InlineKeyboardButton("Thông tin tài chính", callback_data=f"vnstock_financial_info_{self.current_symbol}"),
                        InlineKeyboardButton("Thông tin công ty", callback_data=f"vnstock_company_info_{self.current_symbol}")
                    ],
                    [
                        InlineKeyboardButton("Biểu đồ", callback_data="vnstock_chart")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(f"Chọn loại thông tin về {self.current_symbol} bạn muốn xem:", reply_markup=reply_markup)
            else:
                await query.edit_message_text("Vui lòng sử dụng /search [mã cổ phiếu] để bắt đầu.")
        
        elif query.data == "vnstock_help":
            help_text = self.get_help()
            await query.edit_message_text(help_text)
                
    async def vnstock_help_command(self, update: Update, context: CallbackContext):
        """Handle /vnstock_help command"""
        help_text = self.get_help()
        await update.message.reply_text(help_text)

    def get_help(self):
        """Return a help message"""
        return (
            "Hướng dẫn sử dụng tìm kiếm chứng khoán:\n\n"
            "1. Sử dụng lệnh /search [mã cổ phiếu] để bắt đầu.\n"
            "2. Chọn loại chỉ số tài chính hoặc thông tin công ty để xem.\n"
            "3. Sử dụng các nút tương tác để điều hướng và xem thêm thông tin.\n"
            "4. Sử dụng lệnh /vnstock_get [chỉ tiêu] để lấy dữ liệu tài chính cụ thể.\n"
            "5. Sử dụng lệnh /search_chart để xem biểu đồ giá cổ phiếu.\n"
            "6. Sử dụng lệnh /search_help để xem hướng dẫn sử dụng.\n"
        )
