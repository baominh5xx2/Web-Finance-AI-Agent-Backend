import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Sử dụng backend không cần màn hình

def create_chart_directory(report_dir):
    """Tạo thư mục để lưu biểu đồ"""
    chart_dir = os.path.join(report_dir, "images", "output")
    os.makedirs(chart_dir, exist_ok=True)
    return chart_dir

def format_number_with_suffix(value):
    """Format số với các đơn vị K, M, B"""
    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B"
    elif abs(value) >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return f"{value:.1f}"

def generate_revenue_profit_chart(chart_dir, years, revenue, net_income, symbol="VCB"):
    """Tạo biểu đồ doanh thu và lợi nhuận"""
    fig, ax = plt.figure(figsize=(12, 8)), plt.subplot()
    
    # Chuyển đổi dữ liệu sang số nếu cần
    try:
        revenue = [float(str(x).replace(',', '')) if isinstance(x, str) else float(x) for x in revenue]
        net_income = [float(str(x).replace(',', '')) if isinstance(x, str) else float(x) for x in net_income]
    except (ValueError, TypeError) as e:
        print(f"Error converting data: {e}")
        revenue = [0 if not isinstance(x, (int, float)) else x for x in revenue]
        net_income = [0 if not isinstance(x, (int, float)) else x for x in net_income]
    
    x = np.arange(len(years))
    width = 0.35
    
    # Vẽ biểu đồ cột
    rects1 = ax.bar(x - width/2, revenue, width, label='Doanh thu', color='#4472C4')
    rects2 = ax.bar(x + width/2, net_income, width, label='Lợi nhuận', color='#ED7D31')
    
    # Thêm nhãn và tiêu đề
    ax.set_title(f'Doanh thu và Lợi nhuận - {symbol}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Năm', fontsize=12)
    ax.set_ylabel('Giá trị (VND)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend()
    
    # Thêm giá trị trên mỗi cột
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(format_number_with_suffix(height),
                   xy=(rect.get_x() + rect.get_width()/2, height),
                   xytext=(0, 3),  # 3 điểm ở trên cột
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    for rect in rects2:
        height = rect.get_height()
        ax.annotate(format_number_with_suffix(height),
                   xy=(rect.get_x() + rect.get_width()/2, height),
                   xytext=(0, 3),  # 3 điểm ở trên cột
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Lưu biểu đồ
    chart_path = os.path.join(chart_dir, "chart1.png")
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    return chart_path

def generate_profitability_chart(chart_dir, years, roe, roa, ros, symbol="VCB"):
    """Tạo biểu đồ các chỉ số sinh lời"""
    fig, ax = plt.figure(figsize=(12, 8)), plt.subplot()
    
    # Chuyển đổi dữ liệu phần trăm sang số float
    try:
        roe = [float(str(x).replace(',', '').replace('%', '')) if isinstance(x, str) else float(x) for x in roe]
        roa = [float(str(x).replace(',', '').replace('%', '')) if isinstance(x, str) else float(x) for x in roa]
        ros = [float(str(x).replace(',', '').replace('%', '')) if isinstance(x, str) else float(x) for x in ros]
    except (ValueError, TypeError) as e:
        print(f"Error converting ratio data: {e}")
        roe = [0 if not isinstance(x, (int, float)) else x for x in roe]
        roa = [0 if not isinstance(x, (int, float)) else x for x in roa]
        ros = [0 if not isinstance(x, (int, float)) else x for x in ros]
    
    # Vẽ đồ thị đường
    ax.plot(years, roe, 'o-', linewidth=2, label='ROE', color='#4472C4')
    ax.plot(years, roa, 's-', linewidth=2, label='ROA', color='#ED7D31')
    ax.plot(years, ros, '^-', linewidth=2, label='ROS', color='#A5A5A5')
    
    # Thêm giá trị trên các điểm dữ liệu
    for i, (r_roe, r_roa, r_ros) in enumerate(zip(roe, roa, ros)):
        ax.annotate(f"{r_roe:.1f}%", (years[i], r_roe), textcoords="offset points", 
                   xytext=(0,10), ha='center')
        ax.annotate(f"{r_roa:.1f}%", (years[i], r_roa), textcoords="offset points", 
                   xytext=(0,10), ha='center')
        ax.annotate(f"{r_ros:.1f}%", (years[i], r_ros), textcoords="offset points", 
                   xytext=(0,10), ha='center')
    
    # Thêm nhãn và tiêu đề
    ax.set_title(f'Chỉ số sinh lời - {symbol}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Năm', fontsize=12)
    ax.set_ylabel('Tỷ lệ (%)', fontsize=12)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    # Lưu biểu đồ
    chart_path = os.path.join(chart_dir, "chart2.png")
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    return chart_path

def generate_assets_liabilities_chart(chart_dir, years, total_assets, total_equity, total_liabilities, symbol="VCB"):
    """Tạo biểu đồ tài sản và nợ"""
    fig, ax = plt.figure(figsize=(12, 8)), plt.subplot()
    
    # Chuyển đổi dữ liệu sang số nếu cần
    try:
        total_assets = [float(str(x).replace(',', '')) if isinstance(x, str) else float(x) for x in total_assets]
        total_equity = [float(str(x).replace(',', '')) if isinstance(x, str) else float(x) for x in total_equity]
        total_liabilities = [float(str(x).replace(',', '')) if isinstance(x, str) else float(x) for x in total_liabilities]
    except (ValueError, TypeError) as e:
        print(f"Error converting data: {e}")
        total_assets = [0 if not isinstance(x, (int, float)) else x for x in total_assets]
        total_equity = [0 if not isinstance(x, (int, float)) else x for x in total_equity]
        total_liabilities = [0 if not isinstance(x, (int, float)) else x for x in total_liabilities]
    
    x = np.arange(len(years))
    width = 0.25
    
    # Vẽ biểu đồ cột
    rects1 = ax.bar(x - width, total_assets, width, label='Tổng tài sản', color='#4472C4')
    rects2 = ax.bar(x, total_equity, width, label='Vốn chủ sở hữu', color='#ED7D31')
    rects3 = ax.bar(x + width, total_liabilities, width, label='Nợ phải trả', color='#A5A5A5')
    
    # Thêm nhãn và tiêu đề
    ax.set_title(f'Cơ cấu tài sản và nợ - {symbol}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Năm', fontsize=12)
    ax.set_ylabel('Giá trị (VND)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend()
    
    # Thêm giá trị trên mỗi cột
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(format_number_with_suffix(height),
                   xy=(rect.get_x() + rect.get_width()/2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    for rect in rects2:
        height = rect.get_height()
        ax.annotate(format_number_with_suffix(height),
                   xy=(rect.get_x() + rect.get_width()/2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    for rect in rects3:
        height = rect.get_height()
        ax.annotate(format_number_with_suffix(height),
                   xy=(rect.get_x() + rect.get_width()/2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Lưu biểu đồ
    chart_path = os.path.join(chart_dir, "chart3.png")
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    return chart_path

def generate_debt_ratio_chart(chart_dir, years, debt_to_equity, long_term_debt_to_equity, symbol="VCB"):
    """Tạo biểu đồ các tỷ lệ nợ"""
    fig, ax = plt.figure(figsize=(12, 8)), plt.subplot()
    
    # Chuyển đổi dữ liệu phần trăm sang số float
    try:
        debt_to_equity = [float(str(x).replace(',', '').replace('%', '')) if isinstance(x, str) else float(x) for x in debt_to_equity]
        long_term_debt_to_equity = [float(str(x).replace(',', '').replace('%', '')) if isinstance(x, str) else float(x) for x in long_term_debt_to_equity]
    except (ValueError, TypeError) as e:
        print(f"Error converting ratio data: {e}")
        debt_to_equity = [0 if not isinstance(x, (int, float)) else x for x in debt_to_equity]
        long_term_debt_to_equity = [0 if not isinstance(x, (int, float)) else x for x in long_term_debt_to_equity]
    
    # Vẽ biểu đồ đường
    ax.plot(years, debt_to_equity, 'o-', linewidth=2, label='Nợ/Vốn chủ sở hữu', color='#4472C4')
    ax.plot(years, long_term_debt_to_equity, 's-', linewidth=2, label='Nợ dài hạn/Vốn chủ sở hữu', color='#ED7D31')
    
    # Thêm giá trị trên các điểm dữ liệu
    for i, (d_e, ltd_e) in enumerate(zip(debt_to_equity, long_term_debt_to_equity)):
        ax.annotate(f"{d_e:.1f}%", (years[i], d_e), textcoords="offset points", 
                   xytext=(0,10), ha='center')
        ax.annotate(f"{ltd_e:.1f}%", (years[i], ltd_e), textcoords="offset points", 
                   xytext=(0,10), ha='center')
    
    # Thêm nhãn và tiêu đề
    ax.set_title(f'Tỷ lệ nợ - {symbol}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Năm', fontsize=12)
    ax.set_ylabel('Tỷ lệ (%)', fontsize=12)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    # Lưu biểu đồ
    chart_path = os.path.join(chart_dir, "chart4.png")
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    return chart_path

def generate_financial_charts(report_dir, symbol, years, financial_data):
    """Tạo tất cả các biểu đồ tài chính"""
    try:
        # Tạo thư mục cho các biểu đồ
        chart_dir = create_chart_directory(report_dir)
        
        # Extract dữ liệu từ financial_data
        revenue = financial_data.get("revenue", [0] * len(years))
        net_income = financial_data.get("net_income", [0] * len(years))
        roe = financial_data.get("roe", [0] * len(years))
        roa = financial_data.get("roa", [0] * len(years))
        ros = financial_data.get("ros", [0] * len(years))
        total_assets = financial_data.get("total_assets", [0] * len(years))
        total_equity = financial_data.get("total_equity", [0] * len(years))
        total_liabilities = financial_data.get("total_liabilities", [0] * len(years))
        debt_to_equity = financial_data.get("total_debt_to_equity", [0] * len(years))
        long_term_debt_to_equity = financial_data.get("long_term_debt_to_equity", [0] * len(years))
        
        # Tạo các biểu đồ
        chart1 = generate_revenue_profit_chart(chart_dir, years, revenue, net_income, symbol)
        chart2 = generate_profitability_chart(chart_dir, years, roe, roa, ros, symbol)
        chart3 = generate_assets_liabilities_chart(chart_dir, years, total_assets, total_equity, total_liabilities, symbol)
        chart4 = generate_debt_ratio_chart(chart_dir, years, debt_to_equity, long_term_debt_to_equity, symbol)
        
        return [chart1, chart2, chart3, chart4]
        
    except Exception as e:
        print(f"Error generating charts: {str(e)}")
        return [] 