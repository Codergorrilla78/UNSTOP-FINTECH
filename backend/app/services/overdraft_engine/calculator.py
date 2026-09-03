import datetime
from typing import Dict, Any
from backend.app.config.settings import settings

def evaluate_overdraft_offer(
    required_amount: float,
    expected_repayment_date_str: str,
    monthly_income: float,
    current_balance: float,
    recent_defaults_count: int = 0
) -> Dict[str, Any]:
    """
    Evaluates short-term liquidity bridging overdraft offer.
    Compliant with FR-005.
    """
    # Parse date
    try:
        expected_date = datetime.date.fromisoformat(expected_repayment_date_str)
    except Exception:
        expected_date = datetime.date.today() + datetime.timedelta(days=25)
        
    duration_days = max(1, (expected_date - datetime.date.today()).days)
    
    # Eligibility checks
    min_income_met = monthly_income >= settings.OVERDRAFT_MIN_INCOME
    no_defaults = recent_defaults_count == 0
    within_limit = required_amount <= settings.OVERDRAFT_MAX_LIMIT
    salary_pattern = monthly_income > 0
    
    is_eligible = min_income_met and no_defaults and within_limit and salary_pattern
    
    approved_amount = min(required_amount, settings.OVERDRAFT_MAX_LIMIT) if is_eligible else 0.0
    
    # Calculations
    daily_rate = settings.OVERDRAFT_DAILY_INTEREST_RATE
    fee = settings.OVERDRAFT_PROCESSING_FEE if approved_amount > 0 else 0.0
    total_interest = round(approved_amount * daily_rate * duration_days, 2)
    total_repayment = round(approved_amount + total_interest + fee, 2)
    
    return {
        "eligible": is_eligible,
        "required_amount": required_amount,
        "approved_amount": approved_amount,
        "duration_days": duration_days,
        "daily_interest_rate": daily_rate,
        "processing_fee": fee,
        "total_interest": total_interest,
        "total_repayment": total_repayment,
        "expected_repayment_date": expected_date.isoformat(),
        "eligibility_check": {
            "minimum_income_met": min_income_met,
            "regular_salary_pattern": salary_pattern,
            "no_recent_defaults": no_defaults,
            "within_limit": within_limit
        },
        "impact": {
            "monthly_cost": round(total_interest + fee, 2),
            "impact_on_risk_score": -1.5 if is_eligible else 0.0
        }
    }
