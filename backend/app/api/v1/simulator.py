from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.models.database import get_db, Customer, Loan, RiskAssessment
from backend.app.schemas.schemas import ApiResponse, LoanSimulateRequest, EMISimulateRequest
from backend.app.services.simulator_engine.simulator import simulate_loan_scenario
from backend.app.services.financial_engine.emi import generate_amortization_schedule

router = APIRouter(prefix="/simulator", tags=["What-If Simulator"])

@router.post("/loan", response_model=ApiResponse)
def simulate_loan(req: LoanSimulateRequest, db: Session = Depends(get_db)):
    """Simulates impact of loan terms on monthly surplus and resilience score."""
    customer = db.query(Customer).first()
    inc = customer.monthly_income if customer else 50000.0
    
    loans = db.query(Loan).filter(Loan.customer_id == customer.id).all() if customer else []
    tot_emi = sum(l.emi_amount for l in loans)
    
    ra = db.query(RiskAssessment).filter(RiskAssessment.customer_id == customer.id).first() if customer else None
    score = ra.risk_score if ra else 70.0
    
    result = simulate_loan_scenario(
        loan_amount=req.loan_amount,
        interest_rate=req.interest_rate,
        tenure_months=req.tenure_months,
        processing_fee=req.processing_fee or 0.0,
        current_monthly_income=inc,
        current_total_emi=tot_emi,
        current_risk_score=score
    )
    return ApiResponse(data=result)

@router.post("/emi", response_model=ApiResponse)
def simulate_emi(req: EMISimulateRequest):
    """Calculates EMI and complete monthly amortization breakdown."""
    schedule = generate_amortization_schedule(
        principal=req.principal,
        annual_interest_rate=req.interest_rate,
        tenure_months=req.tenure_months
    )
    return ApiResponse(data=schedule)
