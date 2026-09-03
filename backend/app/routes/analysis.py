from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Customer
from ..services import calculate_financial_resilience

router = APIRouter(
    prefix="/analysis",
    tags=["Financial Analysis"]
)


@router.post("/{customer_id}")
def analyze_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    result = calculate_financial_resilience(
        monthly_income=customer.monthly_income,
        monthly_expenses=customer.monthly_expenses,
        monthly_debt_payment=customer.monthly_debt_payment,
        savings=customer.savings,
        existing_debt=customer.existing_debt
    )

    return {
        "customer_id": customer.id,
        **result
    }