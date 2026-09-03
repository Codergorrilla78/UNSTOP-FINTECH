import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# =============================================================================
# API Endpoint Health & Status Tests
# =============================================================================

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert "postgresql" in data["data"]["database"]
    assert len(data["data"]["engines"]) == 10

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Debtkart" in data["data"]["partner"]
    assert "+91 6293629300" in data["data"]["helpline"]

# =============================================================================
# Customer & Account Endpoints Tests
# =============================================================================

def test_customers_me():
    response = client.get("/api/v1/customers/me")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["first_name"] == "Saptarshi"
    assert data["data"]["last_name"] == "Masid"
    assert data["data"]["city"] == "Kolkata"

def test_customers_list():
    response = client.get("/api/v1/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] >= 2

def test_customer_by_id():
    # Get current customer id
    me = client.get("/api/v1/customers/me").json()["data"]
    response = client.get(f"/api/v1/customers/{me['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["email"] == me["email"]

def test_customer_not_found():
    response = client.get("/api/v1/customers/non-existent-uuid")
    assert response.status_code == 404

def test_accounts_list():
    response = client.get("/api/v1/accounts")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["accounts"]) >= 2
    assert data["data"]["total_balance"] >= 0

# =============================================================================
# Financial Health & Risk Assessment Endpoints
# =============================================================================

def test_financial_health_endpoint():
    response = client.get("/api/v1/financial-health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_debt"] == 2530760.0
    assert data["data"]["monthly_income"] == 0.0

def test_risk_score_endpoint():
    response = client.get("/api/v1/risk/score")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    score_data = data["data"]
    assert score_data["risk_category"] == "critical"
    assert score_data["risk_score"] < 30.0
    assert "explanation" in score_data
    assert "advisory" in score_data

def test_ml_distress_prediction_endpoint():
    response = client.get("/api/v1/risk/prediction")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    pred = data["data"]
    assert pred["distress_probability"] > 0.50
    assert pred["risk_level"] in ["high", "critical"]

def test_cashflow_forecast_endpoint():
    response = client.get("/api/v1/forecast?days=90")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    fc = data["data"]
    assert len(fc["daily_projections"]) == 90
    assert "summary" in fc
    assert fc["summary"]["negative_balance_days"] > 0

# =============================================================================
# Interventions & Overdraft Endpoints
# =============================================================================

def test_interventions_endpoint():
    response = client.get("/api/v1/interventions")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["interventions"]) > 0
    types = [i["intervention_type"] for i in data["data"]["interventions"]]
    assert "legal_settlement" in types

def test_overdraft_calculate_endpoint():
    payload = {"required_amount": 10000.0, "expected_repayment_date": "2026-09-30"}
    response = client.post("/api/v1/overdraft/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "eligible" in data["data"]
    assert "total_repayment" in data["data"]

# =============================================================================
# Loans & Comparison Endpoints
# =============================================================================

def test_loans_list_endpoint():
    response = client.get("/api/v1/loans")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_outstanding_debt"] == 2530760.0
    assert len(data["data"]["loans"]) == 3

def test_loan_products_catalog():
    response = client.get("/api/v1/loans/products")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["count"] >= 4

def test_loan_compare_endpoint():
    payload = {
        "loan_amount": 300000.0,
        "tenure_months": 36,
        "loan_type": "personal",
        "purpose": "debt_consolidation"
    }
    response = client.post("/api/v1/loans/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    comp = data["data"]
    assert len(comp["products"]) >= 3
    assert comp["best_fit_product_id"] is not None
    assert comp["best_fit_reason"] is not None

# =============================================================================
# What-If Simulator & AI Endpoints
# =============================================================================

def test_simulator_loan_endpoint():
    payload = {
        "loan_amount": 200000.0,
        "interest_rate": 11.5,
        "tenure_months": 24,
        "processing_fee": 2000.0
    }
    response = client.post("/api/v1/simulator/loan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "calculations" in data["data"]
    assert "impact" in data["data"]

def test_simulator_emi_endpoint():
    payload = {
        "principal": 100000.0,
        "interest_rate": 10.5,
        "tenure_months": 12
    }
    response = client.post("/api/v1/simulator/emi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["amortization_schedule"]) == 12

def test_ai_explain_endpoint():
    payload = {
        "context_type": "risk_score",
        "context_data": {
            "risk_score": 18.5,
            "risk_category": "critical",
            "factors": {"liquidity_score": 5.0, "debt_burden_score": 5.0}
        }
    }
    response = client.post("/api/v1/ai/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "CRITICAL" in data["data"]["explanation"]

# =============================================================================
# Debtkart Real-World Case Study Endpoints
# =============================================================================

def test_debtkart_case_study_endpoint():
    response = client.get("/api/v1/debtkart/case-study/saptarshi-masid")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    cs = data["data"]
    assert cs["client_name"] == "Mr. Saptarshi Masid"
    assert cs["total_exposure_amount"] == 2530760.0
    assert cs["final_settlement_amount"] == 635600.0
    assert cs["liability_reduction_amount"] == 1895160.0
    assert cs["savings_percentage"] == 74.88
    assert len(cs["creditor_breakdown"]) == 3

def test_debtkart_info_endpoint():
    response = client.get("/api/v1/debtkart/info")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    info = data["data"]
    assert info["legal_entity"] == "SETTLEND LEGAL ADVISORS LLP"
    assert info["brand"] == "Debtkart"
    assert info["primary_phone"] == "+91 6293629300"
    assert info["primary_email"] == "info@debtkart.in"
    assert "Kolkata" in info["address"]

def test_debtkart_generate_notice_endpoint():
    payload = {
        "customer_id": "cust-01",
        "lender_name": "RBL Bank",
        "account_number": "RBL-CR-119834",
        "outstanding_amount": 660000.0,
        "hardship_details": "Involuntary job termination and critical family medical crisis",
        "request_moratorium_months": 6
    }
    response = client.post("/api/v1/debtkart/generate-notice", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    notice = data["data"]
    assert notice["status"] == "generated"
    assert "RBI FAIR PRACTICES CODE" in notice["notice_content"]
    assert "SETTLEND LEGAL ADVISORS LLP" in notice["notice_content"]
    assert "6 months" in notice["notice_content"]

# =============================================================================
# Officer & Relationship Manager Endpoints
# =============================================================================

def test_officer_portfolio_summary():
    response = client.get("/api/v1/officer/portfolio-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_customers"] >= 2
    assert "critical" in data["data"]["risk_distribution"]

def test_officer_customers_list():
    response = client.get("/api/v1/officer/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["customers"]) >= 2
