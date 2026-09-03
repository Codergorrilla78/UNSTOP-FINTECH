from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.database import get_db, Customer, Account, Loan
from backend.app.schemas.schemas import ApiResponse
from backend.app.services.forecast_engine.predictor import generate_90_day_cashflow_forecast
from backend.app.services.ai_service.explainer import generate_ai_explanation

router = APIRouter(prefix="/forecast", tags=["Cash Flow Forecast"])

@router.get("", response_model=ApiResponse)
def get_cashflow_forecast(
    customer_id: Optional[str] = None,
    days: int = Query(90, ge=30, le=180),
    db: Session = Depends(get_db)
):
    """Generates day-by-day cashflow forecast over the next 90 days."""
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
    else:
        customer = db.query(Customer).first()
        
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    accounts = db.query(Account).filter(Account.customer_id == customer.id).all()
    loans = db.query(Loan).filter(Loan.customer_id == customer.id, Loan.status != "closed").all()
    
    current_balance = sum(a.current_balance for a in accounts)
    monthly_income = customer.monthly_income or 0.0
    
    # Active EMIs mapping
    active_emis = []
    for l in loans:
        active_emis.append({
            "emi_amount": l.emi_amount,
            "due_day": 5,  # 5th of each month
            "lender_name": l.lender_name
        })
        
    essential_exp = 25000.0 if monthly_income == 0 else monthly_income * 0.35
    discretionary_exp = 0.0 if monthly_income == 0 else monthly_income * 0.15
    
    forecast_data = generate_90_day_cashflow_forecast(
        current_balance=current_balance,
        monthly_income=monthly_income,
        salary_day_of_month=1,
        active_emis=active_emis,
        monthly_essential_expenses=essential_exp,
        monthly_discretionary_expenses=discretionary_exp,
        forecast_days=days
    )
    
    # Enrich with AI narrative
    ai_expl = generate_ai_explanation("forecast", forecast_data["summary"])
    forecast_data["explanation"] = ai_expl["explanation"]
    forecast_data["advisory"] = ai_expl["advisory_recommendation"]
    
    return ApiResponse(data=forecast_data)
