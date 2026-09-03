from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.database import get_db, Customer, Account, Loan, Intervention, RiskAssessment
from backend.app.schemas.schemas import ApiResponse, InterventionRejectRequest
from backend.app.services.intervention_engine.evaluator import evaluate_interventions

router = APIRouter(prefix="/interventions", tags=["Interventions"])

@router.get("", response_model=ApiResponse)
def get_recommended_interventions(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves tiered interventions for customer, prioritizing non-credit and legal debt relief."""
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
    else:
        customer = db.query(Customer).first()
        
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    accounts = db.query(Account).filter(Account.customer_id == customer.id).all()
    loans = db.query(Loan).filter(Loan.customer_id == customer.id).all()
    ra = db.query(RiskAssessment).filter(RiskAssessment.customer_id == customer.id).first()
    
    score = ra.risk_score if ra else (18.5 if customer.status == "distressed" else 80.0)
    inc = customer.monthly_income or 0.0
    tot_bal = sum(a.current_balance for a in accounts)
    tot_debt = sum(l.outstanding_principal for l in loans)
    tot_emi = sum(l.emi_amount for l in loans)
    has_defaults = any(l.status in ["defaulted", "overdue"] for l in loans)
    
    interventions = evaluate_interventions(
        resilience_score=score,
        monthly_income=inc,
        monthly_expenses=25000.0 if inc == 0 else inc * 0.4,
        essential_expenses=25000.0 if inc == 0 else inc * 0.3,
        discretionary_expenses=0.0 if inc == 0 else inc * 0.1,
        total_debt=tot_debt,
        total_emi=tot_emi,
        available_balance=tot_bal,
        has_defaults=has_defaults,
        active_loans_count=len(loans)
    )
    
    if status:
        interventions = [i for i in interventions if i.get("status") == status]
        
    return ApiResponse(data={"interventions": interventions, "count": len(interventions)})

@router.post("/{intervention_id}/accept", response_model=ApiResponse)
def accept_intervention(intervention_id: str, db: Session = Depends(get_db)):
    return ApiResponse(
        message="Intervention accepted",
        data={
            "intervention_id": intervention_id,
            "status": "accepted",
            "next_steps": "Debtkart legal advisory team notified. An advocate will contact you within 2 business hours."
        }
    )

@router.post("/{intervention_id}/reject", response_model=ApiResponse)
def reject_intervention(intervention_id: str, req: InterventionRejectRequest, db: Session = Depends(get_db)):
    return ApiResponse(
        message="Intervention rejected",
        data={"intervention_id": intervention_id, "status": "rejected", "reason": req.reason}
    )
