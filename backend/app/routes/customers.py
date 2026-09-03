from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Customer
from ..schemas import CustomerCreate, CustomerResponse

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post(
    "/",
    response_model=CustomerResponse
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):

    existing = (
        db.query(Customer)
        .filter(Customer.email == customer.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Customer already exists"
        )

    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        monthly_income=customer.monthly_income,
        monthly_expenses=customer.monthly_expenses,
        monthly_debt_payment=customer.monthly_debt_payment,
        savings=customer.savings,
        existing_debt=customer.existing_debt
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
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

    return customer