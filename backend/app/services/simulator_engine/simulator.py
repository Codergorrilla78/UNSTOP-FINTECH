from typing import Dict, Any
from backend.app.services.financial_engine.emi import calculate_emi, generate_amortization_schedule

def simulate_loan_scenario(
    loan_amount: float,
    interest_rate: float,
    tenure_months: int,
    processing_fee: float,
    current_monthly_income: float,
    current_total_emi: float,
    current_risk_score: float
) -> Dict[str, Any]:
    """
    Simulates the before/after financial consequences of taking a loan.
    Compliant with FR-007.
    """
    emi = calculate_emi(loan_amount, interest_rate, tenure_months)
    total_interest = round((emi * tenure_months) - loan_amount, 2)
    total_repayment = round(emi * tenure_months, 2)
    total_cost = round(total_repayment + processing_fee, 2)
    
    # Current state
    current_foir = round(current_total_emi / current_monthly_income, 3) if current_monthly_income > 0 else 1.0
    current_surplus = round(current_monthly_income - current_total_emi, 2)
    
    # Projected state
    projected_total_emi = round(current_total_emi + emi, 2)
    projected_foir = round(projected_total_emi / current_monthly_income, 3) if current_monthly_income > 0 else 1.0
    projected_surplus = round(current_monthly_income - projected_total_emi, 2)
    
    # Risk Score Impact
    # Increased debt burden degrades resilience score proportionally
    score_penalty = round(min(35.0, (emi / (current_monthly_income or 1)) * 30.0 + 3.0), 1)
    projected_risk_score = max(5.0, round(current_risk_score - score_penalty, 1))
    score_change = round(projected_risk_score - current_risk_score, 1)
    
    # Affordability verdict
    if projected_foir <= 0.35:
        affordability = "highly_affordable"
        recommendation = "This loan is well within safe banking limits. Your cash buffer and resilience score remain resilient."
    elif projected_foir <= 0.50:
        affordability = "manageable"
        recommendation = "Manageable obligation, but discretionary spending should be monitored to preserve emergency savings."
    elif projected_foir <= 0.65:
        affordability = "strained"
        recommendation = "Warning: This loan would push your debt obligations above 50% of income. Consider a longer tenure to reduce EMI."
    else:
        affordability = "critical_risk"
        recommendation = "High risk of distress: Over half your income would go toward debt repayments. We advise against this commitment without restructuring existing debts."
        
    return {
        "inputs": {
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "tenure_months": tenure_months,
            "processing_fee": processing_fee
        },
        "calculations": {
            "emi": emi,
            "total_interest": total_interest,
            "total_repayment": total_repayment,
            "total_cost": total_cost
        },
        "current_state": {
            "monthly_income": current_monthly_income,
            "total_emi": current_total_emi,
            "emi_to_income_ratio": current_foir,
            "risk_score": current_risk_score,
            "monthly_surplus": current_surplus
        },
        "projected_state": {
            "total_emi": projected_total_emi,
            "emi_to_income_ratio": projected_foir,
            "risk_score": projected_risk_score,
            "monthly_surplus": projected_surplus
        },
        "impact": {
            "emi_increase": emi,
            "risk_score_change": score_change,
            "surplus_change": round(projected_surplus - current_surplus, 2),
            "affordability": affordability,
            "recommendation": recommendation
        }
    }
