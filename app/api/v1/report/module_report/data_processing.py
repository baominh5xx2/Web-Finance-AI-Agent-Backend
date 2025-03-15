import pandas as pd
import numpy as np

def read_data(file_paths):
    """Read data from Excel files"""
    return [pd.read_excel(path, engine="openpyxl") for path in file_paths]

def clean_column_names(df_list):
    """Clean and standardize column names"""
    for df, year in zip(df_list, range(2020, 2025)):
        df.columns = df.columns.str.replace(f"Năm: {year}", "", regex=True).str.strip()
        df.columns = df.columns.str.replace(r"Đơn vị: (Tỷ|Triệu) VND", "", regex=True).str.strip()
        df.columns = df.columns.str.replace(r"\bHợp nhất\b", "", regex=True).str.strip()
        df.columns = df.columns.str.replace(r"\bQuý: Hàng năm\b", "", regex=True).str.strip()
        # Remove TM columns
        df.drop(columns=[col for col in df.columns if "TM" in col], inplace=True, errors='ignore')

def convert_units(df, factor, start_col):
    """Convert units in a dataframe"""
    # Find position of starting column
    start_idx = df.columns.get_loc(start_col) + 1  # Next column after start_col
    numeric_cols = df.columns[start_idx:]  # Only get columns from this position onwards
    
    # Multiply numeric columns by factor
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce') / factor
    return df

def standardize_columns(df):
    """Standardize column names"""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace("\n", " ")
    df.columns = df.columns.str.upper()
    return df

def merge_balance_sheets(dfs, stock_code):
    """Merge balance sheets for a specific stock code"""
    data = []
    years = list(range(2020, 2025))
    
    dfs = [standardize_columns(df) for df in dfs]
    
    for df, year in zip(dfs, years):        
        if 'MÃ' not in df.columns:
            print(f"ERROR: Column 'MÃ' not found in file for year {year}")
            continue
        
        stock_data = df[df['MÃ'] == stock_code]
        if not stock_data.empty:
            data.append(stock_data)
    
    if data:
        result_df = pd.concat(data, ignore_index=True)
        return result_df
    else:
        return pd.DataFrame()

def get_values(transposed_df, label):
    """Get values from transposed dataframe for a specific label"""
    row = transposed_df[transposed_df["Chỉ tiêu"] == label]
    if row.empty:
        return np.zeros(len(transposed_df.columns[1:]), dtype=float)
    values = row.iloc[:, 1:].fillna(0).values.flatten()
    return np.array(values, dtype=float)
