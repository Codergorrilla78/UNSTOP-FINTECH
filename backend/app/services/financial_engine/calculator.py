import math
from typing import Dict, Any

def calculate_dti(total_debt: float, annual_income: float) -> float:
    """Debt-to-Income Ratio = Total Debt / Annual Income"""
    if annual_income <= 0:
        return 99.9
    return round(total_debt / annual_income, 2)

def calculate_foir(total_monthly_emi: float, monthly_income: float) -> float:
    """Fixed Obligation to Income Ratio = Monthly EMI / Monthly Income"""
    if monthly_income <= 0:
        return 1.0
    return round(total_monthly_emi / monthly_income, 4)

def calculate_monthly_surplus(monthly_income: float, monthly_expenses: float, total_emi: float) -> float:
    """Monthly Net Cash Surplus = Income - (Expenses + EMI)"""
    return round(monthly_income - (monthly_expenses + total_emi), 2)

def calculate_emergency_fund_runway(available_balance: float, essential_monthly_expenses: float) -> float:
    """Emergency Runway in Months = Current Liquid Balance / Essential Expenses"""
    if essential_monthly_expenses <= 0:
        return 12.0
    return round(available_balance / essential_monthly_expenses, 2)

def calculate_savings_rate(monthly_income: float, monthly_expenses: float, total_emi: float) -> float:
    """Savings Rate = Net Surplus / Income"""
    if monthly_income <= 0:
        return 0.0
    surplus = calculate_monthly_surplus(monthly_income, monthly_expenses, total_emi)
    return round(max(0.0, surplus) / monthly_income, 4)
