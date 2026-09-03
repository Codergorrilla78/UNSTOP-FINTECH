from typing import Dict, Any

def generate_ai_explanation(context_type: str, context_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates explainable, deterministic natural language financial explanations.
    Compliant with FR-008.
    """
    if context_type == "risk_score":
        score = context_data.get("risk_score", 50.0)
        category = context_data.get("risk_category", "watch").upper()
        factors = context_data.get("factors", {})
        
        income_s = factors.get("income_stability_score", 50.0)
        debt_s = factors.get("debt_burden_score", 50.0)
        liq_s = factors.get("liquidity_score", 50.0)
        
        if score <= 30.0:
            explanation = (
                f"Your Financial Resilience Score is {score:.1f}/100, placing your account in the CRITICAL category. "
                f"This acute deterioration is primarily driven by depleted liquid reserves (Liquidity Factor: {liq_s:.0f}/100) "
                f"and unsustainable debt service demands relative to active income (Debt Burden: {debt_s:.0f}/100). "
                f"Standard repayment channels are at imminent risk of systemic multi-bank default."
            )
            advisory = (
                "Immediate legal intervention is strongly advised. Engage authorized legal representation through Debtkart "
                "(SETTLEND LEGAL ADVISORS LLP) to invoke the RBI Fair Practices Code, establish an enforceable 4-6 month moratorium, "
                "cease recovery agent contact, and pursue structured one-time settlements across all creditor institutions."
            )
        elif score <= 50.0:
            explanation = (
                f"Your Financial Resilience Score is {score:.1f}/100 ('AT RISK'). "
                f"Your debt obligations consume a disproportionate share of monthly cashflow, leaving insufficient buffer for unforeseen contingencies."
            )
            advisory = "Prioritize halting non-essential discretionary expenses and explore loan tenure extension or balance restructuring."
        elif score <= 70.0:
            explanation = (
                f"Your Financial Resilience Score is {score:.1f}/100 ('WATCH'). "
                f"Your financial foundations are moderately stable, but elevated EMI commitments limit your savings rate."
            )
            advisory = "Maintain a strict 3-month emergency fund before taking on any new credit lines."
        else:
            explanation = (
                f"Your Financial Resilience Score is {score:.1f}/100 ('HEALTHY'). "
                f"Your cash buffer is strong, debt-to-income ratio is conservative, and repayment history is exemplary."
            )
            advisory = "Continue your consistent savings discipline and avoid taking high-cost unsecured credit."
            
    elif context_type == "forecast":
        min_bal = context_data.get("minimum_balance", 0.0)
        neg_days = context_data.get("negative_balance_days", 0)
        if neg_days > 0 or min_bal < 0:
            explanation = (
                f"Cash-flow forecasting projects a cash deficit with minimum projected balance falling to -₹{abs(min_bal):,.2f}. "
                f"You have {neg_days} projected days with negative liquidity balance due to incoming scheduled EMI commitments."
            )
            advisory = "Consider a short-term liquidity bridge or temporary EMI deferral to protect your credit record."
        else:
            explanation = (
                f"Your 90-day cash-flow forecast projects steady solvency with a minimum projected balance of ₹{min_bal:,.2f}."
            )
            advisory = "Cash-flow trajectory remains resilient across upcoming billing cycles."
            
    elif context_type == "debtkart":
        exposure = context_data.get("total_exposure", 2530760.0)
        banks = context_data.get("banks", ["HDFC Bank", "Standard Chartered Bank", "RBL Bank"])
        explanation = (
            f"Case analysis under Debtkart Legal Intervention framework for total multi-lender exposure of ₹{exposure:,.2f} "
            f"across {', '.join(banks)}. Analysis indicates default was driven by involuntary employment disruption and medical emergencies."
        )
        advisory = (
            "Deploy multi-bank formal notices asserting borrower rights under RBI Master Directions. "
            "Enforce a 6-month moratorium and negotiate structured full and final settlement letters."
        )
    else:
        explanation = "Financial evaluation completed according to deterministic banking resilience parameters."
        advisory = "Review personalized interventions on your dashboard."

    return {
        "explanation": explanation,
        "advisory_recommendation": advisory
    }
