from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.database import get_db, Customer, Account, Loan
from backend.app.schemas.schemas import ApiResponse, OverdraftCalculateRequest
from backend.app.services.overdraft_engine.calculator import evaluate_overdraft_offer

router = APIRouter(prefix="/overdraft", tags=["Overdraft Intelligence"])

@router.post("/calculate", response_model=ApiResponse)
def calculate_overdraft(req: OverdraftCalculateRequest, db: Session = Depends(get_db)):
    """Calculates short-term liquidity bridging overdraft terms."""
    # Find primary customer
    customer = db.query(Customer).first()
    inc = customer.monthly_income if customer else 0.0
    
    accounts = db.query(Account).filter(Account.customer_id == customer.id).all() if customer else []
    tot_bal = sum(a.current_balance for a in accounts)
    
    loans = db.query(Loan).filter(Loan.customer_id == customer.id).all() if customer else []
    defaults = sum(1 for l in loans if l.status in ["defaulted", "overdue"])
    
    result = evaluate_overdraft_offer(
        required_amount=req.required_amount,
        expected_repayment_date_str=req.expected_repayment_date,
        monthly_income=inc,
        current_balance=tot_bal,
        recent_defaults_count=defaults
    )
    return ApiResponse(data=result)

@router.post("/apply", response_model=ApiResponse)
def apply_overdraft(req: OverdraftCalculateRequest, db: Session = Depends(get_db)):
    """Applies for overdraft support."""
    return ApiResponse(
        message="Overdraft application submitted for credit officer review",
        data={"required_amount": req.required_amount, "status": "submitted"}
    )
