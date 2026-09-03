from typing import List, Dict, Any
from backend.app.config.settings import settings

def evaluate_interventions(
    resilience_score: float,
    monthly_income: float,
    monthly_expenses: float,
    essential_expenses: float,
    discretionary_expenses: float,
    total_debt: float,
    total_emi: float,
    available_balance: float,
    has_defaults: bool = False,
    active_loans_count: int = 1
) -> List[Dict[str, Any]]:
    """
    Evaluates customer financial profile through the tiered intervention hierarchy.
    Prioritizes non-credit interventions first, and triggers Debtkart Legal Counsel
    for severe distress and multi-lender debt crises.
    """
    interventions = []
    
    # 1. Tier 1: Spending & Savings Adjustment
    if discretionary_expenses > 0 and (resilience_score < 70 or total_emi > 0.4 * monthly_income):
        potential_cut = round(discretionary_expenses * 0.4, 0)
        interventions.append({
            "intervention_type": "spending_adjustment",
            "priority": "high" if resilience_score < 50 else "medium",
            "trigger_reason": f"Discretionary spending is ₹{discretionary_expenses:,.0f}/mo, reducing emergency savings capacity",
            "trigger_score": resilience_score,
            "recommendation_text": f"Reduce non-essential discretionary expenses by ₹{potential_cut:,.0f} per month.",
            "expected_impact": f"Frees up ₹{potential_cut:,.0f}/mo to rebuild emergency cash buffer and lifts resilience score by 4-6 points.",
            "status": "pending"
        })
        
    # 2. Tier 2: Repayment Restructuring / Tenure Extension
    foir = total_emi / monthly_income if monthly_income > 0 else 1.0
    if foir > 0.40 or (has_defaults and resilience_score < 50):
        interventions.append({
            "intervention_type": "repayment_restructure",
            "priority": "critical" if resilience_score < 35 else "high",
            "trigger_reason": f"Fixed debt obligations absorb {foir*100:.1f}% of income, leaving minimal cash for living essentials",
            "trigger_score": resilience_score,
            "recommendation_text": "Request a 12-month tenure extension or moratorium across existing high-interest facilities.",
            "expected_impact": f"Lowers monthly EMI obligations by up to 25-35%, restoring monthly net cashflow surplus.",
            "status": "pending"
        })
        
    # 3. Tier 3: Short-Term Liquidity Support (Overdraft)
    # Recommended ONLY if income is active and gap is temporary
    if monthly_income >= settings.OVERDRAFT_MIN_INCOME and available_balance < 5000 and not has_defaults:
        interventions.append({
            "intervention_type": "overdraft",
            "priority": "medium",
            "trigger_reason": "Temporary liquidity shortfall detected ahead of monthly salary credit",
            "trigger_score": resilience_score,
            "recommendation_text": "Access pre-approved short-term overdraft buffer to bridge essential payments until salary date.",
            "expected_impact": "Prevents dishonored payments and late fees with zero long-term debt accumulation.",
            "status": "pending"
        })
        
    # 4. Tier 4: Responsible Debt Consolidation Loan
    # Only if borrower has active income, manageable DTI, and consolidation lowers interest
    if 45 <= resilience_score <= 65 and active_loans_count >= 2 and monthly_income > 35000 and not has_defaults:
        interventions.append({
            "intervention_type": "debt_consolidation",
            "priority": "medium",
            "trigger_reason": f"Customer holds {active_loans_count} separate loans with divergent interest rates",
            "trigger_score": resilience_score,
            "recommendation_text": "Consolidate scattered personal loans and card balances into a single low-rate structured facility.",
            "expected_impact": "Reduces blended interest rate from ~16% to ~11.5% and simplifies into one manageable monthly EMI.",
            "status": "pending"
        })

    # 5. Tier 5: DEBTKART LEGAL INTERVENTION & SETTLEMENT TRACK
    # Triggered if customer is in critical distress (score < 40), multi-lender exposure, employment loss or defaults
    if resilience_score <= 40 or has_defaults or (monthly_income <= 0 and total_debt > 500000) or active_loans_count >= 3:
        interventions.append({
            "intervention_type": "legal_settlement",
            "priority": "critical",
            "trigger_reason": f"Critical financial distress ({resilience_score}/100) with multi-lender exposure (₹{total_debt:,.0f}) and debt servicing failure",
            "trigger_score": resilience_score,
            "recommendation_text": (
                "Initiate structured legal representation via Debtkart (Settlend Legal Advisors LLP). "
                "Issue formal legal notices under RBI Fair Practices Code, mandate 4-6 month temporary moratorium, "
                "cease recovery agent harassment, and negotiate one-time settlements (OTS) across HDFC, Standard Chartered, and RBL Bank."
            ),
            "expected_impact": (
                "Halts coercive lender harassment immediately, routes all communications through authorized legal counsel, "
                "and creates a structured pathway to achieve up to 70-75% reduction in total liability."
            ),
            "status": "pending",
            "metadata_json": {
                "legal_firm": "SETTLEND LEGAL ADVISORS LLP (Debtkart)",
                "helpline": "+91 6293629300",
                "email": "info@debtkart.in",
                "address": "59, Diamond Harbour Rd, Kolkata-700023",
                "resolution_strategy": "Multi-bank legal notice, RBI borrower rights enforcement, 6-month moratorium, negotiated settlement"
            }
        })
        
    return interventions
