import pytest
from backend.app.config.settings import settings
from backend.app.models.database import engine
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# =============================================================================
# Settings, Configuration & System Health Verification
# =============================================================================

def test_settings_resilience_scoring_weights_sum_to_one():
    weights_sum = (
        settings.WEIGHT_INCOME_STABILITY +
        settings.WEIGHT_LIQUIDITY +
        settings.WEIGHT_DEBT_BURDEN +
        settings.WEIGHT_PAYMENT_BEHAVIOR +
        settings.WEIGHT_CREDIT_UTILIZATION
    )
    assert round(weights_sum, 4) == 1.0, f"Scoring weights must sum to 1.0, got {weights_sum}"

def test_settings_loan_weights_sum_to_one():
    loan_weights_sum = (
        settings.LOAN_WEIGHT_TOTAL_COST +
        settings.LOAN_WEIGHT_EMI_AFFORDABILITY +
        settings.LOAN_WEIGHT_RESILIENCE_IMPACT +
        settings.LOAN_WEIGHT_TENURE_SUITABILITY +
        settings.LOAN_WEIGHT_FEES +
        settings.LOAN_WEIGHT_FLEXIBILITY
    )
    assert round(loan_weights_sum, 4) == 1.0, f"Loan weights must sum to 1.0, got {loan_weights_sum}"

def test_settings_risk_tier_threshold_hierarchy():
    assert 0 < settings.THRESHOLD_CRITICAL < settings.THRESHOLD_AT_RISK < settings.THRESHOLD_WATCH <= settings.THRESHOLD_HEALTHY
    assert settings.THRESHOLD_CRITICAL == 30.0
    assert settings.THRESHOLD_HEALTHY == 100.0

def test_settings_debtkart_official_credentials():
    assert settings.DEBTKART_LEGAL_ENTITY == "SETTLEND LEGAL ADVISORS LLP"
    assert settings.DEBTKART_BRAND == "Debtkart"
    assert settings.DEBTKART_PHONE == "+91 6293629300"
    assert "Kolkata" in settings.DEBTKART_ADDRESS
    assert settings.DEBTKART_EMAIL == "info@debtkart.in"

def test_database_connection_live():
    with engine.connect() as conn:
        assert conn is not None

def test_health_check_payload_structure():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "healthy"
    assert "engines" in data
    assert len(data["engines"]) == 10
    required_engines = [
        "financial_engine", "risk_engine", "forecast_engine", "ml_engine",
        "overdraft_engine", "loan_engine", "simulator_engine",
        "intervention_engine", "debtkart_service", "ai_service"
    ]
    for eng in required_engines:
        assert eng in data["engines"], f"Missing engine: {eng}"

def test_root_meta_payload_structure():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "partner" in body["data"]
    assert "helpline" in body["data"]
    assert "docs" in body["data"]
