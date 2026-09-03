from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.models.database import get_db, Customer
from backend.app.schemas.schemas import CustomerResponse, CustomerCreate, CustomerUpdate, ApiResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/me", response_model=ApiResponse)
def get_current_customer_profile(
    email: Optional[str] = Query("saptarshi.masid@kolkata.debtkart.in"),
    db: Session = Depends(get_db)
):
    """Retrieves profile of active customer (defaults to Mr. Saptarshi Masid case study)."""
    customer = db.query(Customer).filter(Customer.email == email).first()
    if not customer:
        customer = db.query(Customer).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return ApiResponse(
        data={
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "employment_status": customer.employment_status,
            "employer_name": customer.employer_name,
            "monthly_income": customer.monthly_income,
            "address": customer.address,
            "city": customer.city,
            "state": customer.state,
            "pin_code": customer.pin_code,
            "status": customer.status,
            "customer_since": str(customer.customer_since)
        }
    )

@router.get("", response_model=ApiResponse)
def list_customers(db: Session = Depends(get_db)):
    """Lists all registered customer profiles."""
    customers = db.query(Customer).all()
    results = [
        {
            "id": c.id,
            "name": f"{c.first_name} {c.last_name}",
            "email": c.email,
            "phone": c.phone,
            "monthly_income": c.monthly_income,
            "employment_status": c.employment_status,
            "status": c.status,
            "city": c.city
        }
        for c in customers
    ]
    return ApiResponse(data={"customers": results, "total": len(results)})

@router.get("/{customer_id}", response_model=ApiResponse)
def get_customer_by_id(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return ApiResponse(
        data={
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "employment_status": customer.employment_status,
            "employer_name": customer.employer_name,
            "monthly_income": customer.monthly_income,
            "city": customer.city,
            "status": customer.status
        }
    )

@router.put("/{customer_id}", response_model=ApiResponse)
def update_customer_profile(customer_id: str, update_data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    if update_data.phone is not None:
        customer.phone = update_data.phone
    if update_data.monthly_income is not None:
        customer.monthly_income = update_data.monthly_income
    if update_data.employment_status is not None:
        customer.employment_status = update_data.employment_status
    if update_data.address is not None:
        customer.address = update_data.address
        
    db.commit()
    db.refresh(customer)
    return ApiResponse(message="Profile updated successfully", data={"id": customer.id, "email": customer.email})
