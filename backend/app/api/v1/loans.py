from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.database import get_db, Customer, Loan, LoanProduct, Lender, RiskAssessment
from backend.app.schemas.schemas import ApiResponse, LoanCompareRequest
from backend.app.services.loan_engine.comparator import compare_and_rank_loans

router = APIRouter(prefix="/loans", tags=["Loans & Comparison"])

@router.get("", response_model=ApiResponse)
def get_customer_loans(
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves existing active loans for customer."""
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
    else:
        customer = db.query(Customer).first()
        
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    loans = db.query(Loan).filter(Loan.customer_id == customer.id).all()
    results = [
        {
            "id": l.id,
            "loan_number": l.loan_number,
            "loan_type": l.loan_type,
            "lender_name": l.lender_name,
            "product_name": l.product_name,
            "principal_amount": l.principal_amount,
            "outstanding_principal": l.outstanding_principal,
            "interest_rate": l.interest_rate,
            "tenure_months": l.tenure_months,
            "emi_amount": l.emi_amount,
            "status": l.status
        }
        for l in loans
    ]
    total_debt = sum(l["outstanding_principal"] for l in results)
    total_emi = sum(l["emi_amount"] for l in results)
    
    return ApiResponse(
        data={
            "customer_id": customer.id,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "loans": results,
            "total_outstanding_debt": total_debt,
            "total_monthly_emi": total_emi,
            "count": len(results)
        }
    )

@router.get("/products", response_model=ApiResponse)
def get_available_loan_products(db: Session = Depends(get_db)):
    """Catalog of market loan products across partner lenders."""
    products = db.query(LoanProduct).filter(LoanProduct.is_active == True).all()
    results = []
    for p in products:
        lender = db.query(Lender).filter(Lender.id == p.lender_id).first()
        results.append({
            "id": p.id,
            "lender_name": lender.lender_name if lender else "Bank",
            "product_name": p.product_name,
            "product_code": p.product_code,
            "min_loan_amount": p.min_loan_amount,
            "max_loan_amount": p.max_loan_amount,
            "min_interest_rate": p.min_interest_rate,
            "max_interest_rate": p.max_interest_rate,
            "min_tenure_months": p.min_tenure_months,
            "max_tenure_months": p.max_tenure_months,
            "processing_fee_percent": p.processing_fee_percent
        })
    return ApiResponse(data={"products": results, "count": len(results)})

@router.post("/compare", response_model=ApiResponse)
def compare_loans(req: LoanCompareRequest, db: Session = Depends(get_db)):
    """Compares market loan products using composite Best-Fit scoring algorithm."""
    customer = db.query(Customer).first()
    inc = customer.monthly_income if customer else 50000.0
    
    loans = db.query(Loan).filter(Loan.customer_id == customer.id).all() if customer else []
    tot_emi = sum(l.emi_amount for l in loans)
    
    ra = db.query(RiskAssessment).filter(RiskAssessment.customer_id == customer.id).first() if customer else None
    score = ra.risk_score if ra else 70.0
    
    # Load products
    products = db.query(LoanProduct).filter(LoanProduct.is_active == True).all()
    prod_dicts = []
    for p in products:
        lender = db.query(Lender).filter(Lender.id == p.lender_id).first()
        prod_dicts.append({
            "id": p.id,
            "lender_name": lender.lender_name if lender else "Bank",
            "product_name": p.product_name,
            "interest_rate": p.min_interest_rate,
            "processing_fee_percent": p.processing_fee_percent,
            "processing_fee_fixed": p.processing_fee_fixed,
            "prepayment_charges_percent": p.prepayment_charges_percent
        })
        
    result = compare_and_rank_loans(
        loan_amount=req.loan_amount,
        tenure_months=req.tenure_months,
        monthly_income=inc,
        current_total_emi=tot_emi,
        current_resilience_score=score,
        available_products=prod_dicts
    )
    return ApiResponse(data=result)
