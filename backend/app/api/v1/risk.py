from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.database import get_db, Customer, RiskAssessment, Account, Loan
from backend.app.schemas.schemas import ApiResponse
from backend.app.services.risk_engine.scorer import calculate_resilience_score
from backend.app.services.ml_engine.predictor import ml_distress_predictor
from backend.app.services.ai_service.explainer import generate_ai_explanation

router = APIRouter(prefix="/risk", tags=["Risk & Resilience"])

@router.get("/score", response_model=ApiResponse)
def get_risk_score(
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves current explainable Financial Resilience Score (0-100) and factor contributions."""
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
    else:
        customer = db.query(Customer).first()
        
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    # Query latest assessment
    ra = db.query(RiskAssessment).filter(RiskAssessment.customer_id == customer.id).order_by(RiskAssessment.assessment_date.desc()).first()
    
    if ra:
        score_data = {
            "assessment_date": ra.assessment_date.isoformat(),
            "risk_score": ra.risk_score,
            "risk_category": ra.risk_category,
            "previous_score": ra.previous_score,
            "score_change": ra.score_change,
            "trend": ra.trend,
            "factors": {
                "income_stability_score": ra.income_stability_score,
                "liquidity_score": ra.liquidity_score,
                "debt_burden_score": ra.debt_burden_score,
                "payment_behavior_score": ra.payment_behavior_score,
                "credit_utilization_score": ra.credit_utilization_score
            },
            "weights": ra.weights or {},
            "risk_factors": ra.risk_factors or [],
            "ml_distress_probability": ra.ml_distress_probability
        }
    else:
        # Compute dynamically from database
        accounts = db.query(Account).filter(Account.customer_id == customer.id).all()
        loans = db.query(Loan).filter(Loan.customer_id == customer.id).all()
        
        tot_bal = sum(a.current_balance for a in accounts)
        tot_debt = sum(l.outstanding_principal for l in loans)
        tot_emi = sum(l.emi_amount for l in loans)
        inc = customer.monthly_income or 0.0
        exp = 25000.0 if inc == 0 else inc * 0.4
        
        res = calculate_resilience_score(
            monthly_income=inc,
            employment_status=customer.employment_status,
            available_balance=tot_bal,
            monthly_expenses=exp,
            total_debt=tot_debt,
            total_monthly_emi=tot_emi,
            active_loans_count=len(loans)
        )
        score_data = res
        
    # Generate AI explanation
    ai_expl = generate_ai_explanation("risk_score", score_data)
    score_data["explanation"] = ai_expl["explanation"]
    score_data["advisory"] = ai_expl["advisory_recommendation"]
    
    return ApiResponse(data=score_data)

@router.get("/prediction", response_model=ApiResponse)
def get_ml_distress_prediction(
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """ML-powered Financial Distress prediction (Logistic Regression)."""
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
    else:
        customer = db.query(Customer).first()
        
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    inc = customer.monthly_income or 0.0
    loans = db.query(Loan).filter(Loan.customer_id == customer.id).all()
    tot_debt = sum(l.outstanding_principal for l in loans)
    tot_emi = sum(l.emi_amount for l in loans)
    
    dti = tot_debt / (inc * 12) if inc > 0 else 9.9
    foir = tot_emi / inc if inc > 0 else 1.0
    missed = 4 if customer.status in ["distressed", "defaulted"] else 0
    buffer = 0.1 if inc == 0 else 3.5
    
    pred = ml_distress_predictor.predict(
        income_trend=-0.9 if inc == 0 else 0.1,
        income_volatility=0.8 if inc == 0 else 0.1,
        expense_growth_rate=0.2 if inc == 0 else 0.03,
        cash_buffer_months=buffer,
        debt_to_income_ratio=min(10.0, dti),
        emi_to_income_ratio=min(1.5, foir),
        credit_utilization=0.95 if customer.status == "distressed" else 0.3,
        missed_payments_count=missed
    )
    return ApiResponse(data=pred)
