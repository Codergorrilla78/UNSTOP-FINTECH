from typing import Dict, Any, List, Tuple
from backend.app.config.settings import settings

def calculate_income_stability_factor(
    monthly_income: float,
    employment_status: str,
    months_unemployed: int = 0
) -> Tuple[float, str]:
    """Score income stability from 0 to 100"""
    if employment_status in ["unemployed", "job_loss"] or monthly_income <= 0:
        score = max(5.0, 30.0 - (months_unemployed * 10))
        desc = "Severe loss of primary employment income"
    elif employment_status == "medical_leave":
        score = 35.0
        desc = "Reduced earnings due to medical emergency and leave"
    elif employment_status == "self_employed":
        score = 70.0
        desc = "Moderate volatility inherent in self-employed income"
    else:  # employed
        score = 90.0 if monthly_income >= 40000 else 80.0
        desc = "Regular salaried income with stable inflow"
    return score, desc

def calculate_liquidity_factor(
    available_balance: float,
    monthly_expenses: float
) -> Tuple[float, str]:
    """Score liquidity buffer from 0 to 100"""
    if monthly_expenses <= 0:
        return 80.0, "Healthy liquidity"
    runway = available_balance / monthly_expenses
    if runway >= 6.0:
        return 100.0, f"Exceptional liquidity runway ({runway:.1f} months of expenses)"
    elif runway >= 3.0:
        return 80.0, f"Adequate emergency reserve ({runway:.1f} months of expenses)"
    elif runway >= 1.0:
        return 50.0, f"Borderline liquid buffer ({runway:.1f} months remaining)"
    elif runway > 0.0:
        return 25.0, f"Critical cash shortfall ({runway:.1f} months of emergency funds)"
    else:
        return 5.0, "Zero or depleted cash balance; immediate overdraft risk"

def calculate_debt_burden_factor(
    total_debt: float,
    total_monthly_emi: float,
    monthly_income: float
) -> Tuple[float, str]:
    """Score debt burden from 0 to 100"""
    if monthly_income <= 0:
        return 5.0, "Unsustainable debt burden with zero recorded income"
    foir = total_monthly_emi / monthly_income
    if foir <= 0.25:
        return 95.0, f"Low debt burden; EMIs consume only {foir*100:.1f}% of income"
    elif foir <= 0.40:
        return 75.0, f"Manageable EMI obligations ({foir*100:.1f}% of income)"
    elif foir <= 0.55:
        return 45.0, f"Elevated debt pressure ({foir*100:.1f}% of income allocated to debt)"
    elif foir <= 0.75:
        return 20.0, f"Severe debt distress; EMIs absorb {foir*100:.1f}% of income"
    else:
        return 5.0, f"Critical default threshold; EMIs exceed {foir*100:.1f}% of income"

def calculate_payment_behavior_factor(
    overdue_days_max: int,
    missed_payments_count: int
) -> Tuple[float, str]:
    """Score repayment timeliness from 0 to 100"""
    if missed_payments_count == 0 and overdue_days_max == 0:
        return 100.0, "Flawless payment history across all lenders"
    elif overdue_days_max <= 30 and missed_payments_count <= 1:
        return 70.0, "Minor delayed payment incident recorded"
    elif overdue_days_max <= 60:
        return 40.0, f"Moderate delinquency with {missed_payments_count} missed installments"
    elif overdue_days_max <= 90:
        return 20.0, f"Serious delinquency ({overdue_days_max} days overdue)"
    else:
        return 5.0, f"Prolonged multi-lender default ({overdue_days_max}+ days past due)"

def calculate_credit_utilization_factor(
    active_loans_count: int,
    unsecured_debt_ratio: float
) -> Tuple[float, str]:
    """Score credit exposure from 0 to 100"""
    if active_loans_count <= 1 and unsecured_debt_ratio <= 0.3:
        return 95.0, "Conservative credit utilization"
    elif active_loans_count <= 2:
        return 75.0, "Controlled credit footprint"
    elif active_loans_count <= 3:
        return 50.0, f"Multi-lender credit exposure across {active_loans_count} facilities"
    else:
        return 25.0, f"High credit fragmentation across {active_loans_count} institutions"

def calculate_resilience_score(
    monthly_income: float,
    employment_status: str,
    available_balance: float,
    monthly_expenses: float,
    total_debt: float,
    total_monthly_emi: float,
    overdue_days_max: int = 0,
    missed_payments_count: int = 0,
    active_loans_count: int = 1,
    unsecured_debt_ratio: float = 0.5,
    previous_score: float = None
) -> Dict[str, Any]:
    """
    Computes overall Financial Resilience Score and factor breakdown.
    Deterministic, explainable, and compliant with FR-001.
    """
    s_income, desc_income = calculate_income_stability_factor(monthly_income, employment_status)
    s_liquidity, desc_liquidity = calculate_liquidity_factor(available_balance, monthly_expenses)
    s_debt, desc_debt = calculate_debt_burden_factor(total_debt, total_monthly_emi, monthly_income)
    s_payment, desc_payment = calculate_payment_behavior_factor(overdue_days_max, missed_payments_count)
    s_credit, desc_credit = calculate_credit_utilization_factor(active_loans_count, unsecured_debt_ratio)

    w_income = settings.WEIGHT_INCOME_STABILITY
    w_liquidity = settings.WEIGHT_LIQUIDITY
    w_debt = settings.WEIGHT_DEBT_BURDEN
    w_payment = settings.WEIGHT_PAYMENT_BEHAVIOR
    w_credit = settings.WEIGHT_CREDIT_UTILIZATION

    composite_score = round(
        (s_income * w_income) +
        (s_liquidity * w_liquidity) +
        (s_debt * w_debt) +
        (s_payment * w_payment) +
        (s_credit * w_credit),
        1
    )
    composite_score = max(0.0, min(100.0, composite_score))

    # Category classification
    if composite_score <= settings.THRESHOLD_CRITICAL:
        category = "critical"
    elif composite_score <= settings.THRESHOLD_AT_RISK:
        category = "at_risk"
    elif composite_score <= settings.THRESHOLD_WATCH:
        category = "watch"
    else:
        category = "healthy"

    # Trend detection
    if previous_score is not None:
        change = round(composite_score - previous_score, 1)
        if change > 2.0:
            trend = "improving"
        elif change < -2.0:
            trend = "declining"
        else:
            trend = "stable"
    else:
        change = 0.0
        trend = "stable"

    # Identified risk factors list
    risk_factors = []
    if s_income < 50:
        risk_factors.append({"factor": "income_stability", "impact": "critical", "description": desc_income})
    if s_debt < 50:
        risk_factors.append({"factor": "debt_burden", "impact": "high", "description": desc_debt})
    if s_liquidity < 50:
        risk_factors.append({"factor": "liquidity", "impact": "high", "description": desc_liquidity})
    if s_payment < 50:
        risk_factors.append({"factor": "payment_behavior", "impact": "medium", "description": desc_payment})
    if s_credit < 50:
        risk_factors.append({"factor": "credit_utilization", "impact": "medium", "description": desc_credit})

    return {
        "risk_score": composite_score,
        "risk_category": category,
        "previous_score": previous_score or composite_score,
        "score_change": change,
        "trend": trend,
        "factors": {
            "income_stability_score": round(s_income, 1),
            "liquidity_score": round(s_liquidity, 1),
            "debt_burden_score": round(s_debt, 1),
            "payment_behavior_score": round(s_payment, 1),
            "credit_utilization_score": round(s_credit, 1)
        },
        "weights": {
            "income_stability": w_income,
            "liquidity": w_liquidity,
            "debt_burden": w_debt,
            "payment_behavior": w_payment,
            "credit_utilization": w_credit
        },
        "risk_factors": risk_factors
    }
