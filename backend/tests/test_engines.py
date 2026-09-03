import pytest
from backend.app.services.financial_engine.calculator import (
    calculate_dti, calculate_foir, calculate_monthly_surplus,
    calculate_emergency_fund_runway, calculate_savings_rate
)
from backend.app.services.financial_engine.emi import (
    calculate_emi, generate_amortization_schedule
)
from backend.app.services.risk_engine.scorer import (
    calculate_resilience_score,
    calculate_income_stability_factor,
    calculate_liquidity_factor,
    calculate_debt_burden_factor,
    calculate_payment_behavior_factor,
    calculate_credit_utilization_factor
)
from backend.app.services.forecast_engine.predictor import generate_90_day_cashflow_forecast
from backend.app.services.ml_engine.predictor import ml_distress_predictor
from backend.app.services.overdraft_engine.calculator import evaluate_overdraft_offer
from backend.app.services.loan_engine.comparator import compare_and_rank_loans
from backend.app.services.simulator_engine.simulator import simulate_loan_scenario
from backend.app.services.intervention_engine.evaluator import evaluate_interventions
from backend.app.services.debtkart_service.service import (
    get_saptarshi_masid_case_study, generate_debtkart_legal_notice
)
from backend.app.services.ai_service.explainer import generate_ai_explanation

# =============================================================================
# 1. Financial Arithmetic & Boundary Conditions Tests
# =============================================================================

def test_financial_calculator_standard_case():
    dti = calculate_dti(total_debt=2530760.0, annual_income=900000.0)
    assert dti == 2.81
    foir = calculate_foir(total_monthly_emi=30000.0, monthly_income=75000.0)
    assert foir == 0.4
    surplus = calculate_monthly_surplus(monthly_income=75000.0, monthly_expenses=30000.0, total_emi=30000.0)
    assert surplus == 15000.0
    runway = calculate_emergency_fund_runway(available_balance=120000.0, essential_monthly_expenses=30000.0)
    assert runway == 4.0
    savings_r = calculate_savings_rate(monthly_income=75000.0, monthly_expenses=30000.0, total_emi=30000.0)
    assert savings_r == 0.2

def test_financial_calculator_zero_income_edge_case():
    # Mr. Saptarshi Masid hardship case
    dti = calculate_dti(total_debt=2530760.0, annual_income=0.0)
    assert dti == 99.9  # Safeguarded against division by zero
    foir = calculate_foir(total_monthly_emi=80700.0, monthly_income=0.0)
    assert foir == 1.0
    surplus = calculate_monthly_surplus(monthly_income=0.0, monthly_expenses=25000.0, total_emi=80700.0)
    assert surplus == -105700.0
    runway = calculate_emergency_fund_runway(available_balance=2770.0, essential_monthly_expenses=25000.0)
    assert runway == 0.11

def test_financial_calculator_zero_debt_case():
    dti = calculate_dti(total_debt=0.0, annual_income=1200000.0)
    assert dti == 0.0
    foir = calculate_foir(total_monthly_emi=0.0, monthly_income=100000.0)
    assert foir == 0.0
    surplus = calculate_monthly_surplus(monthly_income=100000.0, monthly_expenses=35000.0, total_emi=0.0)
    assert surplus == 65000.0

def test_emi_calculation_zero_rate_and_zero_principal():
    assert calculate_emi(principal=0.0, annual_interest_rate=12.0, tenure_months=24) == 0.0
    assert calculate_emi(principal=120000.0, annual_interest_rate=0.0, tenure_months=12) == 10000.0

def test_amortization_schedule_terminal_balance():
    schedule = generate_amortization_schedule(principal=50000.0, annual_interest_rate=10.0, tenure_months=6)
    assert len(schedule["amortization_schedule"]) == 6
    # Terminal balance in the final month must reach 0.0
    last_month = schedule["amortization_schedule"][-1]
    assert last_month["balance"] == 0.0
    assert schedule["total_repayment"] > 50000.0

# =============================================================================
# 2. Financial Resilience Scoring Across All 4 Risk Tiers
# =============================================================================

def test_resilience_tier_critical():
    # Saptarshi Masid case: Unemployed, heavy debt, medical expenses, overdue
    res = calculate_resilience_score(
        monthly_income=0.0,
        employment_status="unemployed",
        available_balance=2770.0,
        monthly_expenses=25000.0,
        total_debt=2530760.0,
        total_monthly_emi=80700.0,
        overdue_days_max=95,
        missed_payments_count=4,
        active_loans_count=3,
        unsecured_debt_ratio=0.9
    )
    assert res["risk_score"] <= 30.0
    assert res["risk_category"] == "critical"
    assert any(rf["factor"] == "income_stability" for rf in res["risk_factors"])
    assert any(rf["factor"] == "debt_burden" for rf in res["risk_factors"])

def test_resilience_tier_at_risk():
    # Strained borrower: moderate income, high debt burden, 1 missed payment
    res = calculate_resilience_score(
        monthly_income=40000.0,
        employment_status="employed",
        available_balance=8000.0,
        monthly_expenses=22000.0,
        total_debt=800000.0,
        total_monthly_emi=22000.0,
        overdue_days_max=45,
        missed_payments_count=1,
        active_loans_count=3,
        unsecured_debt_ratio=0.7
    )
    assert 30.0 < res["risk_score"] <= 50.0
    assert res["risk_category"] == "at_risk"

def test_resilience_tier_watch():
    # Watch tier borrower: moderate income, tighter liquidity, elevated EMI obligations
    res = calculate_resilience_score(
        monthly_income=50000.0,
        employment_status="employed",
        available_balance=18000.0,
        monthly_expenses=28000.0,
        total_debt=650000.0,
        total_monthly_emi=24000.0,
        overdue_days_max=0,
        missed_payments_count=0,
        active_loans_count=2,
        unsecured_debt_ratio=0.5
    )
    assert 50.0 < res["risk_score"] <= 70.0
    assert res["risk_category"] == "watch"

def test_resilience_tier_healthy():
    # High earner, strong liquidity runway > 6 months, conservative debt
    res = calculate_resilience_score(
        monthly_income=120000.0,
        employment_status="employed",
        available_balance=350000.0,
        monthly_expenses=40000.0,
        total_debt=800000.0,
        total_monthly_emi=24000.0,
        overdue_days_max=0,
        missed_payments_count=0,
        active_loans_count=1,
        unsecured_debt_ratio=0.1
    )
    assert res["risk_score"] >= 71.0
    assert res["risk_category"] == "healthy"

def test_resilience_score_trend_detection():
    improving = calculate_resilience_score(
        monthly_income=90000.0, employment_status="employed", available_balance=200000.0,
        monthly_expenses=30000.0, total_debt=400000.0, total_monthly_emi=15000.0,
        previous_score=60.0
    )
    assert improving["trend"] == "improving"
    assert improving["score_change"] > 0

    declining = calculate_resilience_score(
        monthly_income=0.0, employment_status="unemployed", available_balance=3000.0,
        monthly_expenses=25000.0, total_debt=2500000.0, total_monthly_emi=75000.0,
        previous_score=55.0
    )
    assert declining["trend"] == "declining"
    assert declining["score_change"] < 0

# =============================================================================
# 3. Cash-Flow Forecast Scenarios
# =============================================================================

def test_forecast_with_positive_cashflow():
    forecast = generate_90_day_cashflow_forecast(
        current_balance=100000.0,
        monthly_income=80000.0,
        salary_day_of_month=1,
        active_emis=[{"emi_amount": 15000.0, "due_day": 5, "lender_name": "HDFC Bank"}],
        monthly_essential_expenses=25000.0,
        monthly_discretionary_expenses=10000.0,
        forecast_days=90
    )
    assert len(forecast["daily_projections"]) == 90
    assert forecast["summary"]["negative_balance_days"] == 0
    assert forecast["summary"]["minimum_balance"] > 50000.0

def test_forecast_with_deficit_and_alerts():
    forecast = generate_90_day_cashflow_forecast(
        current_balance=2000.0,
        monthly_income=0.0,
        salary_day_of_month=1,
        active_emis=[
            {"emi_amount": 25000.0, "due_day": 5, "lender_name": "HDFC Bank"},
            {"emi_amount": 28000.0, "due_day": 10, "lender_name": "SCB"}
        ],
        monthly_essential_expenses=25000.0,
        monthly_discretionary_expenses=0.0,
        forecast_days=90
    )
    assert forecast["summary"]["negative_balance_days"] > 70
    assert forecast["summary"]["minimum_balance"] < -100000.0
    assert len(forecast["summary"]["low_balance_alerts"]) > 0

# =============================================================================
# 4. ML Distress Engine Across Diverse Risk Profiles
# =============================================================================

def test_ml_distress_predictor_healthy():
    pred = ml_distress_predictor.predict(
        income_trend=0.1, income_volatility=0.05, expense_growth_rate=0.01,
        cash_buffer_months=6.0, debt_to_income_ratio=1.5, emi_to_income_ratio=0.20,
        credit_utilization=0.25, missed_payments_count=0
    )
    assert pred["distress_probability"] < 0.20
    assert pred["risk_level"] == "low"

def test_ml_distress_predictor_crisis():
    pred = ml_distress_predictor.predict(
        income_trend=-1.0, income_volatility=0.85, expense_growth_rate=0.25,
        cash_buffer_months=0.1, debt_to_income_ratio=9.5, emi_to_income_ratio=1.2,
        credit_utilization=0.98, missed_payments_count=5
    )
    assert pred["distress_probability"] > 0.85
    assert pred["risk_level"] == "critical"
    assert len(pred["contributing_features"]) >= 3

# =============================================================================
# 5. Overdraft Engine Eligibility Scenarios
# =============================================================================

def test_overdraft_eligible():
    res = evaluate_overdraft_offer(
        required_amount=20000.0,
        expected_repayment_date_str="2026-09-30",
        monthly_income=55000.0,
        current_balance=2500.0,
        recent_defaults_count=0
    )
    assert res["eligible"] is True
    assert res["approved_amount"] == 20000.0
    assert res["total_repayment"] > 20000.0

def test_overdraft_ineligible_due_to_defaults():
    res = evaluate_overdraft_offer(
        required_amount=15000.0,
        expected_repayment_date_str="2026-09-30",
        monthly_income=45000.0,
        current_balance=1000.0,
        recent_defaults_count=2
    )
    assert res["eligible"] is False
    assert res["approved_amount"] == 0.0

def test_overdraft_ineligible_due_to_zero_income():
    res = evaluate_overdraft_offer(
        required_amount=10000.0,
        expected_repayment_date_str="2026-09-30",
        monthly_income=0.0,
        current_balance=500.0,
        recent_defaults_count=0
    )
    assert res["eligible"] is False

# =============================================================================
# 6. Loan Comparator Best-Fit Ranking Tests
# =============================================================================

def test_loan_comparator_ranking():
    sample_products = [
        {"id": "p1", "lender_name": "Bank A", "product_name": "Loan A", "interest_rate": 14.0, "processing_fee_percent": 1.0, "prepayment_charges_percent": 0.0},
        {"id": "p2", "lender_name": "Bank B", "product_name": "Loan B", "interest_rate": 10.5, "processing_fee_percent": 0.5, "prepayment_charges_percent": 1.0},
        {"id": "p3", "lender_name": "Bank C", "product_name": "Loan C", "interest_rate": 16.0, "processing_fee_percent": 2.0, "prepayment_charges_percent": 3.0},
    ]
    res = compare_and_rank_loans(
        loan_amount=200000.0,
        tenure_months=24,
        monthly_income=60000.0,
        current_total_emi=10000.0,
        current_resilience_score=75.0,
        available_products=sample_products
    )
    assert len(res["products"]) == 3
    # Bank B (10.5% rate and low fee) should rank #1 as best fit
    best = res["products"][0]
    assert best["is_best_fit"] is True
    assert best["lender_name"] == "Bank B"
    assert best["rank"] == 1

# =============================================================================
# 7. What-If Simulator Scenarios
# =============================================================================

def test_whatif_simulator_affordable_loan():
    sim = simulate_loan_scenario(
        loan_amount=150000.0,
        interest_rate=10.5,
        tenure_months=36,
        processing_fee=1500.0,
        current_monthly_income=90000.0,
        current_total_emi=12000.0,
        current_risk_score=80.0
    )
    assert sim["impact"]["affordability"] in ["highly_affordable", "manageable"]
    assert sim["impact"]["emi_increase"] > 0
    assert sim["projected_state"]["monthly_surplus"] > 50000.0

def test_whatif_simulator_unaffordable_loan():
    sim = simulate_loan_scenario(
        loan_amount=1000000.0,
        interest_rate=15.0,
        tenure_months=12,
        processing_fee=10000.0,
        current_monthly_income=30000.0,
        current_total_emi=15000.0,
        current_risk_score=45.0
    )
    assert sim["impact"]["affordability"] == "critical_risk"
    assert "High risk of distress" in sim["impact"]["recommendation"]

# =============================================================================
# 8. Intervention Engine Hierarchy Tests
# =============================================================================

def test_intervention_hierarchy_triggers_legal_for_severe_distress():
    # Should trigger Debtkart legal settlement when score is critical and defaulted
    interventions = evaluate_interventions(
        resilience_score=18.5,
        monthly_income=0.0,
        monthly_expenses=25000.0,
        essential_expenses=25000.0,
        discretionary_expenses=0.0,
        total_debt=2530760.0,
        total_emi=80700.0,
        available_balance=2770.0,
        has_defaults=True,
        active_loans_count=3
    )
    types = [i["intervention_type"] for i in interventions]
    assert "legal_settlement" in types
    legal_int = next(i for i in interventions if i["intervention_type"] == "legal_settlement")
    assert legal_int["priority"] == "critical"
    assert "Debtkart" in legal_int["recommendation_text"]

# =============================================================================
# 9. Debtkart Real-World Kolkata Case Study & Legal Notice Generator
# =============================================================================

def test_debtkart_case_study_data_integrity():
    case = get_saptarshi_masid_case_study()
    assert case["client_name"] == "Mr. Saptarshi Masid"
    assert "Kolkata" in case["location"]
    assert case["total_exposure_amount"] == 2530760.0
    assert case["final_settlement_amount"] == 635600.0
    assert case["liability_reduction_amount"] == 1895160.0
    assert case["savings_percentage"] == 74.88
    assert len(case["creditor_breakdown"]) == 3

    # Check the 3 banks
    banks = [c["lender_name"] for c in case["creditor_breakdown"]]
    assert "HDFC Bank" in banks
    assert "Standard Chartered Bank" in banks
    assert "RBL Bank" in banks

def test_debtkart_legal_notice_generation():
    notice = generate_debtkart_legal_notice(
        client_name="Mr. Saptarshi Masid",
        lender_name="RBL Bank",
        account_number="RBL-CR-119834",
        outstanding_amount=660000.0,
        hardship_reason="Sudden job loss and continuous family medical crisis",
        moratorium_months=6
    )
    content = notice["notice_content"]
    assert "RBI FAIR PRACTICES CODE" in content
    assert "SETTLEND LEGAL ADVISORS LLP" in content
    assert "Debtkart" in content
    assert "+91 6293629300" in content
    assert "info@debtkart.in" in content
    assert "59, Diamond Harbour Rd" in content
    assert "civil contractual dispute" in content

def test_ai_explanation_engine_all_contexts():
    # Risk context
    exp1 = generate_ai_explanation("risk_score", {"risk_score": 18.5, "risk_category": "critical", "factors": {"liquidity_score": 5, "debt_burden_score": 5}})
    assert "CRITICAL" in exp1["explanation"]
    assert "Debtkart" in exp1["advisory_recommendation"]

    # Forecast context
    exp2 = generate_ai_explanation("forecast", {"minimum_balance": -15000.0, "negative_balance_days": 12})
    assert "deficit" in exp2["explanation"]

    # Debtkart context
    exp3 = generate_ai_explanation("debtkart", {"total_exposure": 2530760.0, "banks": ["HDFC Bank", "RBL Bank"]})
    assert "RBI Master Directions" in exp3["advisory_recommendation"]
