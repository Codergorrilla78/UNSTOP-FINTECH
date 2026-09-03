from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.database import get_db, Customer, RiskAssessment, Loan, FinancialSnapshot
from backend.app.schemas.schemas import ApiResponse

router = APIRouter(prefix="/officer", tags=["Bank Officer & Relationship Manager"])

@router.get("/customers", response_model=ApiResponse)
def get_officer_customer_portfolio(
    risk_category: Optional[str] = None,
    limit: int = Query(50),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Lists customers assigned to the officer, filtered by risk tier."""
    query = db.query(Customer)
    customers = query.offset(offset).limit(limit).all()
    
    results = []
    for c in customers:
        ra = db.query(RiskAssessment).filter(RiskAssessment.customer_id == c.id).order_by(RiskAssessment.assessment_date.desc()).first()
        loans = db.query(Loan).filter(Loan.customer_id == c.id).all()
        
        tot_debt = sum(l.outstanding_principal for l in loans)
        score = ra.risk_score if ra else 70.0
        cat = ra.risk_category if ra else "healthy"
        
        if risk_category and cat != risk_category:
            continue
            
        results.append({
            "customer_id": c.id,
            "name": f"{c.first_name} {c.last_name}",
            "email": c.email,
            "phone": c.phone,
            "city": c.city,
            "risk_score": score,
            "risk_category": cat,
            "total_debt": tot_debt,
            "employment_status": c.employment_status,
            "status": c.status
        })
        
    return ApiResponse(data={"customers": results, "total_count": len(results)})

@router.get("/portfolio-summary", response_model=ApiResponse)
def get_portfolio_summary(db: Session = Depends(get_db)):
    """Summary metrics of portfolio risk distribution."""
    customers = db.query(Customer).all()
    total = len(customers)
    
    categories = {"critical": 0, "at_risk": 0, "watch": 0, "healthy": 0}
    total_portfolio_debt = 0.0
    
    for c in customers:
        ra = db.query(RiskAssessment).filter(RiskAssessment.customer_id == c.id).first()
        cat = ra.risk_category if ra else "healthy"
        categories[cat] = categories.get(cat, 0) + 1
        
        loans = db.query(Loan).filter(Loan.customer_id == c.id).all()
        total_portfolio_debt += sum(l.outstanding_principal for l in loans)
        
    return ApiResponse(
        data={
            "total_customers": total,
            "total_portfolio_debt": total_portfolio_debt,
            "risk_distribution": categories,
            "critical_cases_requiring_intervention": categories["critical"]
        }
    )
