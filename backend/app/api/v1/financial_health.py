from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.database import get_db, Customer, FinancialSnapshot, Account, Loan
from backend.app.schemas.schemas import ApiResponse
from backend.app.services.financial_engine.calculator import (
    calculate_dti, calculate_foir, calculate_monthly_surplus,
    calculate_emergency_fund_runway, calculate_savings_rate
)

router = APIRouter(prefix="/financial-health", tags=["Financial Health"])

@router.get("", response_model=ApiResponse)
def get_financial_health_snapshot(
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Returns complete deterministic financial health snapshot."""
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
    else:
        customer = db.query(Customer).first()
        
    if not customer:
        raise HTTPException(status_code=404, detail="Customer record not found")
        
    # Check snapshot in DB or compute dynamically
    snap = db.query(FinancialSnapshot).filter(FinancialSnapshot.customer_id == customer.id).order_by(FinancialSnapshot.snapshot_date.desc()).first()
    
    if snap:
        data = {
            "customer_id": customer.id,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "snapshot_date": str(snap.snapshot_date),
            "monthly_income": snap.monthly_income,
            "total_balance": snap.total_balance,
            "average_balance": snap.average_balance,
            "total_debt": snap.total_debt,
            "total_emi": snap.total_emi,
            "debt_to_income_ratio": snap.debt_to_income_ratio,
            "emi_to_income_ratio": snap.emi_to_income_ratio,
            "monthly_expenses": snap.monthly_expenses,
            "essential_expenses": snap.essential_expenses,
            "discretionary_expenses": snap.discretionary_expenses,
            "savings_rate": snap.savings_rate,
            "emergency_fund_months": snap.emergency_fund_months
        }
    else:
        # Calculate from active loans and accounts
        accounts = db.query(Account).filter(Account.customer_id == customer.id).all()
        loans = db.query(Loan).filter(Loan.customer_id == customer.id, Loan.status != "closed").all()
        
        tot_bal = sum(a.current_balance for a in accounts)
        tot_debt = sum(l.outstanding_principal for l in loans)
        tot_emi = sum(l.emi_amount for l in loans)
        
        monthly_inc = customer.monthly_income or 0.0
        exp = 25000.0 if monthly_inc == 0 else monthly_inc * 0.4
        
        dti = calculate_dti(tot_debt, monthly_inc * 12)
        foir = calculate_foir(tot_emi, monthly_inc)
        runway = calculate_emergency_fund_runway(tot_bal, exp)
        savings_r = calculate_savings_rate(monthly_inc, exp, tot_emi)
        
        data = {
            "customer_id": customer.id,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "snapshot_date": str(datetime.date.today()),
            "monthly_income": monthly_inc,
            "total_balance": tot_bal,
            "average_balance": tot_bal,
            "total_debt": tot_debt,
            "total_emi": tot_emi,
            "debt_to_income_ratio": dti,
            "emi_to_income_ratio": foir,
            "monthly_expenses": exp,
            "essential_expenses": exp,
            "discretionary_expenses": 0.0,
            "savings_rate": savings_r,
            "emergency_fund_months": runway
        }
        
    return ApiResponse(data=data)
