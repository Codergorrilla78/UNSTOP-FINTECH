from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.models.database import get_db, Customer, RiskAssessment, Loan
from backend.app.schemas.schemas import ApiResponse

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("", response_model=ApiResponse)
def get_actionable_recommendations(db: Session = Depends(get_db)):
    """Personalized actionable recommendations based on customer resilience."""
    customer = db.query(Customer).first()
    ra = db.query(RiskAssessment).filter(RiskAssessment.customer_id == customer.id).first() if customer else None
    score = ra.risk_score if ra else 50.0
    
    recs = []
    if score <= 30:
        recs.append({
            "id": "rec-01",
            "type": "debtkart_legal_protection",
            "title": "Enforce RBI Anti-Harassment & Moratorium Notice",
            "description": "Engage Debtkart (Settlend Legal Advisors LLP) to restrain unlawful recovery tactics and establish 6-month moratorium across HDFC, Standard Chartered, and RBL Bank.",
            "priority": 1,
            "impact": "Halts collection harassment immediately and enables up to 74% debt reduction.",
            "status": "active"
        })
        recs.append({
            "id": "rec-02",
            "type": "stop_fragmented_payments",
            "title": "Halt scattered token payments",
            "description": "Cease informal partial payments to individual recovery agents; token sums only get swallowed by late penalties without reducing principal.",
            "priority": 2,
            "impact": "Conserves remaining cash for medical and survival necessities.",
            "status": "active"
        })
    else:
        recs.append({
            "id": "rec-03",
            "type": "emergency_buffer",
            "title": "Automate 15% Monthly Savings Transfer",
            "description": "Set up an automated standing instruction to build a 6-month emergency reserve.",
            "priority": 1,
            "impact": "Improves liquidity factor by 12 points over 90 days.",
            "status": "active"
        })
        
    return ApiResponse(data={"recommendations": recs, "count": len(recs)})
