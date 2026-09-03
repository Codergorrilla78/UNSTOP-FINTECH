"""
FinShield Services & Intelligence Engines Package
"""

def calculate_financial_resilience(
    monthly_income: float,
    monthly_expenses: float,
    monthly_debt_payment: float,
    savings: float,
    existing_debt: float
):
    # -----------------------------
    # Basic calculations
    # -----------------------------

    total_monthly_outflow = (
        monthly_expenses +
        monthly_debt_payment
    )

    monthly_surplus = (
        monthly_income -
        total_monthly_outflow
    )

    # Avoid division by zero
    if monthly_income > 0:
        debt_to_income = (
            monthly_debt_payment /
            monthly_income
        ) * 100
    else:
        debt_to_income = 100

    if total_monthly_outflow > 0:
        emergency_months = (
            savings /
            total_monthly_outflow
        )
    else:
        emergency_months = 0

    # -----------------------------
    # Score calculation
    # -----------------------------

    score = 100

    # Cash-flow health
    if monthly_surplus < 0:
        score -= 35
    elif monthly_surplus < monthly_income * 0.10:
        score -= 20
    elif monthly_surplus < monthly_income * 0.20:
        score -= 10

    # Debt burden
    if debt_to_income > 50:
        score -= 30
    elif debt_to_income > 40:
        score -= 20
    elif debt_to_income > 30:
        score -= 10

    # Emergency savings
    if emergency_months < 1:
        score -= 25
    elif emergency_months < 3:
        score -= 15
    elif emergency_months < 6:
        score -= 5

    # Existing debt
    if existing_debt > monthly_income * 12:
        score -= 10

    score = max(0, min(100, score))

    # -----------------------------
    # Risk classification
    # -----------------------------

    if score >= 75:
        risk_level = "LOW"
    elif score >= 50:
        risk_level = "MEDIUM"
    elif score >= 25:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    # -----------------------------
    # Recommendation hierarchy
    # -----------------------------

    if monthly_surplus < 0:
        recommendation = (
            "Reduce discretionary spending and "
            "review recurring expenses before taking "
            "additional debt."
        )

    elif debt_to_income > 40:
        recommendation = (
            "Prioritize debt reduction and avoid "
            "taking on additional high-cost debt."
        )

    elif emergency_months < 3:
        recommendation = (
            "Build an emergency fund before considering "
            "additional borrowing."
        )

    elif score >= 75:
        recommendation = (
            "Financial position is relatively resilient. "
            "Continue maintaining savings and controlled debt."
        )

    else:
        recommendation = (
            "Improve monthly cash flow and strengthen "
            "emergency savings."
        )

    return {
        "resilience_score": round(score, 2),
        "monthly_surplus": round(monthly_surplus, 2),
        "debt_to_income": round(debt_to_income, 2),
        "emergency_months": round(emergency_months, 2),
        "risk_level": risk_level,
        "recommendation": recommendation
    }

__all__ = ["calculate_financial_resilience"]
