import pandas as pd
import numpy as np

def calculate_total_current_assets(dataframes):
    """Calculate total current assets"""
    cash_equivalents = dataframes.get("cash_equivalents", pd.DataFrame())
    short_term_investments = dataframes.get("short_term_investments", pd.DataFrame())
    short_term_receivables = dataframes.get("short_term_receivables", pd.DataFrame())
    inventory = dataframes.get("inventory", pd.DataFrame())
    other_current_assets = dataframes.get("other_current_assets", pd.DataFrame())
    
    # Sum all components
    return cash_equivalents.sum() + short_term_investments.sum() + short_term_receivables.sum() + inventory.sum() + other_current_assets.sum()

def calculate_ppe(tangible_assets, finance_leased_assets, intangible_assets, construction_in_progress):
    """Calculate Property, Plant & Equipment (PPE)"""
    return tangible_assets + finance_leased_assets + intangible_assets + construction_in_progress

def calculate_total_assets(total_current_assets, total_non_current_assets):
    """Calculate total assets"""
    return total_current_assets + total_non_current_assets

def calculate_ebitda(net_income, interest_expense, taxes, depreciation_amortization):
    """Calculate EBITDA"""
    return net_income + interest_expense + taxes + depreciation_amortization

def calculate_total_operating_expense(revenue, gross_profit, financial_expense, selling_expense, admin_expense):
    """Calculate total operating expense"""
    return revenue - gross_profit + financial_expense + selling_expense + admin_expense

def calculate_net_income_before_taxes(operating_profit, other_profit, jv_profit):
    """Calculate net income before taxes"""
    return operating_profit + other_profit + jv_profit

def calculate_net_income_before_extraordinary_items(net_income_after_taxes, other_income):
    """Calculate net income before extraordinary items"""
    return net_income_after_taxes + other_income

def calculate_financial_ratios(net_income, total_equity, total_assets, revenue, long_term_debt, total_debt):
    """Calculate financial ratios"""
    # Avoid division by zero
    roe = np.divide(net_income, total_equity, out=np.zeros_like(net_income), where=total_equity != 0)
    roa = np.divide(net_income, total_assets, out=np.zeros_like(net_income), where=total_assets != 0)
    income_after_tax_margin = np.divide(net_income, revenue, out=np.zeros_like(net_income), where=revenue != 0)
    revenue_to_total_assets = np.divide(revenue, total_assets, out=np.zeros_like(revenue), where=total_assets != 0)
    long_term_debt_to_equity = np.divide(long_term_debt, total_equity, out=np.zeros_like(long_term_debt), where=total_equity != 0)
    total_debt_to_equity = np.divide(total_debt, total_equity, out=np.zeros_like(total_debt), where=total_equity != 0)
    ros = np.divide(net_income, revenue, out=np.zeros_like(net_income), where=revenue != 0)
    
    return {
        "roe": roe,
        "roa": roa,
        "income_after_tax_margin": income_after_tax_margin,
        "revenue_to_total_assets": revenue_to_total_assets,
        "long_term_debt_to_equity": long_term_debt_to_equity,
        "total_debt_to_equity": total_debt_to_equity,
        "ros": ros
    }
