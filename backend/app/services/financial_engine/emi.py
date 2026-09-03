from typing import Dict, Any, List

def calculate_emi(principal: float, annual_interest_rate: float, tenure_months: int) -> float:
    """
    Standard Banking Reducing Balance EMI formula:
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    where r = annual_interest_rate / (12 * 100)
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    
    if annual_interest_rate <= 0:
        return round(principal / tenure_months, 2)
    
    monthly_rate = annual_interest_rate / (12 * 100)
    pow_factor = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * (pow_factor / (pow_factor - 1))
    return round(emi, 2)

def generate_amortization_schedule(
    principal: float, 
    annual_interest_rate: float, 
    tenure_months: int,
    limit_months: int = 24
) -> Dict[str, Any]:
    """Generates monthly amortization schedule breakdown"""
    emi = calculate_emi(principal, annual_interest_rate, tenure_months)
    monthly_rate = annual_interest_rate / (12 * 100) if annual_interest_rate > 0 else 0.0
    
    balance = principal
    total_interest = 0.0
    schedule = []
    
    for month in range(1, tenure_months + 1):
        interest_payment = round(balance * monthly_rate, 2)
        principal_payment = round(emi - interest_payment, 2)
        if principal_payment > balance or month == tenure_months:
            principal_payment = balance
            emi = round(principal_payment + interest_payment, 2)
            balance = 0.0
        else:
            balance = round(balance - principal_payment, 2)
            
        total_interest += interest_payment
        
        if month <= limit_months or month == tenure_months:
            schedule.append({
                "month": month,
                "emi": emi,
                "principal": principal_payment,
                "interest": interest_payment,
                "balance": max(0.0, balance)
            })
            
        if balance <= 0:
            break
            
    total_repayment = round(principal + total_interest, 2)
    
    return {
        "emi": emi,
        "principal": principal,
        "total_interest": round(total_interest, 2),
        "total_repayment": total_repayment,
        "tenure_months": tenure_months,
        "amortization_schedule": schedule
    }
